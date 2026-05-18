import {
	executeIntent,
	getSystemState,
	initOrchestrator,
	processCommand,
} from "../../agents/orchestrator/index.ts";
import { config } from "../../packages/core/config.ts";
import { readEvidence } from "../../packages/core/evidence-ledger.ts";
import { createLogger } from "../../packages/core/logger.ts";
import {
	getAllApprovals,
	resolveApproval,
} from "../../packages/policy/approval-gate.ts";
import { getApproval } from "../../packages/policy/approval-gate.ts";
import { classifyIntent } from "../../packages/routing/classifier.ts";
import {
	getAllClarifications,
	resolveClarification,
} from "../../services/spokenly-mcp-bridge/bridge.ts";

const log = createLogger("operator-console");

function html(state: Awaited<ReturnType<typeof getSystemState>>): string {
	const pendingRows = state.pendingApprovals
		.map(
			(a) => `
		<tr>
			<td>${a.id}</td>
			<td>${a.action}</td>
			<td>${a.reason}</td>
			<td>${a.expiresAt}</td>
			<td>
				<form method="POST" action="/approvals/${a.id}/approve" style="display:inline">
					<button type="submit" class="btn-approve">Approve</button>
				</form>
				<form method="POST" action="/approvals/${a.id}/deny" style="display:inline">
					<button type="submit" class="btn-deny">Deny</button>
				</form>
			</td>
		</tr>`,
		)
		.join("");

	const evidenceRows = state.recentEvidence
		.slice(0, 15)
		.map(
			(e) => `
		<tr class="${e.success ? "success" : "failure"}">
			<td>${e.timestamp.slice(0, 19)}</td>
			<td>${e.action}</td>
			<td>${e.category}</td>
			<td>${e.trustLevel}</td>
			<td>${e.durationMs}ms</td>
			<td>${e.success ? "OK" : "FAIL"}</td>
		</tr>`,
		)
		.join("");

	return `<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Agentic OS — Operator Console</title>
	<style>
		:root { --bg: #0a0a0f; --fg: #e0e0e0; --accent: #6c5ce7; --green: #00b894; --red: #d63031; --border: #2d2d44; }
		* { margin: 0; padding: 0; box-sizing: border-box; }
		body { font-family: 'SF Mono', 'Fira Code', monospace; background: var(--bg); color: var(--fg); padding: 2rem; }
		h1 { color: var(--accent); margin-bottom: 0.5rem; font-size: 1.5rem; }
		h2 { color: var(--accent); margin: 1.5rem 0 0.75rem; font-size: 1.1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
		.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin: 1rem 0; }
		.stat { background: #14141f; border: 1px solid var(--border); border-radius: 8px; padding: 1rem; }
		.stat-label { font-size: 0.75rem; color: #888; text-transform: uppercase; }
		.stat-value { font-size: 1.5rem; font-weight: bold; color: var(--green); }
		table { width: 100%; border-collapse: collapse; margin: 0.5rem 0; }
		th { text-align: left; padding: 0.5rem; color: #888; font-size: 0.75rem; text-transform: uppercase; border-bottom: 1px solid var(--border); }
		td { padding: 0.5rem; font-size: 0.85rem; border-bottom: 1px solid #1a1a2e; }
		tr.success td:last-child { color: var(--green); }
		tr.failure td:last-child { color: var(--red); }
		.btn-approve { background: var(--green); color: #000; border: none; padding: 0.3rem 0.8rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
		.btn-deny { background: var(--red); color: #fff; border: none; padding: 0.3rem 0.8rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
		form.command-form { display: flex; gap: 0.5rem; margin: 1rem 0; }
		form.command-form input { flex: 1; background: #14141f; border: 1px solid var(--border); color: var(--fg); padding: 0.5rem; border-radius: 4px; font-family: inherit; }
		form.command-form button { background: var(--accent); color: #fff; border: none; padding: 0.5rem 1.5rem; border-radius: 4px; cursor: pointer; font-family: inherit; }
		.subtitle { color: #666; font-size: 0.85rem; margin-bottom: 1rem; }
	</style>
</head>
<body>
	<h1>Agentic OS</h1>
	<p class="subtitle">Operator Console — Phase 0</p>

	<div class="stats">
		<div class="stat">
			<div class="stat-label">Up Since</div>
			<div class="stat-value" style="font-size:0.9rem">${state.upSince.slice(0, 19)}</div>
		</div>
		<div class="stat">
			<div class="stat-label">Commands</div>
			<div class="stat-value">${state.totalCommands}</div>
		</div>
		<div class="stat">
			<div class="stat-label">Approvals</div>
			<div class="stat-value">${state.totalApprovals}</div>
		</div>
		<div class="stat">
			<div class="stat-label">Executions</div>
			<div class="stat-value">${state.totalExecutions}</div>
		</div>
		<div class="stat">
			<div class="stat-label">Router Accuracy</div>
			<div class="stat-value">${(state.routerAccuracy * 100).toFixed(1)}%</div>
		</div>
	</div>

	<h2>Command Input</h2>
	<form class="command-form" method="POST" action="/command">
		<input type="text" name="command" placeholder="Speak or type a command..." autofocus required />
		<button type="submit">Execute</button>
	</form>

	<h2>Pending Approvals (${state.pendingApprovals.length})</h2>
	<table>
		<thead><tr><th>ID</th><th>Action</th><th>Reason</th><th>Expires</th><th>Actions</th></tr></thead>
		<tbody>${pendingRows || '<tr><td colspan="5" style="color:#666">No pending approvals</td></tr>'}</tbody>
	</table>

	<h2>Evidence Ledger</h2>
	<table>
		<thead><tr><th>Time</th><th>Action</th><th>Category</th><th>Trust</th><th>Duration</th><th>Status</th></tr></thead>
		<tbody>${evidenceRows || '<tr><td colspan="6" style="color:#666">No evidence recorded yet</td></tr>'}</tbody>
	</table>
</body>
</html>`;
}

async function handleRequest(req: Request): Promise<Response> {
	const url = new URL(req.url);
	const { method } = req;

	// API routes (JSON)
	if (url.pathname === "/api/state") {
		const state = await getSystemState();
		return Response.json(state);
	}

	if (url.pathname === "/api/command" && method === "POST") {
		const body = await req.json();
		const result = await processCommand(
			body.command as string,
			(body.source as "typed") ?? "typed",
		);
		return Response.json(result);
	}

	if (url.pathname === "/api/evidence") {
		const limit = Number.parseInt(url.searchParams.get("limit") ?? "50", 10);
		const evidence = await readEvidence(limit);
		return Response.json({ evidence, count: evidence.length });
	}

	if (url.pathname === "/api/approvals") {
		return Response.json({ approvals: getAllApprovals() });
	}

	if (url.pathname === "/api/clarifications") {
		return Response.json({ clarifications: getAllClarifications() });
	}

	// Approval resolution via API
	const approvalMatch = url.pathname.match(
		/^\/api\/approvals\/(apr_[a-f0-9]+)\/(approve|deny)$/,
	);
	if (approvalMatch && method === "POST") {
		const [, id, action] = approvalMatch;
		const status = action === "approve" ? "approved" : "denied";
		const result = resolveApproval(id, status);

		if (result && result.status === "approved") {
			const approval = getApproval(id);
			if (approval) {
				const intent = classifyIntent({
					id: approval.intentId,
					raw: approval.action,
					source: "typed",
					timestamp: approval.createdAt,
				});
				await executeIntent(intent, approval.action, id);
			}
		}

		return Response.json({ approval: result });
	}

	// HTML form handlers
	if (url.pathname === "/command" && method === "POST") {
		const formData = await req.formData();
		const command = formData.get("command") as string;
		if (command) await processCommand(command, "typed");
		return Response.redirect(`${url.origin}/`, 303);
	}

	const htmlApprovalMatch = url.pathname.match(
		/^\/approvals\/(apr_[a-f0-9]+)\/(approve|deny)$/,
	);
	if (htmlApprovalMatch && method === "POST") {
		const [, id, action] = htmlApprovalMatch;
		const status = action === "approve" ? "approved" : "denied";
		const result = resolveApproval(id, status);

		if (result && result.status === "approved") {
			const approval = getApproval(id);
			if (approval) {
				const intent = classifyIntent({
					id: approval.intentId,
					raw: approval.action,
					source: "typed",
					timestamp: approval.createdAt,
				});
				await executeIntent(intent, approval.action, id);
			}
		}

		return Response.redirect(`${url.origin}/`, 303);
	}

	// Clarification resolution
	if (url.pathname.startsWith("/api/clarifications/") && method === "POST") {
		const id = url.pathname.split("/").pop() ?? "";
		const body = await req.json();
		const result = resolveClarification(id, body.response as string);
		return Response.json({ clarification: result });
	}

	// Health check
	if (url.pathname === "/health") {
		return Response.json({ ok: true, service: "agentic-os-operator-console" });
	}

	// Panel HTML
	if (url.pathname === "/" || url.pathname === "/panel") {
		const state = await getSystemState();
		return new Response(html(state), {
			headers: { "Content-Type": "text/html; charset=utf-8" },
		});
	}

	return new Response("Not Found", { status: 404 });
}

initOrchestrator();

const server = Bun.serve({
	port: config.server.port,
	hostname: config.server.host,
	fetch: handleRequest,
});

log.info(
	`Operator Console running at http://${server.hostname}:${server.port}`,
);
log.info(
	"Routes: / (panel), /api/state, /api/command, /api/evidence, /api/approvals, /health",
);
