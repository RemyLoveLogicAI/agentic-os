import { openUrl, pasteText } from "../../apps/desktop-control/actions.ts";
import { readEvidence } from "../../packages/core/evidence-ledger.ts";
import { generateId } from "../../packages/core/id.ts";
import { createLogger } from "../../packages/core/logger.ts";
import type {
	ClassifiedIntent,
	CommandInput,
	ExecutionResult,
	SystemState,
} from "../../packages/core/types.ts";
import {
	createApprovalRequest,
	getPendingApprovals,
	requiresApproval,
	startExpiryLoop,
	stopExpiryLoop,
} from "../../packages/policy/approval-gate.ts";
import { classifyIntent } from "../../packages/routing/classifier.ts";
import { queryStatus } from "../../services/api-adapter/adapter.ts";
import { createClarificationRequest } from "../../services/spokenly-mcp-bridge/bridge.ts";

const log = createLogger("orchestrator");

let commandCount = 0;
let approvalCount = 0;
let executionCount = 0;
const upSince = new Date().toISOString();

export function initOrchestrator(): void {
	startExpiryLoop();
	log.info("Orchestrator initialized");
}

export function shutdownOrchestrator(): void {
	stopExpiryLoop();
	log.info("Orchestrator shutdown");
}

/**
 * Main orchestration loop entry point.
 *
 * Processes: voice/typed input → classify → approve if needed → execute → evidence
 */
export async function processCommand(
	raw: string,
	source: CommandInput["source"] = "typed",
): Promise<{
	intent: ClassifiedIntent;
	result?: ExecutionResult;
	approvalRequired?: boolean;
	approvalId?: string;
	clarificationId?: string;
}> {
	const command: CommandInput = {
		id: generateId("cmd"),
		raw,
		source,
		timestamp: new Date().toISOString(),
	};

	commandCount++;
	log.info(`Processing command: "${raw}" (source: ${source})`);

	const intent = classifyIntent(command);

	if (intent.category === "unknown") {
		log.warn("Unknown intent, requesting clarification");
		const clarification = createClarificationRequest(
			`I didn't understand: "${raw}". Could you rephrase?`,
		);
		return { intent, clarificationId: clarification.id };
	}

	if (intent.category === "clarification") {
		const clarification = createClarificationRequest(raw);
		return { intent, clarificationId: clarification.id };
	}

	if (requiresApproval(intent)) {
		approvalCount++;
		const approval = createApprovalRequest(
			intent,
			raw,
			`Action "${raw}" classified as ${intent.category} with trust level ${intent.trustLevel}`,
		);
		log.info(`Approval required: ${approval.id}`);
		return { intent, approvalRequired: true, approvalId: approval.id };
	}

	const result = await executeIntent(intent, raw);
	return { intent, result };
}

/**
 * Execute a pre-approved or safe intent.
 */
export async function executeIntent(
	intent: ClassifiedIntent,
	raw: string,
	approvalId?: string,
): Promise<ExecutionResult> {
	executionCount++;

	switch (intent.category) {
		case "safe_desktop": {
			if (intent.matchedRule === "safe_desktop_open_url") {
				const url =
					intent.parameters.capture_1 ??
					raw.replace(/^(open|navigate|go to|browse)\s+/i, "");
				return openUrl(url, intent.inputId);
			}
			const text = raw.replace(/^(paste|type|insert|write)\s+/i, "");
			return pasteText(text, intent.inputId);
		}

		case "safe_api":
		case "query":
			return queryStatus(intent.inputId);

		default: {
			const execId = generateId("exec");
			return {
				id: execId,
				intentId: intent.inputId,
				approvalId,
				action: `unhandled.${intent.category}`,
				status: "failed",
				error: `No executor for category: ${intent.category}`,
				startedAt: new Date().toISOString(),
				evidence: {
					id: generateId("evi"),
					timestamp: new Date().toISOString(),
					action: `unhandled.${intent.category}`,
					actor: "orchestrator",
					input: raw,
					output: "",
					category: intent.category,
					trustLevel: intent.trustLevel,
					durationMs: 0,
					success: false,
				},
			};
		}
	}
}

export async function getSystemState(): Promise<SystemState> {
	const recentEvidence = await readEvidence(20);
	const pendingApprovals = getPendingApprovals();

	const successCount = recentEvidence.filter((e) => e.success).length;
	const routerAccuracy =
		recentEvidence.length > 0 ? successCount / recentEvidence.length : 1.0;

	return {
		upSince,
		totalCommands: commandCount,
		totalApprovals: approvalCount,
		totalExecutions: executionCount,
		pendingApprovals,
		recentEvidence,
		routerAccuracy,
	};
}
