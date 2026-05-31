# Assist Frontend

Frontend moderno en React con principios SOLID. Interfaz de control en tiempo real para el sistema de asistencia en ejercicios de peso libre.

## Arquitectura

### Principios SOLID aplicados

1. **Single Responsibility Principle**: Cada componente/hook tiene una única responsabilidad
2. **Open/Closed Principle**: Componentes abiertos a extensión, cerrados a modificación
3. **Liskov Substitution Principle**: Props interfaces bien definidas
4. **Interface Segregation Principle**: Componentes reciben solo lo que necesitan
5. **Dependency Inversion Principle**: Inyección de dependencias mediante props y hooks

### Estructura de carpetas

```
src/
├── components/
│   ├── TrafficLight/         # Semáforo de fatiga (presentacional)
│   ├── ControlButtons/       # Botones start/stop (orquestación)
│   ├── SessionDisplay/       # Métricas de sesión (presentacional)
│   ├── Layout/              # Estructura general (presentacional)
│   └── index.ts             # Barrel export
│
├── hooks/
│   ├── useWebSocket.ts      # Gestiona conexión WebSocket
│   ├── useAudio.ts          # Reproductor de audio
│   ├── useApi.ts            # Manejo async de llamadas HTTP
│   └── index.ts             # Barrel export
│
├── services/
│   └── api.ts               # Servicio API (HTTP calls)
│
├── types/
│   └── index.ts             # Tipos compartidos
│
├── App.tsx                  # Componente raíz
├── App.module.css          # Estilos de App
├── index.tsx               # Punto de entrada
└── index.css               # Estilos globales
```

## Componentes

### `TrafficLight`

**Responsabilidad**: Mostrar el semáforo de fatiga (verde, amarillo, rojo)

**Props**:
```typescript
interface TrafficLightProps {
  fatigue: FatigueFlags;  // { green, yellow, red }
}
```

**Características**:
- Completamente presentacional (dumb component)
- Estilos modernos con glow effect
- Responsive

### `ControlButtons`

**Responsabilidad**: Proporcionar botones de control y manejar el estado de carga

**Props**:
```typescript
interface ControlButtonsProps {
  isActive: boolean;
  onStateChange?: () => void;
}
```

**Características**:
- Gestiona llamadas a la API (start/stop)
- Muestra estado de carga
- Manejo de errores
- Botones deshabilitados según el estado

### `SessionDisplay`

**Responsabilidad**: Mostrar métricas de la sesión (reps, conexión)

**Props**:
```typescript
interface SessionDisplayProps {
  repetitions: number;
  isConnected: boolean;
}
```

**Características**:
- Grid responsive
- Indicador de conexión con animación
- Contador de repeticiones

### `Layout`

**Responsabilidad**: Estructura general de la página

**Props**:
```typescript
interface LayoutProps {
  children: ReactNode;
}
```

**Características**:
- Header con título
- Main content área
- Footer
- Responsive

## Hooks Personalizados

### `useWebSocket`

Gestiona la conexión WebSocket con el servidor.

```typescript
const { state, isConnected, error } = useWebSocket();

// state: SessionState | null
// isConnected: boolean
// error: Error | null
```

**Características**:
- Reconexión automática
- Parseo de JSON
- Manejo de errores
- Usa `WS_URL` desde env

### `useAudio`

Gestiona reproducción de audio.

```typescript
const { playSound } = useAudio();

// Reproducir sonido
await playSound();
```

**Características**:
- Carga de audio una sola vez
- Reinicia reproducción si ya estaba sonando
- Manejo seguro de excepciones

### `useApi`

Maneja el ciclo de vida de llamadas HTTP (loading, error, success).

```typescript
const { isLoading, error, execute } = useApi();

// Ejecutar función async
const result = await execute(() => apiService.startAssist());
```

**Características**:
- Estados de loading automáticos
- Captura de errores
- Finally block para cleanup

## Servicio API

**Responsabilidad**: Comunicación HTTP con el backend

```typescript
import { apiService } from "@/services/api";

// Iniciar asistencia
await apiService.startAssist();  // POST /assist/start

// Detener asistencia
await apiService.stopAssist();   // POST /assist/stop
```

**Características**:
- Abstrae los detalles de fetch
- URLs configurables via env
- Validación de respuestas
- Manejo centralizado de errores

## Tipos Compartidos

```typescript
// Estado enviado por WebSocket
interface SessionState {
  repetitions: number;
  fatigue: FatigueFlags;
  play_sound: boolean;
  active: boolean;
}

// Flags del semáforo
interface FatigueFlags {
  green: boolean;
  yellow: boolean;
  red: boolean;
}

// Respuesta de API
interface ApiResponse {
  active: boolean;
}
```

## Flujo de Datos

```
WebSocket                HTTP REST
    │                      │
    ├─→ useWebSocket       ├─→ ControlButtons
    │   (SessionState)     │   (onClick)
    │                      │
    ├─→ App.tsx            ├─→ useApi.execute()
    │                      │
    ├─→ TrafficLight       ├─→ apiService
    │   (fatigue)          │   (POST /assist/*)
    │                      │
    ├─→ SessionDisplay     └─→ Backend (API)
    │   (reps, conexión)
    │
    └─→ useAudio (play_sound)
        (Si play_sound=true)
```

## Variables de Entorno

```env
# API Gateway (default: http://localhost:8000)
VITE_API_URL=http://api:8000

# WebSocket (default: ws://localhost:8000)
VITE_WS_URL=ws://api:8000
```

Ver `.env.example` para más detalles.

## Ejecución Local

### Desarrollo

```bash
npm install
npm run dev
```

Abre [http://localhost:5173](http://localhost:5173)

### Build para producción

```bash
npm run build
npm run preview
```

## Docker

### Build

```bash
docker build -t assist-frontend .
```

### Run (Desarrollo con hot reload)

```bash
docker run -p 5173:5173 \
  -e VITE_API_URL=http://localhost:8000 \
  -e VITE_WS_URL=ws://localhost:8000 \
  assist-frontend
```

### Con Docker Compose

```bash
docker compose up frontend
```

Requiere que la API esté ejecutándose en `http://localhost:8000`

## Decisiones Arquitectónicas

### 1. **React 18 + TypeScript**

Tipo seguro, mejor DX, performance mejorado con concurrent features.

### 2. **Hooks personalizados**

- `useWebSocket`: Lógica de transporte aislada
- `useAudio`: Audio como efecto secundario
- `useApi`: Async state management

Permite testear lógica de negocio sin testing de componentes.

### 3. **CSS Modules**

- Styles scoped por componente
- Evita conflictos de nombres
- Mejor maintainability que CSS global

### 4. **Componentes presentacionales vs contenedores**

- **Presentacionales**: `TrafficLight`, `SessionDisplay`, `Layout` (props only)
- **Contenedores**: `ControlButtons`, `App` (hooks + lógica)

### 5. **Barrel exports**

Importes claros:
```typescript
import { TrafficLight, ControlButtons } from "@/components";
import { useWebSocket, useApi } from "@/hooks";
```

### 6. **Vite como bundler**

- Fast HMR (Hot Module Replacement)
- Build time rápido
- Production-ready bundle

### 7. **Sin estado global (Redux, Zustand)**

El estado es simple y viene del servidor via WebSocket. No necesita sincronización compleja.

## Testing

La arquitectura facilita testing:

```typescript
// Mock useWebSocket
jest.mock("@/hooks", () => ({
  useWebSocket: () => ({
    state: { repetitions: 5, fatigue: { green: true, yellow: false, red: false }, ... },
    isConnected: true,
    error: null,
  }),
}));

// Testear ControlButtons sin WebSocket real
render(<ControlButtons isActive={false} />);
```

## Extensiones futuras

- [ ] Autenticación con JWT
- [ ] Historial de sesiones (localStorage)
- [ ] Gráficos de tendencia (Chart.js)
- [ ] Tema claro/oscuro
- [ ] Soporte PWA (offline)
- [ ] Unit tests con Vitest
- [ ] E2E tests con Playwright
- [ ] Notificaciones (toast)
- [ ] Estado de sincronización visual
- [ ] Análisis de rendimiento (Lighthouse CI)

## Performance

- **Code splitting**: Automático con Vite
- **Lazy loading**: Components cargados on-demand
- **Memoization**: React.memo donde sea necesario
- **CSS-in-JS**: CSS Modules (0 runtime overhead)
- **Bundle size**: ~50KB gzipped (sin deps externas)

## Accesibilidad

- Semántica HTML5
- ARIA labels en botones
- Keyboard navigation
- Color contrast >= 4.5:1

## Compatibilidad

- Chrome, Firefox, Safari, Edge (últimas 2 versiones)
- iOS 14+, Android 9+
- Tailwind-free (CSS Modules puro)

## Licencia

MIT - Libre para usar, modificar y distribuir
