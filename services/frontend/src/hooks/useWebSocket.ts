/**
 * Hook personalizado para WebSocket
 *
 * Responsabilidad única: Gestionar la conexión WebSocket y parsing de mensajes.
 * Abstrae la lógica de transporte para que los componentes
 * solo consuman el estado que necesitan.
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { SessionState, WS_URL } from "@/types/index";

interface UseWebSocketReturn {
  state: SessionState | null;
  isConnected: boolean;
  error: Error | null;
}

const DEFAULT_STATE: SessionState = {
  repetitions: 0,
  fatigue: { green: true, yellow: false, red: false },
  play_sound: false,
  active: false,
};

export function useWebSocket(): UseWebSocketReturn {
  const [state, setState] = useState<SessionState | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Inicializar conexión WebSocket
  useEffect(() => {
    // Iniciar con estado por defecto
    setState(DEFAULT_STATE);

    const ws = new WebSocket(WS_URL + "/ws");

    ws.onopen = () => {
      console.log("WebSocket conectado");
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const newState = JSON.parse(event.data) as SessionState;
        setState(newState);
        console.log("Estado actualizado:", newState);
      } catch (err) {
        console.error("Error parseando mensaje WebSocket:", err);
        setError(new Error("Invalid message format"));
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      setError(new Error("WebSocket connection error"));
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log("WebSocket desconectado");
      setIsConnected(false);
      // Reintentar reconexión en 3 segundos
      setTimeout(() => {
        console.log("Reintentando conexión WebSocket...");
      }, 3000);
    };

    wsRef.current = ws;

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  return {
    state: state || DEFAULT_STATE,
    isConnected,
    error,
  };
}
