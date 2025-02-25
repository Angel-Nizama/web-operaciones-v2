import emparejadorService from '@/services/emparejadorService';

export default {
  namespaced: true,
  
  state: () => ({
    // Afiliados por rangos
    afiliadosPorRangos: {
      '0-500': [],
      '500-700': [],
      '700-1000': []
    },
    
    // Configuración
    configuracion: {
      diasMinimos: 1,
      riesgoMaximo: 50
    },
    
    // Resultados de emparejamiento
    resultadosEmparejamiento: [],
    resultadosFiltrados: [],
    
    // Detalles de pareja
    detallesPareja: null,
    
    // Búsqueda de emparejamiento
    filtroAfiliado1: '',
    filtroAfiliado2: '',
    
    // Estadísticas
    totalAfiliadosInscritos: 0,
    
    // Estado
    cargandoRango: false,
    cargandoEmparejamientos: false,
    cargandoDetalles: false,
    error: null
  }),
  
  mutations: {
    // Actualizar afiliados de un rango
    SET_AFILIADOS_RANGO(state, { rangoKey, afiliados }) {
      state.afiliadosPorRangos[rangoKey] = afiliados;
    },
    
    // Actualizar configuración
    SET_CONFIGURACION(state, config) {
      state.configuracion = { ...config };
    },
    
    // Actualizar resultados de emparejamiento
    SET_RESULTADOS_EMPAREJAMIENTO(state, resultados) {
      state.resultadosEmparejamiento = resultados;
      state.resultadosFiltrados = resultados;
    },
    
    // Actualizar resultados filtrados
    SET_RESULTADOS_FILTRADOS(state, resultados) {
      state.resultadosFiltrados = resultados;
    },
    
    // Actualizar detalles de pareja
    SET_DETALLES_PAREJA(state, detalles) {
      state.detallesPareja = detalles;
    },
    
    // Actualizar filtros de búsqueda
    SET_FILTRO_AFILIADO1(state, filtro) {
      state.filtroAfiliado1 = filtro;
    },
    
    SET_FILTRO_AFILIADO2(state, filtro) {
      state.filtroAfiliado2 = filtro;
    },
    
    // Actualizar total de afiliados
    SET_TOTAL_AFILIADOS(state, total) {
      state.totalAfiliadosInscritos = total;
    },
    
    // Actualizar estados de carga
    SET_CARGANDO_RANGO(state, cargando) {
      state.cargandoRango = cargando;
    },
    
    SET_CARGANDO_EMPAREJAMIENTOS(state, cargando) {
      state.cargandoEmparejamientos = cargando;
    },
    
    SET_CARGANDO_DETALLES(state, cargando) {
      state.cargandoDetalles = cargando;
    },
    
    // Actualizar error
    SET_ERROR(state, error) {
      state.error = error;
    }
  },
  
  actions: {
    /**
     * Cargar afiliados de un rango específico
     */
    async cargarAfiliadosRango({ commit }, { inicio, fin }) {
      const rangoKey = `${inicio}-${fin}`;
      
      try {
        commit('SET_CARGANDO_RANGO', true);
        commit('SET_ERROR', null);
        
        const response = await emparejadorService.getAfiliadosPorRango(inicio, fin);
        
        if (response.success) {
          commit('SET_AFILIADOS_RANGO', { 
            rangoKey,
            afiliados: response.data 
          });
          commit('SET_TOTAL_AFILIADOS', response.total_afiliados || 0);
        } else {
          commit('SET_ERROR', 'Error al cargar los afiliados del rango');
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error(`Error en cargarAfiliadosRango [${rangoKey}]:`, error);
      } finally {
        commit('SET_CARGANDO_RANGO', false);
      }
    },
    
    /**
     * Cargar todos los rangos
     */
    async cargarTodosLosRangos({ dispatch }) {
      await Promise.all([
        dispatch('cargarAfiliadosRango', { inicio: 0, fin: 500 }),
        dispatch('cargarAfiliadosRango', { inicio: 500, fin: 700 }),
        dispatch('cargarAfiliadosRango', { inicio: 700, fin: 1000 })
      ]);
    },
    
    /**
     * Agregar afiliado a un rango
     */
    async agregarAfiliadoRango({ dispatch, commit }, datos) {
      try {
        commit('SET_CARGANDO_RANGO', true);
        commit('SET_ERROR', null);
        
        const response = await emparejadorService.agregarAfiliadoRango(datos);
        
        if (response.success) {
          // Recargar el rango específico
          await dispatch('cargarAfiliadosRango', { 
            inicio: datos.rango_inicio, 
            fin: datos.rango_fin 
          });
          
          return { success: true, message: response.message };
        } else {
          commit('SET_ERROR', 'Error al agregar afiliado al rango');
          return { success: false, message: 'Error al agregar afiliado' };
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en agregarAfiliadoRango:', error);
        return { success: false, message: error.message || 'Error de conexión' };
      } finally {
        commit('SET_CARGANDO_RANGO', false);
      }
    },
    
    /**
     * Eliminar afiliado de un rango
     */
    async eliminarAfiliadoRango({ dispatch, commit }, { id, inicio, fin }) {
      try {
        commit('SET_CARGANDO_RANGO', true);
        commit('SET_ERROR', null);
        
        const response = await emparejadorService.eliminarAfiliadoRango(id);
        
        if (response.success) {
          // Recargar el rango específico
          await dispatch('cargarAfiliadosRango', { inicio, fin });
          
          return { success: true, message: response.message };
        } else {
          commit('SET_ERROR', 'Error al eliminar afiliado del rango');
          return { success: false, message: 'Error al eliminar afiliado' };
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en eliminarAfiliadoRango:', error);
        return { success: false, message: error.message || 'Error de conexión' };
      } finally {
        commit('SET_CARGANDO_RANGO', false);
      }
    },
    
    /**
     * Eliminar todos los afiliados de un rango
     */
    async eliminarAfiliadosRango({ dispatch, commit }, { inicio, fin }) {
      try {
        commit('SET_CARGANDO_RANGO', true);
        commit('SET_ERROR', null);
        
        const response = await emparejadorService.eliminarAfiliadosRango(inicio, fin);
        
        if (response.success) {
          // Recargar el rango específico
          await dispatch('cargarAfiliadosRango', { inicio, fin });
          
          return { success: true, message: response.message };
        } else {
          commit('SET_ERROR', 'Error al eliminar afiliados del rango');
          return { success: false, message: 'Error al eliminar afiliados' };
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en eliminarAfiliadosRango:', error);
        return { success: false, message: error.message || 'Error de conexión' };
      } finally {
        commit('SET_CARGANDO_RANGO', false);
      }
    },
    
    /**
     * Eliminar todos los afiliados de todos los rangos
     */
    async eliminarTodosAfiliados({ dispatch, commit }) {
      try {
        commit('SET_CARGANDO_RANGO', true);
        commit('SET_ERROR', null);
        
        const response = await emparejadorService.eliminarTodosAfiliados();
        
        if (response.success) {
          // Recargar todos los rangos
          await dispatch('cargarTodosLosRangos');
          
          return { success: true, message: response.message };
        } else {
          commit('SET_ERROR', 'Error al eliminar todos los afiliados');
          return { success: false, message: 'Error al eliminar todos los afiliados' };
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en eliminarTodosAfiliados:', error);
        return { success: false, message: error.message || 'Error de conexión' };
      } finally {
        commit('SET_CARGANDO_RANGO', false);
      }
    },
    
    /**
     * Calcular emparejamientos
     */
    async calcularEmparejamientos({ commit, state }) {
      try {
        commit('SET_CARGANDO_EMPAREJAMIENTOS', true);
        commit('SET_ERROR', null);
        
        const filtros = {
          dias_minimos: state.configuracion.diasMinimos,
          riesgo_maximo: state.configuracion.riesgoMaximo
        };
        
        const response = await emparejadorService.calcularEmparejamientos(filtros);
        
        if (response.success) {
          commit('SET_RESULTADOS_EMPAREJAMIENTO', response.data);
          return { success: true };
        } else {
          commit('SET_ERROR', 'Error al calcular emparejamientos');
          return { success: false, message: 'Error al calcular emparejamientos' };
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en calcularEmparejamientos:', error);
        return { success: false, message: error.message || 'Error de conexión' };
      } finally {
        commit('SET_CARGANDO_EMPAREJAMIENTOS', false);
      }
    },
    
    /**
     * Filtrar resultados de emparejamientos
     */
    filtrarResultados({ commit, state }) {
      const { resultadosEmparejamiento, filtroAfiliado1, filtroAfiliado2 } = state;
      
      // Si no hay filtros, mostrar todos
      if (!filtroAfiliado1 && !filtroAfiliado2) {
        commit('SET_RESULTADOS_FILTRADOS', resultadosEmparejamiento);
        return;
      }
      
      const resultadosFiltrados = resultadosEmparejamiento.filter(resultado => {
        const afiliado1Lower = resultado.afiliado1.toLowerCase();
        const afiliado2Lower = resultado.afiliado2.toLowerCase();
        const filtro1Lower = filtroAfiliado1.toLowerCase();
        const filtro2Lower = filtroAfiliado2.toLowerCase();
        
        // Si solo hay filtro1
        if (filtro1Lower && !filtro2Lower) {
          return afiliado1Lower.includes(filtro1Lower) || afiliado2Lower.includes(filtro1Lower);
        }
        
        // Si solo hay filtro2
        if (!filtro1Lower && filtro2Lower) {
          return afiliado1Lower.includes(filtro2Lower) || afiliado2Lower.includes(filtro2Lower);
        }
        
        // Si hay ambos filtros
        return (
          (afiliado1Lower.includes(filtro1Lower) && afiliado2Lower.includes(filtro2Lower)) ||
          (afiliado1Lower.includes(filtro2Lower) && afiliado2Lower.includes(filtro1Lower))
        );
      });
      
      commit('SET_RESULTADOS_FILTRADOS', resultadosFiltrados);
    },
    
    /**
     * Obtener detalles de emparejamiento
     */
    async obtenerDetallesPareja({ commit }, { afiliado1, afiliado2 }) {
      try {
        commit('SET_CARGANDO_DETALLES', true);
        commit('SET_ERROR', null);
        
        const response = await emparejadorService.obtenerDetallesEmparejamiento(afiliado1, afiliado2);
        
        if (response.success) {
          commit('SET_DETALLES_PAREJA', response);
          return { success: true };
        } else {
          commit('SET_ERROR', 'Error al obtener detalles de emparejamiento');
          return { success: false, message: response.error || 'Error al obtener detalles' };
        }
      } catch (error) {
        commit('SET_ERROR', error.message || 'Error de conexión');
        console.error('Error en obtenerDetallesPareja:', error);
        return { success: false, message: error.message || 'Error de conexión' };
      } finally {
        commit('SET_CARGANDO_DETALLES', false);
      }
    },
    
    /**
     * Actualizar configuración
     */
    actualizarConfiguracion({ commit }, config) {
      commit('SET_CONFIGURACION', config);
    }
  },
  
  getters: {
    // Obtener afiliados por rango
    afiliadosRango: state => rangoKey => state.afiliadosPorRangos[rangoKey] || [],
    
    // Obtener configuración
    configuracion: state => state.configuracion,
    
    // Obtener resultados de emparejamiento
    resultadosEmparejamiento: state => state.resultadosEmparejamiento,
    resultadosFiltrados: state => state.resultadosFiltrados,
    tieneResultados: state => state.resultadosEmparejamiento.length > 0,
    
    // Obtener detalles de pareja
    detallesPareja: state => state.detallesPareja,
    
    // Obtener total de afiliados
    totalAfiliadosInscritos: state => state.totalAfiliadosInscritos,
    
    // Estado
    cargandoRango: state => state.cargandoRango,
    cargandoEmparejamientos: state => state.cargandoEmparejamientos,
    cargandoDetalles: state => state.cargandoDetalles,
    cargando: state => state.cargandoRango || state.cargandoEmparejamientos || state.cargandoDetalles,
    hayError: state => !!state.error,
    mensajeError: state => state.error
  }
};