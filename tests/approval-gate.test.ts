import { beforeEach, describe, expect, it } from "bun:test";
import type { ClassifiedIntent } from "../packages/core/types.ts";
import {
	clearApprovals,
	createApprovalRequest,
	getApproval,
	getPendingApprovals,
	requiresApproval,
	resolveApproval,
} from "../packages/policy/approval-gate.ts";

function makeIntent(
	category: ClassifiedIntent["category"],
	trustLevel: ClassifiedIntent["trustLevel"],
): ClassifiedIntent {
	return {
		inputId: `test_${Date.now()}`,
		category,
		confidence: 0.9,
		trustLevel,
		matchedRule: "test_rule",
		parameters: {},
	};
}

describe("Approval Gate", () => {
	beforeEach(() => {
		clearApprovals();
	});

	it("requires approval for needs_approval category", () => {
		const intent = makeIntent("needs_approval", "low");
		expect(requiresApproval(intent)).toBe(true);
	});

	it("requires approval for low trust level", () => {
		const intent = makeIntent("safe_desktop", "low");
		expect(requiresApproval(intent)).toBe(true);
	});

	it("does not require approval for safe actions with medium trust", () => {
		const intent = makeIntent("safe_desktop", "medium");
		expect(requiresApproval(intent)).toBe(false);
	});

	it("creates and retrieves approval requests", () => {
		const intent = makeIntent("needs_approval", "low");
		const request = createApprovalRequest(intent, "delete logs", "risky");
		expect(request.status).toBe("pending");
		expect(request.id).toMatch(/^apr_/);

		const retrieved = getApproval(request.id);
		expect(retrieved).toBeDefined();
		expect(retrieved?.action).toBe("delete logs");
	});

	it("approves requests", () => {
		const intent = makeIntent("needs_approval", "low");
		const request = createApprovalRequest(intent, "test action", "test");
		const result = resolveApproval(request.id, "approved");
		expect(result).not.toBeNull();
		expect(result?.status).toBe("approved");
		expect(result?.resolvedBy).toBe("operator");
	});

	it("denies requests", () => {
		const intent = makeIntent("needs_approval", "low");
		const request = createApprovalRequest(intent, "test action", "test");
		const result = resolveApproval(request.id, "denied");
		expect(result).not.toBeNull();
		expect(result?.status).toBe("denied");
	});

	it("lists pending approvals", () => {
		const intent = makeIntent("needs_approval", "low");
		createApprovalRequest(intent, "action 1", "test");
		createApprovalRequest(intent, "action 2", "test");

		const pending = getPendingApprovals();
		expect(pending.length).toBe(2);
	});

	it("sets TTL expiry on approvals", () => {
		const intent = makeIntent("needs_approval", "low");
		const request = createApprovalRequest(intent, "test", "test");
		expect(new Date(request.expiresAt).getTime()).toBeGreaterThan(
			new Date(request.createdAt).getTime(),
		);
	});

	it("returns null for nonexistent approval IDs", () => {
		const result = resolveApproval("apr_nonexistent", "approved");
		expect(result).toBeNull();
	});

	it("prevents double resolution", () => {
		const intent = makeIntent("needs_approval", "low");
		const request = createApprovalRequest(intent, "test", "test");
		resolveApproval(request.id, "approved");
		const second = resolveApproval(request.id, "denied");
		expect(second?.status).toBe("approved");
	});
});
