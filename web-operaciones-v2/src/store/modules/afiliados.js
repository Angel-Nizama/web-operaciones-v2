// File: src/store/modules/afiliados.js
// Fixed version with proper action names and structure

import afiliadosService from '@/services/afiliadosService';

export default {
  namespaced: true,
  
  state: () => ({
    // Datos
    afiliados: [],
    
    // Estadísticas
    totalAfiliados: 0,
    afiliadosActivos: 0,
    
    // Filtros
    filtros: {
      numero: '',
      nombre: '',
      dni: '',
      estado: 'Todos'
    },
    
    // Paginación
    paginacion: {
      paginaActual: 1,
      totalPaginas: 1,
      itemsPorPagina: 100
    },
    
    // Resultados de búsqueda
    resultadosBusqueda: [],
    buscando: false,
    
    // Estado
    cargando: false,
    error: null,
    ultimaActualizacion: null
  }),
  
  mutations: {
    // Actualizar afiliados
    SET_AFILIADOS(state, afiliados) {
      state.afiliados = afiliados;
    },
    
    // Actualizar estadísticas
    SET_ESTADISTICAS(state, { totalAfiliados, afiliadosActivos }) {
      state.totalAfiliados = totalAfiliados;
      state.afiliadosActivos = afiliadosActivos;
    },
    
    // Actualizar filtros
    SET_FILTROS(state, filtros) {
      state.filtros = { ...filtros };
    },
    
    // Actualizar paginación
    SET_PAGINACION(state, paginacion) {
      state.paginacion = { ...state.paginacion, ...paginacion };
    },
    
    // Actualizar resultados de búsqueda
    SET_RESULTADOS_BUSQUEDA(state, resultados) {
      state.resultadosBusqueda = resultados;
    },
    
    // Actualizar estado de búsqueda
    SET_BUSCANDO(state, buscando) {
      state.buscando = buscando;
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
     * Cargar listado de afiliados
     */
    async cargarAfiliados({ commit, state }) {
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
        const response = await afiliadosService.obtenerAfiliados(params);
        
        if (response.success) {
          commit('SET_AFILIADOS', response.data);
          commit('SET_ESTADISTICAS', { 
            totalAfiliados: response.totalAfiliados || 0, 
            afiliadosActivos: response.afiliadosActivos || 0 
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
        console.error('Error en cargarAfiliados:', error);
      } finally {
        commit('SET_CARGANDO', false);
      }
    },
    
    /**
     * Cambiar página
     */
    async cambiarPagina({ commit, dispatch, state }, pagina) {
      commit('SET_PAGINACION', { paginaActual: pagina });
      return dispatch('cargarAfiliados');
    },
    
    /**
     * Cambiar tamaño de página
     */
    async cambiarItemsPorPagina({ commit, dispatch }, itemsPorPagina) {
      commit('SET_PAGINACION', { 
        itemsPorPagina,
        paginaActual: 1 
      });
      return dispatch('cargarAfiliados');
    },
    
    /**
     * Aplicar filtros de búsqueda
     */
    async aplicarFiltros({ commit, dispatch }, filtros) {
      commit('SET_FILTROS', filtros);
      commit('SET_PAGINACION', { paginaActual: 1 });
      return dispatch('cargarAfiliados');
    },
    
    /**
     * Limpiar filtros
     */
    async limpiarFiltros({ commit, dispatch }) {
      commit('SET_FILTROS', {
        numero: '',
        nombre: '',
        dni: '',
        estado: 'Todos'
      });
      commit('SET_PAGINACION', { paginaActual: 1 });
      return dispatch('cargarAfiliados');
    },
    
    /**
     * Buscar afiliados
     */
    async buscarAfiliados({ commit }, { texto, tipo }) {
      if (!texto || texto.length < 2) {
        commit('SET_RESULTADOS_BUSQUEDA', []);
        return;
      }
      
      try {
        commit('SET_BUSCANDO', true);
        const resultados = await afiliadosService.buscarAfiliado(texto, tipo);
        commit('SET_RESULTADOS_BUSQUEDA', resultados);
      } catch (error) {
        console.error('Error en buscarAfiliados:', error);
      } finally {
        commit('SET_BUSCANDO', false);
      }
    },
    
    /**
     * Subir archivo de afiliados
     */
    async subirArchivoAfiliados({ dispatch, commit }, formData) {
      try {
        commit('SET_CARGANDO', true);
        const response = await afiliadosService.subirArchivoAfiliados(formData);
        
        if (response.success) {
          return dispatch('cargarAfiliados');
        } else {
          commit('SET_ERROR', 'Error al subir el archivo');
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en subirArchivoAfiliados:', error);
      } finally {
        commit('SET_CARGANDO', false);
      }
    },
    
    /**
     * Eliminar todos los afiliados
     * FIX: Renamed from 'eliminarTodos' to 'eliminarTodo' to match component call
     */
    async eliminarTodo({ dispatch, commit }) {
      try {
        commit('SET_CARGANDO', true);
        const response = await afiliadosService.eliminarTodos();
        
        if (response.success) {
          await dispatch('cargarAfiliados');
          return { success: true, message: response.message || 'Afiliados eliminados correctamente' };
        } else {
          commit('SET_ERROR', 'Error al eliminar los afiliados');
          return { success: false, message: response.message || 'Error al eliminar los afiliados' };
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en eliminarTodo:', error);
        return { success: false, message: error.message || 'Error de conexión' };
      } finally {
        commit('SET_CARGANDO', false);
      }
    },
    
    /**
     * Crear un nuevo afiliado
     */
    async crearAfiliado({ dispatch, commit }, data) {
      try {
        commit('SET_CARGANDO', true);
        const response = await afiliadosService.crearAfiliado(data);
        
        if (response.success) {
          await dispatch('cargarAfiliados');
          return { success: true, message: response.message || 'Afiliado creado correctamente' };
        } else {
          commit('SET_ERROR', 'Error al crear el afiliado');
          return { success: false, message: response.message || 'Error al crear el afiliado' };
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en crearAfiliado:', error);
        return { success: false, message: error.message || 'Error de conexión' };
      } finally {
        commit('SET_CARGANDO', false);
      }
    },
    
    /**
     * Actualizar un afiliado existente
     */
    async actualizarAfiliado({ dispatch, commit }, { id, data }) {
      try {
        commit('SET_CARGANDO', true);
        const response = await afiliadosService.actualizarAfiliado(id, data);
        
        if (response.success) {
          await dispatch('cargarAfiliados');
          return { success: true, message: response.message || 'Afiliado actualizado correctamente' };
        } else {
          commit('SET_ERROR', 'Error al actualizar el afiliado');
          return { success: false, message: response.message || 'Error al actualizar el afiliado' };
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en actualizarAfiliado:', error);
        return { success: false, message: error.message || 'Error de conexión' };
      } finally {
        commit('SET_CARGANDO', false);
      }
    },

    /**
     * Actualizar estados de afiliados basados en actividad reciente
     * FIX: Moved into actions object to make it a proper Vuex action
     */
    async actualizarEstadosPorActividad({ dispatch, commit }) {
      try {
        commit('SET_CARGANDO', true);
        const response = await afiliadosService.actualizarEstados();
        
        if (response.success) {
          await dispatch('cargarAfiliados');
          return { success: true, message: response.message };
        } else {
          commit('SET_ERROR', 'Error al actualizar estados');
          return { success: false, message: 'Error al actualizar estados' };
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en actualizarEstadosPorActividad:', error);
        return { success: false, message: error.message || 'Error de conexión' };
      } finally {
        commit('SET_CARGANDO', false);
      }
    }
  },
  
  getters: {
    // Obtener afiliados
    afiliados: state => state.afiliados,
    
    // Obtener estadísticas
    totalAfiliados: state => state.totalAfiliados,
    afiliadosActivos: state => state.afiliadosActivos,
    
    // Obtener filtros
    filtrosActivos: state => state.filtros,
    
    // Obtener paginación
    paginaActual: state => state.paginacion.paginaActual,
    totalPaginas: state => state.paginacion.totalPaginas,
    itemsPorPagina: state => state.paginacion.itemsPorPagina,
    
    // Resultados de búsqueda
    resultadosBusqueda: state => state.resultadosBusqueda,
    buscando: state => state.buscando,
    
    // Estado
    cargando: state => state.cargando,
    hayError: state => !!state.error,
    mensajeError: state => state.error,
    
    // Calcular si hay filtros activos
    tieneFiltrosActivos: state => {
      return Object.values(state.filtros).some(v => !!v && v !== 'Todos');
    }
  }
};