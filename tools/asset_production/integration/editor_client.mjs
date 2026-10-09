/** Private asset production MCP transport; never discovers or switches a shared editor. */
import fs from 'node:fs';
import path from 'node:path';

const state = '/tmp/asset-register-production-editor';
const root = '/home/regner/.paseo/worktrees/0u71f39f/asset-register-production';
const launch = JSON.parse(fs.readFileSync(path.join(state, 'launch.json')));
if (launch.cwd !== root || fs.realpathSync(`/proc/${launch.pid}/cwd`) !== root)
  throw new Error('Private editor project ownership mismatch');
const args = fs.readFileSync(`/proc/${launch.pid}/cmdline`, 'utf8').split('\0');
if (!args.includes(root) || !args.includes('22652')) throw new Error('Private PID mismatch');
const token = fs.readFileSync(path.join(state,
  'data/godot/app_userdata/Fun Things/addons/godot_mcp_toolkit/project_instance_e3d7eccfd893/mcp_token'), 'utf8').trim();
const requests = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const port = process.argv.includes('--runtime') ? 22651 : 22650;
const ws = new WebSocket(`ws://127.0.0.1:${port}`);
let serial = 0;
const pending = new Map();
ws.addEventListener('message', event => {
  const msg = JSON.parse(event.data);
  if (msg.authed) pending.get('auth')?.(msg);
  if (msg.id !== undefined) pending.get(msg.id)?.(msg);
});
await new Promise((resolve, reject) => {
  ws.addEventListener('open', resolve, {once:true});
  ws.addEventListener('error', reject, {once:true});
});
await new Promise((resolve, reject) => {
  const timer = setTimeout(() => reject(new Error('Private endpoint authentication timeout')), 5000);
  pending.set('auth', msg => {clearTimeout(timer); pending.delete('auth'); resolve(msg);});
  ws.send(JSON.stringify({auth:token}));
});
for (const request of requests) {
  const id = ++serial;
  const result = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`Timeout: ${request.method}`)), 45000);
    pending.set(id, msg => {clearTimeout(timer); pending.delete(id); resolve(msg);});
    ws.send(JSON.stringify({jsonrpc:'2.0', id, method:request.method, params:request.params ?? {}}));
  });
  console.log(JSON.stringify({method:request.method,result}));
  if (result.error || result.result?.success === false || result.result?.valid === false)
    throw new Error('MCP command failed');
  // Editor calls can report protocol success after an assertion; require substantive receipts.
  if (request.method === 'node.call_method' &&
      ['context', 'inspect_prefab', 'build_static', 'build_pole'].includes(request.params?.method_name) &&
      Object.keys(result.result?.result ?? {}).length === 0)
    throw new Error('Editor method returned an empty validation receipt');
}
ws.close();
