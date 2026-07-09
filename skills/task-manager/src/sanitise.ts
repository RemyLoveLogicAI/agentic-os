/**
 * Input sanitisation helpers.
 *
 * The primary purpose is to prevent the runtime error:
 *   "Cannot read properties of undefined (reading 'trim')"
 *
 * Every string that enters the task-manager boundary passes through
 * {@link sanitiseString} so that `undefined`, `null`, and non-string
 * values are normalised to a safe default before `.trim()` is called.
 */

/**
 * Coerce an unknown value to a trimmed string.
 *
 * - `undefined` / `null` → `fallback` (default `""`)
 * - `number` / `boolean` → `String(value).trim()`
 * - `string` → `value.trim()`
 * - objects / arrays / symbols → `fallback` (rejects silently to avoid
 *   `"[object Object]"` data corruption)
 */
export function sanitiseString(
  value: unknown,
  fallback: string = "",
): string {
  if (value === undefined || value === null) return fallback;
  if (typeof value === "string") return value.trim();
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value).trim();
  }
  // Objects, arrays, symbols, functions — reject rather than silently
  // coercing to "[object Object]" or similar nonsense.
  return fallback;
}

/**
 * Coerce an unknown value to a trimmed, non-empty string or `undefined`.
 * Useful for optional fields: returns `undefined` when the input is blank
 * so callers can distinguish "not provided" from "empty string".
 */
export function sanitiseOptionalString(
  value: unknown,
): string | undefined {
  const s = sanitiseString(value);
  return s.length > 0 ? s : undefined;
}

/**
 * Coerce an unknown value to an array of trimmed, non-empty strings.
 */
export function sanitiseStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .map((v) => sanitiseString(v))
    .filter((s) => s.length > 0);
}
