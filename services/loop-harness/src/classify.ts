/**
 * Failure classification.
 *
 * Maps raw command output to a coarse {@link ErrorSignature} so planners can
 * select a repair strategy without re-parsing stderr. The patterns cover the
 * failure modes the harness is explicitly required to handle — `node_modules`
 * crashes, syntax errors — plus the common neighbours.
 */

import type { CommandResult, ErrorSignature } from "./types.js";

interface Rule {
  signature: ErrorSignature;
  test: RegExp;
}

// Order matters: the first matching rule wins, most-specific first.
const RULES: Rule[] = [
  {
    signature: "missing_dependencies",
    test: /cannot find module|module not found|error: cannot find package|command not found|is not recognized as an internal|no such file or directory.*node_modules|ENOENT.*node_modules|npm ERR!.*missing/i,
  },
  {
    signature: "syntax_error",
    test: /syntaxerror|unexpected token|unexpected end of|parse error|expected .* but found|unterminated/i,
  },
  {
    signature: "type_error",
    test: /\bTS\d{3,5}\b|type '.*' is not assignable|typeerror: .* is not a function|has no exported member/i,
  },
  {
    signature: "test_failure",
    test: /\d+ (tests?|specs?) failed|assertionerror|expect\(.*\)|✕|failing\b/i,
  },
  {
    signature: "runtime_error",
    test: /uncaught|unhandled(rejection| promise)|referenceerror|rangeerror|segmentation fault|core dumped/i,
  },
];

/** Classify a failed command result into a matchable signature. */
export function classify(result: CommandResult): ErrorSignature {
  const haystack = `${result.stderr}\n${result.stdout}`;
  for (const rule of RULES) {
    if (rule.test.test(haystack)) return rule.signature;
  }
  return "build_failure";
}
