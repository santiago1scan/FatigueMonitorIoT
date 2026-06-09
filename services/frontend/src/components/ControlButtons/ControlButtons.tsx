/**
 * Componente ControlButtons
 *
 * Responsabilidad única: Proporcionar botones de control (start/stop)
 * y manejar el estado de carga/error.
 */

import { useCallback } from "react";
import { apiService } from "@/services/api";
import { useApi } from "@/hooks";
import styles from "./ControlButtons.module.css";
import { API_BASE_URL, WS_URL } from "@/types";

interface ControlButtonsProps {
  isActive: boolean;
  onStateChange?: () => void;
}

export function ControlButtons({ isActive, onStateChange }: ControlButtonsProps) {
  const { isLoading, error, execute } = useApi();

  const handleStart = useCallback(async () => {
    await execute(async () => {
      await apiService.startAssist();
      onStateChange?.();
    });
  }, [execute, onStateChange]);

  const handleStop = useCallback(async () => {
    await execute(async () => {
      await apiService.stopAssist();
      onStateChange?.();
    });
  }, [execute, onStateChange]);

  return (
    <div className={styles.container}>
      <button
        className={`${styles.button} ${styles.start}`}
        onClick={handleStart}
        disabled={isLoading || isActive}
        aria-label="Iniciar asistencia"
      >
        {isLoading ? "Iniciando..." : "Iniciar"}
      </button>

      <button
        className={`${styles.button} ${styles.stop}`}
        onClick={handleStop}
        disabled={isLoading || !isActive}
        aria-label="Detener asistencia"
      >
        {isLoading ? "Deteniendo..." : "Detener"}
      </button>

      {error && (
        <div className={styles.error}>
          <p>Error: {error.message}</p>
        </div>
      )}
      <div>
        <p>Host: {window.location.hostname}</p>
        <p>API: {API_BASE_URL}</p>
        <p>WS: {WS_URL}</p>
      </div>
    </div>

  );
}
