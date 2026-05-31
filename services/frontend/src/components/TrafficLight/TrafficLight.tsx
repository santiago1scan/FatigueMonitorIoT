/**
 * Componente TrafficLight
 *
 * Responsabilidad única: Mostrar el semáforo de fatiga
 * Recibe flags (green, yellow, red) y renderiza de forma visual.
 * No contiene lógica, solo presentación.
 */

import { FatigueFlags } from "@/types/index";
import styles from "./TrafficLight.module.css";

interface TrafficLightProps {
  fatigue: FatigueFlags;
}

export function TrafficLight({ fatigue }: TrafficLightProps) {
  return (
    <div className={styles.trafficLight}>
      <div className={`${styles.light} ${styles.green} ${fatigue.green ? styles.active : ""}`} />
      <div className={`${styles.light} ${styles.yellow} ${fatigue.yellow ? styles.active : ""}`} />
      <div className={`${styles.light} ${styles.red} ${fatigue.red ? styles.active : ""}`} />
    </div>
  );
}
