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

const host = window.location.hostname;

export const API_BASE_URL = `http://${host}:8000`;
export const WS_URL = `ws://${host}:8000`;

