// Connect only to this worktree's explicitly reserved editor; never scan other ports.
import fs from 'node:fs';
import path from 'node:path';
const root=fs.realpathSync(process.cwd());
const state='/tmp/brackett-player-editor';
const receipt=JSON.parse(fs.readFileSync(`${state}/process.json`,'utf8'));
const entry=JSON.parse(fs.readFileSync(`${state}/data/godot-mcp-toolkit/entries/578f26c7b901.json`,'utf8'));
if(receipt.project!==root || entry._key!==root || entry.pid!==receipt.pid || entry.port!==17650)
 throw Error('Player editor ownership mismatch');
const cmd=fs.readFileSync(`/proc/${receipt.pid}/cmdline`,'utf8');
if(!cmd.includes(root)) throw Error('Process project mismatch');
const requests=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const token=fs.readFileSync(entry.token_path,'utf8').trim();
const ws=new WebSocket('ws://127.0.0.1:17650');
let pending, counter=0;
const timer=setTimeout(()=>{console.error('Private editor request timeout');process.exit(1);},45000);
ws.addEventListener('error',()=>{console.error('Private editor connection failed');process.exit(1);});
ws.addEventListener('message',e=>{
 const reply=JSON.parse(e.data);
 if(reply.authed && pending){ const p=pending;pending=null;p(reply); }
 else if(reply.id && pending && !reply.method){ const p=pending;pending=null;p(reply); }
});
await new Promise(resolve=>ws.addEventListener('open',resolve,{once:true}));
const wait=()=>new Promise(resolve=>{pending=resolve;});
let p=wait();ws.send(JSON.stringify({auth:token}));await p;
for(const request of requests){
 p=wait();ws.send(JSON.stringify({jsonrpc:'2.0',id:++counter,method:request.method,params:request.params??{}}));
 const reply=await p;console.log(JSON.stringify({method:request.method,...reply}));
 if(reply.error || reply.result?.success===false) { ws.close();clearTimeout(timer);process.exit(1); }
}
ws.close();clearTimeout(timer);
