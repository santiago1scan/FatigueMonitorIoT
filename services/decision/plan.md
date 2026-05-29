## Plan: Decision Engine biomecanico

Disenar e implementar un servicio Decision Engine en services/decision que consuma MQTT de Vision, aplique buffers + smoothing + estabilizacion temporal, ejecute una maquina de estados biomecanica con hysteresis y confirmacion temporal, compute metrics temporales (fatiga, degradacion, etc.) y publique eventos MQTT estables. Se reutilizan patrones de MQTT/config de Vision/HAL y se agregan defaults configurables. La frecuencia real de Vision se inferira del FPS reportado en health (frame_fps_limit default es 0 = sin limite).

**Steps**
1. Discovery local: alinear configuracion y topicos MQTT con Vision/HAL; decidir libreria MQTT async (recomendado aiomqtt como HAL) y normalizar payloads.  
2. Estructura del servicio: crear services/decision/app con submodulos consumers, buffers, smoothing, biomechanics, state_machine, fatigue, failure_detection, mqtt, schemas, config, metrics, services, utils, y main.py. *Depende de 1.*  
3. Configuracion y schemas: definir Settings (env vars) y schemas de input/output; defaults para thresholds (profundidad, inclinacion) y timings (min_frames_confirm, hysteresis). *Depende de 2.*  
4. MQTT layer: consumer async para gym/vision/pose y gym/vision/metrics con encolado; publisher async para topics de salida. *Depende de 3.*  
5. Buffers temporales: PoseBuffer con deque + ventanas deslizantes; helpers de tendencias (pendiente, varianza, estabilidad). *Depende de 2.*  
6. Smoothing y estabilizacion: filtros EMA para angulos, velocidad vertical, inclinacion espalda y posiciones clave; aplica antes de state machine. *Depende de 5.*  
7. Metrics: separar Instantaneous vs Temporal; calcular profundidad, asimetria, estabilidad, velocidades, sticking duration, consistency score. *Depende de 6.*  
8. State machine centralizada: definir estados en state_machine/states.py y transiciones con hysteresis + confirmacion temporal; manejar TRACKING_LOST/UNSTABLE via confidence. *Depende de 6.*  
9. Repetition counting: validar ciclo completo STANDING->DESCENDING->BOTTOM->ASCENDING->LOCKOUT; anti-rebote y no contar medias reps. *Depende de 8.*  
10. Fatigue score: baseline con 3 reps; score continuo basado en degradacion de velocidad, incremento de torso lean, asimetria y estabilidad. *Depende de 7 y 9.*  
11. Failure detection: near-failure y failure con intento de ascenso + velocidad ~0 + sticking duration excesiva + incapacidad de lockout. *Depende de 8 y 10.*  
12. Observabilidad: metrics internas (latency, throughput, dropped/invalid frames, transition rate) y topic debug. *Depende de 4 y 6.*  
13. Docker/compose: Dockerfile, requirements y fragment docker-compose para decision con env vars. *Depende de 2 y 3.*  
14. README tecnico: documentar pipeline, smoothing, estabilidad temporal, estados y eventos MQTT. *Depende de 13.*

**Relevant files**
- [services/vision/app/config/settings.py](services/vision/app/config/settings.py) — referencia de env vars y topicos  
- [services/vision/app/mqtt/publisher.py](services/vision/app/mqtt/publisher.py) — patron de publish JSON  
- [services/hal/app/mqtt/client.py](services/hal/app/mqtt/client.py) — patron async MQTT (aiomqtt)  
- services/decision — nuevo servicio Decision Engine

**Verification**
1. Ejecutar unit tests de state machine, smoothing y fatigue (pytest).  
2. Simular stream MQTT con payloads grabados y verificar estabilidad de estados y conteo de reps.  
3. Verificar que se publiquen topics de salida con payloads correctos y sin duplicados bajo jitter.

**Decisions**
- Servicio se llama decision y vive en services/decision.  
- Reutilizar configuracion MQTT igual a Vision/HAL.  
- Defaults configurables para thresholds y timings; baseline de fatiga en 3 reps.  
- README y docs en espanol.

**Further Considerations**
1. Frecuencia real de Vision: frame_fps_limit default es 0 (sin limite); ajustar buffers/ventanas segun FPS reportado por Vision health.  
2. Libreria MQTT: aiomqtt para async consumer/publisher (coherente con HAL) vs paho-mqtt (coherente con Vision). Recomendacion: aiomqtt.  
3. Thresholds: ajustar con datos reales; exponer en env/config para tuning.
