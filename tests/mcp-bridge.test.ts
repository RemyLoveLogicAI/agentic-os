import { describe, expect, it } from "bun:test";
import {
	askUserDictation,
	createClarificationRequest,
	getPendingClarifications,
	processMCPResult,
	resolveClarification,
} from "../services/spokenly-mcp-bridge/bridge.ts";

describe("Spokenly MCP Bridge", () => {
	it("creates MCP tool calls", () => {
		const call = askUserDictation("What file should I open?");
		expect(call.tool).toBe("ask_user_dictation");
		expect(call.arguments.question).toBe("What file should I open?");
		expect(call.arguments.mode).toBe("dictation");
	});

	it("creates and resolves clarification requests", () => {
		const clarification = createClarificationRequest("What do you mean?");
		expect(clarification.id).toMatch(/^clr_/);
		expect(clarification.response).toBeUndefined();

		const resolved = resolveClarification(
			clarification.id,
			"I meant the config file",
		);
		expect(resolved).not.toBeNull();
		expect(resolved?.response).toBe("I meant the config file");
		expect(resolved?.respondedAt).toBeTruthy();
	});

	it("lists pending clarifications", () => {
		const c1 = createClarificationRequest("Question 1?");
		const _c2 = createClarificationRequest("Question 2?");
		const pending = getPendingClarifications();
		expect(pending.length).toBeGreaterThanOrEqual(2);

		resolveClarification(c1.id, "answer");
		const after = getPendingClarifications();
		expect(after.some((c) => c.id === c1.id)).toBe(false);
	});

	it("processes MCP results", () => {
		const result = processMCPResult({
			content: [{ type: "text", text: "Hello world" }],
		});
		expect(result).toBe("Hello world");
	});

	it("handles MCP errors", () => {
		const result = processMCPResult({
			content: [{ type: "text", text: "error" }],
			isError: true,
		});
		expect(result).toBeNull();
	});

	it("returns null for missing text content", () => {
		const result = processMCPResult({
			content: [{ type: "image", text: "" }],
		});
		expect(result).toBeNull();
	});
});
