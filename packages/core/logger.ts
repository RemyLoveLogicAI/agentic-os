type LogLevel = "debug" | "info" | "warn" | "error";

const LEVEL_ORDER: Record<LogLevel, number> = {
	debug: 0,
	info: 1,
	warn: 2,
	error: 3,
};

const currentLevel: LogLevel = (process.env.LOG_LEVEL as LogLevel) ?? "info";

function shouldLog(level: LogLevel): boolean {
	return LEVEL_ORDER[level] >= LEVEL_ORDER[currentLevel];
}

function formatTimestamp(): string {
	return new Date().toISOString();
}

function formatMessage(
	level: LogLevel,
	component: string,
	message: string,
): string {
	return `[${formatTimestamp()}] [${level.toUpperCase()}] [${component}] ${message}`;
}

export function createLogger(component: string) {
	return {
		debug(message: string, data?: unknown) {
			if (shouldLog("debug")) {
				console.debug(formatMessage("debug", component, message), data ?? "");
			}
		},
		info(message: string, data?: unknown) {
			if (shouldLog("info")) {
				console.info(formatMessage("info", component, message), data ?? "");
			}
		},
		warn(message: string, data?: unknown) {
			if (shouldLog("warn")) {
				console.warn(formatMessage("warn", component, message), data ?? "");
			}
		},
		error(message: string, data?: unknown) {
			if (shouldLog("error")) {
				console.error(formatMessage("error", component, message), data ?? "");
			}
		},
	};
}
