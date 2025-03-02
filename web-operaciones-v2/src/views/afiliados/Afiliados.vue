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
            class="btn btn-primario" 
            @click="mostrarFormularioCreacion"
          >
            Agregar Afiliado
          </button>
          <button 
            class="btn btn-secundario" 
            @click="actualizarEstados"
            :disabled="cargando"
          >
            Actualizar Estados
          </button>
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

    <!-- Información sobre estados -->
    <div class="info-estados">
      <p><strong>Nota:</strong> Un afiliado se considera <span class="estado-badge estado-activo">Activo</span> si ha participado en operaciones en los últimos 3 meses.</p>
      <p>De lo contrario, se considera <span class="estado-badge estado-inactivo">Inactivo</span>. Los estados se actualizan automáticamente al cargar afiliados u operaciones.</p>
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

    <!-- Modal para Crear Afiliado -->
    <Teleport to="body">
      <div v-if="mostrarFormulario" class="modal-overlay" @click.self="cerrarFormulario">
        <div class="modal-container">
          <div class="modal-header">
            <h3>{{ modoEdicion ? 'Editar Afiliado' : 'Agregar Nuevo Afiliado' }}</h3>
            <button class="modal-close" @click="cerrarFormulario">&times;</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="guardarAfiliado">
              <div class="form-group">
                <label for="numero">Número *</label>
                <input 
                  id="numero" 
                  v-model="formAfiliado.numero" 
                  class="form-control" 
                  required
                  placeholder="Número de afiliado"
                >
              </div>
              <div class="form-group">
                <label for="nombre">Nombre *</label>
                <input 
                  id="nombre" 
                  v-model="formAfiliado.nombre" 
                  class="form-control" 
                  required
                  placeholder="Nombre"
                >
              </div>
              <div class="form-group">
                <label for="apellido_paterno">Apellido Paterno *</label>
                <input 
                  id="apellido_paterno" 
                  v-model="formAfiliado.apellido_paterno" 
                  class="form-control" 
                  required
                  placeholder="Apellido paterno"
                >
              </div>
              <div class="form-group">
                <label for="apellido_materno">Apellido Materno *</label>
                <input 
                  id="apellido_materno" 
                  v-model="formAfiliado.apellido_materno" 
                  class="form-control" 
                  required
                  placeholder="Apellido materno"
                >
              </div>
              <div class="form-group">
                <label for="dni">DNI *</label>
                <input 
                  id="dni" 
                  v-model="formAfiliado.dni" 
                  class="form-control" 
                  required
                  placeholder="DNI"
                >
              </div>
              <div class="form-group">
                <label for="email">Email</label>
                <input 
                  id="email" 
                  v-model="formAfiliado.email" 
                  class="form-control" 
                  type="email"
                  placeholder="Email (opcional)"
                >
              </div>
              <div class="form-group">
                <label for="estado">Estado</label>
                <select 
                  id="estado" 
                  v-model="formAfiliado.estado" 
                  class="form-control"
                >
                  <option value="Activo">Activo</option>
                  <option value="Inactivo">Inactivo</option>
                </select>
                <small class="form-text text-muted">El estado se actualizará automáticamente según la actividad reciente.</small>
              </div>
              <div class="form-actions">
                <button 
                  type="button" 
                  class="btn btn-secundario" 
                  @click="cerrarFormulario"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  class="btn btn-primario"
                  :disabled="enviandoForm"
                >
                  {{ modoEdicion ? 'Actualizar' : 'Guardar' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import FileUploader from '@/components/common/FileUploader.vue';
import Paginacion from '@/components/common/Paginacion.vue';
import afiliadosService from '@/services/afiliadosService';

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
      },
      mostrarFormulario: false,
      modoEdicion: false,
      formAfiliado: {
        id: null,
        numero: '',
        nombre: '',
        apellido_paterno: '',
        apellido_materno: '',
        dni: '',
        email: '',
        estado: 'Activo'
      },
      enviandoForm: false
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
      'subirArchivoAfiliados',
      'actualizarEstadosPorActividad',
      'eliminarTodo'
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
    
    mostrarFormularioCreacion() {
      this.modoEdicion = false;
      this.formAfiliado = {
        id: null,
        numero: '',
        nombre: '',
        apellido_paterno: '',
        apellido_materno: '',
        dni: '',
        email: '',
        estado: 'Activo'
      };
      this.mostrarFormulario = true;
    },
    
    editarAfiliado(afiliado) {
      this.modoEdicion = true;
      this.formAfiliado = { ...afiliado };
      this.mostrarFormulario = true;
    },
    
    cerrarFormulario() {
      this.mostrarFormulario = false;
    },
    
    async guardarAfiliado() {
      if (!this.validarFormulario()) {
        return;
      }
      
      this.enviandoForm = true;
      
      try {
        let response;
        
        if (this.modoEdicion) {
          response = await afiliadosService.actualizarAfiliado(this.formAfiliado.id, this.formAfiliado);
        } else {
          response = await afiliadosService.crearAfiliado(this.formAfiliado);
        }
        
        if (response.success) {
          this.mostrarExito(response.message || 'Afiliado guardado correctamente');
          this.cerrarFormulario();
          this.cargarAfiliados();
        } else {
          this.mostrarError(response.error || 'Error al guardar afiliado');
        }
      } catch (error) {
        this.mostrarError('Error de conexión al guardar afiliado');
        console.error('Error guardando afiliado:', error);
      } finally {
        this.enviandoForm = false;
      }
    },
    
    validarFormulario() {
      const camposRequeridos = ['numero', 'nombre', 'apellido_paterno', 'apellido_materno', 'dni'];
      
      for (const campo of camposRequeridos) {
        if (!this.formAfiliado[campo]) {
          this.mostrarError(`El campo ${campo.replace('_', ' ')} es obligatorio`);
          return false;
        }
      }
      
      return true;
    },
    
    async actualizarEstados() {
      try {
        this.mostrarMensaje({
          texto: "Actualizando estados según participación en los últimos 3 meses...",
          tipo: "info",
          duracion: 0 // No auto-cerrar
        });
        
        const resultado = await this.actualizarEstadosPorActividad();
        
        if (resultado.success) {
          this.mostrarExito(resultado.message);
        } else {
          this.mostrarError(resultado.message || "Error al actualizar los estados");
        }
      } catch (error) {
        this.mostrarError("Error al actualizar los estados de los afiliados");
        console.error("Error actualizando estados:", error);
      }
    },
    
    async confirmarBorrarTodo() {
      const confirmar = await this.pedirConfirmacion('¿Está seguro de eliminar todos los afiliados? Esta acción no se puede deshacer.');
      if (confirmar) {
        try {
          await this.eliminarTodo();
          this.mostrarExito('Todos los afiliados han sido eliminados correctamente.');
        } catch (error) {
          this.mostrarError('Error al eliminar los afiliados');
          console.error('Error en confirmarBorrarTodo:', error);
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

.info-estados {
  background-color: #f8f9fa;
  border-left: 4px solid var(--color-info);
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  border-radius: var(--border-radius-sm);
}

.info-estados p {
  margin: var(--spacing-xs) 0;
  color: var(--color-texto);
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

/* Estilos para el modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-primario);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--color-borde);
  border-radius: var(--border-radius-sm);
  transition: border-color var(--transition-fast);
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primario);
  box-shadow: 0 0 0 2px rgba(0, 120, 215, 0.1);
}

.form-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.85rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
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