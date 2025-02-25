<template>
  <div class="afiliados">
    <div class="seccion-header">
      <h2>Información de Afiliados</h2>
      <p class="seccion-descripcion">Gestione la información de los afiliados registrados.</p>
    </div>

    <!-- Panel de subida de archivos -->
    <div class="panel-control mb-3">
      <FileUploader 
        title="Subir Lista de Afiliados" 
        infoText="Formatos permitidos: XLSX, XLS, CSV. Máximo 10MB."
        :multiple="false"
        @upload="subirArchivoAfiliados"
      />
    </div>

    <!-- Panel de resumen -->
    <div class="panel-control-tabla">
      <div class="resumen-panel">
        <div class="resumen-item">
          <span class="resumen-label">Total Afiliados:</span>
          <span class="resumen-valor">{{ totalAfiliados }}</span>
        </div>
        <div class="resumen-item">
          <span class="resumen-label">Afiliados Activos:</span>
          <span class="resumen-valor">{{ afiliadosActivos }}</span>
        </div>
        <div class="acciones-resumen">
          <button 
            class="btn btn-secundario" 
            @click="exportarDatos" 
            :disabled="!hayDatos"
          >
            Exportar
          </button>
        </div>
      </div>
    </div>

    <!-- Buscador -->
    <div class="buscador">
      <div class="campo">
        <label for="buscar-numero">Número:</label>
        <input 
          type="text" 
          id="buscar-numero" 
          v-model="filtros.numero" 
          placeholder="Buscar por número"
        >
      </div>
      <div class="campo">
        <label for="buscar-nombre">Nombre:</label>
        <input 
          type="text" 
          id="buscar-nombre" 
          v-model="filtros.nombre" 
          placeholder="Buscar por nombre"
        >
      </div>
      <div class="campo">
        <label for="buscar-dni">DNI:</label>
        <input 
          type="text" 
          id="buscar-dni" 
          v-model="filtros.dni" 
          placeholder="Buscar por DNI"
        >
      </div>
      <div class="campo">
        <label for="filtro-estado">Estado:</label>
        <select id="filtro-estado" v-model="filtros.estado">
          <option value="Todos">Todos</option>
          <option value="Activo">Activo</option>
          <option value="Inactivo">Inactivo</option>
        </select>
      </div>
      <div class="campo campo-botones">
        <button 
          class="btn btn-primario" 
          @click="buscar"
        >
          Buscar
        </button>
        <button 
          class="btn btn-secundario" 
          @click="limpiarFiltros"
        >
          Limpiar
        </button>
      </div>
    </div>

    <!-- Tabla de afiliados -->
    <div class="tabla-container">
      <table id="tabla-afiliados">
        <thead>
          <tr>
            <th>Número</th>
            <th>Nombre</th>
            <th>Apellidos</th>
            <th>DNI</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="cargando">
            <tr>
              <td colspan="6" class="text-center">Cargando datos...</td>
            </tr>
          </template>
          <template v-else-if="!afiliados.length">
            <tr>
              <td colspan="6" class="text-center">No se encontraron afiliados.</td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="afiliado in afiliados" :key="afiliado.id">
              <td>{{ afiliado.numero }}</td>
              <td>{{ afiliado.nombre }}</td>
              <td>{{ afiliado.apellido_paterno }} {{ afiliado.apellido_materno }}</td>
              <td>{{ afiliado.dni }}</td>
              <td>
                <span 
                  :class="['estado-badge', afiliado.estado === 'Activo' ? 'estado-activo' : 'estado-inactivo']"
                >
                  {{ afiliado.estado }}
                </span>
              </td>
              <td>
                <button 
                  class="btn-editar" 
                  @click="editarAfiliado(afiliado)"
                >
                  Editar
                </button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Paginación -->
    <Paginacion 
      :pagina-actual="paginacion.paginaActual"
      :total-paginas="paginacion.totalPaginas"
      :items-por-pagina="paginacion.itemsPorPagina"
      @cambiar-pagina="cambiarPagina"
      @cambiar-items="cambiarItemsPorPagina"
    />
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import FileUploader from '@/components/common/FileUploader.vue';
import Paginacion from '@/components/common/Paginacion.vue';

export default {
  name: 'AfiliadosView',
  components: {
    FileUploader,
    Paginacion
  },
  data() {
    return {
      filtros: {
        numero: '',
        nombre: '',
        dni: '',
        estado: 'Todos'
      }
    };
  },
  computed: {
    ...mapState('afiliados', [
      'afiliados',
      'totalAfiliados',
      'afiliadosActivos',
      'cargando',
      'error'
    ]),
    ...mapGetters('afiliados', [
      'paginaActual',
      'totalPaginas'
    ]),
    hayDatos() {
      return this.totalAfiliados > 0;
    },
    paginacion() {
      return {
        paginaActual: this.paginaActual,
        totalPaginas: this.totalPaginas,
        itemsPorPagina: this.$store.state.afiliados.paginacion.itemsPorPagina
      };
    }
  },
  created() {
    // Cargar datos al iniciar el componente
    this.cargarAfiliados();
    
    // Inicializar filtros desde el store si existen
    const filtrosStore = this.$store.state.afiliados.filtros;
    if (filtrosStore) {
      this.filtros = { ...filtrosStore };
    }
  },
  methods: {
    ...mapActions('afiliados', [
      'cargarAfiliados',
      'aplicarFiltros',
      'limpiarFiltros',
      'cambiarPagina',
      'cambiarItemsPorPagina',
      'subirArchivoAfiliados'
    ]),
    ...mapActions('ui', [
      'mostrarMensaje',
      'mostrarExito',
      'mostrarError',
      'pedirConfirmacion'
    ]),
    
    buscar() {
      // Aplicar filtros al store
      this.aplicarFiltros(this.filtros);
    },
    
    editarAfiliado(afiliado) {
      // Función para editar afiliado
      this.mostrarMensaje({
        texto: `Funcionalidad de edición en desarrollo para ${afiliado.nombre}`,
        tipo: 'info'
      });
    },
    
    async exportarDatos() {
      // Esta función implementará la exportación de datos
      this.mostrarMensaje({
        texto: 'Funcionalidad de exportación en desarrollo',
        tipo: 'info'
      });
    }
  }
};
</script>

<style scoped>
.seccion-header {
  margin-bottom: var(--spacing-lg);
}

.seccion-header h2 {
  margin-bottom: var(--spacing-xs);
  color: var(--color-primario);
}

.seccion-descripcion {
  color: var(--color-texto-claro);
}

.panel-control {
  background-color: var(--color-blanco);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--box-shadow);
}

.panel-control-tabla {
  background-color: var(--color-blanco);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--box-shadow);
}

.resumen-panel {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-lg);
}

.resumen-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  white-space: nowrap;
}

.resumen-label {
  font-weight: 500;
  color: var(--color-texto-claro);
}

.resumen-valor {
  font-weight: 600;
  color: var(--color-texto);
}

.acciones-resumen {
  display: flex;
  gap: var(--spacing-md);
  margin-left: auto;
  flex-wrap: wrap;
}

.buscador {
  background-color: var(--color-blanco);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  box-shadow: var(--box-shadow);
}

.campo {
  margin-bottom: var(--spacing-md);
  position: relative;
}

.campo label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
  color: var(--color-texto);
}

.campo input,
.campo select {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-borde);
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
  transition: all var(--transition-fast);
}

.campo input:focus,
.campo select:focus {
  outline: none;
  border-color: var(--color-primario);
  box-shadow: 0 0 0 2px rgba(0, 120, 215, 0.1);
}

.campo-botones {
  display: flex;
  gap: var(--spacing-sm);
  align-items: flex-end;
}

.tabla-container {
  overflow-x: auto;
  background-color: var(--color-blanco);
  border-radius: var(--border-radius-md);
  box-shadow: var(--box-shadow);
  margin-bottom: var(--spacing-lg);
}

table {
  width: 100%;
  border-collapse: collapse;
}

table th,
table td {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-borde);
  text-align: left;
}

table th {
  background-color: var(--color-primario);
  color: var(--color-blanco);
  font-weight: 500;
  white-space: nowrap;
}

table tr:nth-child(even) {
  background-color: var(--color-fondo-alterno);
}

table tr:hover {
  background-color: var(--color-fondo-hover);
}

.estado-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.estado-activo {
  background-color: var(--color-exito);
  color: white;
}

.estado-inactivo {
  background-color: var(--color-texto-claro);
  color: white;
}

.btn-editar {
  background-color: var(--color-info);
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-editar:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .panel-control-tabla {
    padding: var(--spacing-md);
  }

  .resumen-panel {
    flex-direction: column;
    align-items: flex-start;
  }

  .acciones-resumen {
    margin-left: 0;
    width: 100%;
    justify-content: space-between;
    margin-top: var(--spacing-md);
  }

  .campo-botones {
    flex-direction: column;
    width: 100%;
  }

  .campo-botones button {
    width: 100%;
  }
}
</style>