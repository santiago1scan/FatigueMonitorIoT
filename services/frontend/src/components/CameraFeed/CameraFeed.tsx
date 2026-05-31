import { useEffect, useRef, useState } from "react";
import styles from "./CameraFeed.module.css";

export function CameraFeed() {
  const imgRef = useRef<HTMLImageElement>(null);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    let isActive = true;

    const updateFrame = () => {
      if (!isActive) return;
      
      if (imgRef.current) {
        imgRef.current.src = `http://localhost:8090/frame.jpg?ts=${Date.now()}`;
      }
      
      timeoutId = setTimeout(updateFrame, 150); 
    };

    updateFrame();

    return () => {
      isActive = false;
      clearTimeout(timeoutId);
    };
  }, []);

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Camera Feed (Vision Debug)</h3>
      <div style={{ position: "relative" }}>
        {hasError && (
          <div className={styles.error} style={{ position: "absolute", top: 0, width: "100%", background: "rgba(0,0,0,0.7)" }}>
            Buscando señal de video...
          </div>
        )}
        <img
          ref={imgRef}
          alt="Pose Detections"
          className={styles.image}
          // Si carga exitosamente, quitamos el error
          onLoad={() => setHasError(false)}
          // Si da error, mostramos advertencia pero no desmontamos la imagen para poder reintentar
          onError={() => setHasError(true)}
        />
      </div>
    </div>
  );
}
