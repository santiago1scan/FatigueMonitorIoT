/**
 * Tipos compartidos del frontend
 */

export type FatigueLevel = "GREEN" | "YELLOW" | "RED";

export interface FatigueFlags {
  green: boolean;
  yellow: boolean;
  red: boolean;
}

export interface SessionState {
  repetitions: number;
  fatigue: FatigueFlags;
  play_sound: boolean;
  active: boolean;
}

export interface ApiResponse {
  active: boolean;
}

const env: Record<string, string> = (import.meta as Record<string, any>).env || {};

export const API_BASE_URL = env.VITE_API_URL || "http://localhost:8000";
export const WS_URL = (env.VITE_WS_URL || "ws://localhost:8000").replace(
  /^http/,
  "ws"
);
