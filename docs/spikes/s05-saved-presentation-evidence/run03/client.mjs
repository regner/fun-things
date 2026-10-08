import {Client} from "/home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js";
import {StdioClientTransport} from "/home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js";
import readline from "node:readline";
const transport=new StdioClientTransport({command:"/usr/bin/node",args:["/home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules/@npgamedev/godot-mcp-server/dist/index.js"],cwd:process.cwd(),env:process.env,stderr:"inherit"});
const client=new Client({name:"S05 owned author",version:"1"});
await client.connect(transport);
for await(const line of readline.createInterface({input:process.stdin,crlfDelay:Infinity})) {
 const req=JSON.parse(line);
 try {const response=req.list?await client.listTools():await client.callTool({name:req.name,arguments:req.args??{}},undefined,{timeout:30000});process.stdout.write(JSON.stringify(response)+"\n");}
 catch(e){process.stdout.write(JSON.stringify({isError:true,error:String(e)})+"\n");}
}
await client.close();
