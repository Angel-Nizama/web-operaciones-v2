<template>
  <div class="emparejador-rangos">
    <div class="seccion-header">
      <h2>Emparejador de Operaciones</h2>
      <div class="tabs-container">
        <router-link to="/emparejador" class="tab-btn active">Gestión de Rangos</router-link>
        <router-link to="/emparejador/calcular" class="tab-btn">Emparejamiento Automático</router-link>
      </div>
      <p class="seccion-descripcion">Gestione los afiliados por rangos de montos.</p>
    </div>

    <!-- Panel de resumen -->
    <div class="resumen-panel">
      <div class="resumen-item">
        <span class="resumen-label">Total Afiliados Inscritos:</span>
        <span class="resumen-valor">{{ totalAfiliadosInscritos }}</span>
      </div>
      <div class="acciones-resumen">
        <button 
          class="btn btn-peligro" 
          @click="confirmarBorrarTodos" 
          :disabled="!hayAfiliados"
        >
          Borrar Todos los Afiliados
        </button>
      </div>
    </div>

    <div v-if="cargando" class="cargando-container">
      <div class="spinner"></div>
      <p>Cargando datos...</p>
    </div>

    <!-- Rangos -->
    <div v-else class="rangos-container">
      <!-- Iterar sobre cada rango configurado -->
      <div 
        v-for="(rango, index) in rangosDisponibles" 
        :key="index"
        class="rango-seccion"
      >
        <div class="rango-header">
          <h3>Rango: {{ rango.inicio }} - {{ rango.fin }}</h3>
          <button 
            class="btn btn-peligro btn-borrar-rango" 
            @click="confirmarBorrarRango(rango.inicio, rango.fin)"
            :disabled="afiliadosEnRango(rango).length === 0"
          >
            Borrar Afiliados del Rango
          </button>
        </div>
        
        <div class="afiliados-lista">
          <template v-if="afiliadosEnRango(rango).length === 0">
            <p class="text-center">No hay afiliados en este rango</p>
          </template>
          <template v-else>
            <div 
              v-for="afiliado in afiliadosEnRango(rango)" 
              :key="afiliado.id"
              class="afiliado-item"
            >
              <div class="afiliado-info">
                <strong>{{ afiliado.nombre_completo }}</strong>
                <span>Recibe en: {{ afiliado.recibe_en }}</span>
                <span>Envía a: {{ afiliado.envia_a }}</span>
              </div>
              <button 
                class="btn btn-peligro btn-borrar-afiliado" 
                @click="confirmarBorrarAfiliado(afiliado.id, rango.inicio, rango.fin)"
              >
                Borrar
              </button>
            </div>
          </template>
        </div>
        
        <div class="agregar-afiliado-form">
          <div class="campo">
            <input 
              type="text" 
              class="buscar-afiliado" 
              v-model="inputBusqueda[rango.rangoKey]"
              placeholder="Buscar afiliado..." 
              @input="buscarAfiliado($event, rango.rangoKey)"
            >
            <div 
              v-if="sugerencias[rango.rangoKey] && sugerencias[rango.rangoKey].length > 0" 
              class="sugerencias-container"
            >
              <div 
                v-for="(item, idx) in sugerencias[rango.rangoKey]" 
                :key="idx"
                class="sugerencia-item"
                @click="seleccionarSugerencia(rango.rangoKey, item)"
              >
                <strong>{{ item.nombre_completo }}</strong>
                <small>({{ item.numero }})</small>
              </div>
            </div>
          </div>
          <div class="campo">
            <select 
              class="select-recibe" 
              v-model="seleccionRecibe[rango.rangoKey]"
            >
              <option value="">Recibe en...</option>
              <option value="Izipay" selected>Izipay</option>
              <option value="Iziya">Iziya</option>
              <option value="Ambos">Ambos</option>
            </select>
          </div>
          <div class="campo">
            <select 
              class="select-envia" 
              v-model="seleccionEnvia[rango.rangoKey]"
            >
              <option value="">Envía a...</option>
              <option value="Izipay" selected>Izipay</option>
              <option value="Iziya">Iziya</option>
              <option value="Ambos">Ambos</option>
            </select>
          </div>
          <button 
            class="btn btn-primario btn-agregar" 
            @click="agregarAfiliado(rango)"
            :disabled="!puedeAgregar(rango.rangoKey)"
          >
            Agregar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import afiliadosService from '@/services/afiliadosService';

export default {
  name: 'EmparejadorRangos',
  data() {
    return {
      rangosDisponibles: [
        { inicio: 0, fin: 500, rangoKey: '0-500' },
        { inicio: 500, fin: 700, rangoKey: '500-700' },
        { inicio: 700, fin: 1000, rangoKey: '700-1000' }
      ],
      sugerencias: {},
      inputBusqueda: {},
      seleccionRecibe: {},
      seleccionEnvia: {},
      timeouts: {},
      valorSeleccionado: {}
    };
  },
  computed: {
    ...mapState('emparejador', [
      'afiliadosPorRangos',
      'totalAfiliadosInscritos',
      'cargandoRango',
      'error'
    ]),
    hayAfiliados() {
      return this.totalAfiliadosInscritos > 0;
    },
    cargando() {
      return this.cargandoRango;
    }
  },
  created() {
    // Inicializar datos para cada rango
    this.rangosDisponibles.forEach(rango => {
      this.sugerencias[rango.rangoKey] = [];
      this.inputBusqueda[rango.rangoKey] = '';
      this.seleccionRecibe[rango.rangoKey] = 'Izipay';
      this.seleccionEnvia[rango.rangoKey] = 'Izipay';
      this.valorSeleccionado[rango.rangoKey] = null;
    });
    
    // Cargar datos de todos los rangos
    this.cargarTodosLosRangos();
    
    // Eliminar eventos de click global al desmontar
    document.addEventListener('click', this.cerrarSugerencias);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.cerrarSugerencias);
  },
  methods: {
    ...mapActions('emparejador', [
      'cargarAfiliadosRango',
      'cargarTodosLosRangos',
      'agregarAfiliadoRango',
      'eliminarAfiliadoRango',
      'eliminarAfiliadosRango',
      'eliminarTodosAfiliados'
    ]),
    ...mapActions('ui', [
      'mostrarMensaje',
      'mostrarExito',
      'mostrarError',
      'pedirConfirmacion'
    ]),
    
    afiliadosEnRango(rango) {
      return this.afiliadosPorRangos[rango.rangoKey] || [];
    },
    
    async buscarAfiliado(event, rangoKey) {
      const texto = event.target.value.trim();
      
      // Limpiar valor seleccionado previo
      this.valorSeleccionado[rangoKey] = null;
      
      // Si hay menos de 2 caracteres, no buscar
      if (texto.length < 2) {
        this.sugerencias[rangoKey] = [];
        return;
      }
      
      // Cancelar timeout anterior si existe
      if (this.timeouts[rangoKey]) {
        clearTimeout(this.timeouts[rangoKey]);
      }
      
      // Esperar 300ms antes de buscar (debounce)
      this.timeouts[rangoKey] = setTimeout(async () => {
        try {
          const resultados = await afiliadosService.buscarAfiliado(texto);
          this.sugerencias[rangoKey] = resultados;
        } catch (error) {
          console.error('Error al buscar afiliados:', error);
        }
      }, 300);
    },
    
    seleccionarSugerencia(rangoKey, item) {
      this.inputBusqueda[rangoKey] = item.nombre_completo;
      this.valorSeleccionado[rangoKey] = item.numero;
      this.sugerencias[rangoKey] = [];
    },
    
    cerrarSugerencias(event) {
      // Cerrar todas las sugerencias si se hace clic fuera
      if (!event.target.closest('.campo')) {
        this.rangosDisponibles.forEach(rango => {
          this.sugerencias[rango.rangoKey] = [];
        });
      }
    },
    
    puedeAgregar(rangoKey) {
      return (
        this.valorSeleccionado[rangoKey] && 
        this.seleccionRecibe[rangoKey] && 
        this.seleccionEnvia[rangoKey]
      );
    },
    
    async agregarAfiliado(rango) {
      const rangoKey = rango.rangoKey;
      
      if (!this.puedeAgregar(rangoKey)) {
        this.mostrarError('Debe seleccionar un afiliado y las opciones de recibe y envía');
        return;
      }
      
      try {
        const datos = {
          numero: this.valorSeleccionado[rangoKey],
          rango_inicio: rango.inicio,
          rango_fin: rango.fin,
          recibe_en: this.seleccionRecibe[rangoKey],
          envia_a: this.seleccionEnvia[rangoKey]
        };
        
        const resultado = await this.agregarAfiliadoRango(datos);
        
        if (resultado.success) {
          this.mostrarExito(resultado.message);
          
          // Limpiar formulario manteniendo Izipay seleccionado
          this.inputBusqueda[rangoKey] = '';
          this.valorSeleccionado[rangoKey] = null;
          this.seleccionRecibe[rangoKey] = 'Izipay';
          this.seleccionEnvia[rangoKey] = 'Izipay';
        } else {
          this.mostrarError(resultado.message);
        }
      } catch (error) {
        this.mostrarError('Error al agregar afiliado');
      }
    },
    
    async confirmarBorrarAfiliado(id, inicio, fin) {
      const confirmar = await this.pedirConfirmacion('¿Está seguro de eliminar este afiliado del rango?');
      if (confirmar) {
        try {
          const resultado = await this.eliminarAfiliadoRango({ id, inicio, fin });
          
          if (resultado.success) {
            this.mostrarExito(resultado.message);
          } else {
            this.mostrarError(resultado.message);
          }
        } catch (error) {
          this.mostrarError('Error al eliminar afiliado');
        }
      }
    },
    
    async confirmarBorrarRango(inicio, fin) {
      const confirmar = await this.pedirConfirmacion(`¿Está seguro de eliminar todos los afiliados del rango ${inicio}-${fin}?`);
      if (confirmar) {
        try {
          const resultado = await this.eliminarAfiliadosRango({ inicio, fin });
          
          if (resultado.success) {
            this.mostrarExito(resultado.message);
          } else {
            this.mostrarError(resultado.message);
          }
        } catch (error) {
          this.mostrarError('Error al eliminar afiliados del rango');
        }
      }
    },
    
    async confirmarBorrarTodos() {
      const confirmar = await this.pedirConfirmacion('¿Está seguro de eliminar todos los afiliados de todos los rangos?');
      if (confirmar) {
        try {
          const resultado = await this.eliminarTodosAfiliados();
          
          if (resultado.success) {
            this.mostrarExito(resultado.message);
          } else {
            this.mostrarError(resultado.message);
          }
        } catch (error) {
          this.mostrarError('Error al eliminar todos los afiliados');
        }
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

.seccion-descripcion {
  color: var(--color-texto-claro);
  margin-top: var(--spacing-sm);
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

.resumen-panel {
  background-color: var(--color-blanco);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--box-shadow);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.resumen-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.resumen-label {
  font-weight: 500;
  color: var(--color-texto-claro);
}

.resumen-valor {
  font-weight: 600;
  color: var(--color-texto);
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

.rangos-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.rango-seccion {
  background-color: var(--color-blanco);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  box-shadow: var(--box-shadow);
}

.rango-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.rango-header h3 {
  margin: 0;
  color: var(--color-primario);
}

.afiliados-lista {
  margin-bottom: var(--spacing-md);
  min-height: 50px;
}

.afiliado-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-borde);
  border-radius: var(--border-radius-sm);
  margin-bottom: var(--spacing-sm);
}

.afiliado-info {
  display: flex;
  gap: var(--spacing-md);
}

.afiliado-info span {
  color: var(--color-texto-claro);
}

.agregar-afiliado-form {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: var(--spacing-md);
  align-items: end;
  background-color: var(--color-fondo);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-sm);
}

.campo {
  margin-bottom: 0;
  position: relative;
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

@media (max-width: 768px) {
  .agregar-afiliado-form {
    grid-template-columns: 1fr;
  }
  
  .rango-header {
    flex-direction: column;
    gap: var(--spacing-sm);
    text-align: center;
  }
  
  .resumen-panel {
    flex-direction: column;
    gap: var(--spacing-md);
  }
}
</style>