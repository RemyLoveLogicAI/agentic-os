/**
 * Core types for Agentic OS.
 *
 * Nine-layer operating system: voice in, governed command routing,
 * safe execution, durable memory, and portable packaging.
 */

export type IntentCategory =
	| "safe_desktop"
	| "safe_api"
	| "needs_approval"
	| "clarification"
	| "query"
	| "unknown";

export type TrustLevel = "high" | "medium" | "low" | "untrusted";

export type ApprovalStatus = "pending" | "approved" | "denied" | "expired";

export type ActionStatus =
	| "queued"
	| "approved"
	| "executing"
	| "completed"
	| "failed"
	| "blocked";

export interface CommandInput {
	id: string;
	raw: string;
	source: "voice" | "typed" | "api" | "agent";
	timestamp: string;
	metadata?: Record<string, unknown>;
}

export interface ClassifiedIntent {
	inputId: string;
	category: IntentCategory;
	confidence: number;
	trustLevel: TrustLevel;
	matchedRule: string;
	parameters: Record<string, string>;
}

export interface ApprovalRequest {
	id: string;
	intentId: string;
	action: string;
	reason: string;
	status: ApprovalStatus;
	createdAt: string;
	expiresAt: string;
	resolvedAt?: string;
	resolvedBy?: string;
}

export interface ExecutionResult {
	id: string;
	intentId: string;
	approvalId?: string;
	action: string;
	status: ActionStatus;
	output?: string;
	error?: string;
	startedAt: string;
	completedAt?: string;
	evidence: EvidenceRecord;
}

export interface EvidenceRecord {
	id: string;
	timestamp: string;
	action: string;
	actor: string;
	input: string;
	output: string;
	category: IntentCategory;
	trustLevel: TrustLevel;
	approvalId?: string;
	durationMs: number;
	success: boolean;
}

export interface SystemState {
	upSince: string;
	totalCommands: number;
	totalApprovals: number;
	totalExecutions: number;
	pendingApprovals: ApprovalRequest[];
	recentEvidence: EvidenceRecord[];
	routerAccuracy: number;
}

export interface VoiceClarification {
	id: string;
	question: string;
	response?: string;
	requestedAt: string;
	respondedAt?: string;
}

export interface MCPToolCall {
	tool: string;
	arguments: Record<string, unknown>;
}

export interface MCPToolResult {
	content: Array<{ type: string; text: string }>;
	isError?: boolean;
}
