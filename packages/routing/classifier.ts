import { config } from "../core/config.ts";
import { generateId } from "../core/id.ts";
import { createLogger } from "../core/logger.ts";
import type { ClassifiedIntent, CommandInput } from "../core/types.ts";
import { type RoutingRule, routingRules } from "./rules.ts";

const log = createLogger("router");

interface RuleMatch {
	rule: RoutingRule;
	score: number;
}

function scoreInput(input: string, rule: RoutingRule): number {
	const lowerInput = input.toLowerCase();
	let patternScore = 0;
	let keywordScore = 0;

	for (const pattern of rule.patterns) {
		if (pattern.test(input)) {
			patternScore = 0.8;
			break;
		}
	}

	const words = lowerInput.split(/\s+/);
	let keywordHits = 0;
	for (const keyword of rule.keywords) {
		if (words.includes(keyword) || lowerInput.includes(keyword)) {
			keywordHits++;
		}
	}
	if (rule.keywords.length > 0) {
		keywordScore = (keywordHits / rule.keywords.length) * 0.6;
	}

	return Math.min(
		Math.max(patternScore, keywordScore) +
			Math.min(patternScore, keywordScore) * 0.3,
		1.0,
	);
}

function extractParameters(
	input: string,
	rule: RoutingRule,
): Record<string, string> {
	const params: Record<string, string> = {};

	for (const pattern of rule.patterns) {
		const match = input.match(pattern);
		if (match && match.length > 1) {
			for (let i = 1; i < match.length; i++) {
				params[`capture_${i}`] = match[i];
			}
		}
	}

	return params;
}

export function classifyIntent(command: CommandInput): ClassifiedIntent {
	const matches: RuleMatch[] = [];

	for (const rule of routingRules) {
		const score = scoreInput(command.raw, rule);
		if (score > 0) {
			matches.push({ rule, score });
		}
	}

	matches.sort((a, b) => {
		if (Math.abs(a.score - b.score) < 0.1) {
			return a.rule.priority - b.rule.priority;
		}
		return b.score - a.score;
	});

	if (
		matches.length === 0 ||
		matches[0].score < config.router.confidenceThreshold
	) {
		log.warn(`No confident match for: "${command.raw}"`);
		return {
			inputId: command.id,
			category: "unknown",
			confidence: matches.length > 0 ? matches[0].score : 0,
			trustLevel: "untrusted",
			matchedRule: "none",
			parameters: {},
		};
	}

	const best = matches[0];
	const result: ClassifiedIntent = {
		inputId: command.id,
		category: best.rule.category,
		confidence: best.score,
		trustLevel: best.rule.trustLevel,
		matchedRule: best.rule.name,
		parameters: extractParameters(command.raw, best.rule),
	};

	log.info(
		`Classified "${command.raw}" → ${result.category} (${result.matchedRule}, confidence: ${result.confidence})`,
	);

	return result;
}

export function generateCommandId(): string {
	return generateId("cmd");
}
