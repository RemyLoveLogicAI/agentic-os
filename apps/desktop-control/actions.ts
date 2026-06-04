import { writeEvidence } from "../../packages/core/evidence-ledger.ts";
import { generateId } from "../../packages/core/id.ts";
import { createLogger } from "../../packages/core/logger.ts";
import type {
	EvidenceRecord,
	ExecutionResult,
} from "../../packages/core/types.ts";

const log = createLogger("desktop-control");

/**
 * Safe desktop action: paste text to clipboard.
 * Phase 0 simulates the paste — in production this uses macOS automation.
 */
export async function pasteText(
	text: string,
	intentId: string,
): Promise<ExecutionResult> {
	const execId = generateId("exec");
	const startedAt = new Date();

	log.info(`Executing paste: "${text.slice(0, 50)}..."`);

	let output: string;
	let success: boolean;
	let error: string | undefined;

	try {
		// Phase 0: simulate clipboard paste
		// Production: Use macOS osascript or pbcopy
		output = `Text pasted to clipboard: "${text.slice(0, 100)}"`;
		success = true;
		log.info(`Paste completed: ${execId}`);
	} catch (e) {
		const err = e instanceof Error ? e : new Error(String(e));
		output = "";
		error = err.message;
		success = false;
		log.error(`Paste failed: ${execId}`, err);
	}

	const completedAt = new Date();
	const durationMs = completedAt.getTime() - startedAt.getTime();

	const evidence: EvidenceRecord = {
		id: generateId("evi"),
		timestamp: completedAt.toISOString(),
		action: "desktop.paste",
		actor: "desktop-control",
		input: text,
		output,
		category: "safe_desktop",
		trustLevel: "medium",
		durationMs,
		success,
	};

	await writeEvidence(evidence);

	return {
		id: execId,
		intentId,
		action: "desktop.paste",
		status: success ? "completed" : "failed",
		output,
		error,
		startedAt: startedAt.toISOString(),
		completedAt: completedAt.toISOString(),
		evidence,
	};
}

/**
 * Safe desktop action: open a URL in the default browser.
 * Phase 0 simulates — in production this uses macOS `open` command.
 */
export async function openUrl(
	url: string,
	intentId: string,
): Promise<ExecutionResult> {
	const execId = generateId("exec");
	const startedAt = new Date();

	log.info(`Executing open URL: ${url}`);

	let output: string;
	let success: boolean;
	let error: string | undefined;

	try {
		if (!url.startsWith("http://") && !url.startsWith("https://")) {
			throw new Error(`Invalid URL scheme: ${url}`);
		}
		// Phase 0: simulate URL open
		// Production: Use `open` on macOS, `xdg-open` on Linux
		output = `Opened URL: ${url}`;
		success = true;
		log.info(`URL opened: ${execId}`);
	} catch (e) {
		const err = e instanceof Error ? e : new Error(String(e));
		output = "";
		error = err.message;
		success = false;
		log.error(`URL open failed: ${execId}`, err);
	}

	const completedAt = new Date();
	const durationMs = completedAt.getTime() - startedAt.getTime();

	const evidence: EvidenceRecord = {
		id: generateId("evi"),
		timestamp: completedAt.toISOString(),
		action: "desktop.open_url",
		actor: "desktop-control",
		input: url,
		output,
		category: "safe_desktop",
		trustLevel: "medium",
		durationMs,
		success,
	};

	await writeEvidence(evidence);

	return {
		id: execId,
		intentId,
		action: "desktop.open_url",
		status: success ? "completed" : "failed",
		output,
		error,
		startedAt: startedAt.toISOString(),
		completedAt: completedAt.toISOString(),
		evidence,
	};
}
