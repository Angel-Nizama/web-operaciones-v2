<template>
  <div class="emparejador-calculador">
    <div class="seccion-header">
      <h2>Emparejador de Operaciones</h2>
      <div class="tabs-container">
        <router-link to="/emparejador" class="tab-btn">Gestión de Rangos</router-link>
        <router-link to="/emparejador/calcular" class="tab-btn active">Emparejamiento Automático</router-link>
      </div>
    </div>

    <!-- Panel de control de emparejamiento -->
    <div class="panel-control">
      <div class="filtros-emparejamiento">
        <div class="campo">
          <label for="dias-minimos">Días mínimos entre operaciones:</label>
          <input 
            type="number" 
            id="dias-minimos" 
            v-model.number="configuracion.diasMinimos"
            min="1" 
            class="form-input"
          >
        </div>
        <div class="campo">
          <label for="riesgo-maximo">Riesgo máximo permitido:</label>
          <input 
            type="number" 
            id="riesgo-maximo"
            v-model.number="configuracion.riesgoMaximo" 
            min="0" 
            max="100" 
            class="form-input"
          >
        </div>
        <button 
          id="calcular-emparejamientos" 
          class="btn btn-primario"
          @click="calcularEmparejamientos"
          :disabled="cargando"
        >
          <span v-if="!cargando">Calcular Emparejamientos</span>
          <span v-else>Calculando...</span>
        </button>
      </div>
      <div class="buscador-emparejador">
        <div class="campo">
          <label for="emparejador-nombre1">Afiliado 1:</label>
          <input 
            type="text" 
            id="emparejador-nombre1" 
            v-model="filtroAfiliado1"
            placeholder="Buscar por nombre o número"
            @input="filtrarResultados"
          >
        </div>
        <div class="campo">
          <label for="emparejador-nombre2">Afiliado 2:</label>
          <input 
            type="text" 
            id="emparejador-nombre2" 
            v-model="filtroAfiliado2"
            placeholder="Buscar por nombre o número"
            @input="filtrarResultados"
          >
        </div>
        <div class="campo campo-botones">
          <button 
            id="emparejador-limpiar-btn" 
            class="btn btn-secundario"
            @click="limpiarFiltros"
          >
            Limpiar
          </button>
        </div>
      </div>
    </div>

    <!-- Tabla de resultados -->
    <div 
      v-if="cargandoEmparejamientos || cargandoDetalles" 
      class="cargando-container"
    >
      <div class="spinner"></div>
      <p>{{ cargandoDetalles ? 'Cargando detalles...' : 'Calculando emparejamientos...' }}</p>
    </div>
    <div v-else-if="!tieneResultados && !hayError" class="mensaje-info">
      <p>Configure los parámetros y haga clic en "Calcular Emparejamientos" para ver los resultados.</p>
    </div>
    <div v-else-if="hayError" class="mensaje-error">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="tieneResultados && resultadosFiltrados.length === 0" class="mensaje-info">
      <p>No se encontraron emparejamientos que cumplan con los filtros actuales.</p>
    </div>
    <div v-else class="tabla-container">
      <table id="tabla-emparejamientos">
        <thead>
          <tr>
            <th>Afiliado 1</th>
            <th>Afiliado 2</th>
            <th>Días desde última</th>
            <th>Diversidad mínima</th>
            <th>Operaciones mínimas</th>
            <th>Monto sugerido</th>
            <th>Riesgo</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="resultado in resultadosFiltrados" :key="resultado.pareja.join('-')">
            <td>{{ resultado.afiliado1 }}</td>
            <td>{{ resultado.afiliado2 }}</td>
            <td>{{ resultado.dias_desde_ultima }}</td>
            <td>{{ resultado.diversidad_minima }}</td>
            <td>{{ resultado.operaciones_intermedias_minimas }}</td>
            <td>{{ formatMonto(resultado.monto_asignado) }}</td>
            <td>{{ resultado.riesgo }}</td>
            <td>
              <button 
                class="btn-ver-detalles" 
                @click="verDetalles(resultado.pareja)"
              >
                Ver Detalles
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal de detalles -->
    <Teleport to="body">
      <div v-if="modalVisible" class="modal-detalles" @click.self="cerrarModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Detalles de Operaciones</h3>
            <button class="modal-close" @click="cerrarModal">&times;</button>
          </div>
          <div class="modal-body">
            <!-- Sección de montos sugeridos -->
            <div class="seccion-montos-sugeridos">
              <h4>Montos Sugeridos Adicionales</h4>
              <div v-if="detallesPareja && detallesPareja.montos_sugeridos && detallesPareja.montos_sugeridos.length > 0" class="montos-sugeridos-container">
                <div 
                  v-for="(monto, index) in detallesPareja.montos_sugeridos" 
                  :key="index"
                  class="monto-sugerido"
                >
                  <span class="monto-valor">{{ formatMonto(monto) }}</span>
                </div>
              </div>
              <div v-else class="no-montos">
                No hay montos sugeridos adicionales disponibles
              </div>
            </div>

            <!-- Sección de historial -->
            <div class="seccion-historial">
              <h4>Últimas Operaciones</h4>
              <table v-if="detallesPareja && detallesPareja.data && detallesPareja.data.length > 0" class="tabla-detalles">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Hora</th>
                    <th>Monto</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(op, index) in detallesPareja.data" :key="index">
                    <td>{{ formatFecha(op.fecha) }}</td>
                    <td>{{ op.hora }}</td>
                    <td>{{ formatMonto(op.monto) }}</td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="no-data">No hay operaciones previas</p>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import dayjs from 'dayjs';

export default {
  name: 'EmparejadorCalculador',
  data() {
    return {
      configuracionLocal: {
        diasMinimos: 1,
        riesgoMaximo: 50
      },
      filtroAfiliado1: '',
      filtroAfiliado2: '',
      modalVisible: false
    };
  },
  computed: {
    ...mapState('emparejador', [
      'configuracion',
      'resultadosEmparejamiento',
      'resultadosFiltrados',
      'detallesPareja',
      'cargandoEmparejamientos',
      'cargandoDetalles',
      'error'
    ]),
    ...mapGetters('emparejador', [
      'tieneResultados',
      'hayError'
    ]),
    cargando() {
      return this.cargandoEmparejamientos || this.cargandoDetalles;
    }
  },
  created() {
    // Inicializar configuración desde el store
    this.configuracionLocal = { ...this.configuracion };
  },
  methods: {
    ...mapActions('emparejador', [
      'calcularEmparejamientos',
      'obtenerDetallesPareja',
      'actualizarConfiguracion'
    ]),
    ...mapActions('ui', [
      'mostrarMensaje',
      'mostrarExito',
      'mostrarError'
    ]),
    
    async calcularEmparejamientos() {
      try {
        // Actualizar configuración en el store
        this.actualizarConfiguracion(this.configuracionLocal);
        
        // Calcular emparejamientos
        const resultado = await this.calcularEmparejamientos();
        
        if (resultado.success) {
          this.mostrarExito('Emparejamientos calculados exitosamente');
        } else {
          this.mostrarError(resultado.message || 'Error al calcular emparejamientos');
        }
      } catch (error) {
        this.mostrarError('Error al calcular emparejamientos');
      }
    },
    
    filtrarResultados() {
      // El filtrado real se hace en el store
      this.$store.commit('emparejador/SET_FILTRO_AFILIADO1', this.filtroAfiliado1);
      this.$store.commit('emparejador/SET_FILTRO_AFILIADO2', this.filtroAfiliado2);
      this.$store.dispatch('emparejador/filtrarResultados');
    },
    
    limpiarFiltros() {
      this.filtroAfiliado1 = '';
      this.filtroAfiliado2 = '';
      this.filtrarResultados();
    },
    
    async verDetalles(pareja) {
      try {
        const resultado = await this.obtenerDetallesPareja({ 
          afiliado1: pareja[0], 
          afiliado2: pareja[1] 
        });
        
        if (resultado.success) {
          this.modalVisible = true;
        } else {
          this.mostrarError(resultado.message || 'Error al obtener detalles');
        }
      } catch (error) {
        this.mostrarError('Error al obtener detalles');
      }
    },
    
    cerrarModal() {
      this.modalVisible = false;
    },
    
    formatMonto(monto) {
      if (!monto) return 'N/A';
      
      return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
      }).format(monto);
    },
    
    formatFecha(fecha) {
      return dayjs(fecha).format('DD/MM/YYYY');
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

.tabs-container {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-borde);
  padding-bottom: var(--spacing-sm);
}

.tab-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background: none;
  cursor: pointer;
  color: var(--color-texto);
  font-weight: 500;
  position: relative;
  text-decoration: none;
}

.tab-btn.active {
  color: var(--color-primario);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--color-primario);
}

.panel-control {
  margin-bottom: var(--spacing-lg);
}

.filtros-emparejamiento {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--color-blanco);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--box-shadow);
}

.buscador-emparejador {
  padding: var(--spacing-lg);
  background-color: var(--color-blanco);
  border-radius: var(--border-radius-md);
  box-shadow: var(--box-shadow);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.campo {
  margin-bottom: var(--spacing-sm);
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

.cargando-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  gap: var(--spacing-md);
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid var(--color-primario);
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.mensaje-info,
.mensaje-error {
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
  text-align: center;
}

.mensaje-info {
  background-color: var(--color-blanco);
  color: var(--color-texto);
  box-shadow: var(--box-shadow);
}

.mensaje-error {
  background-color: #ffebee;
  color: var(--color-error);
  border: 1px solid #ffcdd2;
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

.btn-ver-detalles {
  background-color: var(--color-info);
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-ver-detalles:hover {
  opacity: 0.9;
}

.modal-detalles {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: var(--spacing-sm);
}

.modal-content {
  background-color: var(--color-blanco);
  border-radius: var(--border-radius-lg);
  width: 95%;
  min-width: 500px;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: var(--spacing-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-borde);
  position: sticky;
  top: 0;
  background-color: var(--color-blanco);
  z-index: 1;
}

.modal-body {
  padding: var(--spacing-md);
  max-height: 70vh;
  overflow-y: auto;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-texto);
}

.seccion-montos-sugeridos,
.seccion-historial {
  margin-bottom: var(--spacing-lg);
}

.seccion-montos-sugeridos {
  padding: var(--spacing-md);
  background-color: var(--color-fondo);
  border-radius: var(--border-radius-md);
}

.seccion-montos-sugeridos h4,
.seccion-historial h4 {
  margin-bottom: var(--spacing-md);
  color: var(--color-primario);
}

.montos-sugeridos-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.monto-sugerido {
  padding: var(--spacing-md);
  background-color: var(--color-blanco);
  border: 2px solid var(--color-primario);
  border-radius: var(--border-radius-sm);
  font-weight: 600;
  color: var(--color-primario);
  flex: 1;
  min-width: 150px;
  text-align: center;
}

.monto-valor {
  font-size: 1.1em;
}

.tabla-detalles {
  width: 100%;
  margin-top: var(--spacing-md);
}

.no-montos,
.no-data {
  padding: var(--spacing-md);
  text-align: center;
  color: var(--color-texto-claro);
  background-color: var(--color-fondo);
  border-radius: var(--border-radius-sm);
}

@media (max-width: 768px) {
  .filtros-emparejamiento,
  .buscador-emparejador {
    grid-template-columns: 1fr;
  }

  .campo-botones {
    flex-direction: column;
    width: 100%;
  }

  .campo-botones button {
    width: 100%;
  }

  .modal-content {
    width: 100%;
    min-width: auto;
    height: auto;
    max-height: 85vh;
    margin: 0;
  }

  .montos-sugeridos-container {
    gap: var(--spacing-sm);
  }

  .monto-sugerido {
    flex: 1 1 calc(50% - var(--spacing-sm));
    min-width: 120px;
  }

  .tabla-detalles {
    font-size: 0.9rem;
  }
}
</style>