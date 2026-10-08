import { lookupProject } from "../registry.js";
// Matches the toolkit's default editor bind port and the historical fallback.
const DEFAULT_EDITOR_PORT = "6550";
/** A pin failed validation — the composition root turns this into stderr + exit 1. */
export class PortConfigError extends Error {
    constructor(message) {
        super(message);
        this.name = "PortConfigError";
    }
}
/**
 * Whether a raw pin string is a usable TCP port: all digits (no sign, decimal,
 * or unit suffix) and in 1–65535. Port 0 ("any free port") is rejected — a pin
 * must name the exact port both sides agree on.
 */
export function isValidPort(value) {
    if (!/^\d+$/.test(value))
        return false;
    const port = parseInt(value, 10);
    return port >= 1 && port <= 65535;
}
// Fail loud on a bad pin. `label` names the exact source the user typed
// (`--editor-port` or GODOT_MCP_EDITOR_PORT) so the error is directly fixable.
function requireValidPin(value, label) {
    if (!isValidPort(value)) {
        throw new PortConfigError(`${label} value "${value}" is not a valid port — expected an integer 1–65535`);
    }
}
/**
 * Resolve editor / runtime / LSP dial config from CLI flags, env, and the
 * registry. The editor port is fully resolved (CLI > env > registry > `6550`);
 * the runtime and LSP channels resolve a pin only (CLI > env, else `undefined` =
 * discover lazily).
 *
 * @param cli - parsed CLI flags (the highest-precedence tier)
 * @param projectPath - absolute project path used for registry discovery when
 *   the editor channel has no pin
 * @throws PortConfigError when an effective pin (the value precedence selected)
 *   is not an integer 1–65535 — shadowed values are not validated
 */
export function resolvePortConfig(cli, projectPath) {
    // Editor — the one channel dialed eagerly, so resolve to a concrete port.
    let editorPort;
    let editorPinned;
    let editorSource;
    const envEditorPort = process.env.GODOT_MCP_EDITOR_PORT;
    if (cli.editorPort) {
        requireValidPin(cli.editorPort, "--editor-port");
        editorPort = cli.editorPort;
        editorPinned = true;
        editorSource = "cli";
    }
    else if (envEditorPort) {
        requireValidPin(envEditorPort, "GODOT_MCP_EDITOR_PORT");
        editorPort = envEditorPort;
        editorPinned = true;
        editorSource = "env";
    }
    else {
        const entry = lookupProject(projectPath);
        if (entry) {
            editorPort = String(entry.port);
            editorSource = "discovery";
        }
        else {
            editorPort = DEFAULT_EDITOR_PORT;
            editorSource = "default";
        }
        editorPinned = false;
    }
    // Runtime — pin only (CLI > env); undefined → runtimeConnection discovers lazily.
    const envRuntimePort = process.env.GODOT_MCP_RUNTIME_PORT;
    if (cli.runtimePort)
        requireValidPin(cli.runtimePort, "--runtime-port");
    else if (envRuntimePort)
        requireValidPin(envRuntimePort, "GODOT_MCP_RUNTIME_PORT");
    const runtimePort = cli.runtimePort ?? envRuntimePort;
    const runtimeSource = cli.runtimePort ? "cli" : envRuntimePort ? "env" : "discovery";
    // LSP — override only (CLI > env); undefined → lspClient discovers lazily.
    const envLspPort = process.env.GODOT_MCP_LSP_PORT;
    if (cli.lspPort)
        requireValidPin(cli.lspPort, "--lsp-port");
    else if (envLspPort)
        requireValidPin(envLspPort, "GODOT_MCP_LSP_PORT");
    const lspPort = cli.lspPort ?? envLspPort;
    const lspHost = cli.lspHost ?? process.env.GODOT_MCP_LSP_HOST;
    const lspSource = cli.lspPort ? "cli" : envLspPort ? "env" : "discovery";
    return {
        editorPort,
        editorPinned,
        editorSource,
        runtimePort,
        runtimeSource,
        lspPort,
        lspHost,
        lspSource,
    };
}
/**
 * {@link resolvePortConfig} as a preflight gate: a {@link PortConfigError}
 * becomes a precise stderr line + `process.exit(1)` (fail loud at startup, never
 * an ERR_INVALID_URL crash at first dial). Anything else rethrows.
 */
export function resolvePortConfigOrExit(cli, projectPath) {
    try {
        return resolvePortConfig(cli, projectPath);
    }
    catch (err) {
        if (err instanceof PortConfigError) {
            process.stderr.write(`[godot-mcp] ${err.message}\n`);
            process.exit(1);
        }
        throw err;
    }
}
/**
 * Log each channel's resolved port + source to **stderr** — never stdout, which
 * is the MCP transport (a stray write there reaches the LLM). Informational; the
 * actionable desync error surfaces separately from the bridge. "auto" marks a
 * channel with no pin (discovered per connect).
 */
export function logResolvedPortConfig(config) {
    const runtime = config.runtimePort ?? "auto";
    const lsp = config.lspPort ?? "auto";
    process.stderr.write(`[godot-mcp] port config: editor=${config.editorPort} [${config.editorSource}], ` +
        `runtime=${runtime} [${config.runtimeSource}], lsp=${lsp} [${config.lspSource}]\n`);
}
