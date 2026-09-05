export interface SerializedSaveQueueSnapshot {
  queuedWrites: number;
  active: boolean;
}

export interface SerializedSaveJob<TRequest> {
  request: TRequest;
  execute: (request: TRequest) => Promise<void>;
}

export interface SerializedSaveQueue<TRequest> {
  enqueue(job: SerializedSaveJob<TRequest>): Promise<void>;
  drain(): Promise<void>;
  getSnapshot(): SerializedSaveQueueSnapshot;
}

export function createSerializedSaveQueue<TRequest>(options: {
  clone: (request: TRequest) => TRequest;
  onChange?: (snapshot: SerializedSaveQueueSnapshot) => void;
}): SerializedSaveQueue<TRequest> {
  let tail: Promise<void> = Promise.resolve();
  let queuedWrites = 0;
  let active = false;

  const notify = () => options.onChange?.({ queuedWrites, active });

  function enqueue(job: SerializedSaveJob<TRequest>) {
    const frozenRequest = options.clone(job.request);
    queuedWrites += 1;
    notify();

    const execution = tail
      .catch(() => undefined)
      .then(async () => {
        active = true;
        notify();
        await job.execute(frozenRequest);
      });

    const tracked = execution.finally(() => {
      queuedWrites = Math.max(0, queuedWrites - 1);
      active = false;
      notify();
    });
    tail = tracked;
    return tracked;
  }

  return {
    enqueue,
    drain: () => tail,
    getSnapshot: () => ({ queuedWrites, active }),
  };
}
