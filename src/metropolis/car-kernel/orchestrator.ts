// CAR Kernel — CAROrchestrator
// Processes commands into events, drives tick advancement

import { randomUUID } from 'crypto';
import type {
  Command, CommandType, WorldState, WorldEvent,
  AgentRegisterPayload, ToolInvokePayload, TickAdvancePayload,
} from './types.js';
import type { EventStore } from './eventStore.js';
import type { ToolRouter } from './toolRouter.js';
import { reduce } from './state.js';

export class CAROrchestrator {
  private state: WorldState;

  constructor(
    initialState: WorldState,
    private readonly store: EventStore,
    private readonly router: ToolRouter,
  ) {
    this.state = initialState;
  }

  getState(): WorldState {
    return this.state;
  }

  async dispatch(command: Command): Promise<WorldEvent[]> {
    const emitted: WorldEvent[] = [];

    switch (command.type) {
      case 'AGENT_REGISTER': {
        const p = command.payload as AgentRegisterPayload;
        const event = this.store.append('AGENT_REGISTERED', {
          agentId: p.agentId,
          capabilities: p.capabilities,
        }, this.state.tick);
        emitted.push(event);
        break;
      }

      case 'AGENT_DEREGISTER': {
        const p = command.payload as { agentId: string };
        const event = this.store.append('AGENT_DEREGISTERED', {
          agentId: p.agentId,
        }, this.state.tick);
        emitted.push(event);
        break;
      }

      case 'TOOL_INVOKE': {
        const p = command.payload as ToolInvokePayload;
        const invokeEvent = this.store.append('TOOL_INVOKED', p, this.state.tick);
        emitted.push(invokeEvent);

        const { result, error } = await this.router.route(p);
        const resultEvent = this.store.append('TOOL_RESULT_RECEIVED', {
          agentId: p.agentId,
          tool: p.tool,
          result,
          error,
        }, this.state.tick);
        emitted.push(resultEvent);
        break;
      }

      case 'TICK_ADVANCE': {
        const p = command.payload as TickAdvancePayload;
        const event = this.store.append('TICK_PROCESSED', { tick: p.tick }, p.tick);
        emitted.push(event);
        break;
      }

      case 'WORLD_RESET': {
        const event = this.store.append('WORLD_RESET', {}, this.state.tick);
        emitted.push(event);
        break;
      }
    }

    // Apply all emitted events to state in order
    for (const event of emitted) {
      this.state = reduce(this.state, event);
    }

    return emitted;
  }
}
