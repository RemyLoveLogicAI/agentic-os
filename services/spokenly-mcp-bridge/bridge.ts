import { generateId } from "../../packages/core/id.ts";
import { createLogger } from "../../packages/core/logger.ts";
import type {
	MCPToolCall,
	MCPToolResult,
	VoiceClarification,
} from "../../packages/core/types.ts";

const log = createLogger("spokenly-mcp-bridge");

const clarificationStore = new Map<string, VoiceClarification>();

/**
 * MCP tool: ask_user_dictation
 *
 * Requests a voice clarification from the user through the Spokenly MCP bridge.
 * In production this connects to the Spokenly sideload via stdio or HTTP.
 * Phase 0 supports a local simulation mode for testing.
 */
export function askUserDictation(question: string): MCPToolCall {
	return {
		tool: "ask_user_dictation",
		arguments: {
			question,
			mode: "dictation",
			timeout_seconds: 30,
		},
	};
}

export function createClarificationRequest(
	question: string,
): VoiceClarification {
	const clarification: VoiceClarification = {
		id: generateId("clr"),
		question,
		requestedAt: new Date().toISOString(),
	};

	clarificationStore.set(clarification.id, clarification);
	log.info(`Clarification requested: ${clarification.id} — "${question}"`);
	return clarification;
}

export function resolveClarification(
	id: string,
	response: string,
): VoiceClarification | null {
	const clarification = clarificationStore.get(id);
	if (!clarification) {
		log.error(`Clarification not found: ${id}`);
		return null;
	}

	clarification.response = response;
	clarification.respondedAt = new Date().toISOString();
	log.info(`Clarification resolved: ${id} — "${response}"`);
	return clarification;
}

export function getClarification(id: string): VoiceClarification | undefined {
	return clarificationStore.get(id);
}

export function getPendingClarifications(): VoiceClarification[] {
	return Array.from(clarificationStore.values()).filter((c) => !c.response);
}

export function getAllClarifications(): VoiceClarification[] {
	return Array.from(clarificationStore.values());
}

/**
 * Process an MCP tool result from Spokenly.
 * Extracts the transcribed text from the response.
 */
export function processMCPResult(result: MCPToolResult): string | null {
	if (result.isError) {
		log.error("MCP tool returned error", result);
		return null;
	}

	const textContent = result.content.find((c) => c.type === "text");
	if (!textContent) {
		log.warn("No text content in MCP result");
		return null;
	}

	return textContent.text;
}
