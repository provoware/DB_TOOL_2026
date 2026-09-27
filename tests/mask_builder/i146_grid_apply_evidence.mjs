import fs from "node:fs";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";

const [targetUrl, outputPath] = process.argv.slice(2);
if (!targetUrl || !outputPath) throw new Error("usage: node i146_grid_apply_evidence.mjs <url> <output.json>");
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
      type, key: "Enter", code: "Enter",
      windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13,
      text: type === "keyDown" ? "\r" : undefined,
      unmodifiedText: type === "keyDown" ? "\r" : undefined,
    });
  }
  await sleep(120);
}

const browser = spawn(browserExecutable(), [
  "--headless=new","--disable-gpu","--no-sandbox","--remote-debugging-port=0",
  "--remote-debugging-address=127.0.0.1",
  "--user-data-dir=" + path.join(process.cwd(), "runtime", "iteration-0146", "chrome-profile"),
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
  await cdp.send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await cdp.send("Page.navigate", { url: targetUrl });
  if (!await waitFor(cdp, 'document.readyState==="complete" && !!document.querySelector("#grid-assistant-button")')) {
    throw new Error("page did not become ready");
  }

  await evaluate(cdp, `(() => {
    const field=document.querySelector('.palette-item[data-kind="field"]');
    const note=document.querySelector('.palette-item[data-kind="note"]');
    field.click(); document.querySelector('.placement-target[data-column="8"]').click();
    note.click(); document.querySelector('.placement-target[data-column="6"]').click();
    field.click(); document.querySelector('.placement-target[data-column="4"]').click();
  })()`);

  const snapshot = () => `(() => ({
    cards:Array.from(document.querySelectorAll(".placed-element")).map((card)=>({
      id:card.dataset.draftId,
      row:card.dataset.gridRow,
      column:card.dataset.gridColumn,
      label:card.getAttribute("aria-label"),
      width:card.querySelector(".width-select")?.value ?? null
    })),
    preview:document.querySelector("#preview").innerText,
    status:document.querySelector("#interaction-status").textContent,
    activeId:document.activeElement?.id ?? null,
    applyExists:!!document.querySelector(".grid-assistant-apply"),
    comparison:document.querySelector("#grid-assistant-output").innerText
  }))()`;

  const before = await evaluate(cdp, snapshot());
  await evaluate(cdp, 'document.querySelector("#grid-assistant-button").click()');
  if (!await waitFor(cdp, '!!document.querySelector(".grid-assistant-apply")')) throw new Error("apply button missing");

  const comparison = await evaluate(cdp, snapshot());
  await evaluate(cdp, 'document.querySelector(".grid-assistant-apply").focus()');
  await pressEnter(cdp);
  const after = await evaluate(cdp, snapshot());

  const failures = [];
  const beforeIds = before.cards.map((x) => x.id);
  const afterIds = after.cards.map((x) => x.id);
  const beforeWidths = before.cards.map((x) => x.width);
  const afterWidths = after.cards.map((x) => x.width);
  const beforeLabels = before.cards.map((x) => x.label);
  const afterLabels = after.cards.map((x) => x.label);
  const afterPositions = after.cards.map((x) => [x.row, x.column]);

  if (!comparison.applyExists) failures.push("apply-control");
  if (!comparison.comparison.includes("Geplante Änderung")) failures.push("before-after-comparison");
  if (JSON.stringify(beforeIds) !== JSON.stringify(afterIds)) failures.push("draft-order-changed");
  if (JSON.stringify(beforeWidths) !== JSON.stringify(afterWidths)) failures.push("widths-changed");
  if (JSON.stringify(beforeLabels) !== JSON.stringify(afterLabels)) failures.push("draft-labels-changed");
  if (JSON.stringify(afterPositions) !== JSON.stringify([["1","0"],["1","4"],["2","0"]])) failures.push("temporary-layout-not-applied");
  if (after.applyExists) failures.push("apply-still-offered");
  if (after.activeId !== "grid-assistant-button") failures.push("focus-not-returned");
  if (!after.status.includes("browserlokal übernommen")) failures.push("status");
  if (!after.preview.includes("Spalten 1–4") || !after.preview.includes("Spalten 5–10")) failures.push("preview-not-synced");

  const evidence = {
    iteration:146,
    overall_status:failures.length===0 ? "GREEN" : "RED",
    failures,
    before,
    comparison,
    after
  };
  fs.mkdirSync(path.dirname(outputPath), { recursive:true });
  fs.writeFileSync(outputPath, JSON.stringify(evidence,null,2)+"\n","utf8");
  cdp.close();
  if (failures.length) process.exitCode=2;
} finally {
  browser.kill("SIGTERM");
}
