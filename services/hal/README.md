# HAL Service

Base funcional del Hardware Abstraction Layer (HAL) para el sistema Smart Gym Assistant.

## Objetivos

- Abstraer GPIO, PWM, servos y camara.
- Exponer una API local de diagnostico.
- Consumir eventos MQTT y ejecutar acciones fisicas.
- Publicar estado y salud por MQTT.

## Estructura

```text
hal/
├── app/
│   ├── actuators/
│   ├── camera/
│   ├── config/
│   ├── domain/
│   ├── drivers/
│   ├── gpio/
│   ├── mqtt/
│   ├── api/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
├── Dockerfile
├── docker-compose.hal.yml
├── requirements.txt
└── README.md
```

## MQTT

Topics suscritos:

- gym/assist/activate
- gym/assist/disable

Topics publicados:

- gym/system/status
- gym/hal/health
- gym/hal/errors

Payload ejemplo:

```json
{
  "force": 0.6
}
```

## API local

- GET /health
- GET /status
- POST /servo/test
- GET /camera/status

## Variables de entorno

Todas usan prefijo `HAL_`.

- HAL_MQTT_HOST
- HAL_MQTT_PORT
- HAL_MQTT_USERNAME
- HAL_MQTT_PASSWORD
- HAL_SERVO_PROVIDER: mock | raspberry
- HAL_CAMERA_PROVIDER: mock | opencv
- HAL_GPIO_PROVIDER: mock | raspberry
- HAL_PWM_PROVIDER: mock | raspberry
- HAL_SERVO_PIN
- HAL_STATUS_LED_PIN
- HAL_CAMERA_DEVICE_INDEX

## Flujo funcional minimo

1. MQTT publica en `gym/assist/activate` con `force`.
2. HAL mueve servo y activa GPIO de estado.
3. HAL publica evento en `gym/system/status`.
4. HAL publica estado de salud periodico en `gym/hal/health`.

## Docker

Fragmento listo en `docker-compose.hal.yml`.

## Siguiente paso

- agregar tests de integracion en `tests/`.
- habilitar metricas o trazas si se requiere observabilidad.
