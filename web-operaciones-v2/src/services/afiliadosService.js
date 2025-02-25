import api from './api';

export default {
  /**
   * Obtiene el listado de afiliados con filtros
   * @param {Object} filtros - Filtros a aplicar
   * @returns {Promise} - Promesa con los resultados
   */
  async obtenerAfiliados(filtros = {}) {
    return api.post('/afiliados', filtros);
  },

  /**
   * Sube un archivo de afiliados
   * @param {FormData} formData - FormData con el archivo
   * @returns {Promise} - Promesa con el resultado
   */
  async subirArchivoAfiliados(formData) {
    return api.upload('/upload_afiliados', formData);
  },

  /**
   * Busca afiliados según un texto y tipo de búsqueda
   * @param {String} texto - Texto a buscar
   * @param {String} tipo - Tipo de búsqueda (nombre, numero, dni)
   * @returns {Promise} - Promesa con los resultados
   */
  async buscarAfiliado(texto, tipo = 'nombre') {
    return api.post('/buscar_afiliado', { texto, tipo });
  }
};