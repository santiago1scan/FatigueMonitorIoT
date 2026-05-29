# AI Agent Guide

## Project overview
- Sistema IoT edge-native para asistencia inteligente en ejercicios de peso libre.
- Arquitectura event-driven via MQTT; servicios desacoplados (Vision, Decision, HAL, API).
- Documento general: [README.md](README.md).

## Core services
- Vision Service (pose + metricas biomecanicas basicas, publica MQTT): [services/vision/README.md](services/vision/README.md).
- HAL Service (hardware abstraction, consume MQTT para actuadores): [services/hal/README.md](services/hal/README.md).
- Decision Engine (en construccion; pipeline biomecanico temporal): [services/decision/plan.md](services/decision/plan.md).

## MQTT topics clave
- Vision publica: `gym/vision/pose`, `gym/vision/metrics`, `gym/vision/debug`, `gym/vision/health`.
- HAL consume: `gym/assist/activate`, `gym/assist/disable`.
- Decision Engine esperado: `gym/decision/state`, `gym/decision/repetition`, `gym/decision/fatigue`, `gym/decision/failure`, `gym/decision/metrics`, `gym/decision/debug`.

## Docker compose
- Servicios definidos en [docker-compose.yml](docker-compose.yml).
- El servicio decision esta comentado; activarlo cuando exista Dockerfile y config.

## Coding conventions
- Python-first, modular, tipado, con configuracion via variables de entorno por servicio.
- Evitar acoplar hardware fuera de HAL; toda logica biomecanica debe ir en Decision.
- Publicar/consumir por MQTT; no llamadas directas entre servicios salvo necesidad local.

## Where to look first
- Configuracion y env vars de Vision: [services/vision/app/config/settings.py](services/vision/app/config/settings.py).
- MQTT client async en HAL: [services/hal/app/mqtt/client.py](services/hal/app/mqtt/client.py).
- Plan detallado Decision Engine: [services/decision/plan.md](services/decision/plan.md).

## Common tasks
- Levantar servicios: `docker compose up vision hal mqtt`.
- Verificar topics de Vision usando broker local en `mqtt:1883`.

## Notes
- El sistema es edge-first; decisiones criticas deben ejecutarse localmente.
- Evitar copiar documentacion existente; enlazar a los README en lugar de duplicar contenido.
