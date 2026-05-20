// CAR Kernel — Append-Only Replayable Event Store
// In-memory with optional JSON flush for persistence

import { randomUUID } from 'crypto';
import type { WorldEvent, EventType, TickId } from './types.js';

export class EventStore {
  private log: WorldEvent[] = [];

  append<P>(type: EventType, payload: P, tick: TickId): WorldEvent<EventType, P> {
    const event: WorldEvent<EventType, P> = {
      id: randomUUID(),
      type,
      payload,
      tick,
      timestamp: new Date().toISOString(),
    };
    this.log.push(event as WorldEvent);
    return event;
  }

  since(afterId: string | null): WorldEvent[] {
    if (!afterId) return [...this.log];
    const idx = this.log.findIndex((e) => e.id === afterId);
    return idx === -1 ? [] : this.log.slice(idx + 1);
  }

  all(): WorldEvent[] {
    return [...this.log];
  }

  length(): number {
    return this.log.length;
  }

  // Snapshot for persistence
  serialize(): string {
    return JSON.stringify(this.log, null, 2);
  }

  static hydrate(json: string): EventStore {
    const store = new EventStore();
    store.log = JSON.parse(json) as WorldEvent[];
    return store;
  }
}
