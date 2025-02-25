<template>
  <div class="mensajes-container">
    <TransitionGroup name="mensaje-list">
      <Mensaje
        v-for="mensaje in mensajes"
        :key="mensaje.id"
        :texto="mensaje.texto"
        :tipo="mensaje.tipo"
        :duracion="mensaje.duracion"
        @cerrar="eliminarMensaje(mensaje.id)"
      />
    </TransitionGroup>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import Mensaje from './Mensaje.vue';

export default {
  name: 'Mensajes',
  components: {
    Mensaje
  },
  computed: {
    ...mapState({
      mensajes: state => state.ui.mensajes
    })
  },
  methods: {
    eliminarMensaje(id) {
      this.$store.commit('ui/REMOVE_MENSAJE', id);
    }
  }
};
</script>

<style scoped>
.mensajes-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  width: 300px;
}

.mensaje-list-enter-active,
.mensaje-list-leave-active {
  transition: all 0.3s;
}

.mensaje-list-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.mensaje-list-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

@media (max-width: 576px) {
  .mensajes-container {
    width: calc(100% - 2rem);
  }
}
</style>