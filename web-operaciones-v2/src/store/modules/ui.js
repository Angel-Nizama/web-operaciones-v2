// Estado UI para controlar elementos visuales globales
export default {
    namespaced: true,
    
    state: () => ({
      // Sección actual activa
      ultimaSeccion: 'home',
      
      // Estado de carga global
      loading: false,
      
      // Mensajes de notificación
      mensajes: [],
      
      // Confirmar acción
      confirmacion: {
        visible: false,
        mensaje: '',
        callback: null
      }
    }),
    
    mutations: {
      // Actualizar sección activa
      SET_ULTIMA_SECCION(state, seccion) {
        state.ultimaSeccion = seccion;
      },
      
      // Actualizar estado de carga
      SET_LOADING(state, isLoading) {
        state.loading = isLoading;
      },
      
      // Agregar un mensaje
      ADD_MENSAJE(state, mensaje) {
        const id = Date.now();
        state.mensajes.push({
          id,
          texto: mensaje.texto,
          tipo: mensaje.tipo || 'info',
          duracion: mensaje.duracion || 5000
        });
        
        // Auto-eliminar después del tiempo
        if (mensaje.duracion !== 0) {
          setTimeout(() => {
            this.commit('ui/REMOVE_MENSAJE', id);
          }, mensaje.duracion || 5000);
        }
      },
      
      // Eliminar un mensaje
      REMOVE_MENSAJE(state, id) {
        state.mensajes = state.mensajes.filter(m => m.id !== id);
      },
      
      // Mostrar confirmación
      SHOW_CONFIRMACION(state, { mensaje, callback }) {
        state.confirmacion = {
          visible: true,
          mensaje,
          callback
        };
      },
      
      // Ocultar confirmación
      HIDE_CONFIRMACION(state) {
        state.confirmacion.visible = false;
      }
    },
    
    actions: {
      // Cambiar sección activa
      cambiarSeccion({ commit }, seccion) {
        commit('SET_ULTIMA_SECCION', seccion);
      },
      
      // Mostrar mensaje
      mostrarMensaje({ commit }, mensaje) {
        commit('ADD_MENSAJE', mensaje);
      },
      
      // Mostrar error
      mostrarError({ commit }, texto) {
        commit('ADD_MENSAJE', {
          texto,
          tipo: 'error',
          duracion: 8000
        });
      },
      
      // Mostrar éxito
      mostrarExito({ commit }, texto) {
        commit('ADD_MENSAJE', {
          texto,
          tipo: 'success',
          duracion: 5000
        });
      },
      
      // Pedir confirmación
      async pedirConfirmacion({ commit, state }, mensaje) {
        return new Promise((resolve) => {
          commit('SHOW_CONFIRMACION', {
            mensaje,
            callback: (respuesta) => {
              commit('HIDE_CONFIRMACION');
              resolve(respuesta);
            }
          });
        });
      }
    },
    
    getters: {
      isLoading: state => state.loading,
      mensajesActivos: state => state.mensajes,
      confirmacionVisible: state => state.confirmacion.visible,
      mensajeConfirmacion: state => state.confirmacion.mensaje
    }
  };