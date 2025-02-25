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
   * Calcula emparejamientos según filtros
   * @param {Object} filtros - Filtros para el cálculo
   * @returns {Promise} - Promesa con los resultados
   */
  async calcularEmparejamientos(filtros = {}) {
    return api.post('/emparejador/calcular', filtros);
  },
  
  /**
   * Obtiene detalles de un emparejamiento específico
   * @param {String} afiliado1 - Número del primer afiliado
   * @param {String} afiliado2 - Número del segundo afiliado
   * @returns {Promise} - Promesa con los detalles
   */
  async obtenerDetallesEmparejamiento(afiliado1, afiliado2) {
    return api.get(`/emparejador/detalles/${afiliado1}/${afiliado2}`);
  }
};