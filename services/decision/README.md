# Decision Engine

Servicio edge-native para analisis biomecanico temporal, deteccion de estados, conteo de reps, fatiga y fallo. Consume eventos MQTT desde Vision y publica eventos estructurados para el resto del sistema.

## Responsabilidad

- Consumir eventos de `gym/vision/pose` y `gym/vision/metrics`.
- Suavizar senales y estabilizar features antes de la maquina de estados.
- Detectar estados biomecanicos, reps, fatiga y fallo.
- Publicar eventos en `gym/decision/*`.

No procesa vision, no accede a hardware, no controla GPIO.

## Pipeline

```
MQTT Consumer
  -> Pose Buffer
  -> EMA Smoothing
  -> Feature Stabilization
  -> Biomech State Machine
  -> Temporal Analysis
  -> Fatigue Estimation
  -> Failure Detection
  -> MQTT Events
```

## MQTT

Input:
- `gym/vision/pose`
- `gym/vision/metrics`

Ejemplo `gym/vision/pose`:

```json
{
  "timestamp": "2026-05-29T02:32:21.037464+00:00",
  "tracking": true,
  "landmarks": {
    "left_knee": {"x": 0.62, "y": 1.97, "z": -0.21}
  },
  "confidence": 0.48,
  "inference_ms": 35.1
}
```

Ejemplo `gym/vision/metrics`:

```json
{
  "timestamp": "2026-05-29T02:32:21.037464+00:00",
  "tracking": true,
  "angles": {
    "left_knee": 176.7,
    "right_knee": 175.8,
    "left_hip": 178.8,
    "right_hip": 170.4
  },
  "back_inclination": 0.13,
  "torso_leg_ratio": 0.63,
  "velocity": {"vertical": -0.08},
  "positions": {
    "left_shoulder": {"x": 0.71, "y": 0.46, "z": -0.31}
  }
}
```

Output:
- `gym/decision/state`
- `gym/decision/repetition`
- `gym/decision/fatigue`
- `gym/decision/failure`
- `gym/decision/metrics`
- `gym/decision/debug`

Ejemplo `gym/decision/state`:

```json
{
  "timestamp": "2026-05-29T02:40:20.123456+00:00",
  "state": "DESCENDING",
  "rep": 4,
  "fatigue_score": 0.62,
  "confidence": 0.86,
  "tracking": true,
  "metrics": {
    "knee_angle_avg": 122.1,
    "hip_angle_avg": 98.2,
    "knee_asymmetry": 3.4,
    "back_inclination": 4.7,
    "velocity_vertical": -0.18,
    "depth_score": 0.81,
    "stability": 0.92,
    "consistency": 0.88
  }
}
```

Ejemplo `gym/decision/repetition`:

```json
{
  "timestamp": "2026-05-29T02:40:20.123456+00:00",
  "event": "NEW_REP",
  "rep": 5,
  "depth_ok": true
}
```

Ejemplo `gym/decision/fatigue`:

```json
{
  "timestamp": "2026-05-29T02:40:20.123456+00:00",
  "fatigue_score": 0.58
}
```

Ejemplo `gym/decision/failure`:

```json
{
  "timestamp": "2026-05-29T02:40:20.123456+00:00",
  "event": "NEAR_FAILURE",
  "confidence": 0.81
}
```

Ejemplo `gym/decision/metrics`:

```json
{
  "timestamp": "2026-05-29T02:40:20.123456+00:00",
  "metrics": {
    "knee_angle_avg": 122.1,
    "back_inclination": 4.7,
    "velocity_vertical": -0.18,
    "depth_score": 0.81
  }
}
```

Ejemplo `gym/decision/debug`:

```json
{
  "timestamp": "2026-05-29T02:40:20.123456+00:00",
  "debug": {
    "frames_received": 418,
    "frames_processed": 418,
    "frames_invalid": 0,
    "frames_dropped": 0,
    "state_transitions": 32,
    "last_processing_ms": 0.12,
    "queue_size": 0,
    "current_state": "STANDING",
    "seconds_since_last_frame": 0.01,
    "tuning_suggestions": {
      "standing_knee_angle_min": 169.9,
      "bottom_knee_angle_max": 89.0,
      "vel_descend_threshold": -0.15,
      "vel_ascend_threshold": 0.17,
      "samples": {"standing": 200, "bottom": 40, "descending": 200, "ascending": 200}
    }
  }
}
```

Ejemplo para ver cualquier topic:

```bash
docker compose exec mqtt mosquitto_sub -t <topic> -v
```

## Variables de entorno

Prefijo `DECISION_`.

Basicas:
- `DECISION_ENV` (default: `dev`)
- `DECISION_LOG_LEVEL` (default: `INFO`)
- `DECISION_MQTT_HOST` (default: `mqtt`)
- `DECISION_MQTT_PORT` (default: `1883`)
- `DECISION_MQTT_USERNAME`
- `DECISION_MQTT_PASSWORD`

Smoothing y buffers:
- `DECISION_BUFFER_SIZE` (default: `30`)
- `DECISION_SMOOTHING_ALPHA_ANGLES` (default: `0.2`)
- `DECISION_SMOOTHING_ALPHA_VELOCITY` (default: `0.3`)
- `DECISION_SMOOTHING_ALPHA_BACK` (default: `0.2`)

Tuning guiado:
- `DECISION_TUNING_ENABLED` (default: `true`)
- `DECISION_TUNING_WINDOW_SIZE` (default: `200`)
- `DECISION_TUNING_MIN_SAMPLES` (default: `40`)

Estados y thresholds:
- `DECISION_STANDING_KNEE_ANGLE_MIN` (default: `165`)
- `DECISION_BOTTOM_KNEE_ANGLE_MAX` (default: `100`)
- `DECISION_KNEE_HYSTERESIS_DEG` (default: `4`)
- `DECISION_VEL_DESCEND_THRESHOLD` (default: `-0.05`)
- `DECISION_VEL_ASCEND_THRESHOLD` (default: `0.05`)
- `DECISION_VEL_IDLE_THRESHOLD` (default: `0.02`)
- `DECISION_MIN_CONFIRM_FRAMES` (default: `3`)
- `DECISION_MIN_REP_INTERVAL_S` (default: `1.0`)

Fatiga y fallo:
- `DECISION_BASELINE_REPS` (default: `3`)
- `DECISION_NEAR_FAILURE_VELOCITY_ABS` (default: `0.03`)
- `DECISION_NEAR_FAILURE_STICKING_S` (default: `1.2`)
- `DECISION_FAILURE_STICKING_S` (default: `2.5`)

## Ejecucion local

```bash
docker compose up decision
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Notas

- El servicio opera con confirmacion temporal de estados (min frames).
- Los thresholds se ajustan con datos reales para minimizar falsos positivos.
- El output de estado se publica de forma continua (frame a frame).
- El topic debug incluye `tuning_suggestions` con thresholds sugeridos basados en muestras reales.
