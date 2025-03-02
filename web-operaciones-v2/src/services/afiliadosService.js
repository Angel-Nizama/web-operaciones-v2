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
  },
  
  /**
   * Elimina todos los afiliados
   * @returns {Promise} - Promesa con el resultado
   */
  async eliminarTodos() {
    return api.delete('/delete_all_afiliados');
  },
  
  /**
   * Crea un nuevo afiliado
   * @param {Object} data - Datos del afiliado
   * @returns {Promise} - Promesa con el resultado
   */
  async crearAfiliado(data) {
    return api.post('/afiliados/crear', data);
  },
  
  /**
   * Actualiza un afiliado existente
   * @param {Number} id - ID del afiliado
   * @param {Object} data - Datos actualizados
   * @returns {Promise} - Promesa con el resultado
   */
  async actualizarAfiliado(id, data) {
    return api.put(`/afiliados/${id}`, data);
  },

  // Añadir a web-operaciones-v2/src/services/afiliadosService.js

/**
   * Actualiza los estados de afiliados basados en actividad reciente
   * @returns {Promise} - Promesa con el resultado
   */
  async actualizarEstados() {
    return api.post('/afiliados/actualizar-estados');
  }
};

