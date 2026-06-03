# Assist API Gateway

Microservicio FastAPI que actúa como API Gateway entre MQTT (Decision Engine) y frontend web. Implementa principios SOLID y arquitectura en capas.

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│         Assist API Gateway (FastAPI)            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐        ┌──────────────────┐   │
│  │  REST API   │        │   WebSocket /ws  │   │
│  │  /assist/*  │        │  (Broadcast)     │   │
│  └──────┬──────┘        └────────┬─────────┘   │
│         │                        │              │
│         └────────────┬───────────┘              │
│                      ▼                          │
│           AssistantService                     │
│        (Business Logic + State)                │
│                      │                         │
│         ┌────────────┼────────────┐            │
│         ▼            ▼            ▼            │
│    MQTTClient   Handlers    ConnectionManager  │
│    (Publish)   (Parse JSON)  (Broadcast)       │
│         │                       │              │
└─────────┼───────────────────────┼──────────────┘
          │                       │
        MQTT                   WebSocket
       Broker                  Clients
       :1883                   (Frontend)
```

## Responsabilidades por módulo

### Core

- **`config.py`**: Configuración mediante variables de entorno (pydantic BaseSettings)

### Models

- **`frontend_state.py`**: `FrontendState` (broadcast a clientes), `FatigueFlags` (semáforo)
- **`repetition.py`**: `RepetitionEvent` (eventos desde Decision Engine)
- **`fatigue.py`**: `FatigueEvent` (score de fatiga)
- **`failure.py`**: `FailureEvent` (fallos y near-failures)
- **`state.py`**: Snapshot genérico (no persistido)

### MQTT

- **`mqtt_client.py`**: Cliente async reutilizable usando `asyncio_mqtt`
  - Gestiona ciclo de vida (connect/disconnect)
  - Publica comandos a HAL (`gym/assist/activate`, `gym/assist/disable`)
  - Expone método `listen(handlers)` para suscribirse
  
- **`handlers.py`**: Adapta payloads JSON a modelos de dominio
  - `on_repetition()`, `on_fatigue()`, `on_failure()`
  - Llama métodos del `AssistantService`

### Services

- **`assistant_service.py`**: Lógica de negocio centralizada
  - Mantiene estado en memoria: `repetitions`, `fatigue_score`, `play_sound`, `active`
  - Procesa eventos MQTT y convierte a actualizaciones de estado
  - Publica comandos MQTT (start/stop)
  - Orquesta broadcasts a WebSocket
  - Implementa conversión fatiga → semáforo (GREEN/YELLOW/RED)

### WebSocket

- **`connection_manager.py`**: Gestión de clientes WebSocket
  - Registra y elimina conexiones
  - `broadcast_state()`: envía `FrontendState` a todos los clientes
  - Manejo de desconexiones automáticas

### API

- **`routes.py`**: Endpoints REST
  - `POST /assist/start`: activa HAL
  - `POST /assist/stop`: desactiva HAL
  - Usa Dependency Injection para acceder al `AssistantService`

### Main

- **`main.py`**: Factory y ciclo de vida de la app
  - Factory pattern para instantiar singletons
  - Startup: conecta MQTT y inicia background task de escucha
  - Shutdown: cancela task y desconecta MQTT
  - WebSocket endpoint `/ws` integrado
  - CORS habilitado para desarrollo

## Flujo de datos

### Ingreso: MQTT → WebSocket

```
Decision Engine
    ↓
 MQTT Broker
    ↓
MQTTClient.listen()
    ↓
MQTTHandlers (parse JSON)
    ↓
AssistantService.process_*()
    ↓
_broadcast()
    ↓
ConnectionManager.broadcast_state()
    ↓
WebSocket Clients (Frontend)
```

### Egreso: REST API → MQTT

```
POST /assist/start
    ↓
AssistantService.start_assist()
    ↓
MQTTClient.publish_activate()
    ↓
MQTT Broker
    ↓
HAL Service
```

## Topics MQTT

### Suscritos (Entrada)

- `gym/decision/repetition`
  ```json
  {
    "timestamp": "2026-05-29T02:40:20.123456+00:00",
    "event": "NEW_REP",
    "rep": 5,
    "depth_ok": true
  }
  ```

- `gym/decision/fatigue`
  ```json
  {
    "timestamp": "2026-05-29T02:40:20.123456+00:00",
    "fatigue_score": 0.58
  }
  ```

- `gym/decision/failure`
  ```json
  {
    "timestamp": "2026-05-29T02:40:20.123456+00:00",
    "event": "NEAR_FAILURE",
    "confidence": 0.81
  }
  ```

### Publicados (Salida)

- `gym/assist/activate`
  ```json
  {
    "command": "activate"
  }
  ```

- `gym/assist/disable`
  ```json
  {
    "command": "disable"
  }
  ```

## Estado en memoria

```python
AssistantService:
  repetitions: int          # número de reps (0-∞)
  fatigue_score: float      # 0.0-1.0
  play_sound: bool          # trigger para audio en frontend
  active: bool              # HAL habilitado
```

### Lógica de fatiga (semáforo)

```
score < 0.40        → GREEN (ok)
0.40 ≤ score < 0.75 → YELLOW (atención)
score >= 0.75       → RED (crítico)
```

### Estados de fallo

- `NEAR_FAILURE`: escalada a RED (fatiga_score = 1.0)
- `FAILURE`: activa `play_sound = true` (single-shot)

## Endpoints REST

### `POST /assist/start`

Activa el sistema de asistencia.

**Efecto**:
- Publica `gym/assist/activate` a MQTT
- Establece `active = true`
- Broadcast nuevo estado a WebSocket

**Respuesta**:
```json
{
  "active": true
}
```

### `POST /assist/stop`

Desactiva el sistema de asistencia.

**Efecto**:
- Publica `gym/assist/disable` a MQTT
- Establece `active = false`
- Resetea `repetitions = 0`, `fatigue_score = 0.0` y `play_sound = false`
- Broadcast nuevo estado a WebSocket

**Respuesta**:
```json
{
  "active": false
}
```

## WebSocket

### Endpoint: `/ws`

Broadcast en tiempo real del estado de sesión.

**Mensaje (cada cambio de estado)**:
```json
{
  "repetitions": 12,
  "fatigue": {
    "green": true,
    "yellow": false,
    "red": false
  },
  "play_sound": false,
  "active": true
}
```

**Cliente de ejemplo (JavaScript)**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
  const state = JSON.parse(event.data);
  console.log('New state:', state);
  if (state.play_sound) {
    playAudio();
  }
};
```

## Variables de entorno

Prefijo: `ASSIST_`

```env
# MQTT
ASSIST_MQTT_HOST=mqtt          # default: mqtt
ASSIST_MQTT_PORT=1883          # default: 1883

# Logging
ASSIST_LOG_LEVEL=INFO          # default: INFO
```

## Ejecución

### Local con Docker Compose

```bash
docker compose up api
```

Requiere que `mqtt` esté ejecutándose (broker Mosquitto).

### Local con Python

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testing

No hay tests unitarios incluidos, pero la arquitectura permite:

```python
# Mock del MQTT client
mqtt_mock = MagicMock(spec=MQTTClient)

# Instancia de servicio para testing
svc = AssistantService(mqtt_client=mqtt_mock, connection_manager=conn_mgr)

# Test de lógica de negocio
await svc.process_fatigue(FatigueEvent(timestamp="...", fatigue_score=0.85))
assert svc.fatigue_score == 0.85
```

## Decisiones arquitectónicas

### 1. **Factory pattern en main.py**

Facilita testing e instantiación de singletons. Cada módulo puede mockease sin afectar otros.

### 2. **AssistantService centralizado**

Toda la lógica de negocio en un único servicio. Sin Repository ni persistencia. Estado en memoria optimizado para latencia baja.

### 3. **MQTTHandlers separado**

Desacopla parsing de JSON de la lógica. Permite cambiar formato sin tocar `AssistantService`.

### 4. **Dependency Injection en rutas**

`Depends(get_assistant)` permite acceder a `AssistantService` desde endpoints sin imports circulares.

### 5. **Broadcast automático tras cada cambio**

Cada `process_*()` y `start_assist()` / `stop_assist()` llama `_broadcast()`. Frontend siempre recibe el estado actual.

### 6. **`play_sound` es stateless tras broadcast**

Se resetea después de cada envío. Frontend debe trigger audio una sola vez por evento.

### 7. **ConnectionManager sin lógica de negocio**

Solo maneja WebSocket; `AssistantService` no depende de detalles de transporte.

### 8. **Tipado completo (Pydantic v2)**

Validación automática de payloads MQTT. Errores de parsing no rompen el servicio.

## Ejemplo de flujo completo

1. Usuario presiona "Start" en frontend
   ```
   POST /assist/start
   ```

2. AssistantService publica a MQTT
   ```
   gym/assist/activate → HAL Service
   ```

3. Usuario realiza squat
   ```
   Decision Engine → gym/decision/repetition
   ```

4. AssistantService recibe repetición
   ```
   on_repetition() → repetitions = 1
   ```

5. Broadcast a todos los clientes WebSocket
   ```json
   {
     "repetitions": 1,
     "fatigue": {"green": true, "yellow": false, "red": false},
     "play_sound": false,
     "active": true
   }
   ```

6. Frontend recibe y actualiza UI

## Dependencias

```
fastapi>=0.104.0
pydantic>=2.0.0
asyncio-mqtt>=0.16.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
```

Ver `requirements.txt` para pinned versions.

## Extensiones futuras

- Autenticación (JWT en WebSocket)
- Persistencia de sesiones (Redis)
- Métricas (Prometheus)
- Health check endpoint
- Logging estructurado (JSON)
- Rate limiting en REST endpoints
- Retry policy en MQTT
