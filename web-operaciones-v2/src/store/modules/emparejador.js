import emparejadorService from '@/services/emparejadorService';
import api from '@/services/api'; // Añadir esta importación

export default {
  namespaced: true,
  
  state: () => ({
    // Afiliados por rangos
    afiliadosPorRangos: {
      '0-500': [],
      '500-700': [],
      '700-1000': []
    },
    
    // Configuración mejorada
    configuracion: {
      diasMinimos: 1,
      riesgoMaximo: 50,
      montoMinimo: 0,
      montoMaximo: 0,
      ponderacionDias: 0.4,
      ponderacionDiversidad: 0.25,
      ponderacionOperaciones: 0.25,
      ponderacionPatron: 0.1
    },
    
    // Resultados de emparejamiento
    resultadosEmparejamiento: [],
    resultadosFiltrados: [],
    
    // Historial completo para análisis
    historialOperaciones: [],
    
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
    
    // Actualizar historial de operaciones
    SET_HISTORIAL_OPERACIONES(state, historial) {
      state.historialOperaciones = historial;
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
     * Calcular emparejamientos (versión mejorada)
     */
    async calcularEmparejamientos({ commit, state }) {
      try {
        // Indicar inicio de carga
        commit('SET_CARGANDO_EMPAREJAMIENTOS', true);
        commit('SET_ERROR', null);
        
        // Preparar los filtros para el cálculo
        const filtros = {
          dias_minimos: state.configuracion.diasMinimos,
          riesgo_maximo: state.configuracion.riesgoMaximo,
          monto_minimo: state.configuracion.montoMinimo,
          monto_maximo: state.configuracion.montoMaximo,
          ponderaciones: {
            dias: state.configuracion.ponderacionDias,
            diversidad: state.configuracion.ponderacionDiversidad,
            operaciones: state.configuracion.ponderacionOperaciones,
            patron: state.configuracion.ponderacionPatron
          },
          usar_algoritmo_avanzado: true,
          limite: 1000 // Limitar número de resultados para mejor rendimiento
        };
        
        // Usar el servicio normal en lugar de API directamente
        const response = await emparejadorService.calcularEmparejamientos(filtros);
        
        if (response.success) {
          // Guardar los resultados en el store
          commit('SET_RESULTADOS_EMPAREJAMIENTO', response.data || []);
          
          // Almacenar historial para análisis posterior si está disponible
          if (response.historial) {
            commit('SET_HISTORIAL_OPERACIONES', response.historial);
          }
          
          return { success: true, message: "Emparejamientos calculados exitosamente", executionTime: response.execution_time };
        } else {
          commit('SET_ERROR', response.error || 'Error al calcular emparejamientos');
          return { 
            success: false, 
            message: response.message || 'Error al calcular emparejamientos' 
          };
        }
      } catch (error) {
        // Manejar errores específicos
        let errorMessage = 'Error de conexión';
        
        if (error.name === 'AbortError') {
          errorMessage = 'La operación ha excedido el tiempo límite. Por favor, intente con filtros más restrictivos.';
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        commit('SET_ERROR', errorMessage);
        console.error('Error en calcularEmparejamientos:', error);
        return { success: false, message: errorMessage };
      } finally {
        // Siempre finalizar el estado de carga
        commit('SET_CARGANDO_EMPAREJAMIENTOS', false);
      }
    },
    
    /**
     * Filtrar resultados de emparejamientos (versión mejorada)
     */
    filtrarResultados({ commit, state }, opciones = {}) {
      const { resultadosEmparejamiento, filtroAfiliado1, filtroAfiliado2 } = state;
      const { riesgoMaximo = 100, montoMinimo = 0, montoMaximo = 0 } = opciones;
      
      // Si no hay resultados originales, no hay nada que filtrar
      if (!resultadosEmparejamiento.length) {
        commit('SET_RESULTADOS_FILTRADOS', []);
        return;
      }
      
      const resultadosFiltrados = resultadosEmparejamiento.filter(resultado => {
        // Filtrar por nombres
        const pasaFiltroNombres = filtrarPorNombres(resultado, filtroAfiliado1, filtroAfiliado2);
        
        // Filtrar por riesgo
        const pasaFiltroRiesgo = !riesgoMaximo || resultado.riesgo <= riesgoMaximo;
        
        // Filtrar por monto
        const pasaFiltroMonto = 
          (!montoMinimo || resultado.monto_asignado >= montoMinimo) &&
          (!montoMaximo || resultado.monto_asignado <= montoMaximo);
        
        return pasaFiltroNombres && pasaFiltroRiesgo && pasaFiltroMonto;
      });
      
      commit('SET_RESULTADOS_FILTRADOS', resultadosFiltrados);
      
      // Función auxiliar para filtrar por nombres
      function filtrarPorNombres(resultado, filtro1, filtro2) {
        // Si no hay filtros, mostrar todos
        if (!filtro1 && !filtro2) {
          return true;
        }
        
        const afiliado1Lower = resultado.afiliado1.toLowerCase();
        const afiliado2Lower = resultado.afiliado2.toLowerCase();
        const filtro1Lower = filtro1 ? filtro1.toLowerCase() : '';
        const filtro2Lower = filtro2 ? filtro2.toLowerCase() : '';
        
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
      }
    },
    
    /**
     * Ordenar resultados por un campo específico
     * @param {Object} options - Opciones de ordenamiento
     * @param {string} options.campo - Campo por el que ordenar
     * @param {string} options.direccion - Dirección ('asc' o 'desc')
     */
    ordenarResultados({ commit, state }, { campo, direccion }) {
      const resultados = [...state.resultadosFiltrados];
      
      // Función comparadora genérica
      const comparar = (a, b, campo, dir) => {
        let valorA = a[campo];
        let valorB = b[campo];
        
        // Manejar caso especial para 'dias_desde_ultima'
        if (campo === 'dias_desde_ultima') {
          // Convertir a número si es posible
          valorA = typeof valorA === 'string' && valorA !== 'Sin operaciones previas' 
            ? parseInt(valorA) 
            : valorA === 'Sin operaciones previas' ? 9999 : valorA;
          valorB = typeof valorB === 'string' && valorB !== 'Sin operaciones previas' 
            ? parseInt(valorB) 
            : valorB === 'Sin operaciones previas' ? 9999 : valorB;
        }
        
        // Si son cadenas, comparar ignorando mayúsculas/minúsculas
        if (typeof valorA === 'string' && typeof valorB === 'string') {
          return dir === 'asc' 
            ? valorA.localeCompare(valorB) 
            : valorB.localeCompare(valorA);
        }
        
        // Para valores numéricos
        return dir === 'asc' ? valorA - valorB : valorB - valorA;
      };
      
      // Ordenar resultados
      resultados.sort((a, b) => comparar(a, b, campo, direccion));
      
      // Actualizar resultados filtrados
      commit('SET_RESULTADOS_FILTRADOS', resultados);
    },
    
    /**
     * Obtener detalles de emparejamiento (versión mejorada)
     */
    async obtenerDetallesPareja({ commit, state }, { afiliado1, afiliado2 }) {
      try {
        commit('SET_CARGANDO_DETALLES', true);
        commit('SET_ERROR', null);
        
        // Añadir análisis de historial completo
        const opciones = {
          incluirHistorialCompleto: true,
          configuracion: state.configuracion
        };
        
        const response = await emparejadorService.obtenerDetallesEmparejamiento(
          afiliado1, 
          afiliado2,
          opciones
        );
        
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