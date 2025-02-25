<template>
  <Teleport to="body">
    <transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="cancelar">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Confirmación</h3>
            <button class="modal-close" @click="cancelar">&times;</button>
          </div>
          <div class="modal-body">
            <p>{{ mensaje }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secundario" @click="cancelar">Cancelar</button>
            <button class="btn btn-primario" @click="confirmar">Confirmar</button>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'Confirmacion',
  computed: {
    ...mapState({
      visible: state => state.ui.confirmacion.visible,
      mensaje: state => state.ui.confirmacion.mensaje,
      callback: state => state.ui.confirmacion.callback
    })
  },
  methods: {
    confirmar() {
      if (this.callback) {
        this.callback(true);
      }
    },
    cancelar() {
      if (this.callback) {
        this.callback(false);
      }
    }
  }
};
</script>

<style scoped>
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
  max-width: 500px;
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
  color: #333;
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 1rem;
  border-top: 1px solid #eee;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  border: none;
}

.btn-primario {
  background-color: #0078d7;
  color: white;
}

.btn-primario:hover {
  background-color: #005bb5;
}

.btn-secundario {
  background-color: #f5f5f5;
  color: #333;
}

.btn-secundario:hover {
  background-color: #e5e5e5;
}

/* Transiciones */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>