# Vision Service

Servicio edge-native para inferencia de pose con MediaPipe, calculo de metricas biomecanicas y publicacion de eventos MQTT.

## Responsabilidad

- Consumir frames desde HAL.
- Inferir pose con MediaPipe.
- Extraer landmarks y metricas biomecanicas.
- Publicar eventos estructurados por MQTT.
- Exponer metricas internas y estado.

No realiza logica de negocio, no controla hardware y no detecta fatiga final.

## Arquitectura interna

```
app/
  consumers/   # Ingestion de frames desde HAL
  providers/   # Pose providers (MediaPipe)
  processing/  # Pipeline de procesamiento
  metrics/     # Biomecanica e internos
  mqtt/        # Publicacion MQTT
  schemas/     # Payloads estructurados
  services/    # Servicios auxiliares (debug video)
  config/      # Configuracion centralizada
  utils/       # Utilidades
  main.py
```

## Variables de entorno

Prefijo `VISION_`.

- `VISION_ENV` (default: `dev`)
- `VISION_MQTT_HOST` (default: `mqtt`)
- `VISION_MQTT_PORT` (default: `1883`)
- `VISION_MQTT_USERNAME`
- `VISION_MQTT_PASSWORD`
- `VISION_FRAME_SOURCE` (`stream` | `snapshot`, default: `stream`)
- `VISION_HAL_STREAM_URL` (default: `http://hal:8080/camera/stream`)
- `VISION_HAL_SNAPSHOT_URL` (default: `http://hal:8080/camera/frame`)
- `VISION_FRAME_FPS_LIMIT` (default: `0`, sin limite)
- `VISION_POSE_DET_CONF` (default: `0.5`)
- `VISION_POSE_TRACK_CONF` (default: `0.5`)
- `VISION_POSE_MODEL_PATH` (default: `pose_landmarker.task`)
- `VISION_METRICS_INTERVAL_SEC` (default: `5`)
- `VISION_DEBUG_VIDEO_ENABLE` (default: `false`)
- `VISION_DEBUG_VIDEO_PORT` (default: `8090`)
- `VISION_LOG_LEVEL` (default: `INFO`)
- `VISION_TOPIC_POSE` (default: `gym/vision/pose`)
- `VISION_TOPIC_METRICS` (default: `gym/vision/metrics`)
- `VISION_TOPIC_DEBUG` (default: `gym/vision/debug`)
- `VISION_TOPIC_HEALTH` (default: `gym/vision/health`)
- `VISION_IDLE_SLEEP_SEC` (default: `0.02`)

## MQTT topics

- `gym/vision/pose`
- `gym/vision/metrics`
- `gym/vision/debug`
- `gym/vision/health`

### Payloads

Pose (`gym/vision/pose`):

```json
{
  "timestamp": "2026-05-28T02:32:21.037464+00:00",
  "tracking": true,
  "landmarks": {
    "left_knee": {"x": 0.62, "y": 1.97, "z": -0.21}
  },
  "confidence": 0.48,
  "inference_ms": 35.1
}
```

Metrics (`gym/vision/metrics`):

```json
{
  "timestamp": "2026-05-28T02:32:21.037464+00:00",
  "tracking": true,
  "angles": {"left_knee": 178.0},
  "back_inclination": 1.4,
  "torso_leg_ratio": 0.65,
  "velocity": {"vertical": 0.04},
  "positions": {
    "left_shoulder": {"x": 0.68, "y": 0.67, "z": -0.82}
  }
}
```

Health (`gym/vision/health`):

```json
{
  "timestamp": "2026-05-28T02:32:25.000000+00:00",
  "fps": 12.4,
  "inference_ms_avg": 41.3,
  "frames_processed": 120,
  "frames_dropped": 2,
  "tracking": true,
  "pipeline_latency_ms": 58.7
}
```

## Debug video (HTTP)

- `GET /` pagina con video y metricas.
- `GET /frame.jpg` frame anotado (JPEG).
- `GET /metrics.json` ultimo payload combinado.
- `GET /health` estado simple.

## Ejecucion local

```bash
docker compose up vision
```

## Notas

- El servicio es stateless.
- No accede a hardware fisico.
- La salida de video anotado es opcional y local (no MQTT).
