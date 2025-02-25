# Sistema de Gestión de Operaciones v2

Versión mejorada del Sistema de Gestión de Operaciones utilizando Vue.js.

## Características

- Gestión completa de operaciones y afiliados
- Emparejador automático de operaciones
- Interfaz moderna y responsive
- Optimizado para rendimiento

## Requisitos

- Node.js >= 14.x
- npm >= 6.x
- Backend API (Flask) ejecutándose en localhost:5000 o configurado en .env

## Instalación

```bash
# Clonar el repositorio
git clone [url-del-repositorio]
cd web-operaciones-v2

# Instalar dependencias
npm install

# Crear archivo .env.local si se necesita sobrescribir configuración
cp .env.development .env.local
```

## Uso

```bash
# Iniciar servidor de desarrollo
npm run serve
# o
npm run dev

# Compilar para producción
npm run build
# o
npm run prod

# Ejecutar linting
npm run lint
```

## Estructura del Proyecto

```
web-operaciones-v2/
├── public/                 # Archivos públicos
├── src/                    # Código fuente
│   ├── assets/             # Recursos estáticos
│   ├── components/         # Componentes Vue
│   │   ├── common/         # Componentes comunes
│   │   ├── layout/         # Componentes de layout
│   │   ├── operaciones/    # Componentes específicos de operaciones
│   │   ├── afiliados/      # Componentes específicos de afiliados
│   │   └── emparejador/    # Componentes específicos del emparejador
│   ├── router/             # Configuración de rutas
│   ├── services/           # Servicios de API
│   ├── store/              # Store Vuex
│   │   ├── modules/        # Módulos del store
│   │   └── index.js        # Configuración principal del store
│   ├── utils/              # Utilidades y helpers
│   ├── views/              # Vistas/Páginas
│   ├── App.vue             # Componente raíz
│   └── main.js             # Punto de entrada
├── .env.development        # Variables de entorno para desarrollo
├── .env.production         # Variables de entorno para producción
├── vue.config.js           # Configuración de Vue CLI
└── package.json            # Dependencias y scripts
```

## API Backend

Este proyecto requiere un backend funcionando en `http://localhost:5000` o la URL especificada en `.env.local`. Asegúrese de que la API backend esté en ejecución antes de iniciar la aplicación.

## Licencia

Todos los derechos reservados.