<template>
  <div class="operaciones">
    <div class="seccion-header">
      <h2>Histórico de Operaciones</h2>
      <p class="seccion-descripcion">Consulte y gestione el histórico de operaciones realizadas.</p>
    </div>

    <!-- Panel de subida de archivos -->
    <div class="panel-control mb-3">
      <FileUploader 
        title="Subir Operaciones" 
        infoText="Formatos permitidos: XLSX, XLS, CSV. Máximo 10MB por archivo."
        @upload="subirArchivos"
      />
    </div>

    <!-- Panel de resumen -->
    <div class="panel-control-tabla">
      <div class="resumen-panel">
        <div class="resumen-item">
          <span class="resumen-label">Monto Total:</span>
          <span class="resumen-valor">{{ formatMonto(montoTotal) }}</span>
        </div>
        <div class="resumen-item">
          <span class="resumen-label">Total Operaciones:</span>
          <span class="resumen-valor">{{ totalOperaciones }}</span>
        </div>
        <div class="acciones-resumen">
          <button 
            class="btn btn-secundario" 
            @click="exportarDatos" 
            :disabled="!hayDatos"
          >
            Exportar
          </button>
          <button 
            class="btn btn-peligro" 
            @click="confirmarBorrarTodo" 
            :disabled="!hayDatos"
          >
            Borrar Todo
          </button>
        </div>
      </div>
    </div>

    <!-- Buscador -->
    <div class="buscador">
      <div class="campo">
        <label for="nombre1">Persona 1:</label>
        <input 
          type="text" 
          id="nombre1" 
          v-model="filtros.nombre1" 
          placeholder="Buscar por nombre o número"
          @input="buscarAfiliado($event, 'nombre1')"
        >
        <div v-if="sugerencias.nombre1.length" class="sugerencias-container">
          <div 
            v-for="(item, index) in sugerencias.nombre1" 
            :key="index"
            class="sugerencia-item"
            @click="seleccionarSugerencia('nombre1', item)"
          >
            <strong>{{ item.nombre_completo }}</strong>
            <small>({{ item.numero }})</small>
          </div>
        </div>
      </div>
      
      <div class="campo">
        <label for="nombre2">Persona 2:</label>
        <input 
          type="text" 
          id="nombre2" 
          v-model="filtros.nombre2" 
          placeholder="Buscar por nombre o número"
          @input="buscarAfiliado($event, 'nombre2')"
        >
        <div v-if="sugerencias.nombre2.length" class="sugerencias-container">
          <div 
            v-for="(item, index) in sugerencias.nombre2" 
            :key="index"
            class="sugerencia-item"
            @click="seleccionarSugerencia('nombre2', item)"
          >
            <strong>{{ item.nombre_completo }}</strong>
            <small>({{ item.numero }})</small>
          </div>
        </div>
      </div>
      
      <div class="campo">
        <label for="fecha-desde">Desde:</label>
        <input 
          type="date" 
          id="fecha-desde" 
          v-model="filtros.fecha_desde"
        >
      </div>
      
      <div class="campo">
        <label for="fecha-hasta">Hasta:</label>
        <input 
          type="date" 
          id="fecha-hasta" 
          v-model="filtros.fecha_hasta"
        >
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
          Limpiar Filtros
        </button>
      </div>
    </div>

    <!-- Tabla de operaciones -->
    <div class="tabla-container">
      <table id="tabla-operaciones">
        <thead>
          <tr>
            <th>Persona 1</th>
            <th>Persona 2</th>
            <th>Monto</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="cargando">
            <tr>
              <td colspan="5" class="text-center">Cargando datos...</td>
            </tr>
          </template>
          <template v-else-if="!operaciones.length">
            <tr>
              <td colspan="5" class="text-center">No se encontraron registros.</td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="operacion in operaciones" :key="operacion.id">
              <td>{{ operacion.nombre1 }}</td>
              <td>{{ operacion.nombre2 }}</td>
              <td>{{ formatMonto(operacion.monto) }}</td>
              <td>{{ formatFecha(operacion.fecha) }}</td>
              <td>
                <button 
                  class="btn-eliminar" 
                  @click="confirmarBorrarOperacion(operacion.id)"
                >
                  Eliminar
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
import afiliadosService from '@/services/afiliadosService';
import dayjs from 'dayjs';

export default {
  name: 'OperacionesView',
  components: {
    FileUploader,
    Paginacion
  },
  data() {
    return {
      sugerencias: {
        nombre1: [],
        nombre2: []
      },
      timeouts: {
        nombre1: null,
        nombre2: null
      },
      filtros: {
        nombre1: '',
        nombre2: '',
        fecha_desde: '',
        fecha_hasta: ''
      },
      valorSeleccionado: {
        nombre1: null,
        nombre2: null
      }
    };
  },
  computed: {
    ...mapState('operaciones', [
      'operaciones',
      'montoTotal',
      'totalOperaciones',
      'cargando',
      'error'
    ]),
    ...mapGetters('operaciones', [
      'paginaActual',
      'totalPaginas'
    ]),
    hayDatos() {
      return this.totalOperaciones > 0;
    },
    paginacion() {
      return {
        paginaActual: this.paginaActual,
        totalPaginas: this.totalPaginas,
        itemsPorPagina: this.$store.state.operaciones.paginacion.itemsPorPagina
      };
    }
  },
  created() {
    // Cargar datos al iniciar el componente
    this.cargarHistorico();
    
    // Inicializar filtros desde el store si existen
    const filtrosStore = this.$store.state.operaciones.filtros;
    if (filtrosStore) {
      this.filtros = { ...filtrosStore };
    }
    
    // Eliminar eventos de click global al desmontar
    document.addEventListener('click', this.cerrarSugerencias);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.cerrarSugerencias);
  },
  methods: {
    ...mapActions('operaciones', [
      'cargarHistorico',
      'aplicarFiltros',
      'limpiarFiltros',
      'cambiarPagina',
      'cambiarItemsPorPagina',
      'eliminarOperacion',
      'eliminarTodo',
      'subirArchivos'
    ]),
    ...mapActions('ui', [
      'mostrarMensaje',
      'mostrarExito',
      'mostrarError',
      'pedirConfirmacion'
    ]),
    
    formatMonto(monto) {
      return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
      }).format(monto);
    },
    
    formatFecha(fecha) {
      return dayjs(fecha).format('DD/MM/YYYY HH:mm');
    },
    
    async buscarAfiliado(event, campo) {
      const texto = event.target.value.trim();
      
      // Limpiar valor seleccionado previo
      this.valorSeleccionado[campo] = null;
      
      // Si hay menos de 2 caracteres, no buscar
      if (texto.length < 2) {
        this.sugerencias[campo] = [];
        return;
      }
      
      // Cancelar timeout anterior si existe
      if (this.timeouts[campo]) {
        clearTimeout(this.timeouts[campo]);
      }
      
      // Esperar 300ms antes de buscar (debounce)
      this.timeouts[campo] = setTimeout(async () => {
        try {
          const resultados = await afiliadosService.buscarAfiliado(texto);
          this.sugerencias[campo] = resultados;
        } catch (error) {
          console.error('Error al buscar afiliados:', error);
        }
      }, 300);
    },
    
    seleccionarSugerencia(campo, item) {
      this.filtros[campo] = item.nombre_completo;
      this.valorSeleccionado[campo] = item.numero;
      this.sugerencias[campo] = [];
    },
    
    cerrarSugerencias(event) {
      // Cerrar sugerencias si se hace clic fuera
      if (!event.target.closest('.campo')) {
        this.sugerencias.nombre1 = [];
        this.sugerencias.nombre2 = [];
      }
    },
    
    buscar() {
      // Aplicar filtros al store
      const filtrosAplicar = {
        ...this.filtros
      };
      
      // Si hay valores seleccionados, usarlos en lugar del texto
      if (this.valorSeleccionado.nombre1) {
        filtrosAplicar.nombre1 = this.valorSeleccionado.nombre1;
      }
      
      if (this.valorSeleccionado.nombre2) {
        filtrosAplicar.nombre2 = this.valorSeleccionado.nombre2;
      }
      
      this.aplicarFiltros(filtrosAplicar);
    },
    
    async confirmarBorrarOperacion(id) {
      const confirmar = await this.pedirConfirmacion('¿Está seguro de eliminar esta operación?');
      if (confirmar) {
        try {
          await this.eliminarOperacion(id);
          this.mostrarExito('Operación eliminada correctamente');
        } catch (error) {
          this.mostrarError('Error al eliminar la operación');
        }
      }
    },
    
    async confirmarBorrarTodo() {
      const confirmar = await this.pedirConfirmacion('¿Está seguro de eliminar todo el histórico?');
      if (confirmar) {
        try {
          await this.eliminarTodo();
          this.mostrarExito('Histórico eliminado correctamente');
        } catch (error) {
          this.mostrarError('Error al eliminar el histórico');
        }
      }
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

.sugerencias-container {
  position: absolute;
  z-index: 10;
  width: 100%;
  background: white;
  border: 1px solid var(--color-borde);
  border-radius: var(--border-radius-sm);
  box-shadow: var(--box-shadow);
  max-height: 200px;
  overflow-y: auto;
}

.sugerencia-item {
  padding: var(--spacing-sm) var(--spacing-md);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sugerencia-item:hover {
  background-color: var(--color-fondo-hover);
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

.btn-eliminar {
  background-color: var(--color-error);
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-eliminar:hover {
  background-color: #bd2130;
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