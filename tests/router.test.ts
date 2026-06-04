import { describe, expect, it } from "bun:test";
import type { CommandInput } from "../packages/core/types.ts";
import { classifyIntent } from "../packages/routing/classifier.ts";

function makeInput(raw: string): CommandInput {
	return {
		id: `test_${Date.now()}`,
		raw,
		source: "typed",
		timestamp: new Date().toISOString(),
	};
}

describe("Deterministic Router", () => {
	it("classifies status queries correctly", () => {
		const result = classifyIntent(makeInput("check status"));
		expect(result.category).toBe("query");
		expect(result.confidence).toBeGreaterThan(0);
	});

	it("classifies safe desktop paste actions", () => {
		const result = classifyIntent(makeInput("paste hello world"));
		expect(result.category).toBe("safe_desktop");
		expect(result.matchedRule).toBe("safe_desktop_paste");
	});

	it("classifies safe desktop URL open actions", () => {
		const result = classifyIntent(makeInput("open https://example.com"));
		expect(result.category).toBe("safe_desktop");
		expect(result.matchedRule).toBe("safe_desktop_open_url");
	});

	it("classifies API queries", () => {
		const result = classifyIntent(makeInput("query api status"));
		expect(result.category).toBe("safe_api");
	});

	it("flags destructive actions as needing approval", () => {
		const result = classifyIntent(makeInput("delete all logs"));
		expect(result.category).toBe("needs_approval");
		expect(result.trustLevel).toBe("low");
	});

	it("flags system modifications as needing approval", () => {
		const result = classifyIntent(makeInput("install new package"));
		expect(result.category).toBe("needs_approval");
	});

	it("flags data mutations as needing approval", () => {
		const result = classifyIntent(makeInput("update database record"));
		expect(result.category).toBe("needs_approval");
	});

	it("classifies clarification questions", () => {
		const result = classifyIntent(makeInput("what is the current build?"));
		expect(result.category).toBe("clarification");
	});

	it("returns unknown for unrecognized inputs", () => {
		const result = classifyIntent(makeInput("xyzzy foobar baz"));
		expect(result.category).toBe("unknown");
	});

	it("routes without LLM — pure rule-based", () => {
		const inputs = [
			"show status",
			"paste clipboard text",
			"delete everything",
			"what is this?",
			"query api health",
		];
		for (const raw of inputs) {
			const result = classifyIntent(makeInput(raw));
			expect(result.matchedRule).not.toBe("none");
			expect(result.confidence).toBeGreaterThan(0);
		}
	});
});
