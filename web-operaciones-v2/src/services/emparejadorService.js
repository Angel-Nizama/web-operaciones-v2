import api from './api';

export default {
  /**
   * Obtiene afiliados para un rango específico
   * @param {Number} rangoInicio - Inicio del rango
   * @param {Number} rangoFin - Fin del rango
   * @returns {Promise} - Promesa con los resultados
   */
  async getAfiliadosPorRango(rangoInicio, rangoFin) {
    return api.get(`/emparejador/afiliados?rango_inicio=${rangoInicio}&rango_fin=${rangoFin}`);
  },
  
  /**
   * Agrega un afiliado a un rango específico
   * @param {Object} data - Datos del afiliado y rango
   * @returns {Promise} - Promesa con el resultado
   */
  async agregarAfiliadoRango(data) {
    return api.post('/emparejador/afiliados', data);
  },
  
  /**
   * Elimina un afiliado de un rango
   * @param {Number} id - ID del registro a eliminar
   * @returns {Promise} - Promesa con el resultado
   */
  async eliminarAfiliadoRango(id) {
    return api.delete(`/emparejador/afiliados/${id}`);
  },
  
  /**
   * Elimina todos los afiliados de un rango específico
   * @param {Number} rangoInicio - Inicio del rango
   * @param {Number} rangoFin - Fin del rango
   * @returns {Promise} - Promesa con el resultado
   */
  async eliminarAfiliadosRango(rangoInicio, rangoFin) {
    return api.delete(`/emparejador/afiliados/rango?rango_inicio=${rangoInicio}&rango_fin=${rangoFin}`);
  },
  
  /**
   * Elimina todos los afiliados de todos los rangos
   * @returns {Promise} - Promesa con el resultado
   */
  async eliminarTodosAfiliados() {
    return api.delete('/emparejador/afiliados/todos');
  },
  
  /**
   * Calcula emparejamientos según filtros mejorados
   * @param {Object} filtros - Filtros para el cálculo
   * @returns {Promise} - Promesa con los resultados
   */
  async calcularEmparejamientos(filtros = {}) {
    // Versión mejorada que acepta configuración de ponderaciones
    const parametros = {
      dias_minimos: filtros.dias_minimos || 1,
      riesgo_maximo: filtros.riesgo_maximo || 50,
      
      // Nuevos parámetros
      monto_minimo: filtros.monto_minimo || 0,
      monto_maximo: filtros.monto_maximo || 0,
      
      // Parámetros de ponderación para el algoritmo avanzado
      ponderaciones: filtros.ponderaciones || {
        dias: 0.4,
        diversidad: 0.25,
        operaciones: 0.25,
        patron: 0.1
      },
      
      // Indicar si queremos usar el algoritmo mejorado
      usar_algoritmo_avanzado: true
    };
    
    return api.post('/emparejador/calcular', parametros);
  },
  
  /**
   * Obtiene detalles de un emparejamiento específico con opciones avanzadas
   * @param {String} afiliado1 - Número del primer afiliado
   * @param {String} afiliado2 - Número del segundo afiliado
   * @param {Object} opciones - Opciones adicionales
   * @returns {Promise} - Promesa con los detalles
   */
  async obtenerDetallesEmparejamiento(afiliado1, afiliado2, opciones = {}) {
    // Construir parámetros de consulta
    const params = new URLSearchParams();
    
    // Añadir opciones avanzadas si están presentes
    if (opciones.incluirHistorialCompleto) {
      params.append('incluir_historial_completo', 'true');
    }
    
    if (opciones.configuracion) {
      params.append('configuracion', JSON.stringify(opciones.configuracion));
    }
    
    // Construir URL con parámetros
    const queryString = params.toString() ? `?${params.toString()}` : '';
    
    return api.get(`/emparejador/detalles/${afiliado1}/${afiliado2}${queryString}`);
  },
  
  /**
   * Analiza patrones de comportamiento entre afiliados
   * @param {Object} params - Parámetros para el análisis
   * @returns {Promise} - Promesa con los resultados del análisis
   */
  async analizarPatrones(params = {}) {
    return api.post('/emparejador/analizar-patrones', params);
  },
  
  /**
   * Exporta resultados del emparejador
   * @param {Array} resultados - Resultados a exportar
   * @param {String} formato - Formato de exportación ('csv' o 'excel')
   * @returns {Promise} - Promesa con la URL del archivo generado
   */
  async exportarResultados(resultados, formato = 'csv') {
    return api.post('/emparejador/exportar', { resultados, formato });
  }
};