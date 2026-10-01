import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";

const [targetUrl, outputPath] = process.argv.slice(2);
if (!targetUrl || !outputPath) {
  throw new Error("usage: node i175_chromium_evidence.mjs <url> <output.json>");
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function browserExecutable() {
  for (const candidate of ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]) {
    const result = spawnSync("which", [candidate], { encoding: "utf8" });
    if (result.status === 0 && result.stdout.trim()) return result.stdout.trim();
  }
  throw new Error("No Chrome/Chromium executable found.");
}

async function pollJson(url, timeoutMs = 10000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
    } catch {}
    await sleep(100);
  }
  throw new Error("Timed out waiting for " + url);
}

class CdpClient {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.handlers = new Map();
  }

  async open() {
    await new Promise((resolve, reject) => {
      this.ws.addEventListener("open", resolve, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
      this.ws.addEventListener("message", (event) => {
        const message = JSON.parse(String(event.data));
        if (message.id !== undefined) {
          const pending = this.pending.get(message.id);
          if (!pending) return;
          this.pending.delete(message.id);
          if (message.error) pending.reject(new Error(message.error.message));
          else pending.resolve(message.result || {});
          return;
        }
        for (const handler of this.handlers.get(message.method) || []) handler(message.params || {});
      });
    });
  }

  on(method, handler) {
    this.handlers.set(method, [...(this.handlers.get(method) || []), handler]);
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  close() { this.ws.close(); }
}

async function evaluate(cdp, expression) {
  const result = await cdp.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || "Runtime.evaluate failed");
  return result.result ? result.result.value : undefined;
}

async function waitFor(cdp, expression, timeoutMs = 5000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await evaluate(cdp, expression)) return true;
    await sleep(80);
  }
  return false;
}

async function pressEnter(cdp) {
  for (const type of ["keyDown", "keyUp"]) {
    await cdp.send("Input.dispatchKeyEvent", {
      type, key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13,
      text: type === "keyDown" ? "\r" : undefined,
    });
  }
  await sleep(100);
}

function sha256(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

const browserPath = browserExecutable();
const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), "provoware-i175-chrome-"));
const browser = spawn(browserPath, [
  "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage",
  "--force-dark-mode", "--remote-debugging-port=0", "--remote-debugging-address=127.0.0.1",
  "--user-data-dir=" + profileDir, "about:blank",
], { stdio: ["ignore", "ignore", "pipe"] });

let debugPort = null;
let browserStderr = "";
browser.stderr.setEncoding("utf8");
browser.stderr.on("data", (chunk) => {
  browserStderr += chunk;
  const match = chunk.match(/DevTools listening on ws:\/\/127\.0\.0\.1:(\d+)\//);
  if (match) debugPort = Number(match[1]);
});

let cdp = null;
try {
  const deadline = Date.now() + 10000;
  while (debugPort === null && Date.now() < deadline) await sleep(50);
  if (debugPort === null) throw new Error("Chromium debug port unavailable: " + browserStderr);

  const targets = await pollJson(`http://127.0.0.1:${debugPort}/json`);
  const pageTarget = targets.find((item) => item.type === "page");
  if (!pageTarget?.webSocketDebuggerUrl) throw new Error("No page CDP target available.");

  cdp = new CdpClient(pageTarget.webSocketDebuggerUrl);
  await cdp.open();
  const browserErrors = [];
  cdp.on("Runtime.exceptionThrown", (params) => browserErrors.push(params.exceptionDetails?.text || "exception"));
  cdp.on("Runtime.consoleAPICalled", (params) => {
    if (["error", "warning"].includes(params.type)) browserErrors.push("console-" + params.type);
  });
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: 1440, height: 900, deviceScaleFactor: 1, mobile: false,
  });
  await cdp.send("Emulation.setEmulatedMedia", {
    features: [{ name: "prefers-color-scheme", value: "dark" }],
  });
  await cdp.send("Page.navigate", { url: targetUrl });
  if (!await waitFor(cdp, 'document.readyState === "complete" && !!document.querySelector(".palette-item")')) {
    throw new Error("Editor page did not become ready.");
  }

  await evaluate(cdp, `(() => {
    document.querySelector('.palette-item[data-kind="field"]').click();
    document.querySelector('.placement-target').click();
    const dataType = document.querySelector('.datatype-select');
    dataType.value = "date";
    dataType.dispatchEvent(new Event("change", { bubbles: true }));
  })()`);
  if (!await waitFor(cdp, '!!document.querySelector(".date-range-preview")')) {
    throw new Error("Date-range preview did not open.");
  }
  const dateStates = await evaluate(cdp, `(() => {
    const from = document.querySelector(".date-range-from");
    const to = document.querySelector(".date-range-to");
    const value = document.querySelector(".date-range-value");
    const result = document.querySelector(".date-range-result");
    from.value = "2026-01-10"; to.value = "2026-01-20"; value.value = "2026-01-09";
    value.dispatchEvent(new Event("input", { bubbles: true }));
    const violated = result.dataset.ruleState;
    value.value = "2026-01-15"; value.dispatchEvent(new Event("input", { bubbles: true }));
    return { violated, satisfied: result.dataset.ruleState, live: result.getAttribute("aria-live"), described: value.getAttribute("aria-describedby") };
  })()`);
  await evaluate(cdp, `(() => {
    const dataType = document.querySelector('.datatype-select');
    dataType.value = "file";
    dataType.dispatchEvent(new Event("change", { bubbles: true }));
  })()`);
  if (!await waitFor(cdp, '!!document.querySelector(".file-type-preview")')) {
    throw new Error("File-type preview did not open.");
  }
  const fileStates = await evaluate(cdp, `(() => {
    const types = document.querySelector(".file-type-extensions");
    const value = document.querySelector(".file-type-value");
    const result = document.querySelector(".file-type-result");
    types.value = ".pdf, .jpg"; value.value = "rechnung.exe";
    value.dispatchEvent(new Event("input", { bubbles: true }));
    const violated = result.dataset.ruleState;
    value.value = "rechnung.PDF"; value.dispatchEvent(new Event("input", { bubbles: true }));
    return { violated, satisfied: result.dataset.ruleState, live: result.getAttribute("aria-live"), described: value.getAttribute("aria-describedby") };
  })()`);
  const layout = await evaluate(cdp, `({
    viewport: { width: innerWidth, height: innerHeight },
    dark: matchMedia("(prefers-color-scheme: dark)").matches,
    overflow: document.documentElement.scrollWidth <= document.documentElement.clientWidth,
  })`);

  const failures = [];
  if (dateStates.violated !== "violated" || dateStates.satisfied !== "satisfied") failures.push("date-states");
  if (fileStates.violated !== "violated" || fileStates.satisfied !== "satisfied") failures.push("file-states");
  if (dateStates.live !== "polite" || fileStates.live !== "polite") failures.push("live-status");
  if (!dateStates.described?.includes("date-range-help-") || !fileStates.described?.includes("file-type-help-")) failures.push("description-link");
  if (layout.viewport.width !== 1440 || layout.viewport.height !== 900 || !layout.dark) failures.push("viewport-or-theme");
  if (!layout.overflow) failures.push("horizontal-overflow");
  if (browserErrors.length) failures.push("browser-errors");

  const screenshot = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  const png = Buffer.from(screenshot.data, "base64");
  const screenshotPath = path.join(path.dirname(outputPath), "i175-rule-previews-1440x900-dark.png");
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(screenshotPath, png);
  const version = await cdp.send("Browser.getVersion");
  const evidence = {
    iteration: 175,
    overall_status: failures.length === 0 ? "GREEN" : "RED",
    browser_executable: browserPath,
    browser_product: version.product,
    viewport: layout.viewport,
    theme: "dark",
    date_states: dateStates, file_states: fileStates, layout, browser_errors: browserErrors,
    screenshot_path: screenshotPath,
    screenshot_sha256: sha256(png),
    failures,
  };
  fs.writeFileSync(outputPath, JSON.stringify(evidence, null, 2) + "\n", "utf8");
  process.stdout.write(JSON.stringify(evidence, null, 2) + "\n");
  process.exitCode = failures.length === 0 ? 0 : 2;
} finally {
  if (cdp) cdp.close();
  browser.kill("SIGTERM");
  await sleep(100);
  fs.rmSync(profileDir, { recursive: true, force: true });
}
