/**
 * Componente SessionDisplay
 *
 * Responsabilidad única: Mostrar métricas de la sesión
 * (repeticiones, estado de conexión)
 */

import styles from "./SessionDisplay.module.css";

interface SessionDisplayProps {
  repetitions: number;
  isConnected: boolean;
}

export function SessionDisplay({ repetitions, isConnected }: SessionDisplayProps) {
  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h3>Repeticiones</h3>
        <div className={styles.value}>{repetitions}</div>
      </div>

      <div className={styles.card}>
        <h3>Estado de conexión</h3>
        <div className={`${styles.status} ${isConnected ? styles.connected : styles.disconnected}`}>
          <span className={styles.indicator}></span>
          {isConnected ? "Conectado" : "Desconectado"}
        </div>
      </div>
    </div>
  );
}
