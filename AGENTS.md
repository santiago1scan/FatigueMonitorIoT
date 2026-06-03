# AI Agent Guide

## Architecture
- 5 microservicios, event-driven via MQTT (Eclipse Mosquitto, puerto 1883).
- Edge-first: sin dependencia cloud; decisiones locales.
- Hardware solo en HAL; logica biomecanica solo en Decision.

| Servicio | Directorio | Entrypoint | MQTT lib |
|----------|------------|------------|----------|
| Vision | `services/vision` | `python -m app.main` | paho-mqtt (blocking) |
| Decision | `services/decision` | `python -m app.main` | aiomqtt (async) |
| HAL | `services/hal` | uvicorn FastAPI (factory) | aiomqtt |
| API | `services/api` | uvicorn FastAPI | aiomqtt |
| Frontend | `services/frontend` | Vite dev server | — |

Env vars por servicio: `VISION_*`, `DECISION_*`, `HAL_*`, `ASSIST_*` (API).

## Topics MQTT
- Vision pub: `gym/vision/pose`, `gym/vision/metrics`, `gym/vision/debug`, `gym/vision/health`
- Decision pub: `gym/decision/state`, `gym/decision/repetition`, `gym/decision/fatigue`, `gym/decision/failure`, `gym/decision/metrics`, `gym/decision/debug`
- HAL pub: `gym/system/status`, `gym/hal/health`, `gym/hal/errors`; sub: `gym/assist/activate`, `gym/assist/disable`
- API sub (todos los topics decision) + pub (`gym/assist/*`)
- Frontend se conecta via WebSocket a API (no MQTT directo)

## Comandos
```sh
docker compose up --build                          # todos los servicios
docker compose up vision hal mqtt                  # subset
docker compose up <service>                        # uno solo
python -m pytest tests/    # (en services/decision) # unicos tests del repo
cd services/frontend && npm run dev                 # frontend fuera de Docker
docker compose -f services/hal/docker-compose.hal.yml up  # HAL standalone con GPIO
```

## Gotchas
- **Vision usa paho-mqtt (blocking)**, todos los demas servicios Python usan aiomqtt (async).
- El modelo MediaPipe `services/vision/pose_landmarker.task` es binario y esta commiteado.
- HAL selecciona drivers via `HAL_SERVO_PROVIDER`, `HAL_CAMERA_PROVIDER`, etc. (`mock|raspberry`).
- `decision_metrics_debug.jsonl` en raiz es dump de debug runtime (trackeado, sin `.gitignore`).
- `config/` y `volumes/` son placeholders vacios.
- No existe linter/formatter/typecheck configurado a nivel raiz.
- Usar `docker compose` (v2), no `docker-compose` (v1).

## Reglas
- Logica biomecanica exclusivamente en **Decision**.
- Acceso a hardware exclusivamente en **HAL** (usar drivers mock para dev local).
- No duplicar documentacion existente; enlazar a READMEs en su lugar.
