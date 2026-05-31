/**
 * Componente raíz App
 *
 * Responsabilidad única: Orquestar la aplicación
 * - Conectar hooks (WebSocket, Audio)
 * - Manejar efectos secundarios (audio, reset)
 * - Pasar datos a componentes presentacionales
 */

import { useEffect } from "react";
import { useWebSocket, useAudio } from "@/hooks";
import { Layout, TrafficLight, ControlButtons, SessionDisplay, CameraFeed } from "@/components";
import styles from "./App.module.css";

function App() {
  const { state, isConnected } = useWebSocket();
  const { playSound } = useAudio();

  // Reproducir sonido cuando se debe
  useEffect(() => {
    if (state?.play_sound) {
      playSound();
    }
  }, [state?.play_sound, playSound]);

  return (
    <Layout>
      <div className={styles.container}>
        <div className={styles.column}>
          <div className={styles.card}>
            <CameraFeed />
          </div>
          <div className={styles.card}>
            <h2>Estado de Fatiga</h2>
            <TrafficLight fatigue={state?.fatigue || { green: true, yellow: false, red: false }} />
          </div>
        </div>

        <div className={styles.column}>
          <div className={styles.card}>
            <h2>Control</h2>
            <ControlButtons isActive={state?.active || false} />
          </div>

          <div className={styles.card}>
            <SessionDisplay repetitions={state?.repetitions || 0} isConnected={isConnected} />
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default App;
