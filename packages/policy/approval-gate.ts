import { config } from "../core/config.ts";
import { generateId } from "../core/id.ts";
import { createLogger } from "../core/logger.ts";
import type { ApprovalRequest, ClassifiedIntent } from "../core/types.ts";

const log = createLogger("approval-gate");

const approvalStore = new Map<string, ApprovalRequest>();

let expiryInterval: ReturnType<typeof setInterval> | null = null;

export function startExpiryLoop(): void {
	if (expiryInterval) return;
	expiryInterval = setInterval(expireStaleApprovals, 10_000);
	log.info("Approval expiry loop started");
}

export function stopExpiryLoop(): void {
	if (expiryInterval) {
		clearInterval(expiryInterval);
		expiryInterval = null;
	}
}

function expireStaleApprovals(): void {
	const now = new Date().toISOString();
	for (const [id, request] of approvalStore) {
		if (request.status === "pending" && request.expiresAt < now) {
			request.status = "expired";
			request.resolvedAt = now;
			log.warn(`Approval expired: ${id}`);
		}
	}
}

export function requiresApproval(intent: ClassifiedIntent): boolean {
	if (intent.category === "needs_approval") return true;
	if (intent.trustLevel === "low" || intent.trustLevel === "untrusted")
		return true;
	return false;
}

export function createApprovalRequest(
	intent: ClassifiedIntent,
	action: string,
	reason: string,
): ApprovalRequest {
	const now = new Date();
	const expiresAt = new Date(now.getTime() + config.approval.ttlMs);

	const request: ApprovalRequest = {
		id: generateId("apr"),
		intentId: intent.inputId,
		action,
		reason,
		status: "pending",
		createdAt: now.toISOString(),
		expiresAt: expiresAt.toISOString(),
	};

	approvalStore.set(request.id, request);
	log.info(
		`Approval requested: ${request.id} — ${action} (TTL: ${config.approval.ttlMs}ms)`,
	);
	return request;
}

export function resolveApproval(
	id: string,
	status: "approved" | "denied",
	resolvedBy = "operator",
): ApprovalRequest | null {
	const request = approvalStore.get(id);
	if (!request) {
		log.error(`Approval not found: ${id}`);
		return null;
	}

	if (request.status !== "pending") {
		log.warn(`Approval ${id} already resolved: ${request.status}`);
		return request;
	}

	const now = new Date().toISOString();
	if (request.expiresAt < now) {
		request.status = "expired";
		request.resolvedAt = now;
		log.warn(`Approval ${id} expired before resolution`);
		return request;
	}

	request.status = status;
	request.resolvedAt = now;
	request.resolvedBy = resolvedBy;
	log.info(`Approval ${id} ${status} by ${resolvedBy}`);
	return request;
}

export function getApproval(id: string): ApprovalRequest | undefined {
	return approvalStore.get(id);
}

export function getPendingApprovals(): ApprovalRequest[] {
	expireStaleApprovals();
	return Array.from(approvalStore.values()).filter(
		(r) => r.status === "pending",
	);
}

export function getAllApprovals(): ApprovalRequest[] {
	return Array.from(approvalStore.values());
}

export function clearApprovals(): void {
	approvalStore.clear();
}
