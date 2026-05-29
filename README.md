# Smart Gym Assistant - Edge IoT System

Sistema IoT orientado a visión artificial y asistencia inteligente para ejercicios de peso libre utilizando una Raspberry Pi como nodo edge principal.

El proyecto busca detectar estados de fatiga, riesgo biomecánico o fallo muscular durante ejercicios como sentadillas, para posteriormente activar mecanismos de asistencia, alertas o monitoreo inteligente.

La arquitectura fue diseñada siguiendo principios:

- Edge Computing
- Event-Driven Architecture
- Semantic IoT
- W3C Web of Things (WoT)
- Modular Services
- Hardware Abstraction
- Containerized Deployment

---

# Objetivos del Proyecto

## Objetivo Principal

Desarrollar un sistema IoT inteligente capaz de:

- Detectar postura corporal y estado de fatiga.
- Analizar biomecánica en tiempo real.
- Activar mecanismos de asistencia.
- Exponer capacidades mediante estándares W3C WoT.
- Operar localmente en una Raspberry Pi.
- Permitir reemplazo modular de modelos IA y protocolos.

---

# Principios Arquitectónicos

## 1. Arquitectura Modular

Cada responsabilidad del sistema debe estar desacoplada.

NO existe lógica monolítica.

Cada módulo debe poder:

- reiniciarse independientemente,
- reemplazarse,
- escalarse,
- simularse.

---

## 2. Event-Driven System

La comunicación interna ocurre principalmente mediante MQTT.

Los módulos NO deben llamarse directamente entre sí cuando no sea necesario.

Patrón:

```text
Producer -> MQTT -> Consumer
```

---

## 3. Hardware Abstraction Layer (HAL)

Solo una capa debe acceder directamente al hardware físico.

Ningún servicio de negocio debe tocar GPIO directamente.

Incorrecto:

```python
GPIO.output(...)
```

Correcto:

```python
assist_motor.activate()
```

---

## 4. Semantic IoT / W3C WoT

El sistema debe exponer:

- Thing Description (TD),
- propiedades,
- acciones,
- eventos.

El objetivo es lograr interoperabilidad semántica entre dispositivos y servicios.

---

## 5. Edge First

Las decisiones críticas deben ejecutarse localmente.

La nube NO participa en decisiones de tiempo real.

---

# Arquitectura General

```text
┌────────────────────────────────────────────┐
│                Frontend UI                │
│ Dashboard Web                             │
└────────────────────┬──────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼──────────────────────┐
│              API Gateway                  │
│ REST API + WoT Layer                      │
└────────────────────┬──────────────────────┘
                     │
               MQTT Events
                     │
┌────────────────────▼──────────────────────┐
│               MQTT Broker                 │
│               Mosquitto                   │
└─────────────┬──────────────┬──────────────┘
              │              │
     ┌────────▼──────┐ ┌─────▼────────┐
     │ Vision Service│ │Decision Engine│
     │ MediaPipe     │ │ Fatigue Logic │
     │ Future Models │ │ Assistance    │
     └────────┬──────┘ └─────┬─────────┘
              │              │
              └──────┬───────┘
                     │
          ┌──────────▼──────────┐
          │ HAL / Device Layer  │
          │ GPIO / Servo / Cam  │
          └─────────────────────┘
```

---

# Servicios Principales

## 1. Vision Service

Responsabilidad:

- Captura de cámara.
- Procesamiento IA.
- Inferencia de pose.
- Detección de landmarks.
- Publicación de eventos.

Inicialmente el sistema utilizará MediaPipe, pero la arquitectura debe permitir reemplazar fácilmente el proveedor de visión.

Publica eventos estructurados con pose y metricas biomecanicas basicas.

Ejemplo de `gym/vision/pose`:

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

Ejemplo de `gym/vision/metrics`:

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

Topics MQTT:

```text
gym/vision/pose
gym/vision/metrics
gym/vision/debug
gym/vision/health
```

Mas detalle en [services/vision/README.md](services/vision/README.md).

---

## 2. Decision Engine

Responsabilidad:

- Detectar fatiga.
- Detectar fallo muscular.
- Generar alertas.
- Solicitar asistencia física.

Consume eventos de Vision, aplica smoothing + buffers temporales, ejecuta una
maquina de estados biomecanica, cuenta reps, estima fatiga y detecta fallo.

Consume:

```text
gym/vision/pose
gym/vision/metrics
```

Publica:

```text
gym/decision/state
gym/decision/repetition
gym/decision/fatigue
gym/decision/failure
gym/decision/metrics
gym/decision/debug
```

Mas detalle en [services/decision/README.md](services/decision/README.md).

---

## 3. HAL (Hardware Abstraction Layer)

Responsabilidad:

- GPIO
- PWM
- Servos
- LEDs
- Sensores físicos
- Cámaras
- Actuadores

Este es el ÚNICO módulo autorizado a tocar hardware directamente.

Todos los demás módulos deben interactuar mediante eventos o APIs internas.

---

## 4. API Gateway

Responsabilidad:

- REST API
- WebSockets
- Estado sistema
- Métricas
- Exposición WoT
- Configuración runtime

Endpoints principales:

```http
GET  /health
GET  /status
GET  /metrics

POST /session/start
POST /session/stop

POST /assist/test

GET  /things/assistant
GET  /.well-known/wot
```

---

## 5. Frontend

Responsabilidad:

- Visualización.
- Configuración.
- Monitoreo.
- Control remoto.
- Visualización de métricas y eventos.

---

# MQTT Topics (Actuales)

## Vision publica

```text
gym/vision/pose
gym/vision/metrics
gym/vision/debug
gym/vision/health
```

## Decision publica

```text
gym/decision/state
gym/decision/repetition
gym/decision/fatigue
gym/decision/failure
gym/decision/metrics
gym/decision/debug
```

## HAL consume y publica

Consume:

```text
gym/assist/activate
gym/assist/disable
```

Publica:

```text
gym/system/status
gym/hal/health
gym/hal/errors
```

## Ejemplos de payloads

Decision state (`gym/decision/state`):

```json
{
  "timestamp": "2026-05-28T03:10:20.123456+00:00",
  "state": "DESCENDING",
  "rep": 4,
  "fatigue_score": 0.62,
  "confidence": 0.86,
  "tracking": true,
  "metrics": {
    "knee_angle_avg": 122.1,
    "back_inclination": 4.7,
    "velocity_vertical": -0.18,
    "depth_score": 0.81
  }
}
```

Decision repetition (`gym/decision/repetition`):

```json
{
  "timestamp": "2026-05-28T03:10:20.123456+00:00",
  "event": "NEW_REP",
  "rep": 5,
  "depth_ok": true
}
```

Decision failure (`gym/decision/failure`):

```json
{
  "timestamp": "2026-05-28T03:10:20.123456+00:00",
  "event": "NEAR_FAILURE",
  "confidence": 0.81
}
```

HAL activate (`gym/assist/activate`):

```json
{
  "force": 0.6
}
```

---

# W3C Web of Things (WoT)

El sistema debe representar el dispositivo usando Thing Description.

Ejemplo:

```json
{
  "@context": "https://www.w3.org/2022/wot/td/v1.1",
  "title": "SmartGymAssistant",

  "properties": {
    "fatigueLevel": {
      "type": "number"
    }
  },

  "actions": {
    "activateAssist": {}
  },

  "events": {
    "fallDetected": {}
  }
}
```

---

# Estructura del Proyecto

```text
project/
│
├── services/
│   ├── api/
│   ├── vision/
│   ├── decision/
│   ├── hal/
│   ├── frontend/
│   └── mqtt/
│
├── shared/
│   ├── schemas/
│   ├── mqtt/
│   ├── config/
│   └── utils/
│
├── docs/
│
├── docker/
│
├── scripts/
│
├── docker-compose.yml
│
└── README.md
```

---

# Estructura Interna Recomendada

## Vision Service

```text
vision/
│
├── providers/
│   ├── mediapipe_provider.py
│   ├── future_provider.py
│   └── base_provider.py
│
├── processing/
├── models/
├── mqtt/
└── main.py
```

---

## Decision Engine

```text
decision/
│
├── app/
│   ├── consumers/
│   ├── buffers/
│   ├── smoothing/
│   ├── biomechanics/
│   ├── state_machine/
│   ├── fatigue/
│   ├── failure_detection/
│   ├── mqtt/
│   ├── schemas/
│   ├── config/
│   ├── metrics/
│   └── main.py
├── tests/
├── Dockerfile
└── requirements.txt
```

---

# Orquestación con Docker

Todos los servicios deben correr mediante Docker Compose.

Objetivos:

- aislamiento,
- reproducibilidad,
- modularidad,
- facilidad de despliegue,
- desacoplamiento de dependencias.

---

# Docker Compose Esperado

```yaml
services:

  mqtt:
    image: eclipse-mosquitto

  api:
    build: ./services/api

  vision:
    build: ./services/vision

  decision:
    build: ./services/decision

  hal:
    build: ./services/hal
    privileged: true

  frontend:
    build: ./services/frontend

---

# Uso rápido

Levantar servicios core:

```bash
docker compose up -d mqtt hal vision decision
```

Ver logs:

```bash
docker compose logs -f decision
```

---

# Configuración (resumen)

## Vision (prefijo `VISION_`)

Variables clave:
- `VISION_MQTT_HOST`, `VISION_MQTT_PORT`
- `VISION_FRAME_SOURCE` (`stream` | `snapshot`)
- `VISION_HAL_STREAM_URL`, `VISION_HAL_SNAPSHOT_URL`
- `VISION_POSE_DET_CONF`, `VISION_POSE_TRACK_CONF`
- `VISION_TOPIC_POSE`, `VISION_TOPIC_METRICS`, `VISION_TOPIC_DEBUG`, `VISION_TOPIC_HEALTH`

## Decision (prefijo `DECISION_`)

Conexion MQTT:
- `DECISION_MQTT_HOST`, `DECISION_MQTT_PORT`
- `DECISION_MQTT_INPUT_TOPICS` (string separado por comas)

Smoothing y buffers:
- `DECISION_BUFFER_SIZE`
- `DECISION_SMOOTHING_ALPHA_ANGLES`
- `DECISION_SMOOTHING_ALPHA_VELOCITY`
- `DECISION_SMOOTHING_ALPHA_BACK`

Estados y thresholds:
- `DECISION_STANDING_KNEE_ANGLE_MIN`
- `DECISION_BOTTOM_KNEE_ANGLE_MAX`
- `DECISION_VEL_DESCEND_THRESHOLD`
- `DECISION_VEL_ASCEND_THRESHOLD`
- `DECISION_VEL_IDLE_THRESHOLD`
- `DECISION_MIN_CONFIRM_FRAMES`

Tuning guiado:
- `DECISION_TUNING_ENABLED`
- `DECISION_TUNING_MIN_SAMPLES`
- `DECISION_TUNING_WINDOW_SIZE`

Mas detalle en [services/decision/README.md](services/decision/README.md).

## HAL (prefijo `HAL_`)

Variables clave:
- `HAL_MQTT_HOST`, `HAL_MQTT_PORT`
- `HAL_SERVO_PROVIDER`, `HAL_CAMERA_PROVIDER`

Mas detalle en [services/hal/README.md](services/hal/README.md).

---

# Debugging y observabilidad

Ver estado actual del Decision Engine:

```bash
docker compose exec mqtt mosquitto_sub -t gym/decision/state -v
```

Ver debug interno y sugerencias de tuning:

```bash
docker compose exec mqtt mosquitto_sub -t gym/decision/debug -v
```

Ver salida de Vision:

```bash
docker compose exec mqtt mosquitto_sub -t gym/vision/metrics -v
```

Si `frames_received` en `gym/decision/debug` es 0, el Decision no esta recibiendo
mensajes de Vision.

---

# Ajuste y tuning del Decision Engine

1) Asegura que aparezca `BOTTOM` en `gym/decision/state`.
2) Espera a que `tuning_suggestions` deje de ser `null`.
3) Ajusta thresholds con margen conservador:
   - `standing_knee_angle_min`: +2 a +5 grados
   - `bottom_knee_angle_max`: -2 a -5 grados
   - `vel_descend_threshold` / `vel_ascend_threshold`: ajustar 0.01–0.02
4) Desactiva tuning cuando tengas valores finales:

```text
DECISION_TUNING_ENABLED=false
DECISION_TUNING_MIN_SAMPLES=40
```
```

---

# Flujo Principal del Sistema

```text
Camera
   ↓
Vision Service
   ↓
MQTT Event
   ↓
Decision Engine
   ↓
Assist Request
   ↓
HAL
   ↓
Servo/Motor
```

---

# Topics MQTT (resumen)

Ver la seccion MQTT Topics (Actuales) para el listado completo.

---

# Tecnologías Base

## Infraestructura

- Docker
- Docker Compose

## Comunicación

- MQTT
- Mosquitto

## Procesamiento de visión

- MediaPipe

## Hardware

- HAL (Hardware Abstraction Layer)

---

# Reglas Importantes del Proyecto

## 1. No acceder GPIO fuera de HAL

Todo acceso hardware debe pasar por HAL.

---

## 2. No acoplar IA con lógica negocio

Vision solo detecta.

Decision Engine decide.

---

## 3. Todo evento importante debe publicarse

El sistema debe ser observable.

---

## 4. APIs deben ser semánticas

No exponer datos crudos innecesarios.

---

## 5. Mantener interoperabilidad WoT

Los modelos semánticos son parte central del sistema.

---

# Futuras Extensiones

## IA

- Nuevos modelos de visión
- Optimización edge
- Aceleración hardware

## IoT

- Multi-device federation
- Discovery semántico
- Digital Twin

## Observabilidad

- Métricas
- Logging centralizado
- Telemetría

## Cloud

- Históricos
- Analytics
- User profiles

---

# Estado Actual del Proyecto

Estado actual:

- Arquitectura conceptual definida.
- Diseño modular definido.
- Sistema orientado a eventos definido.
- Vision Service operativo (MediaPipe + MQTT).
- Decision Engine operativo (estados, reps, fatiga, fallo).
- Orquestación con Docker definida.
- Frontend y API en progreso.

---

# Filosofía del Sistema

Este proyecto NO busca únicamente detectar poses.

Busca construir una arquitectura IoT edge-native moderna:

- desacoplada,
- semántica,
- extensible,
- observable,
- interoperable,
- preparada para IA modular.