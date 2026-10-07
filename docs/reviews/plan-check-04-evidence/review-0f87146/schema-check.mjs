import fs from 'node:fs';
import { AgentProfileSchema } from '/tmp/p0-profiles-paseo-source/node_modules/@getpaseo/protocol/dist/agent-profile.js';
import { MutableDaemonConfigPatchSchema } from '/tmp/p0-profiles-paseo-source/node_modules/@getpaseo/protocol/dist/messages.js';
const patch = JSON.parse(fs.readFileSync('/home/regner/.paseo/worktrees/0u71f39f/plan-checkpoint-enet-profiles/docs/workflows/p0-profiles-evidence/proposed.patch.json', 'utf8'));
MutableDaemonConfigPatchSchema.parse(patch);
for (const profile of patch.agentProfiles) AgentProfileSchema.parse(profile);
console.log('PASS actual extracted installed profile/patch schemas parse all four inert proposals; no client/service launch');
