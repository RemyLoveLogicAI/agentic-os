import { resolve } from "node:path";

export const config = {
	server: {
		host: process.env.AGENTIC_OS_HOST ?? "0.0.0.0",
		port: Number.parseInt(process.env.AGENTIC_OS_PORT ?? "4200", 10),
	},

	approval: {
		ttlMs: Number.parseInt(
			process.env.APPROVAL_TTL_MS ?? String(5 * 60 * 1000),
			10,
		),
		autoApproveSafe: process.env.AUTO_APPROVE_SAFE !== "false",
	},

	evidence: {
		dir: resolve(process.env.EVIDENCE_DIR ?? "./ops/ledgers/evidence"),
		maxFileSize: 10 * 1024 * 1024,
		rotateAfterEntries: 10_000,
	},

	router: {
		confidenceThreshold: 0.7,
	},

	mcp: {
		spokelyEndpoint: process.env.SPOKENLY_MCP_ENDPOINT ?? "stdio",
	},

	zoSuperServer: {
		url: process.env.ZO_SUPER_SERVER_URL ?? "http://localhost:3000",
		token: process.env.ZO_SUPER_SERVER_TOKEN ?? "",
	},
} as const;
