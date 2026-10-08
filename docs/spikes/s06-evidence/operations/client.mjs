import fs from 'node:fs';
const registry = JSON.parse(fs.readFileSync('/home/regner/.local/share/godot-mcp-toolkit/projects.json', 'utf8'));
const entry = registry.by_path[process.argv[3]];
if (!entry) throw new Error('project registry entry missing');
const requests = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const ws = new WebSocket(`ws://127.0.0.1:${entry.port}`);
let index = -1;
const deadline = setTimeout(() => { console.error('MCP deadline'); process.exit(1); }, 25000);
ws.onopen = () => ws.send(JSON.stringify({auth: fs.readFileSync(entry.token_path, 'utf8').trim()}));
ws.onmessage = e => {
  const msg = JSON.parse(e.data);
  if (index >= 0 && msg.id !== index) return;
  if (index >= 0) console.log(JSON.stringify({method: requests[index].method, response: msg}));
  index++;
  if (index === requests.length) { clearTimeout(deadline); ws.close(); return; }
  ws.send(JSON.stringify({jsonrpc: '2.0', id: index, ...requests[index]}));
};
ws.onerror = e => { console.error(e.message); process.exit(1); };
