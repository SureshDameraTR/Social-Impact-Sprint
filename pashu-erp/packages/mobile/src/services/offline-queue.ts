import AsyncStorage from '@react-native-async-storage/async-storage';

const QUEUE_KEY = 'pashuraksha_offline_queue';

export interface QueuedMutation {
  id: string;
  method: 'POST' | 'PATCH' | 'DELETE';
  url: string;
  body?: unknown;
  timestamp: number;
}

/**
 * Offline mutation queue backed by AsyncStorage.
 * Persists pending writes so they survive app restarts.
 * Processes in FIFO order — no conflict resolution.
 */

function generateId(): string {
  return `${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

async function readQueue(): Promise<QueuedMutation[]> {
  try {
    const raw = await AsyncStorage.getItem(QUEUE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as QueuedMutation[];
  } catch {
    return [];
  }
}

async function writeQueue(queue: QueuedMutation[]): Promise<void> {
  await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
}

/**
 * Add a failed mutation to the persistent queue.
 */
export async function enqueue(
  mutation: Omit<QueuedMutation, 'id' | 'timestamp'>
): Promise<QueuedMutation> {
  const entry: QueuedMutation = {
    ...mutation,
    id: generateId(),
    timestamp: Date.now(),
  };
  const queue = await readQueue();
  queue.push(entry);
  await writeQueue(queue);
  return entry;
}

/**
 * Remove and return the next (oldest) queued mutation.
 * Returns null if the queue is empty.
 */
export async function dequeue(): Promise<QueuedMutation | null> {
  const queue = await readQueue();
  if (queue.length === 0) return null;
  const [first, ...rest] = queue;
  await writeQueue(rest);
  return first;
}

/**
 * Return all pending mutations without removing them.
 */
export async function getAll(): Promise<QueuedMutation[]> {
  return readQueue();
}

/**
 * Return the number of pending mutations.
 */
export async function getPendingCount(): Promise<number> {
  const queue = await readQueue();
  return queue.length;
}

/**
 * Remove all queued mutations.
 */
export async function clear(): Promise<void> {
  await AsyncStorage.removeItem(QUEUE_KEY);
}

/**
 * Remove a single mutation by id (after successful replay).
 */
export async function removeById(id: string): Promise<void> {
  const queue = await readQueue();
  const filtered = queue.filter((m) => m.id !== id);
  await writeQueue(filtered);
}

export interface SyncResult {
  succeeded: number;
  failed: number;
  remaining: number;
}

/**
 * Replay all queued mutations in FIFO order.
 * Successful mutations are removed; failed ones stay in the queue.
 * Accepts a replay function so it does not depend on the ApiClient directly
 * (avoids circular imports).
 */
export async function sync(
  replayFn: (mutation: QueuedMutation) => Promise<boolean>
): Promise<SyncResult> {
  const queue = await readQueue();
  if (queue.length === 0) {
    return { succeeded: 0, failed: 0, remaining: 0 };
  }

  let succeeded = 0;
  let failed = 0;

  for (const mutation of queue) {
    try {
      const ok = await replayFn(mutation);
      if (ok) {
        await removeById(mutation.id);
        succeeded++;
      } else {
        failed++;
      }
    } catch {
      failed++;
    }
  }

  const remaining = (await readQueue()).length;
  return { succeeded, failed, remaining };
}
