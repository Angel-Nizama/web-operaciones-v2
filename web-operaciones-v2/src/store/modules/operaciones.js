import operacionesService from '@/services/operacionesService';

export default {
  namespaced: true,
  
  state: () => ({
    // Datos
    operaciones: [],
    
    // Estadísticas
    montoTotal: 0,
    totalOperaciones: 0,
    
    // Filtros
    filtros: {
      nombre1: '',
      nombre2: '',
      fecha_desde: '',
      fecha_hasta: ''
    },
    
    // Paginación
    paginacion: {
      paginaActual: 1,
      totalPaginas: 1,
      itemsPorPagina: 100
    },
    
    // Estado
    cargando: false,
    error: null,
    ultimaActualizacion: null
  }),
  
  mutations: {
    // Actualizar operaciones
    SET_OPERACIONES(state, operaciones) {
      state.operaciones = operaciones;
    },
    
    // Actualizar estadísticas
    SET_ESTADISTICAS(state, { montoTotal, totalOperaciones }) {
      state.montoTotal = montoTotal;
      state.totalOperaciones = totalOperaciones;
    },
    
    // Actualizar filtros
    SET_FILTROS(state, filtros) {
      state.filtros = { ...filtros };
    },
    
    // Actualizar paginación
    SET_PAGINACION(state, paginacion) {
      state.paginacion = { ...state.paginacion, ...paginacion };
    },
    
    // Actualizar estado de carga
    SET_CARGANDO(state, cargando) {
      state.cargando = cargando;
    },
    
    // Actualizar error
    SET_ERROR(state, error) {
      state.error = error;
    },
    
    // Actualizar timestamp
    SET_ULTIMA_ACTUALIZACION(state) {
      state.ultimaActualizacion = new Date();
    }
  },
  
  actions: {
    /**
     * Cargar histórico de operaciones
     */
    async cargarHistorico({ commit, state }) {
      try {
        commit('SET_CARGANDO', true);
        commit('SET_ERROR', null);
        
        // Preparar parámetros
        const params = {
          ...state.filtros,
          page: state.paginacion.paginaActual,
          per_page: state.paginacion.itemsPorPagina
        };
        
        // Realizar petición
        const response = await operacionesService.obtenerHistorico(params);
        
        if (response.success) {
          commit('SET_OPERACIONES', response.data);
          commit('SET_ESTADISTICAS', { 
            montoTotal: response.montoTotal || 0, 
            totalOperaciones: response.total || 0 
          });
          commit('SET_PAGINACION', {
            totalPaginas: response.pagination.pages || 1
          });
          commit('SET_ULTIMA_ACTUALIZACION');
        } else {
          commit('SET_ERROR', 'Error al cargar los datos');
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en cargarHistorico:', error);
      } finally {
        commit('SET_CARGANDO', false);
      }
    },
    
    /**
     * Cambiar página
     */
    async cambiarPagina({ commit, dispatch, state }, pagina) {
      commit('SET_PAGINACION', { paginaActual: pagina });
      return dispatch('cargarHistorico');
    },
    
    /**
     * Cambiar tamaño de página
     */
    async cambiarItemsPorPagina({ commit, dispatch }, itemsPorPagina) {
      commit('SET_PAGINACION', { 
        itemsPorPagina,
        paginaActual: 1 
      });
      return dispatch('cargarHistorico');
    },
    
    /**
     * Aplicar filtros de búsqueda
     */
    async aplicarFiltros({ commit, dispatch }, filtros) {
      commit('SET_FILTROS', filtros);
      commit('SET_PAGINACION', { paginaActual: 1 });
      return dispatch('cargarHistorico');
    },
    
    /**
     * Limpiar filtros
     */
    async limpiarFiltros({ commit, dispatch }) {
      commit('SET_FILTROS', {
        nombre1: '',
        nombre2: '',
        fecha_desde: '',
        fecha_hasta: ''
      });
      commit('SET_PAGINACION', { paginaActual: 1 });
      return dispatch('cargarHistorico');
    },
    
    /**
     * Eliminar operación
     */
    async eliminarOperacion({ dispatch, commit }, id) {
      try {
        commit('SET_CARGANDO', true);
        const response = await operacionesService.eliminarOperacion(id);
        
        if (response.success) {
          return dispatch('cargarHistorico');
        } else {
          commit('SET_ERROR', 'Error al eliminar la operación');
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en eliminarOperacion:', error);
      } finally {
        commit('SET_CARGANDO', false);
      }
    },
    
    /**
     * Eliminar todas las operaciones
     */
    async eliminarTodo({ dispatch, commit }) {
      try {
        commit('SET_CARGANDO', true);
        const response = await operacionesService.eliminarTodo();
        
        if (response.success) {
          return dispatch('cargarHistorico');
        } else {
          commit('SET_ERROR', 'Error al eliminar las operaciones');
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en eliminarTodo:', error);
      } finally {
        commit('SET_CARGANDO', false);
      }
    },
    
    /**
     * Subir archivos
     */
    async subirArchivos({ dispatch, commit }, formData) {
      try {
        commit('SET_CARGANDO', true);
        const response = await operacionesService.subirArchivos(formData);
        
        if (response.success) {
          return dispatch('cargarHistorico');
        } else {
          commit('SET_ERROR', 'Error al subir los archivos');
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en subirArchivos:', error);
      } finally {
        commit('SET_CARGANDO', false);
      }
    }
  },
  
  getters: {
    // Obtener operaciones
    operaciones: state => state.operaciones,
    
    // Obtener estadísticas
    montoTotal: state => state.montoTotal,
    totalOperaciones: state => state.totalOperaciones,
    
    // Obtener filtros
    filtrosActivos: state => state.filtros,
    
    // Obtener paginación
    paginaActual: state => state.paginacion.paginaActual,
    totalPaginas: state => state.paginacion.totalPaginas,
    itemsPorPagina: state => state.paginacion.itemsPorPagina,
    
    // Estado
    cargando: state => state.cargando,
    hayError: state => !!state.error,
    mensajeError: state => state.error,
    
    // Calcular si hay filtros activos
    tieneFiltrosActivos: state => {
      return Object.values(state.filtros).some(v => !!v);
    }
  }
};