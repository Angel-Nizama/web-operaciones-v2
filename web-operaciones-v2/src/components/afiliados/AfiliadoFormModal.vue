<template>
    <Teleport to="body">
      <transition name="modal">
        <div v-if="visible" class="modal-overlay" @click.self="cerrar">
          <div class="modal-container">
            <div class="modal-header">
              <h3>{{ esEdicion ? 'Editar Afiliado' : 'Nuevo Afiliado' }}</h3>
              <button class="modal-close" @click="cerrar">&times;</button>
            </div>
            
            <div class="modal-body">
              <form @submit.prevent="guardarAfiliado">
                <div class="form-group">
                  <label for="numero">Número (teléfono):</label>
                  <input 
                    type="text" 
                    id="numero" 
                    v-model="formData.numero" 
                    class="form-control"
                    :class="{ 'is-invalid': errores.numero }"
                    required
                  >
                  <div v-if="errores.numero" class="invalid-feedback">
                    {{ errores.numero }}
                  </div>
                </div>
                
                <div class="form-group">
                  <label for="nombre">Nombre:</label>
                  <input 
                    type="text" 
                    id="nombre" 
                    v-model="formData.nombre" 
                    class="form-control"
                    :class="{ 'is-invalid': errores.nombre }"
                    required
                  >
                  <div v-if="errores.nombre" class="invalid-feedback">
                    {{ errores.nombre }}
                  </div>
                </div>
                
                <div class="form-group">
                  <label for="apellido_paterno">Apellido Paterno:</label>
                  <input 
                    type="text" 
                    id="apellido_paterno" 
                    v-model="formData.apellido_paterno" 
                    class="form-control"
                    :class="{ 'is-invalid': errores.apellido_paterno }"
                    required
                  >
                  <div v-if="errores.apellido_paterno" class="invalid-feedback">
                    {{ errores.apellido_paterno }}
                  </div>
                </div>
                
                <div class="form-group">
                  <label for="apellido_materno">Apellido Materno:</label>
                  <input 
                    type="text" 
                    id="apellido_materno" 
                    v-model="formData.apellido_materno" 
                    class="form-control"
                    :class="{ 'is-invalid': errores.apellido_materno }"
                    required
                  >
                  <div v-if="errores.apellido_materno" class="invalid-feedback">
                    {{ errores.apellido_materno }}
                  </div>
                </div>
                
                <div class="form-group">
                  <label for="dni">DNI:</label>
                  <input 
                    type="text" 
                    id="dni" 
                    v-model="formData.dni" 
                    class="form-control"
                    :class="{ 'is-invalid': errores.dni }"
                    required
                  >
                  <div v-if="errores.dni" class="invalid-feedback">
                    {{ errores.dni }}
                  </div>
                </div>
                
                <div class="form-group">
                  <label for="email">Email:</label>
                  <input 
                    type="email" 
                    id="email" 
                    v-model="formData.email" 
                    class="form-control"
                    :class="{ 'is-invalid': errores.email }"
                  >
                  <div v-if="errores.email" class="invalid-feedback">
                    {{ errores.email }}
                  </div>
                </div>
                
                <div class="form-group">
                  <label for="estado">Estado:</label>
                  <select 
                    id="estado" 
                    v-model="formData.estado" 
                    class="form-control"
                    required
                  >
                    <option value="Activo">Activo</option>
                    <option value="Inactivo">Inactivo</option>
                  </select>
                </div>
                
                <div class="modal-footer">
                  <button 
                    type="button" 
                    class="btn btn-secundario" 
                    @click="cerrar"
                  >
                    Cancelar
                  </button>
                  <button 
                    type="submit" 
                    class="btn btn-primario" 
                    :disabled="guardando"
                  >
                    {{ guardando ? 'Guardando...' : 'Guardar' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </template>
  
  <script>
  export default {
    name: 'AfiliadoFormModal',
    emits: ['cerrar'],
    props: {
      visible: {
        type: Boolean,
        default: false
      },
      afiliado: {
        type: Object,
        default: () => null
      }
    },
    data() {
      return {
        formData: {
          numero: '',
          nombre: '',
          apellido_paterno: '',
          apellido_materno: '',
          dni: '',
          email: '',
          estado: 'Activo'
        },
        errores: {},
        guardando: false
      };
    },
    computed: {
      esEdicion() {
        return this.afiliado !== null;
      }
    },
    watch: {
      visible(newVal) {
        if (newVal && this.afiliado) {
          // Si es edición, copia los datos del afiliado
          this.formData = { ...this.afiliado };
        } else if (newVal) {
          // Si es nuevo, reinicia el formulario
          this.reiniciarFormulario();
        }
      }
    },
    methods: {
      cerrar() {
        if (!this.guardando) {
          this.$emit('cerrar');
          this.reiniciarFormulario();
        }
      },
      reiniciarFormulario() {
        this.formData = {
          numero: '',
          nombre: '',
          apellido_paterno: '',
          apellido_materno: '',
          dni: '',
          email: '',
          estado: 'Activo'
        };
        this.errores = {};
      },
      validarFormulario() {
        let valido = true;
        this.errores = {};
        
        // Validar teléfono (solo números)
        if (!/^\d+$/.test(this.formData.numero)) {
          this.errores.numero = 'El número debe contener solo dígitos';
          valido = false;
        }
        
        // Validar que nombre, apellidos no estén vacíos
        if (!this.formData.nombre.trim()) {
          this.errores.nombre = 'El nombre es obligatorio';
          valido = false;
        }
        
        if (!this.formData.apellido_paterno.trim()) {
          this.errores.apellido_paterno = 'El apellido paterno es obligatorio';
          valido = false;
        }
        
        if (!this.formData.apellido_materno.trim()) {
          this.errores.apellido_materno = 'El apellido materno es obligatorio';
          valido = false;
        }
        
        // Validar DNI
        if (!this.formData.dni.trim()) {
          this.errores.dni = 'El DNI es obligatorio';
          valido = false;
        }
        
        // Validar email si está presente
        if (this.formData.email && !/^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/.test(this.formData.email)) {
          this.errores.email = 'El email no es válido';
          valido = false;
        }
        
        return valido;
      },
      async guardarAfiliado() {
        if (!this.validarFormulario()) {
          return;
        }
        
        this.guardando = true;
        
        try {
          let resultado;
          
          if (this.esEdicion) {
            resultado = await this.$store.dispatch('afiliados/actualizarAfiliado', {
              id: this.afiliado.id,
              data: this.formData
            });
          } else {
            resultado = await this.$store.dispatch('afiliados/crearAfiliado', this.formData);
          }
          
          if (resultado.success) {
            this.$store.dispatch('ui/mostrarExito', 
              this.esEdicion 
                ? 'Afiliado actualizado correctamente' 
                : 'Afiliado creado correctamente'
            );
            this.cerrar();
          } else {
            this.$store.dispatch('ui/mostrarError', resultado.message || 'Error al guardar el afiliado');
          }
        } catch (error) {
          this.$store.dispatch('ui/mostrarError', 'Error al guardar el afiliado');
          console.error('Error en guardarAfiliado:', error);
        } finally {
          this.guardando = false;
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
  }
  
  .modal-container {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    width: 90%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #eee;
  }
  
  .modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: var(--color-primario);
  }
  
  .modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #666;
  }
  
  .modal-body {
    padding: 1.5rem;
  }
  
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    padding: 1rem 0 0;
    gap: 1rem;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  .form-control {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--color-borde);
    border-radius: var(--border-radius-sm);
    font-size: 1rem;
  }
  
  .form-control:focus {
    outline: none;
    border-color: var(--color-primario);
    box-shadow: 0 0 0 2px rgba(0, 120, 215, 0.1);
  }
  
  .is-invalid {
    border-color: var(--color-error) !important;
  }
  
  .invalid-feedback {
    color: var(--color-error);
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
  
  /* Transiciones */
  .modal-enter-active,
  .modal-leave-active {
    transition: opacity 0.3s;
  }
  
  .modal-enter-from,
  .modal-leave-to {
    opacity: 0;
  }
  </style>