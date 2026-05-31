/**
 * Componente Layout
 *
 * Responsabilidad única: Proporcionar estructura general de la página
 * (header, main content area, footer)
 */

import { ReactNode } from "react";
import styles from "./Layout.module.css";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <h1>Assist - Sistema de Asistencia</h1>
          <p>Control en tiempo real del entrenamiento</p>
        </div>
      </header>

      <main className={styles.main}>{children}</main>

      <footer className={styles.footer}>
        <p>&copy; 2026 Sistema IoT de Asistencia en Ejercicios. Edge-First Architecture.</p>
      </footer>
    </div>
  );
}
