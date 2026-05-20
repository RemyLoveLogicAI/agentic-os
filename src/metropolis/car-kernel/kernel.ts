// CAR Kernel — Kernel Dispatch Flow
// Single entry point: command in → events out → state updated

import type { Command, WorldEvent, WorldState } from './types.js';
import { EventStore } from './eventStore.js';
import { ToolRouter } from './toolRouter.js';
import { CAROrchestrator } from './orchestrator.js';
import { INITIAL_STATE, replay } from './state.js';

export interface KernelConfig {
  snapshotJson?: string;
}

export class CARKernel {
  private store: EventStore;
  private router: ToolRouter;
  private orchestrator: CAROrchestrator;

  constructor(config: KernelConfig = {}) {
    this.router = new ToolRouter();

    if (config.snapshotJson) {
      this.store = EventStore.hydrate(config.snapshotJson);
      const state = replay(this.store.all());
      this.orchestrator = new CAROrchestrator(state, this.store, this.router);
    } else {
      this.store = new EventStore();
      this.orchestrator = new CAROrchestrator(INITIAL_STATE, this.store, this.router);
    }
  }

  registerTool(name: string, handler: (args: Record<string, unknown>) => Promise<unknown>): void {
    this.router.register(name, handler);
  }

  async dispatch(command: Command): Promise<WorldEvent[]> {
    return this.orchestrator.dispatch(command);
  }

  getState(): WorldState {
    return this.orchestrator.getState();
  }

  snapshot(): string {
    return this.store.serialize();
  }

  eventCount(): number {
    return this.store.length();
  }
}
