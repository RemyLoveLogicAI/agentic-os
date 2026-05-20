// CAR Kernel — Deterministic Tool Router
// Routes tool invocations to registered handlers — no LLM, no drift

import type { ToolInvokePayload } from './types.js';

export type ToolHandler = (args: Record<string, unknown>) => Promise<unknown>;

export class ToolRouter {
  private registry = new Map<string, ToolHandler>();

  register(tool: string, handler: ToolHandler): void {
    this.registry.set(tool, handler);
  }

  has(tool: string): boolean {
    return this.registry.has(tool);
  }

  async route(invocation: ToolInvokePayload): Promise<{ result: unknown; error?: string }> {
    const handler = this.registry.get(invocation.tool);
    if (!handler) {
      return { result: null, error: `No handler registered for tool: ${invocation.tool}` };
    }
    try {
      const result = await handler(invocation.args);
      return { result };
    } catch (err) {
      return {
        result: null,
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }

  list(): string[] {
    return [...this.registry.keys()];
  }
}
