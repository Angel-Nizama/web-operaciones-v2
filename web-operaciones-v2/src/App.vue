<template>
  <AppLayout>
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </AppLayout>
</template>

<script>
import AppLayout from '@/components/layout/AppLayout.vue';

export default {
  name: 'App',
  components: {
    AppLayout
  },
  created() {
    // Inicializaciones globales si son necesarias
  }
};
</script>

<style>
/* Estilos globales adicionales */

/* Animaciones de transición entre rutas */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>