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

Ejemplo de evento:

```json
{
  "timestamp": "2026-05-27T18:00:00Z",
  "knee_angle": 92,
  "hip_angle": 87,
  "fatigue_score": 0.73
}
```

Topics MQTT:

```text
gym/vision/pose
gym/vision/fatigue
```

---

## 2. Decision Engine

Responsabilidad:

- Detectar fatiga.
- Detectar fallo muscular.
- Generar alertas.
- Solicitar asistencia física.

Consume:

```text
gym/vision/#
```

Publica:

```text
gym/assist/activate
gym/user/risk
```

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
├── rules/
├── fatigue/
├── assistance/
├── mqtt/
└── main.py
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

# Topics MQTT Recomendados

```text
gym/vision/pose
gym/vision/fatigue

gym/system/status
gym/system/error

gym/assist/activate
gym/assist/disable

gym/session/start
gym/session/end

gym/user/alert
```

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
- Integración WoT planificada.
- Orquestación con Docker definida.
- Pendiente implementación inicial.

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