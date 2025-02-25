<template>
  <div :class="['file-uploader', { 'is-dragging': isDragging }]">
    <div class="file-uploader-dropzone" 
         @dragover.prevent="onDragOver"
         @dragleave.prevent="onDragLeave"
         @drop.prevent="onDrop">
      <div class="file-uploader-content">
        <div class="file-uploader-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path fill="none" d="M0 0h24v24H0z"/>
            <path d="M12 12.586l4.243 4.242-1.415 1.415L13 16.415V22h-2v-5.587l-1.828 1.83-1.415-1.415L12 12.586zM12 2a7.001 7.001 0 0 1 6.954 6.194 5.5 5.5 0 0 1-.953 10.784v-2.014a3.5 3.5 0 1 0-1.112-6.91 5 5 0 1 0-9.777 0 3.5 3.5 0 0 0-1.292 6.88l.19.031v2.014a5.5 5.5 0 0 1-.954-10.784A7 7 0 0 1 12 2z" fill="currentColor"/>
          </svg>
        </div>
        <h3>{{ title }}</h3>
        <p>Arrastra archivos aquí o <span class="file-uploader-browse">selecciona archivos</span></p>
        <p class="file-uploader-info">{{ infoText }}</p>
        <input
          type="file"
          ref="fileInput"
          :multiple="multiple"
          :accept="accept"
          class="file-uploader-input"
          @change="onFileSelected"
        />
      </div>
    </div>

    <div v-if="selectedFiles.length > 0" class="file-list">
      <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
        <div class="file-item-name">{{ file.name }}</div>
        <div class="file-item-size">{{ formatFileSize(file.size) }}</div>
        <button class="file-item-remove" @click="removeFile(index)">&times;</button>
      </div>
    </div>

    <div class="file-uploader-actions">
      <button class="btn btn-secundario" @click="clearFiles" :disabled="selectedFiles.length === 0">
        Limpiar
      </button>
      <button class="btn btn-primario" @click="uploadFiles" :disabled="selectedFiles.length === 0 || uploading">
        <span v-if="!uploading">Subir Archivos</span>
        <span v-else>Subiendo...</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FileUploader',
  
  props: {
    title: {
      type: String,
      default: 'Subir Archivos'
    },
    infoText: {
      type: String,
      default: 'Formatos permitidos: XLSX, XLS, CSV. Máximo 10MB por archivo.'
    },
    multiple: {
      type: Boolean,
      default: true
    },
    accept: {
      type: String,
      default: '.xlsx,.xls,.csv'
    },
    maxFileSize: {
      type: Number,
      default: 10 * 1024 * 1024 // 10MB
    },
    allowedExtensions: {
      type: Array,
      default: () => ['xlsx', 'xls', 'csv']
    }
  },
  
  data() {
    return {
      selectedFiles: [],
      isDragging: false,
      uploading: false
    };
  },
  
  methods: {
    onDragOver(e) {
      this.isDragging = true;
    },
    
    onDragLeave(e) {
      this.isDragging = false;
    },
    
    onDrop(e) {
      this.isDragging = false;
      const files = e.dataTransfer.files;
      this.processFiles(files);
    },
    
    onFileSelected(e) {
      const files = e.target.files;
      this.processFiles(files);
      // Resetear input para permitir seleccionar el mismo archivo nuevamente
      this.$refs.fileInput.value = '';
    },
    
    processFiles(files) {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Validar tamaño
        if (file.size > this.maxFileSize) {
          this.$store.dispatch('ui/mostrarError', 
            `El archivo ${file.name} supera el tamaño máximo de ${this.formatFileSize(this.maxFileSize)}`
          );
          continue;
        }
        
        // Validar extensión
        const extension = file.name.split('.').pop().toLowerCase();
        if (!this.allowedExtensions.includes(extension)) {
          this.$store.dispatch('ui/mostrarError', 
            `El archivo ${file.name} tiene una extensión no permitida. Use: ${this.allowedExtensions.join(', ')}`
          );
          continue;
        }
        
        // Si todo está bien, agregar a los archivos seleccionados
        this.selectedFiles.push(file);
      }
    },
    
    removeFile(index) {
      this.selectedFiles.splice(index, 1);
    },
    
    clearFiles() {
      this.selectedFiles = [];
    },
    
    async uploadFiles() {
      if (this.selectedFiles.length === 0) return;
      
      this.uploading = true;
      const formData = new FormData();
      
      this.selectedFiles.forEach(file => {
        formData.append('file', file);
      });
      
      try {
        // Emitir evento para que el componente padre maneje la subida
        this.$emit('upload', formData);
      } catch (error) {
        this.$store.dispatch('ui/mostrarError', 'Error al subir los archivos');
        console.error('Error uploading files:', error);
      } finally {
        this.uploading = false;
      }
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
  }
};
</script>

<style scoped>
.file-uploader {
  border: 2px dashed #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.file-uploader.is-dragging {
  border-color: #0078d7;
  background-color: rgba(0, 120, 215, 0.05);
}

.file-uploader-dropzone {
  cursor: pointer;
  text-align: center;
}

.file-uploader-dropzone:hover .file-uploader-browse {
  text-decoration: underline;
}

.file-uploader-icon {
  display: flex;
  justify-content: center;
  color: #0078d7;
  margin-bottom: 1rem;
}

.file-uploader-icon svg {
  width: 48px;
  height: 48px;
}

.file-uploader h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.file-uploader p {
  margin: 0.5rem 0;
  color: #666;
}

.file-uploader-browse {
  color: #0078d7;
  font-weight: 500;
}

.file-uploader-info {
  font-size: 0.8rem;
  opacity: 0.7;
}

.file-uploader-input {
  position: absolute;
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  z-index: -1;
}

.file-list {
  margin-top: 1.5rem;
  border-top: 1px solid #eee;
  padding-top: 1rem;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background-color: white;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.file-item-name {
  flex: 1;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  padding-right: 1rem;
}

.file-item-size {
  color: #666;
  font-size: 0.9rem;
  margin-right: 1rem;
}

.file-item-remove {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0 0.5rem;
}

.file-uploader-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primario {
  background-color: #0078d7;
  color: white;
}

.btn-primario:hover:not(:disabled) {
  background-color: #005bb5;
}

.btn-secundario {
  background-color: #f5f5f5;
  color: #333;
}

.btn-secundario:hover:not(:disabled) {
  background-color: #e5e5e5;
}

/* Hacemos que toda el área sea clickeable para activar el input file */
.file-uploader-content {
  position: relative;
}

.file-uploader-content::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  cursor: pointer;
}

.file-uploader-content::after:hover + .file-uploader-input {
  cursor: pointer;
}
</style>