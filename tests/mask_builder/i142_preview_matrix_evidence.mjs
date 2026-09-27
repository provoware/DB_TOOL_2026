import fs from "node:fs";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";

const [targetUrl, outputPath] = process.argv.slice(2);
if (!targetUrl || !outputPath) {
  throw new Error("usage: node i142_preview_matrix_evidence.mjs <url> <output.json>");
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
  }

  async open() {
    await new Promise((resolve, reject) => {
      this.ws.addEventListener("open", resolve, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
      this.ws.addEventListener("message", (event) => {
        const message = JSON.parse(String(event.data));
        if (message.id === undefined) return;
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(message.error.message));
        else pending.resolve(message.result || {});
      });
    });
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

async function focus(cdp, selector) {
  return Boolean(await evaluate(cdp, `(() => { const el=document.querySelector(${JSON.stringify(selector)}); if(!el) return false; el.focus(); return document.activeElement===el; })()`));
}

async function pressEnter(cdp) {
  for (const type of ["keyDown", "keyUp"]) {
    await cdp.send("Input.dispatchKeyEvent", {
      type,
      key: "Enter",
      code: "Enter",
      windowsVirtualKeyCode: 13,
      nativeVirtualKeyCode: 13,
      text: type === "keyDown" ? "\r" : undefined,
      unmodifiedText: type === "keyDown" ? "\r" : undefined,
    });
  }
  await sleep(100);
}

const browser = spawn(browserExecutable(), [
  "--headless=new",
  "--disable-gpu",
  "--no-sandbox",
  "--remote-debugging-port=0",
  "--remote-debugging-address=127.0.0.1",
  "--user-data-dir=" + path.join(process.cwd(), "runtime", "iteration-0142", "chrome-profile"),
  "about:blank",
], { stdio: ["ignore", "ignore", "pipe"] });

let debugPort = null;
browser.stderr.setEncoding("utf8");
browser.stderr.on("data", (chunk) => {
  const match = chunk.match(/DevTools listening on ws:\/\/127\.0\.0\.1:(\d+)\//);
  if (match) debugPort = Number(match[1]);
});

try {
  const deadline = Date.now() + 10000;
  while (debugPort === null && Date.now() < deadline) await sleep(50);
  if (debugPort === null) throw new Error("Chromium debug port unavailable");

  const targets = await pollJson(`http://127.0.0.1:${debugPort}/json`);
  const pageTarget = targets.find((item) => item.type === "page");
  if (!pageTarget) throw new Error("No page target");

  const cdp = new CdpClient(pageTarget.webSocketDebuggerUrl);
  await cdp.open();
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: 1440,
    height: 900,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await cdp.send("Page.navigate", { url: targetUrl });
  if (!await waitFor(cdp, 'document.readyState==="complete" && !!document.querySelector(".preview-mode-button")')) {
    throw new Error("page did not become ready");
  }

  // Create deterministic preview content once. It must remain identical across viewport switches.
  await evaluate(cdp, `(() => {
    const field=document.querySelector('.palette-item[data-kind="field"]');
    field.click();
    document.querySelector('.placement-target[data-column="1"]').click();
    const section=document.querySelector('.palette-item[data-kind="section"]');
    section.click();
    document.querySelector('.placement-target[data-column="0"]').click();
    field.click();
    document.querySelector('.placement-target[data-column="2"]').click();
  })()`);

  const baselineText = await evaluate(cdp, 'document.querySelector("#preview").innerText');
  const modes = [
    { mode: "desktop", width: "1152", label: "Desktop · 1152 px" },
    { mode: "tablet", width: "768", label: "Tablet · 768 px" },
    { mode: "narrow", width: "360", label: "Schmal · 360 px" },
  ];
  const results = [];

  for (const expected of modes) {
    const selector = `.preview-mode-button[data-preview-mode="${expected.mode}"]`;
    if (!await focus(cdp, selector)) throw new Error("focus failed: " + expected.mode);
    await pressEnter(cdp);

    const state = await evaluate(cdp, `(() => {
      const active=document.activeElement;
      const preview=document.querySelector("#preview");
      const shell=document.querySelector(".preview-viewport-shell");
      const label=document.querySelector("#preview-mode-label");
      const pressed=Array.from(document.querySelectorAll(".preview-mode-button")).map((b)=>({
        mode:b.dataset.previewMode,
        pressed:b.getAttribute("aria-pressed")
      }));
      return {
        activeModeButton: active && active.classList.contains("preview-mode-button") ? active.dataset.previewMode : null,
        mode: preview.dataset.previewMode,
        width: preview.dataset.previewWidth,
        label: label.textContent,
        ariaLabel: shell.getAttribute("aria-label"),
        text: preview.innerText,
        pageScrollWidth: document.documentElement.scrollWidth,
        pageClientWidth: document.documentElement.clientWidth,
        shellScrollWidth: shell.scrollWidth,
        shellClientWidth: shell.clientWidth,
        previewRectWidth: Math.round(preview.getBoundingClientRect().width),
        pressed
      };
    })()`);

    const activePressed = state.pressed.filter((item) => item.pressed === "true");
    const expectedRect = Number(expected.width);
    const failures = [];
    if (state.activeModeButton !== expected.mode) failures.push("focus-not-retained");
    if (state.mode !== expected.mode) failures.push("mode");
    if (state.width !== expected.width) failures.push("width-contract");
    if (state.label !== expected.label) failures.push("label");
    if (!state.ariaLabel.includes(expected.width + " Pixel breit")) failures.push("aria-label");
    if (state.text !== baselineText) failures.push("preview-content-changed");
    if (state.pageScrollWidth > state.pageClientWidth) failures.push("page-horizontal-overflow");
    if (Math.abs(state.previewRectWidth - expectedRect) > 1) failures.push("rendered-width");
    if (activePressed.length !== 1 || activePressed[0].mode !== expected.mode) failures.push("aria-pressed");
    if (expected.mode !== "narrow" && state.shellScrollWidth <= state.shellClientWidth) failures.push("expected-local-preview-scroll");

    results.push({
      ...expected,
      status: failures.length === 0 ? "GREEN" : "RED",
      failures,
      state,
    });
  }

  const overall = results.every((item) => item.status === "GREEN") ? "GREEN" : "RED";
  const evidence = {
    iteration: 142,
    overall_status: overall,
    baseline_preview_text: baselineText,
    checks: results,
  };
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(evidence, null, 2) + "\n", "utf8");
  cdp.close();

  if (overall !== "GREEN") process.exitCode = 2;
} finally {
  browser.kill("SIGTERM");
}
