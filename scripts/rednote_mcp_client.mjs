#!/usr/bin/env node

import { Client } from "../vendor/rednote-runtime/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js";
import { StdioClientTransport } from "../vendor/rednote-runtime/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";

const projectRoot = new URL("..", import.meta.url).pathname.replace(/\/$/, "");
const nodePath = `${projectRoot}/vendor/node-runtime/bin/node`;
const serverPath = `${projectRoot}/vendor/rednote-runtime/node_modules/rednote-mind-mcp/dist/server.js`;
const browserPath = `${projectRoot}/vendor/playwright-browsers`;
const folderConfig = JSON.parse(readFileSync(`${projectRoot}/state/rednote-folder.json`, "utf8"));

const [toolName, rawArguments = "{}"] = process.argv.slice(2);
const callTimeoutMs = Number(process.env.MCP_CALL_TIMEOUT_MS || (toolName === "login" ? 660000 : toolName === "get_batch_notes_from_favorites" ? 1800000 : 600000));

if (!toolName) {
  console.error("Usage: rednote_mcp_client.mjs <tool-name|--list-tools> [json-arguments]");
  process.exit(2);
}

let toolArguments;
try {
  toolArguments = JSON.parse(rawArguments);
  if (toolName === "login" && toolArguments.timeout === undefined) {
    toolArguments.timeout = 600000;
  }
  if (toolName === "get_note_content" && process.env.MCP_NOTE_LIST_PATH) {
    const listPath = resolve(process.env.MCP_NOTE_LIST_PATH);
    if (!listPath.startsWith(`${projectRoot}/state/`)) throw new Error("Note list must be inside state/");
    const envelope = JSON.parse(readFileSync(listPath, "utf8"));
    if (envelope.isError) throw new Error("The saved list contains a tool error");
    const notes = JSON.parse(envelope.content.find(block => block.type === "text").text);
    const note = notes[Number(process.env.MCP_NOTE_INDEX || 0)];
    if (!note) throw new Error("Note index is outside the saved list");
    const links = [note.url, ...(note.observed_links || [])];
    const signed = links.map(link => new URL(link)).find(url =>
      url.origin === "https://www.xiaohongshu.com" &&
      url.pathname.endsWith(`/${note.noteId}`) && url.searchParams.has("xsec_token"));
    if (!signed) throw new Error("Saved note has no platform-provided signed link");
    signed.pathname = `/explore/${note.noteId}`;
    toolArguments.noteUrl = signed.toString();
  }
} catch (error) {
  console.error(`Invalid JSON arguments: ${error.message}`);
  process.exit(2);
}

const client = new Client(
  { name: "interview-kb-rednote-client", version: "0.1.0" },
  { capabilities: {} },
);

const transport = new StdioClientTransport({
  command: nodePath,
  args: [serverPath],
  env: {
    ...process.env,
    PLAYWRIGHT_BROWSERS_PATH: browserPath,
    REDNOTE_FAVORITE_FOLDER: process.env.REDNOTE_FAVORITE_FOLDER || "knowledge",
    REDNOTE_FAVORITE_FOLDER_URL: process.env.REDNOTE_FAVORITE_FOLDER_URL ||
      (!process.env.REDNOTE_FAVORITE_FOLDER || process.env.REDNOTE_FAVORITE_FOLDER === folderConfig.name ? folderConfig.url : ""),
    REDNOTE_BATCH_CHECKPOINT_PATH: process.env.MCP_RESULT_PATH &&
      resolve(process.env.MCP_RESULT_PATH).startsWith(`${projectRoot}/state/rednote-private/`)
      ? `${resolve(process.env.MCP_RESULT_PATH)}.checkpoint.json` : "",
  },
  stderr: "inherit",
});

try {
  await client.connect(transport);
  const result = toolName === "--list-tools"
    ? await client.listTools()
    : await client.callTool(
      { name: toolName, arguments: toolArguments },
      undefined,
      { timeout: callTimeoutMs },
    );
  if (process.env.MCP_RESULT_PATH) {
    const outputPath = resolve(process.env.MCP_RESULT_PATH);
    if (!outputPath.startsWith(`${projectRoot}/state/`)) {
      throw new Error("MCP_RESULT_PATH must be inside the project state directory");
    }
    mkdirSync(dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
    console.log(JSON.stringify({ result_file: outputPath, isError: Boolean(result.isError) }));
  } else {
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  }
} finally {
  await client.close();
}
