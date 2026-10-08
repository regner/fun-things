// Uses the unchanged installed standard discovery/bridge/token modules; no protocol implementation.
import { createBridge } from '/home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules/@npgamedev/godot-mcp-server/dist/transport/bridge.js';
import { resolvePortConfig } from '/home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules/@npgamedev/godot-mcp-server/dist/startup/portConfig.js';
import { lookupProject } from '/home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules/@npgamedev/godot-mcp-server/dist/registry.js';
import { assertPublishedTokenPath } from '/home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules/@npgamedev/godot-mcp-server/dist/transport/tokenPath.js';
import readline from 'node:readline';
const project = process.env.GODOT_MCP_PROJECT_PATH;
const entry = lookupProject(project);
const ports = resolvePortConfig({}, project);
if (process.cwd() !== project || entry?._key !== project || ports.editorSource !== 'discovery' || ports.editorPinned) {
  throw new Error('canonical standard project discovery mismatch');
}
assertPublishedTokenPath(entry.token_path);
const bridge = createBridge(`ws://127.0.0.1:${ports.editorPort}`, { projectPath: project });
process.stdout.write(JSON.stringify({ discovery: ports, registry: entry }) + '\n');
try {
  for await (const line of readline.createInterface({ input: process.stdin, crlfDelay: Infinity })) {
    const request = JSON.parse(line);
    try {
      const result = await bridge.call(request.method, request.params ?? {}, request.timeout_ms ?? 15000);
      process.stdout.write(JSON.stringify({ result, headless: bridge.isHeadless(), version: bridge.getGodotVersionString() }) + '\n');
    } catch (error) {
      process.stdout.write(JSON.stringify({ error: String(error), code: error.code }) + '\n');
      break;
    }
  }
} finally {
  await bridge.close();
}
