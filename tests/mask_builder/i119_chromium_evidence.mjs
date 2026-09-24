import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import net from "node:net";
import { spawn, spawnSync } from "node:child_process";

const [targetUrl, outputPath, scalesArg = "100,150"] = process.argv.slice(2);
if (!targetUrl || !outputPath) {
  throw new Error("usage: node i119_chromium_evidence.mjs <url> <output.json> [100,150,200]");
}

const SCALE_CONFIG = {
  100: { width: 1440, height: 900, dpr: 1 },
  150: { width: 960, height: 600, dpr: 1.5 },
  200: { width: 720, height: 450, dpr: 2 },
};
const requestedScales = scalesArg.split(",").map((value) => Number(value.trim()));
for (const scale of requestedScales) {
  if (!SCALE_CONFIG[scale]) throw new Error("unsupported scale: " + String(scale));
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function browserExecutable() {
  for (const candidate of ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]) {
    const result = spawnSync("which", [candidate], { encoding: "utf8" });
    if (result.status === 0 && result.stdout.trim()) return result.stdout.trim();
  }
  throw new Error("No Chrome/Chromium executable found.");
}

async function freePort() {
  return await new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = address.port;
      server.close(() => resolve(port));
    });
  });
}

async function pollJson(url, timeoutMs = 10000) {
  const deadline = Date.now() + timeoutMs;
  let lastError = null;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
    } catch (error) {
      lastError = error;
    }
    await sleep(100);
  }
  throw new Error("Timed out waiting for " + url + (lastError ? ": " + lastError.message : ""));
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
        const callbacks = this.handlers.get(message.method) || [];
        callbacks.forEach((callback) => callback(message.params || {}));
      });
    });
  }

  on(method, callback) {
    const callbacks = this.handlers.get(method) || [];
    callbacks.push(callback);
    this.handlers.set(method, callbacks);
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  close() {
    this.ws.close();
  }
}

function keyMeta(key) {
  const map = {
    Enter: { code: "Enter", vk: 13 },
    Tab: { code: "Tab", vk: 9 },
    ArrowDown: { code: "ArrowDown", vk: 40 },
    End: { code: "End", vk: 35 },
  };
  return map[key] || { code: key, vk: 0 };
}

async function pressKey(cdp, key) {
  const meta = keyMeta(key);
  const text = key === "Enter" ? "\r" : undefined;
  await cdp.send("Input.dispatchKeyEvent", {
    type: "keyDown",
    key,
    code: meta.code,
    text,
    unmodifiedText: text,
    windowsVirtualKeyCode: meta.vk,
    nativeVirtualKeyCode: meta.vk,
  });
  await cdp.send("Input.dispatchKeyEvent", {
    type: "keyUp",
    key,
    code: meta.code,
    windowsVirtualKeyCode: meta.vk,
    nativeVirtualKeyCode: meta.vk,
  });
  await sleep(80);
}

async function evaluate(cdp, expression) {
  const result = await cdp.send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
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

async function focus(cdp, selector, index = 0) {
  const expression = "(() => { const list = document.querySelectorAll(" + JSON.stringify(selector)
    + "); const el = list[" + String(index)
    + "]; if (!el) return false; el.focus(); return document.activeElement === el; })()";
  return Boolean(await evaluate(cdp, expression));
}

function sha256(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

async function runScale(cdp, scale, screenshotDir, browserErrors) {
  const config = SCALE_CONFIG[scale];
  const checks = [];
  const startErrorIndex = browserErrors.length;

  async function check(name, fn) {
    try {
      const detail = await fn();
      checks.push({ name, status: "GREEN", detail: detail === undefined ? null : detail });
    } catch (error) {
      checks.push({ name, status: "RED", detail: error.message });
    }
  }

  const expect = (condition, message) => {
    if (!condition) throw new Error(message);
  };

  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: config.width,
    height: config.height,
    deviceScaleFactor: config.dpr,
    mobile: false,
  });
  await cdp.send("Page.navigate", { url: targetUrl });
  expect(
    await waitFor(cdp, 'document.readyState === "complete" && !!document.querySelector(".palette-item")'),
    "page did not become ready"
  );

  await check("initial-no-horizontal-overflow", async () => {
    const metrics = await evaluate(cdp, "({scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth})");
    expect(metrics.scrollWidth <= metrics.clientWidth, JSON.stringify(metrics));
    return metrics;
  });

  await check("keyboard-focus-visible", async () => {
    await evaluate(cdp, "if (document.activeElement) document.activeElement.blur();");
    await pressKey(cdp, "Tab");
    const result = await evaluate(
      cdp,
      '(() => { const el=document.activeElement; const s=getComputedStyle(el); return {className:el.className,focusVisible:el.matches(":focus-visible"),outlineWidth:s.outlineWidth,outlineStyle:s.outlineStyle,outlineOffset:s.outlineOffset}; })()'
    );
    expect(String(result.className).includes("palette-item"), JSON.stringify(result));
    expect(result.focusVisible === true, JSON.stringify(result));
    expect(parseFloat(result.outlineWidth) >= 3, JSON.stringify(result));
    return result;
  });

  await check("keyboard-place-field", async () => {
    expect(await focus(cdp, '.palette-item[data-kind="field"]'), "field palette focus failed");
    await pressKey(cdp, "Enter");
    expect(await evaluate(cdp, 'document.querySelector(\'.palette-item[data-kind="field"]\').getAttribute("aria-pressed") === "true"'), "field palette was not selected");
    expect(await focus(cdp, '.placement-target[data-column="2"]'), "target column focus failed");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.querySelectorAll(".placed-element").length === 1'), "field was not placed");
    return await evaluate(cdp, 'document.querySelector("#preview").innerText');
  });

  const expectedControls = [
    ".edit-label", ".edit-help", ".toggle-required", ".datatype-select",
    ".default-value-control", ".width-select", ".toggle-visibility",
    ".move-draft", ".remove-draft",
  ];
  await check("property-controls-reachable", async () => {
    const expression = "(() => { const selectors=" + JSON.stringify(expectedControls)
      + "; return selectors.map((selector)=>{ const el=document.querySelector(selector); if(!el) return {selector,exists:false}; el.focus(); return {selector,exists:true,disabled:!!el.disabled,tabIndex:el.tabIndex,focused:document.activeElement===el,width:el.getBoundingClientRect().width}; }); })()";
    const result = await evaluate(cdp, expression);
    for (const item of result) {
      expect(item.exists && !item.disabled && item.tabIndex >= 0 && item.focused && item.width > 0, JSON.stringify(item));
    }
    return result;
  });

  await check("label-edit-keyboard-and-focus-return", async () => {
    expect(await focus(cdp, ".edit-label"), "edit-label focus failed");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.activeElement && document.activeElement.classList.contains("label-editor-input")'), "label input did not receive focus");
    await cdp.send("Input.insertText", { text: "Kundenname" });
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.querySelector(".placed-element > span").textContent === "Kundenname"'), "label was not saved");
    const active = await evaluate(cdp, 'document.activeElement ? document.activeElement.className : ""');
    expect(String(active).includes("edit-label"), "label focus was not restored: " + String(active));
    return active;
  });

  await check("help-edit-keyboard-and-focus-return", async () => {
    expect(await focus(cdp, ".edit-help"), "edit-help focus failed");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.activeElement && document.activeElement.classList.contains("help-editor-input")'), "help textarea did not receive focus");
    await cdp.send("Input.insertText", { text: "Kurzhilfe" });
    await pressKey(cdp, "Tab");
    expect(await evaluate(cdp, 'document.activeElement && document.activeElement.classList.contains("save-help")'), "save-help did not receive focus");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.querySelector(".draft-help-text").textContent === "Kurzhilfe"'), "help text was not saved");
    const active = await evaluate(cdp, 'document.activeElement ? document.activeElement.className : ""');
    expect(String(active).includes("edit-help"), "help focus was not restored: " + String(active));
    return active;
  });

  await check("required-toggle-keyboard-and-focus-return", async () => {
    expect(await focus(cdp, ".toggle-required"), "required toggle focus failed");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.querySelector(".toggle-required").getAttribute("aria-pressed") === "true"'), "required state did not toggle");
    const active = await evaluate(cdp, 'document.activeElement ? document.activeElement.className : ""');
    expect(String(active).includes("toggle-required"), "required focus was not restored: " + String(active));
    return active;
  });

  await check("visibility-toggle-preview-and-focus-return", async () => {
    expect(await focus(cdp, ".toggle-visibility"), "visibility toggle focus failed");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.querySelector(".toggle-visibility").getAttribute("aria-pressed") === "false"'), "visibility did not toggle off");
    expect(await evaluate(cdp, 'document.querySelector("#preview").innerText.includes("Alle platzierten Komponenten")'), "preview did not reflect hidden state");
    let active = await evaluate(cdp, 'document.activeElement ? document.activeElement.className : ""');
    expect(String(active).includes("toggle-visibility"), "visibility focus was not restored");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.querySelector(".toggle-visibility").getAttribute("aria-pressed") === "true"'), "visibility did not toggle back on");
    active = await evaluate(cdp, 'document.activeElement ? document.activeElement.className : ""');
    expect(String(active).includes("toggle-visibility"), "visibility focus lost after second toggle");
    return active;
  });

  await check("width-keyboard-preview-and-focus-return", async () => {
    expect(await focus(cdp, ".width-select"), "width select focus failed");
    const before = Number(await evaluate(cdp, 'document.querySelector(".width-select").value'));
    await pressKey(cdp, "ArrowDown");
    const after = Number(await evaluate(cdp, 'document.querySelector(".width-select").value'));
    expect(after === before + 1, "width did not advance: " + before + " -> " + after);
    const active = await evaluate(cdp, 'document.activeElement ? document.activeElement.className : ""');
    expect(String(active).includes("width-select"), "width focus was not restored: " + String(active));
    return { before, after, active };
  });

  await check("datatype-keyboard-and-focus-return", async () => {
    expect(await focus(cdp, ".datatype-select"), "datatype select focus failed");
    await pressKey(cdp, "ArrowDown");
    expect(await waitFor(cdp, 'document.querySelector(".datatype-select").value === "number"'), "datatype did not change to number");
    const active = await evaluate(cdp, 'document.activeElement ? document.activeElement.className : ""');
    expect(String(active).includes("datatype-select"), "datatype focus was not restored");
    return active;
  });

  await check("default-value-keyboard-preview-and-focus-return", async () => {
    expect(await focus(cdp, ".default-value-control"), "default value focus failed");
    await cdp.send("Input.insertText", { text: "42" });
    await pressKey(cdp, "Tab");
    expect(await waitFor(cdp, 'document.querySelector("#preview").innerText.includes("Standard: 42")'), "default value was not reflected in preview");
    const active = await evaluate(cdp, 'document.activeElement ? document.activeElement.className : ""');
    expect(String(active).includes("default-value-control"), "default value focus was not restored: " + String(active));
    return active;
  });

  await check("choice-options-keyboard-add-reorder-remove", async () => {
    expect(await focus(cdp, ".datatype-select"), "datatype select focus failed before choice");
    await pressKey(cdp, "End");
    expect(await waitFor(cdp, 'document.querySelector(".datatype-select").value === "multi_choice"'), "datatype did not change to multi_choice");
    expect(await waitFor(cdp, '!!document.querySelector(".option-editor-input")'), "option input missing");

    expect(await focus(cdp, ".option-editor-input"), "option input focus failed");
    await cdp.send("Input.insertText", { text: "Rot" });
    await pressKey(cdp, "Tab");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.querySelectorAll(".choice-option-row").length === 1'), "first option not added");

    await cdp.send("Input.insertText", { text: "Blau" });
    await pressKey(cdp, "Tab");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.querySelectorAll(".choice-option-row").length === 2'), "second option not added");

    expect(await focus(cdp, ".move-option-down:not([disabled])"), "move-down focus failed");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.querySelector("#preview").innerText.includes("Auswahloptionen: Blau | Rot")'), "option reorder not reflected in preview");

    expect(await focus(cdp, ".remove-option"), "remove-option focus failed");
    await pressKey(cdp, "Enter");
    expect(await waitFor(cdp, 'document.querySelectorAll(".choice-option-row").length === 1'), "option remove failed");
    return await evaluate(cdp, 'document.querySelector("#preview").innerText');
  });

  await check("final-no-horizontal-overflow", async () => {
    const metrics = await evaluate(cdp, "({scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,bodyScrollWidth:document.body.scrollWidth})");
    expect(metrics.scrollWidth <= metrics.clientWidth, JSON.stringify(metrics));
    expect(metrics.bodyScrollWidth <= metrics.clientWidth, JSON.stringify(metrics));
    return metrics;
  });

  const screenshot = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  const png = Buffer.from(screenshot.data, "base64");
  const screenshotPath = path.join(screenshotDir, "properties-" + String(scale) + ".png");
  fs.writeFileSync(screenshotPath, png);

  const newErrors = browserErrors.slice(startErrorIndex);
  checks.push({ name: "browser-errors", status: newErrors.length === 0 ? "GREEN" : "RED", detail: newErrors });

  return {
    scale_percent: scale,
    css_viewport: { width: config.width, height: config.height },
    device_scale_factor: config.dpr,
    screenshot_path: screenshotPath,
    screenshot_sha256: sha256(png),
    checks,
    status: checks.every((item) => item.status === "GREEN") ? "GREEN" : "RED",
  };
}

const browserPath = browserExecutable();
const port = await freePort();
const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), "provoware-i119-chrome-"));
const outputDir = path.dirname(outputPath);
const screenshotDir = path.join(outputDir, "screenshots");
fs.mkdirSync(screenshotDir, { recursive: true });

const browser = spawn(browserPath, [
  "--headless=new",
  "--no-sandbox",
  "--disable-gpu",
  "--disable-dev-shm-usage",
  "--remote-debugging-address=127.0.0.1",
  "--remote-debugging-port=" + String(port),
  "--user-data-dir=" + profileDir,
  "about:blank",
], { stdio: ["ignore", "ignore", "pipe"] });

let browserStderr = "";
browser.stderr.on("data", (chunk) => { browserStderr += String(chunk); });

let cdp = null;
try {
  const targets = await pollJson("http://127.0.0.1:" + String(port) + "/json/list");
  const pageTarget = targets.find((target) => target.type === "page");
  if (!pageTarget || !pageTarget.webSocketDebuggerUrl) {
    throw new Error("No page CDP target available. Browser stderr: " + browserStderr);
  }

  cdp = new CdpClient(pageTarget.webSocketDebuggerUrl);
  await cdp.open();
  const browserErrors = [];
  cdp.on("Runtime.exceptionThrown", (params) => {
    browserErrors.push({ type: "page-exception", text: params.exceptionDetails?.text || "exception" });
  });
  cdp.on("Runtime.consoleAPICalled", (params) => {
    if (params.type === "error" || params.type === "warning") {
      browserErrors.push({ type: "console-" + params.type, text: JSON.stringify(params.args || []) });
    }
  });
  cdp.on("Log.entryAdded", (params) => {
    const entry = params.entry || {};
    if (entry.level === "error" || entry.level === "warning") {
      browserErrors.push({ type: "log-" + entry.level, text: entry.text || "" });
    }
  });

  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Log.enable");

  const results = [];
  for (const scale of requestedScales) results.push(await runScale(cdp, scale, screenshotDir, browserErrors));

  const evidence = {
    iteration: 119,
    source_url: targetUrl,
    browser_executable: browserPath,
    scales: results,
    overall_status: results.every((item) => item.status === "GREEN") ? "GREEN" : "RED",
  };
  fs.writeFileSync(outputPath, JSON.stringify(evidence, null, 2) + "\n", "utf8");
  process.stdout.write(JSON.stringify(evidence, null, 2) + "\n");
  process.exitCode = evidence.overall_status === "GREEN" ? 0 : 2;
} finally {
  if (cdp) cdp.close();
  browser.kill("SIGTERM");
  await sleep(100);
  fs.rmSync(profileDir, { recursive: true, force: true });
}
