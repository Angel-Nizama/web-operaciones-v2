<template>
  <transition name="fade">
    <div 
      v-if="visible" 
      :class="['mensaje', `mensaje-${tipo}`, { 'mensaje-cerrable': cerrable }]"
    >
      <div class="mensaje-contenido">{{ texto }}</div>
      <button 
        v-if="cerrable" 
        class="mensaje-cerrar" 
        @click="cerrar"
      >
        &times;
      </button>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'Mensaje',
  props: {
    texto: {
      type: String,
      required: true
    },
    tipo: {
      type: String,
      default: 'info',
      validator: (value) => ['info', 'success', 'error', 'warning'].includes(value)
    },
    duracion: {
      type: Number,
      default: 5000
    },
    cerrable: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      visible: true,
      timeoutId: null
    };
  },
  mounted() {
    if (this.duracion > 0) {
      this.timeoutId = setTimeout(() => {
        this.cerrar();
      }, this.duracion);
    }
  },
  beforeUnmount() {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
  },
  methods: {
    cerrar() {
      this.visible = false;
      this.$emit('cerrar');
    }
  }
};
</script>

<style scoped>
.mensaje {
  padding: 0.75rem 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.mensaje-contenido {
  flex: 1;
}

.mensaje-cerrar {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  margin-left: 0.5rem;
  padding: 0;
  line-height: 1;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.mensaje-cerrar:hover {
  opacity: 1;
}

.mensaje-info {
  background-color: #17a2b8;
  color: white;
}

.mensaje-success {
  background-color: #28a745;
  color: white;
}

.mensaje-error {
  background-color: #dc3545;
  color: white;
}

.mensaje-warning {
  background-color: #ffc107;
  color: #212529;
}

/* Transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>