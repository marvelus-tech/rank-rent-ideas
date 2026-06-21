/**
 * OpenClaw internal hook: start Mission Control if nothing is listening on /health.
 * Keeps port in sync with server.js (PORT constant there).
 */
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HEALTH_URL = "http://127.0.0.1:8765/health";
const HEALTH_TIMEOUT_MS = 1500;

async function missionControlHealthy() {
	try {
		const res = await fetch(HEALTH_URL, {
			signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS),
		});
		if (!res.ok) return false;
		const data = await res.json();
		return data?.status === "ok";
	} catch {
		return false;
	}
}

/** OpenClaw passes an internal hook event; we only need the gateway:startup side effect. */
export default async function spawnMissionControlOnGateway() {
	if (await missionControlHealthy()) return;

	const serverJs = path.join(__dirname, "server.js");
	const child = spawn(process.execPath, [serverJs], {
		cwd: __dirname,
		detached: true,
		stdio: "ignore",
		env: process.env,
	});
	child.unref();
}
