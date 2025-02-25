import api from './api';

export default {
  /**
   * Obtiene el histórico de operaciones con filtros
   * @param {Object} filtros - Filtros a aplicar
   * @returns {Promise} - Promesa con los resultados
   */
  async obtenerHistorico(filtros = {}) {
    return api.post('/historico', filtros);
  },

  /**
   * Sube archivos de operaciones
   * @param {FormData} formData - FormData con los archivos
   * @returns {Promise} - Promesa con los resultados
   */
  async subirArchivos(formData) {
    return api.upload('/upload', formData);
  },

  /**
   * Elimina una operación específica
   * @param {Number} id - ID de la operación a eliminar
   * @returns {Promise} - Promesa con el resultado
   */
  async eliminarOperacion(id) {
    return api.delete(`/delete/operaciones/${id}`);
  },

  /**
   * Elimina todas las operaciones
   * @returns {Promise} - Promesa con el resultado
   */
  async eliminarTodo() {
    return api.delete('/delete_all');
  },

  /**
   * Verifica si un archivo tiene extensión permitida
   * @param {String} filename - Nombre del archivo
   * @returns {Boolean} - True si está permitido, false en caso contrario
   */
  allowedFile(filename) {
    if (!filename || filename.indexOf('.') === -1) {
      return false;
    }
    const ext = filename.split('.').pop().toLowerCase();
    return ['xlsx', 'xls', 'csv'].includes(ext);
  },

  /**
   * Verifica el tamaño del archivo
   * @param {File} file - Archivo a verificar
   * @returns {Boolean} - True si el tamaño es permitido
   */
  validFileSize(file) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    return file.size <= maxSize;
  }
};