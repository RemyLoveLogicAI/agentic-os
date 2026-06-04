import type { IntentCategory, TrustLevel } from "../core/types.ts";

export interface RoutingRule {
	name: string;
	patterns: RegExp[];
	keywords: string[];
	category: IntentCategory;
	trustLevel: TrustLevel;
	priority: number;
}

/**
 * Rule-based intent classification. No LLM drift.
 * Rules are evaluated in priority order (lower number = higher priority).
 */
export const routingRules: RoutingRule[] = [
	// Clarification intents
	{
		name: "clarification_question",
		patterns: [
			/^(what|how|why|when|where|who|which|can you explain|tell me|describe)/i,
			/\?$/,
		],
		keywords: ["what", "how", "why", "explain", "describe", "tell me", "help"],
		category: "clarification",
		trustLevel: "high",
		priority: 10,
	},

	// Safe query intents
	{
		name: "status_query",
		patterns: [
			/^(show|list|get|check|view|display|report)\s+(status|state|health|logs|evidence|approvals)/i,
			/^status\b/i,
		],
		keywords: ["status", "state", "health", "logs", "show", "list", "check"],
		category: "query",
		trustLevel: "high",
		priority: 20,
	},

	// Safe desktop actions
	{
		name: "safe_desktop_paste",
		patterns: [/^(paste|type|insert|write)\s+.+/i, /^(copy|clipboard)\s+.+/i],
		keywords: ["paste", "type", "insert", "clipboard", "copy"],
		category: "safe_desktop",
		trustLevel: "medium",
		priority: 30,
	},
	{
		name: "safe_desktop_open_url",
		patterns: [
			/^open\s+(https?:\/\/\S+)/i,
			/^(navigate|go to|browse)\s+(https?:\/\/\S+)/i,
		],
		keywords: ["open", "navigate", "browse", "url"],
		category: "safe_desktop",
		trustLevel: "medium",
		priority: 31,
	},

	// Safe API actions
	{
		name: "safe_api_query",
		patterns: [
			/^(query|fetch|request|call|hit)\s+(api|endpoint|service|server)/i,
			/^api\s+(get|status|health|ping)/i,
		],
		keywords: ["query", "fetch", "api", "endpoint", "ping"],
		category: "safe_api",
		trustLevel: "medium",
		priority: 40,
	},

	// Needs approval — destructive or risky actions
	{
		name: "destructive_file_ops",
		patterns: [
			/^(delete|remove|drop|truncate|wipe|purge|destroy|rm)\s+/i,
			/^(overwrite|replace)\s+/i,
		],
		keywords: [
			"delete",
			"remove",
			"drop",
			"wipe",
			"purge",
			"destroy",
			"overwrite",
		],
		category: "needs_approval",
		trustLevel: "low",
		priority: 5,
	},
	{
		name: "system_modification",
		patterns: [
			/^(install|uninstall|upgrade|deploy|restart|reboot|shutdown|kill)/i,
			/^(sudo|admin|root)\s+/i,
		],
		keywords: [
			"install",
			"deploy",
			"restart",
			"shutdown",
			"kill",
			"sudo",
			"admin",
		],
		category: "needs_approval",
		trustLevel: "low",
		priority: 6,
	},
	{
		name: "data_mutation",
		patterns: [
			/^(update|modify|change|set|alter|mutate|patch)\s+/i,
			/^(send|post|push|publish|emit)\s+/i,
		],
		keywords: ["update", "modify", "send", "post", "publish", "push", "emit"],
		category: "needs_approval",
		trustLevel: "low",
		priority: 7,
	},
];
