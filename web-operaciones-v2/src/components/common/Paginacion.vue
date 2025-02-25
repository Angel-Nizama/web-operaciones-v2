<template>
  <div class="paginacion-container">
    <div class="paginacion">
      <!-- Botón Anterior -->
      <button 
        v-if="paginaActual > 1" 
        class="btn-pagina" 
        @click="cambiarPagina(paginaActual - 1)"
      >
        &larr;
      </button>
      
      <!-- Primera página -->
      <button 
        v-if="paginaActual > 3" 
        class="btn-pagina" 
        @click="cambiarPagina(1)"
      >
        1
      </button>
      
      <!-- Elipsis izquierda -->
      <span 
        v-if="paginaActual > 4" 
        class="elipsis"
      >
        &hellip;
      </span>
      
      <!-- Páginas cercanas a la actual -->
      <button 
        v-for="pagina in paginasCercanas" 
        :key="pagina"
        :class="['btn-pagina', { active: pagina === paginaActual }]"
        @click="cambiarPagina(pagina)"
      >
        {{ pagina }}
      </button>
      
      <!-- Elipsis derecha -->
      <span 
        v-if="paginaActual < totalPaginas - 3" 
        class="elipsis"
      >
        &hellip;
      </span>
      
      <!-- Última página -->
      <button 
        v-if="paginaActual < totalPaginas - 2" 
        class="btn-pagina" 
        @click="cambiarPagina(totalPaginas)"
      >
        {{ totalPaginas }}
      </button>
      
      <!-- Botón Siguiente -->
      <button 
        v-if="paginaActual < totalPaginas" 
        class="btn-pagina" 
        @click="cambiarPagina(paginaActual + 1)"
      >
        &rarr;
      </button>
    </div>
    
    <div class="info-paginacion">
      <span>Página {{ paginaActual }} de {{ totalPaginas }}</span>
    </div>
    
    <div v-if="mostrarSelector" class="selector-por-pagina">
      <label for="items-por-pagina">Items por página:</label>
      <select 
        id="items-por-pagina" 
        v-model="itemsPorPaginaLocal"
        @change="cambiarItemsPorPagina"
      >
        <option 
          v-for="opcion in opcionesItemsPorPagina" 
          :key="opcion" 
          :value="opcion"
        >
          {{ opcion }}
        </option>
      </select>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Paginacion',
  props: {
    paginaActual: {
      type: Number,
      required: true
    },
    totalPaginas: {
      type: Number,
      required: true
    },
    itemsPorPagina: {
      type: Number,
      default: 100
    },
    opcionesItemsPorPagina: {
      type: Array,
      default: () => [10, 25, 50, 100, 500]
    },
    mostrarSelector: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      itemsPorPaginaLocal: this.itemsPorPagina
    };
  },
  computed: {
    paginasCercanas() {
      const paginas = [];
      const inicio = Math.max(1, this.paginaActual - 2);
      const fin = Math.min(this.totalPaginas, this.paginaActual + 2);
      
      for (let i = inicio; i <= fin; i++) {
        paginas.push(i);
      }
      
      return paginas;
    }
  },
  watch: {
    itemsPorPagina(nuevoValor) {
      this.itemsPorPaginaLocal = nuevoValor;
    }
  },
  methods: {
    cambiarPagina(pagina) {
      if (pagina !== this.paginaActual) {
        this.$emit('cambiar-pagina', pagina);
      }
    },
    cambiarItemsPorPagina() {
      this.$emit('cambiar-items', this.itemsPorPaginaLocal);
    }
  }
};
</script>

<style scoped>
.paginacion-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 1.5rem 0;
  gap: 1rem;
}

.paginacion {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-pagina {
  padding: 0.5rem 0.75rem;
  border: 1px solid #0078d7;
  background-color: white;
  color: #0078d7;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 40px;
  text-align: center;
}

.btn-pagina:hover,
.btn-pagina.active {
  background-color: #0078d7;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.elipsis {
  padding: 0.5rem;
  color: #666;
}

.info-paginacion {
  font-size: 0.9rem;
  color: #666;
  text-align: center;
}

.selector-por-pagina {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.selector-por-pagina select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

@media (min-width: 768px) {
  .paginacion-container {
    flex-direction: row;
    justify-content: space-between;
  }
  
  .info-paginacion {
    order: 2;
  }
  
  .selector-por-pagina {
    order: 3;
  }
}

@media (max-width: 767px) {
  .selector-por-pagina {
    width: 100%;
    justify-content: center;
  }
}
</style>