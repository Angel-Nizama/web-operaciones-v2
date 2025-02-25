import axios from 'axios';

// Configuración base de Axios
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Cache para manejar el throttling de peticiones
const requestCache = new Map();
const THROTTLE_TIME = 5000; // 5 segundos entre peticiones iguales

// Configuración de reintentos
const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY = 1000;
const MAX_RETRY_DELAY = 5000;

// Interceptor para reintentos
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const config = error.config;
    
    // Si no existe la propiedad retryCount, inicializarla
    config.retryCount = config.retryCount || 0;
    
    // Verificar si se debe reintentar
    if (config.retryCount < MAX_RETRIES) {
      config.retryCount += 1;
      
      // Calcular delay con backoff exponencial
      const delay = Math.min(
        INITIAL_RETRY_DELAY * Math.pow(2, config.retryCount - 1),
        MAX_RETRY_DELAY
      );
      
      // Esperar el delay
      await new Promise(resolve => setTimeout(resolve, delay));
      
      // Reintentar la petición
      return apiClient(config);
    }
    
    return Promise.reject(error);
  }
);

// Manejar solicitudes para evitar duplicados (throttling)
function canMakeRequest(endpoint, method, params) {
  const key = `${method}:${endpoint}:${JSON.stringify(params)}`;
  const lastRequest = requestCache.get(key);
  
  if (!lastRequest) return true;
  
  const elapsed = Date.now() - lastRequest;
  return elapsed >= THROTTLE_TIME;
}

function registerRequest(endpoint, method, params) {
  const key = `${method}:${endpoint}:${JSON.stringify(params)}`;
  requestCache.set(key, Date.now());
}

// Funciones helper para las peticiones
export const api = {
  // GET request
  async get(endpoint, params = {}) {
    if (!canMakeRequest(endpoint, 'GET', params)) {
      console.warn(`Request throttled: GET ${endpoint}`);
      return Promise.reject(new Error('Petición limitada por throttling'));
    }
    
    registerRequest(endpoint, 'GET', params);
    
    try {
      const response = await apiClient.get(endpoint, { params });
      return response.data;
    } catch (error) {
      console.error(`Error en GET ${endpoint}:`, error);
      throw handleApiError(error);
    }
  },
  
  // POST request
  async post(endpoint, data = {}) {
    if (!canMakeRequest(endpoint, 'POST', data)) {
      console.warn(`Request throttled: POST ${endpoint}`);
      return Promise.reject(new Error('Petición limitada por throttling'));
    }
    
    registerRequest(endpoint, 'POST', data);
    
    try {
      const response = await apiClient.post(endpoint, data);
      return response.data;
    } catch (error) {
      console.error(`Error en POST ${endpoint}:`, error);
      throw handleApiError(error);
    }
  },
  
  // DELETE request
  async delete(endpoint, params = {}) {
    if (!canMakeRequest(endpoint, 'DELETE', params)) {
      console.warn(`Request throttled: DELETE ${endpoint}`);
      return Promise.reject(new Error('Petición limitada por throttling'));
    }
    
    registerRequest(endpoint, 'DELETE', params);
    
    try {
      const response = await apiClient.delete(endpoint, { params });
      return response.data;
    } catch (error) {
      console.error(`Error en DELETE ${endpoint}:`, error);
      throw handleApiError(error);
    }
  },
  
  // POST con FormData (para subida de archivos)
  async upload(endpoint, formData) {
    if (!canMakeRequest(endpoint, 'UPLOAD', {})) {
      console.warn(`Request throttled: UPLOAD ${endpoint}`);
      return Promise.reject(new Error('Petición limitada por throttling'));
    }
    
    registerRequest(endpoint, 'UPLOAD', {});
    
    try {
      const response = await apiClient.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error en UPLOAD ${endpoint}:`, error);
      throw handleApiError(error);
    }
  }
};

// Manejar errores de API
function handleApiError(error) {
  let errorMessage = 'Error en la conexión con el servidor';
  
  if (error.response) {
    // Error de respuesta del servidor
    const serverError = error.response.data?.error || error.response.statusText;
    errorMessage = `Error del servidor: ${serverError}`;
  } else if (error.request) {
    // Error sin respuesta
    errorMessage = 'No se recibió respuesta del servidor';
  }
  
  return {
    message: errorMessage,
    originalError: error,
    status: error.response?.status
  };
}

export default api;