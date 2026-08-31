import type { DomainRecord, GameActionEffect, GameActionResult } from './types';

export function createGameActionResult<TPayload extends DomainRecord>(
  type: string,
  payload: TPayload,
  createdAt: number,
): GameActionResult<TPayload> {
  return {
    ok: true,
    type,
    payload,
    logs: [],
    effects: [],
    ui: {},
    data: {},
    createdAt,
  };
}

export function failGameActionResult<TPayload extends DomainRecord>(
  type: string,
  message: string,
  payload: TPayload,
  createdAt: number,
): GameActionResult<TPayload> {
  const result = createGameActionResult(type, payload, createdAt);
  result.ok = false;
  if (message) result.logs.push({ message, important: false });
  return result;
}

export function addResultLog<TPayload extends DomainRecord>(
  result: GameActionResult<TPayload>,
  message: string,
  important = false,
): GameActionResult<TPayload> {
  if (message) result.logs.push({ message, important });
  return result;
}

export function addResultEffect<TPayload extends DomainRecord>(
  result: GameActionResult<TPayload>,
  effect: GameActionEffect,
): GameActionResult<TPayload> {
  result.effects.push(effect);
  return result;
}

export function requestUiRefresh<TPayload extends DomainRecord>(
  result: GameActionResult<TPayload>,
  key: string,
  value: unknown = true,
): GameActionResult<TPayload> {
  result.ui[key] = value;
  return result;
}
