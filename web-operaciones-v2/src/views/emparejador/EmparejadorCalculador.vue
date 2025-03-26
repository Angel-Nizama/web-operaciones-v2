<template>
  <div class="emparejador-calculador">
    <div class="seccion-header">
      <h2>Emparejador de Operaciones</h2>
      <div class="tabs-container">
        <router-link to="/emparejador" class="tab-btn">Gestión de Rangos</router-link>
        <router-link to="/emparejador/calcular" class="tab-btn active">Emparejamiento Automático</router-link>
      </div>
    </div>

    <!-- Panel de control de emparejamiento mejorado -->
    <div class="panel-control">
      <div class="configuration-toggle" @click="showAdvancedConfig = !showAdvancedConfig">
        <span>{{ showAdvancedConfig ? 'Ocultar configuración avanzada' : 'Mostrar configuración avanzada' }}</span>
        <i class="toggle-icon">{{ showAdvancedConfig ? '▲' : '▼' }}</i>
      </div>
      
      <div class="filtros-emparejamiento" :class="{'advanced-visible': showAdvancedConfig}">
        <!-- Configuración básica -->
        <div class="basic-config">
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
          <div class="campo">
            <label for="monto-minimo">Monto mínimo (opcional):</label>
            <input 
              type="number" 
              id="monto-minimo"
              v-model.number="configuracion.montoMinimo" 
              min="0" 
              class="form-input"
            >
          </div>
          <div class="campo">
            <label for="monto-maximo">Monto máximo (opcional):</label>
            <input 
              type="number" 
              id="monto-maximo"
              v-model.number="configuracion.montoMaximo"
              min="0" 
              class="form-input"
            >
          </div>
        </div>
        
        <!-- Configuración avanzada (ponderaciones) -->
        <div v-if="showAdvancedConfig" class="advanced-config">
          <h4>Ponderaciones para cálculo de riesgo</h4>
          <div class="ponderaciones-grid">
            <div class="campo">
              <label for="pond-dias">Días desde última operación:</label>
              <input 
                type="range" 
                id="pond-dias" 
                v-model.number="configuracion.ponderacionDias" 
                min="0" 
                max="1" 
                step="0.05"
                class="range-input"
              >
              <span class="range-value">{{ (configuracion.ponderacionDias * 100).toFixed(0) }}%</span>
            </div>
            <div class="campo">
              <label for="pond-diversidad">Diversidad de contrapartes:</label>
              <input 
                type="range" 
                id="pond-diversidad" 
                v-model.number="configuracion.ponderacionDiversidad" 
                min="0" 
                max="1" 
                step="0.05"
                class="range-input"
              >
              <span class="range-value">{{ (configuracion.ponderacionDiversidad * 100).toFixed(0) }}%</span>
            </div>
            <div class="campo">
              <label for="pond-operaciones">Operaciones intermedias:</label>
              <input 
                type="range" 
                id="pond-operaciones" 
                v-model.number="configuracion.ponderacionOperaciones" 
                min="0" 
                max="1" 
                step="0.05"
                class="range-input"
              >
              <span class="range-value">{{ (configuracion.ponderacionOperaciones * 100).toFixed(0) }}%</span>
            </div>
            <div class="campo">
              <label for="pond-patron">Patrones de comportamiento:</label>
              <input 
                type="range" 
                id="pond-patron" 
                v-model.number="configuracion.ponderacionPatron" 
                min="0" 
                max="1" 
                step="0.05"
                class="range-input"
              >
              <span class="range-value">{{ (configuracion.ponderacionPatron * 100).toFixed(0) }}%</span>
            </div>
          </div>
          
          <div class="validation-message" v-if="!isPonderacionValid">
            La suma de las ponderaciones debe ser 100%. Actual: {{ totalPonderacion.toFixed(0) }}%
          </div>
          
          <div class="config-actions">
            <button 
              class="btn btn-secundario" 
              @click="restablecerConfiguracion"
            >
              Restablecer por defecto
            </button>
            
            <button 
              class="btn btn-secundario" 
              @click="normalizarPonderaciones"
              :disabled="isPonderacionValid"
            >
              Normalizar ponderaciones
            </button>
          </div>
        </div>
        
        <button 
          id="calcular-emparejamientos" 
          class="btn btn-primario"
          @click="iniciarCalculoEmparejamientos"
          :disabled="cargando || !isPonderacionValid"
        >
          <span v-if="!cargando">Calcular Emparejamientos</span>
          <span v-else>Calculando...</span>
        </button>
      </div>
      
      <!-- Nuevo contenedor de resultados con estadísticas -->
      <div v-if="tieneResultados" class="resultados-stats">
        <div class="stats-card">
          <span class="stats-value">{{ resultadosFiltrados.length }}</span>
          <span class="stats-label">Emparejamientos encontrados</span>
        </div>
        <div class="stats-card">
          <span class="stats-value">{{ promedioRiesgo.toFixed(1) }}</span>
          <span class="stats-label">Riesgo promedio</span>
        </div>
        <div class="stats-card">
          <span class="stats-value">{{ formatMonto(promedioMonto) }}</span>
          <span class="stats-label">Monto promedio</span>
        </div>
        <div class="stats-card action-card">
          <button 
            class="btn btn-secundario"
            @click="exportarResultados"
            :disabled="!tieneResultados"
          >
            Exportar resultados
          </button>
        </div>
      </div>
      
      <!-- Buscador mejorado con más filtros -->
      <div v-if="tieneResultados" class="buscador-emparejador">
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
        <div class="campo">
          <label for="filtro-riesgo">Riesgo máximo:</label>
          <input 
            type="range" 
            id="filtro-riesgo" 
            v-model.number="filtroRiesgoMax" 
            min="0" 
            max="100"
            @input="filtrarResultados"
            class="range-input"
          >
          <span class="range-value">{{ filtroRiesgoMax }}%</span>
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

    <!-- Tabla de resultados con paginación -->
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
    <div v-else-if="tieneResultados && resultadosPaginados.length === 0" class="mensaje-info">
      <p>No se encontraron emparejamientos que cumplan con los filtros actuales.</p>
    </div>
    <div v-else class="tabla-container">
      <table id="tabla-emparejamientos">
        <thead>
          <tr>
            <th @click="ordenarPor('afiliado1')" class="sortable-header">
              Afiliado 1
              <span v-if="ordenActual.campo === 'afiliado1'" class="sort-icon">
                {{ ordenActual.direccion === 'asc' ? '↓' : '↑' }}
              </span>
            </th>
            <th @click="ordenarPor('afiliado2')" class="sortable-header">
              Afiliado 2
              <span v-if="ordenActual.campo === 'afiliado2'" class="sort-icon">
                {{ ordenActual.direccion === 'asc' ? '↓' : '↑' }}
              </span>
            </th>
            <th @click="ordenarPor('dias_desde_ultima')" class="sortable-header">
              Días desde última
              <span v-if="ordenActual.campo === 'dias_desde_ultima'" class="sort-icon">
                {{ ordenActual.direccion === 'asc' ? '↓' : '↑' }}
              </span>
            </th>
            <th>Diversidad mínima</th>
            <th>Operaciones mínimas</th>
            <th @click="ordenarPor('monto_asignado')" class="sortable-header">
              Monto sugerido
              <span v-if="ordenActual.campo === 'monto_asignado'" class="sort-icon">
                {{ ordenActual.direccion === 'asc' ? '↓' : '↑' }}
              </span>
            </th>
            <th @click="ordenarPor('riesgo')" class="sortable-header">
              Riesgo
              <span v-if="ordenActual.campo === 'riesgo'" class="sort-icon">
                {{ ordenActual.direccion === 'asc' ? '↓' : '↑' }}
              </span>
            </th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="resultado in resultadosPaginados" :key="resultado.pareja.join('-')">
            <td>{{ resultado.afiliado1 }}</td>
            <td>{{ resultado.afiliado2 }}</td>
            <td>{{ resultado.dias_desde_ultima }}</td>
            <td>{{ resultado.diversidad_minima }}</td>
            <td>{{ resultado.operaciones_intermedias_minimas }}</td>
            <td>{{ formatMonto(resultado.monto_asignado) }}</td>
            <td>
              <div class="riesgo-badge" :style="getRiesgoStyle(resultado.riesgo)">
                {{ resultado.riesgo }}
              </div>
            </td>
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
      
      <!-- Paginación para resultados -->
      <div class="paginacion-container">
        <div class="pagination-controls">
          <button 
            class="btn-pagina" 
            @click="irAPagina(paginaActual - 1)" 
            :disabled="paginaActual <= 1"
          >
            &larr;
          </button>
          
          <span v-if="paginaActual > 2" class="btn-pagina" @click="irAPagina(1)">1</span>
          <span v-if="paginaActual > 3" class="elipsis">...</span>
          
          <span 
            v-for="pagina in paginasVisibles" 
            :key="pagina"
            :class="['btn-pagina', { active: pagina === paginaActual }]"
            @click="irAPagina(pagina)"
          >
            {{ pagina }}
          </span>
          
          <span v-if="paginaActual < totalPaginas - 2" class="elipsis">...</span>
          <span 
            v-if="paginaActual < totalPaginas - 1" 
            class="btn-pagina" 
            @click="irAPagina(totalPaginas)"
          >
            {{ totalPaginas }}
          </span>
          
          <button 
            class="btn-pagina" 
            @click="irAPagina(paginaActual + 1)" 
            :disabled="paginaActual >= totalPaginas"
          >
            &rarr;
          </button>
        </div>
        
        <div class="pagination-info">
          Mostrando {{ (paginaActual - 1) * itemsPorPagina + 1 }} - 
          {{ Math.min(paginaActual * itemsPorPagina, resultadosFiltrados.length) }} 
          de {{ resultadosFiltrados.length }}
        </div>
        
        <div class="items-per-page">
          <label for="items-por-pagina">Items por página:</label>
          <select 
            id="items-por-pagina" 
            v-model="itemsPorPagina" 
            @change="cambiarItemsPorPagina"
          >
            <option :value="10">10</option>
            <option :value="25">25</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Modal de detalles mejorado -->
    <Teleport to="body">
      <div v-if="modalVisible" class="modal-detalles" @click.self="cerrarModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Detalles de Operaciones</h3>
            <button class="modal-close" @click="cerrarModal">&times;</button>
          </div>
          <div class="modal-body">
            <!-- Tarjetas de resumen -->
            <div class="detalles-resumen">
              <div class="detalle-card" v-if="detallesPareja">
                <div class="detalle-card-title">Usa Izipay</div>
                <div class="detalle-card-value">
                  <span :class="['badge', detallesPareja.usa_izipay ? 'badge-success' : 'badge-neutral']">
                    {{ detallesPareja.usa_izipay ? 'Sí' : 'No' }}
                  </span>
                </div>
              </div>
              <div class="detalle-card">
                <div class="detalle-card-title">Operaciones previas</div>
                <div class="detalle-card-value">
                  {{ detallesPareja && detallesPareja.data ? detallesPareja.data.length : 0 }}
                </div>
              </div>
              <div class="detalle-card">
                <div class="detalle-card-title">Último monto</div>
                <div class="detalle-card-value">
                  {{ detallesPareja && detallesPareja.data && detallesPareja.data.length > 0 
                     ? formatMonto(detallesPareja.data[0].monto) 
                     : 'N/A' }}
                </div>
              </div>
              <div class="detalle-card">
                <div class="detalle-card-title">Última operación</div>
                <div class="detalle-card-value">
                  {{ detallesPareja && detallesPareja.data && detallesPareja.data.length > 0 
                     ? formatFecha(detallesPareja.data[0].fecha) 
                     : 'N/A' }}
                </div>
              </div>
            </div>
            
            <!-- Sección de montos sugeridos mejorada -->
            <div class="seccion-montos-sugeridos">
              <h4>Montos Sugeridos</h4>
              <div v-if="detallesPareja && detallesPareja.montos_sugeridos && detallesPareja.montos_sugeridos.length > 0" class="montos-sugeridos-container">
                <div 
                  v-for="(monto, index) in detallesPareja.montos_sugeridos" 
                  :key="index"
                  class="monto-sugerido"
                  :class="{'monto-destacado': index === 0}"
                >
                  <span class="monto-valor">{{ formatMonto(monto) }}</span>
                  <div v-if="index === 0" class="monto-recomendado-badge">Recomendado</div>
                </div>
              </div>
              <div v-else class="no-montos">
                No hay montos sugeridos adicionales disponibles
              </div>
            </div>

            <!-- Sección de historial con visualización -->
            <div class="seccion-historial">
              <h4>Historial de Operaciones</h4>
              
              <!-- Nueva visualización gráfica -->
              <div v-if="detallesPareja && detallesPareja.data && detallesPareja.data.length > 0" class="grafico-historial">
                <div class="chart-container">
                  <div 
                    v-for="(op, index) in detallesPareja.data.slice(0, 5)" 
                    :key="index"
                    class="chart-bar"
                    :style="{
                      height: `${Math.min(100, (op.monto / maxMonto) * 100)}%`,
                      backgroundColor: getBarColor(index)
                    }"
                    :title="`${formatFecha(op.fecha)}: ${formatMonto(op.monto)}`"
                  ></div>
                </div>
                <div class="chart-labels">
                  <span 
                    v-for="(op, index) in detallesPareja.data.slice(0, 5)" 
                    :key="index"
                    class="chart-label"
                  >
                    {{ formatFechaCorta(op.fecha) }}
                  </span>
                </div>
              </div>
              
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
        riesgoMaximo: 50,
        montoMinimo: 0,
        montoMaximo: 0,
        ponderacionDias: 0.4,
        ponderacionDiversidad: 0.25,
        ponderacionOperaciones: 0.25,
        ponderacionPatron: 0.1
      },
      filtroAfiliado1: '',
      filtroAfiliado2: '',
      filtroRiesgoMax: 100,
      paginaActual: 1,
      itemsPorPagina: 10,
      modalVisible: false,
      showAdvancedConfig: false,
      ordenActual: {
        campo: 'riesgo',
        direccion: 'asc'
      }
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
    },
    totalPonderacion() {
      return (
        this.configuracionLocal.ponderacionDias + 
        this.configuracionLocal.ponderacionDiversidad + 
        this.configuracionLocal.ponderacionOperaciones + 
        this.configuracionLocal.ponderacionPatron
      ) * 100;
    },
    isPonderacionValid() {
      return Math.abs(this.totalPonderacion - 100) < 0.01;
    },
    promedioRiesgo() {
      if (!this.resultadosFiltrados.length) return 0;
      
      const total = this.resultadosFiltrados.reduce((sum, item) => sum + item.riesgo, 0);
      return total / this.resultadosFiltrados.length;
    },
    promedioMonto() {
      if (!this.resultadosFiltrados.length) return 0;
      
      const total = this.resultadosFiltrados.reduce((sum, item) => sum + item.monto_asignado, 0);
      return total / this.resultadosFiltrados.length;
    },
    totalPaginas() {
      return Math.ceil(this.resultadosFiltrados.length / this.itemsPorPagina);
    },
    resultadosPaginados() {
      const inicio = (this.paginaActual - 1) * this.itemsPorPagina;
      const fin = inicio + this.itemsPorPagina;
      return this.resultadosFiltrados.slice(inicio, fin);
    },
    paginasVisibles() {
      const paginas = [];
      const inicio = Math.max(1, this.paginaActual - 1);
      const fin = Math.min(this.totalPaginas, this.paginaActual + 1);
      
      for (let i = inicio; i <= fin; i++) {
        paginas.push(i);
      }
      
      return paginas;
    },
    maxMonto() {
      if (!this.detallesPareja || !this.detallesPareja.data || !this.detallesPareja.data.length) {
        return 0;
      }
      
      return Math.max(...this.detallesPareja.data.map(op => op.monto));
    }
  },
  created() {
    // Inicializar configuración desde el store
    this.configuracionLocal = { ...this.configuracion };
    if (!this.configuracionLocal.ponderacionDias) {
      this.configuracionLocal.ponderacionDias = 0.4;
      this.configuracionLocal.ponderacionDiversidad = 0.25;
      this.configuracionLocal.ponderacionOperaciones = 0.25;
      this.configuracionLocal.ponderacionPatron = 0.1;
    }
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
    
    // Método modificado para evitar recursión infinita
    async iniciarCalculoEmparejamientos() {
      try {
        // Validar configuración antes de proceder
        if (!this.isPonderacionValid) {
          this.mostrarError('La suma de ponderaciones debe ser 100%. Por favor, ajuste los valores.');
          return;
        }
        
        // Actualizar configuración en el store
        this.actualizarConfiguracion(this.configuracionLocal);
        
        // Mostrar mensaje de procesamiento
        this.mostrarMensaje({
          texto: "Calculando emparejamientos, esto puede tomar unos momentos...",
          tipo: "info",
          duracion: 0 // No auto-cerrar
        });
        
        // Calcular emparejamientos
        const resultado = await this.$store.dispatch('emparejador/calcularEmparejamientos');
        
        // Remover mensaje de procesamiento
        this.$store.commit('ui/REMOVE_ALL_MENSAJES');
        
        if (resultado && resultado.success) {
          // Mostrar mensaje de éxito con tiempo de ejecución si está disponible
          const tiempoEjecucion = resultado.executionTime 
            ? ` (completado en ${resultado.executionTime.toFixed(2)} segundos)` 
            : '';
          
          this.mostrarExito(`Emparejamientos calculados exitosamente${tiempoEjecucion}`);
          
          // Ordenar resultados iniciales
          this.ordenarPor('riesgo');
          
          // Volver a la primera página
          this.paginaActual = 1;
        } else {
          // Mostrar error
          this.mostrarError(resultado && resultado.message ? resultado.message : 'Error al calcular emparejamientos');
        }
      } catch (error) {
        // Remover mensaje de procesamiento
        this.$store.commit('ui/REMOVE_ALL_MENSAJES');
        
        // Mostrar error
        this.mostrarError('Error al calcular emparejamientos: ' + (error && error.message ? error.message : 'Error desconocido'));
        console.error('Error en iniciarCalculoEmparejamientos:', error);
      }
    },
    
    filtrarResultados() {
      // Configurar filtros en el store
      this.$store.commit('emparejador/SET_FILTRO_AFILIADO1', this.filtroAfiliado1);
      this.$store.commit('emparejador/SET_FILTRO_AFILIADO2', this.filtroAfiliado2);
      
      // Aplicar filtro de riesgo
      this.$store.dispatch('emparejador/filtrarResultados', {
        riesgoMaximo: this.filtroRiesgoMax,
        montoMinimo: this.configuracionLocal.montoMinimo,
        montoMaximo: this.configuracionLocal.montoMaximo
      });
      
      // Resetear a la primera página
      this.paginaActual = 1;
    },
    
    limpiarFiltros() {
      this.filtroAfiliado1 = '';
      this.filtroAfiliado2 = '';
      this.filtroRiesgoMax = 100;
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
    },
    
    formatFechaCorta(fecha) {
      return dayjs(fecha).format('DD/MM');
    },
    
    getRiesgoStyle(riesgo) {
      // Determinar el color según el nivel de riesgo
      let color;
      
      if (riesgo < 25) {
        color = '#28a745'; // Verde - riesgo bajo
      } else if (riesgo < 50) {
        color = '#ffc107'; // Amarillo - riesgo medio
      } else if (riesgo < 75) {
        color = '#fd7e14'; // Naranja - riesgo alto
      } else {
        color = '#dc3545'; // Rojo - riesgo muy alto
      }
      
      return {
        backgroundColor: color,
        color: riesgo < 50 ? '#000' : '#fff'
      };
    },
    
    getBarColor(index) {
      // Colores para las barras del gráfico
      const colors = [
        '#0078d7', // Azul primario
        '#1e88e5',
        '#3949ab',
        '#5e35b1',
        '#8e24aa'  // Morado
      ];
      
      return colors[Math.min(index, colors.length - 1)];
    },
    
    irAPagina(pagina) {
      if (pagina < 1 || pagina > this.totalPaginas) return;
      this.paginaActual = pagina;
    },
    
    cambiarItemsPorPagina() {
      this.paginaActual = 1;
    },
    
    ordenarPor(campo) {
      // Si ya está ordenado por este campo, cambiar dirección
      if (this.ordenActual.campo === campo) {
        this.ordenActual.direccion = this.ordenActual.direccion === 'asc' ? 'desc' : 'asc';
      } else {
        // Nuevo campo, ordenar ascendente por defecto
        this.ordenActual.campo = campo;
        this.ordenActual.direccion = 'asc';
      }
      
      // Ordenar resultados
      this.$store.dispatch('emparejador/ordenarResultados', {
        campo: this.ordenActual.campo,
        direccion: this.ordenActual.direccion
      });
      
      // Volver a la primera página
      this.paginaActual = 1;
    },
    
    restablecerConfiguracion() {
      this.configuracionLocal = {
        diasMinimos: 1,
        riesgoMaximo: 50,
        montoMinimo: 0,
        montoMaximo: 0,
        ponderacionDias: 0.4,
        ponderacionDiversidad: 0.25,
        ponderacionOperaciones: 0.25,
        ponderacionPatron: 0.1
      };
    },
    
    normalizarPonderaciones() {
      const total = this.configuracionLocal.ponderacionDias + 
                    this.configuracionLocal.ponderacionDiversidad + 
                    this.configuracionLocal.ponderacionOperaciones + 
                    this.configuracionLocal.ponderacionPatron;
      
      if (total > 0) {
        this.configuracionLocal.ponderacionDias = parseFloat((this.configuracionLocal.ponderacionDias / total).toFixed(2));
        this.configuracionLocal.ponderacionDiversidad = parseFloat((this.configuracionLocal.ponderacionDiversidad / total).toFixed(2));
        this.configuracionLocal.ponderacionOperaciones = parseFloat((this.configuracionLocal.ponderacionOperaciones / total).toFixed(2));
        this.configuracionLocal.ponderacionPatron = parseFloat((1 - this.configuracionLocal.ponderacionDias - 
          this.configuracionLocal.ponderacionDiversidad - this.configuracionLocal.ponderacionOperaciones).toFixed(2));
      }
    },
    
    exportarResultados() {
      try {
        if (!this.resultadosFiltrados.length) {
          this.mostrarError('No hay resultados para exportar');
          return;
        }
        
        // Crear CSV
        const headers = 'Afiliado 1,Afiliado 2,Días desde última,Diversidad mínima,Operaciones mínimas,Monto sugerido,Riesgo\n';
        const rows = this.resultadosFiltrados.map(r => {
          return `"${r.afiliado1}","${r.afiliado2}","${r.dias_desde_ultima}","${r.diversidad_minima}","${r.operaciones_intermedias_minimas}","${r.monto_asignado}","${r.riesgo}"`;
        }).join('\n');
        
        const csvContent = `data:text/csv;charset=utf-8,${headers}${rows}`;
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', `emparejamientos_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.mostrarExito('Resultados exportados correctamente');
      } catch (error) {
        this.mostrarError('Error al exportar resultados');
        console.error('Error en exportarResultados:', error);
      }
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

.configuration-toggle {
  background-color: var(--color-blanco);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-md) var(--border-radius-md) 0 0;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-borde);
}

.toggle-icon {
  font-style: normal;
  color: var(--color-primario);
}

.filtros-emparejamiento {
  padding: var(--spacing-md);
  background-color: var(--color-blanco);
  border-radius: 0 0 var(--border-radius-md) var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--box-shadow);
}

.filtros-emparejamiento.advanced-visible {
  border-radius: 0;
}

.basic-config {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.advanced-config {
  background-color: var(--color-fondo);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-sm);
  margin-bottom: var(--spacing-md);
}

.advanced-config h4 {
  margin-top: 0;
  margin-bottom: var(--spacing-md);
  color: var(--color-primario);
  font-size: 1rem;
}

.ponderaciones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.config-actions {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
  justify-content: flex-end;
}

.validation-message {
  color: var(--color-error);
  font-size: 0.9rem;
  margin-top: var(--spacing-sm);
}

.range-input {
  width: 100%;
  cursor: pointer;
}

.range-value {
  margin-left: var(--spacing-xs);
  font-size: 0.9rem;
  color: var(--color-texto-claro);
}

.resultados-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.stats-card {
  background-color: var(--color-blanco);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  box-shadow: var(--box-shadow);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.stats-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primario);
}

.stats-label {
  font-size: 0.9rem;
  color: var(--color-texto-claro);
  text-align: center;
}

.action-card {
  justify-content: center;
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

.sortable-header {
  cursor: pointer;
  user-select: none;
  position: relative;
}

.sort-icon {
  margin-left: var(--spacing-xs);
}

table tr:nth-child(even) {
  background-color: var(--color-fondo-alterno);
}

table tr:hover {
  background-color: var(--color-fondo-hover);
}

.riesgo-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  text-align: center;
  font-weight: 500;
  min-width: 40px;
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

.paginacion-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  border-top: 1px solid var(--color-borde);
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.btn-pagina {
  padding: 4px 8px;
  border: 1px solid var(--color-borde);
  background-color: white;
  cursor: pointer;
  border-radius: var(--border-radius-sm);
  min-width: 32px;
  text-align: center;
  font-size: 0.9rem;
}

.btn-pagina.active {
  background-color: var(--color-primario);
  color: white;
  border-color: var(--color-primario);
}

.btn-pagina:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.elipsis {
  padding: 0 4px;
}

.pagination-info {
  font-size: 0.9rem;
  color: var(--color-texto-claro);
}

.items-per-page {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 0.9rem;
}

.items-per-page select {
  padding: 4px 8px;
  border: 1px solid var(--color-borde);
  border-radius: var(--border-radius-sm);
  background-color: white;
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

.detalles-resumen {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.detalle-card {
  flex: 1;
  min-width: 100px;
  background-color: var(--color-fondo);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  text-align: center;
}

.detalle-card-title {
  font-size: 0.8rem;
  color: var(--color-texto-claro);
  margin-bottom: var(--spacing-xs);
}

.detalle-card-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-texto);
}

.badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
}

.badge-success {
  background-color: var(--color-exito);
  color: white;
}

.badge-neutral {
  background-color: var(--color-texto-claro);
  color: white;
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
  min-width: 120px;
  text-align: center;
  position: relative;
}

.monto-destacado {
  border-color: var(--color-exito);
  background-color: rgba(40, 167, 69, 0.1);
}

.monto-recomendado-badge {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--color-exito);
  color: white;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
}

.grafico-historial {
  margin: var(--spacing-md) 0;
  padding: var(--spacing-md);
  background-color: var(--color-fondo);
  border-radius: var(--border-radius-sm);
}

.chart-container {
  height: 150px;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  gap: var(--spacing-sm);
  padding-bottom: var(--spacing-sm);
}

.chart-bar {
  flex: 1;
  min-width: 20px;
  max-width: 60px;
  background-color: var(--color-primario);
  border-radius: var(--border-radius-sm) var(--border-radius-sm) 0 0;
  cursor: pointer;
  transition: opacity 0.2s;
}

.chart-bar:hover {
  opacity: 0.8;
}

.chart-labels {
  display: flex;
  justify-content: space-around;
  padding-top: var(--spacing-xs);
}

.chart-label {
  font-size: 0.8rem;
  color: var(--color-texto-claro);
  text-align: center;
  max-width: 60px;
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
  
  .paginacion-container {
    flex-direction: column;
    align-items: center;
  }
  
  .resultados-stats {
    grid-template-columns: 1fr 1fr;
  }
  
  .detalles-resumen {
    grid-template-columns: 1fr 1fr;
  }
}
</style>