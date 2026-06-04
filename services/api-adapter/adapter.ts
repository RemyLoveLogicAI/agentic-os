import { config } from "../../packages/core/config.ts";
import { writeEvidence } from "../../packages/core/evidence-ledger.ts";
import { generateId } from "../../packages/core/id.ts";
import { createLogger } from "../../packages/core/logger.ts";
import type {
	EvidenceRecord,
	ExecutionResult,
} from "../../packages/core/types.ts";

const log = createLogger("api-adapter");

/**
 * Safe API action: query the Zo Super Server health endpoint.
 */
export async function queryStatus(intentId: string): Promise<ExecutionResult> {
	const execId = generateId("exec");
	const startedAt = new Date();
	const url = `${config.zoSuperServer.url}/`;

	log.info(`Querying status: ${url}`);

	let output: string;
	let success: boolean;
	let error: string | undefined;

	try {
		const response = await fetch(url, {
			method: "GET",
			headers: { Accept: "application/json" },
			signal: AbortSignal.timeout(5000),
		});

		const body = await response.text();
		output = `HTTP ${response.status}: ${body}`;
		success = response.ok;

		if (!success) {
			error = `Non-OK status: ${response.status}`;
		}

		log.info(`Status response: ${response.status}`);
	} catch (e) {
		const err = e instanceof Error ? e : new Error(String(e));
		output = "";
		error = err.message;
		success = false;
		log.error(`Status query failed: ${execId}`, err);
	}

	const completedAt = new Date();
	const durationMs = completedAt.getTime() - startedAt.getTime();

	const evidence: EvidenceRecord = {
		id: generateId("evi"),
		timestamp: completedAt.toISOString(),
		action: "api.query_status",
		actor: "api-adapter",
		input: url,
		output,
		category: "safe_api",
		trustLevel: "medium",
		durationMs,
		success,
	};

	await writeEvidence(evidence);

	return {
		id: execId,
		intentId,
		action: "api.query_status",
		status: success ? "completed" : "failed",
		output,
		error,
		startedAt: startedAt.toISOString(),
		completedAt: completedAt.toISOString(),
		evidence,
	};
}

/**
 * Safe API action: send an MCP request to the Zo Super Server.
 */
export async function mcpRequest(
	payload: Record<string, unknown>,
	intentId: string,
): Promise<ExecutionResult> {
	const execId = generateId("exec");
	const startedAt = new Date();
	const url = `${config.zoSuperServer.url}/api/mcp`;

	log.info(`MCP request to: ${url}`);

	let output: string;
	let success: boolean;
	let error: string | undefined;

	try {
		const response = await fetch(url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${config.zoSuperServer.token}`,
			},
			body: JSON.stringify(payload),
			signal: AbortSignal.timeout(10000),
		});

		const body = await response.text();
		output = `HTTP ${response.status}: ${body}`;
		success = response.ok;

		if (!success) {
			error = `Non-OK status: ${response.status}`;
		}
	} catch (e) {
		const err = e instanceof Error ? e : new Error(String(e));
		output = "";
		error = err.message;
		success = false;
		log.error(`MCP request failed: ${execId}`, err);
	}

	const completedAt = new Date();
	const durationMs = completedAt.getTime() - startedAt.getTime();

	const evidence: EvidenceRecord = {
		id: generateId("evi"),
		timestamp: completedAt.toISOString(),
		action: "api.mcp_request",
		actor: "api-adapter",
		input: JSON.stringify(payload),
		output,
		category: "safe_api",
		trustLevel: "medium",
		durationMs,
		success,
	};

	await writeEvidence(evidence);

	return {
		id: execId,
		intentId,
		action: "api.mcp_request",
		status: success ? "completed" : "failed",
		output,
		error,
		startedAt: startedAt.toISOString(),
		completedAt: completedAt.toISOString(),
		evidence,
	};
}
