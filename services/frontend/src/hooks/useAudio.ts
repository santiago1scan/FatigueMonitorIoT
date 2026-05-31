/**
 * Hook personalizado para reproducir sonido de alerta
 *
 * Responsabilidad única: Encapsular la lógica de reproducción de audio.
 * Permite que los componentes no necesiten conocer detalles de HTML5 Audio API.
 */

import { useEffect, useRef, useCallback } from "react";

export function useAudio(soundUrl: string = "/alert.mp3") {
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Crear elemento de audio una sola vez
    if (!audioRef.current) {
      const audio = new Audio(soundUrl);
      audio.preload = "auto";
      audioRef.current = audio;
    }
  }, [soundUrl]);

  const playSound = useCallback(async () => {
    if (audioRef.current) {
      try {
        audioRef.current.currentTime = 0;
        await audioRef.current.play();
      } catch (err) {
        console.error("Error reproduciendo audio:", err);
      }
    }
  }, []);

  return { playSound };
}
