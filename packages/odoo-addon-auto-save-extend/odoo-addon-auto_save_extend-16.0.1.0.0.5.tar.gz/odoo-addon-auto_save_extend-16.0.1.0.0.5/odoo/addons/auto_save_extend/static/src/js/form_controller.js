/** @odoo-module */
import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { CustomConfirmationDialog } from "./custom_confirmation_dialog";

/**
 * Este módulo mejora el comportamiento de auto-guardado de Odoo
 * añadiendo diálogos de confirmación con más opciones
 */
patch(FormController.prototype, 'auto_save_extend.FormController', {
        setup() {
        this._super(...arguments);
        this.dialogService = useService("dialog");
        this.stayOnPage = false;
        this._processingPagerUpdate = false;

        // Registrar el evento beforeUnload para capturar el cierre de pestaña/navegador
        this._registerBeforeUnloadHandler();

        // No usar useSetupView para evitar conflictos con el método original
        // Los métodos beforeLeave y beforeUnload se sobrescriben directamente
    },

    /**
     * Registra el handler para el evento beforeUnload del navegador
     */
    _registerBeforeUnloadHandler() {
        // Eliminar handler previo si existe
        if (this._beforeUnloadHandler) {
            window.removeEventListener('beforeunload', this._beforeUnloadHandler);
        }

        // Crear nuevo handler
        this._beforeUnloadHandler = (ev) => {
            console.log('🌐 window beforeunload event triggered');
            // Forzar que se procesen los cambios pendientes antes de verificar
            this._processActiveFieldChanges();
            return this.beforeUnload(ev);
        };

        // Registrar el handler
        window.addEventListener('beforeunload', this._beforeUnloadHandler);
        console.log('🌐 beforeUnload handler registered');
    },

    /**
     * Procesa los cambios en el campo activo para asegurar que se marque como dirty
     */
    _processActiveFieldChanges() {
        try {
            let activeElement = document.activeElement;

            // Handle fields inside iframes (e.g., rich text editors for 'notes' fields)
            if (activeElement && activeElement.tagName === 'IFRAME' && activeElement.contentDocument) {
                activeElement = activeElement.contentDocument.activeElement || activeElement.contentDocument.body;
            }

            if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA' || activeElement.isContentEditable)) {
                // Forcing blur and change events to ensure the model is updated
                // before the beforeunload event completes.
                activeElement.blur();
                activeElement.dispatchEvent(new Event('change', { bubbles: true, cancelable: false }));
                activeElement.dispatchEvent(new Event('input', { bubbles: true, cancelable: false }));
                console.log('🔄 Processed active field changes on:', activeElement.tagName);
            }
        } catch (error) {
            // Avoid crashing the unload event, just log the error
            console.warn('🔄 Error processing active field changes:', error);
        }
    },

    _getUnsavedMessage() {
        const lang = this.env.services.user.lang || 'en_US';

        if (lang.startsWith('ca')) {
            return "Hi ha modificacions pendents de desar. Estàs segur que vols sortir?";
        } else if (lang.startsWith('es')) {
            return "Hay modificaciones sin guardar. ¿Estás seguro que quieres salir?";
        } else {
            return "You have unsaved changes. Are you sure you want to leave?";
        }
    },

        _getDialogMessages(isNavigation = false) {
        const lang = this.env.services.user.lang || 'en_US';

        if (isNavigation) {
            // Mensajes para navegación entre registros (paginador)
            if (lang.startsWith('ca')) {
                return {
                    title: "Modificacions pendents",
                    body: "Hi ha modificacions pendents de desar. Què vols fer abans de canviar de registre?",
                    saveLabel: "Guardar i continuar",
                    discardLabel: "Descartar i continuar",
                    stayLabel: "Romandre aquí"
                };
            } else if (lang.startsWith('es')) {
                return {
                    title: "Modificaciones sin guardar",
                    body: "Hay modificaciones sin guardar. ¿Qué quieres hacer antes de cambiar de registro?",
                    saveLabel: "Guardar y continuar",
                    discardLabel: "Descartar y continuar",
                    stayLabel: "Permanecer aquí"
                };
            } else {
                return {
                    title: "Unsaved Changes",
                    body: "You have unsaved changes. What do you want to do before changing record?",
                    saveLabel: "Save and Continue",
                    discardLabel: "Discard and Continue",
                    stayLabel: "Stay Here"
                };
            }
        } else {
            // Mensajes para salir de la vista
            if (lang.startsWith('ca')) {
                return {
                    title: "Modificacions pendents",
                    body: "Hi ha modificacions pendents de desar, què vols fer?",
                    saveLabel: "Sortir i desar",
                    discardLabel: "Sortir sense desar",
                    stayLabel: "Romandre aquí"
                };
            } else if (lang.startsWith('es')) {
                return {
                    title: "Modificaciones sin guardar",
                    body: "Hay modificaciones sin guardar, ¿qué quieres hacer?",
                    saveLabel: "Salir y guardar",
                    discardLabel: "Salir sin guardar",
                    stayLabel: "Permanecer aquí"
                };
            } else {
                return {
                    title: "Unsaved Changes",
                    body: "You have unsaved changes, what do you want to do?",
                    saveLabel: "Save and Leave",
                    discardLabel: "Leave without Saving",
                    stayLabel: "Stay Here"
                };
            }
        }
    },

        async _askConfirmation(isNavigation = false) {
        if (!this.model.root.isDirty) {
            return true;
        }

        // Debug: identificar desde dónde se llama
        console.log('🔍 _askConfirmation called with isNavigation:', isNavigation);
        console.log('🔍 Call stack:', new Error().stack);

        const messages = this._getDialogMessages(isNavigation);
        let userChoice = null;

        return new Promise((resolve) => {
            this.dialogService.add(CustomConfirmationDialog, {
                title: messages.title,
                body: messages.body,
                confirmLabel: messages.saveLabel,
                cancelLabel: messages.discardLabel,
                stayLabel: messages.stayLabel,
                confirm: async () => {
                    userChoice = 'save';
                    const saved = await this.model.root.save({
                        stayInEdition: true,
                        useSaveErrorDialog: true
                    });
                    resolve(saved !== false);
                },
                cancel: async () => {
                    userChoice = 'discard';
                    await this.model.root.discard();
                    resolve(true);
                },
                stayHere: () => {
                    userChoice = 'stay';
                    this.stayOnPage = true;
                    resolve(false);
                }
                // No incluir close callback ya que no hay X para cerrar
            });
        });
    },

        /**
     * Sobrescribir el método onPagerUpdate para usar nuestro diálogo personalizado
     */
        async onPagerUpdate(params) {
        console.log('📄 onPagerUpdate called');

        // Prevenir recursión infinita
        if (this._processingPagerUpdate) {
            console.log('📄 onPagerUpdate: already processing, returning');
            return;
        }

        this._processingPagerUpdate = true;

        try {
            await this.model.root.askChanges(); // ensures that isDirty is correct
            let canProceed = true;

            if (this.model.root.isDirty) {
                console.log('📄 onPagerUpdate: model is dirty, asking confirmation');
                // Usar confirmación de navegación (isNavigation = true)
                canProceed = await this._askConfirmation(true);

                // Si se seleccionó "Permanecer aquí", no proceder
                if (this.stayOnPage) {
                    this.stayOnPage = false;
                    console.log('📄 onPagerUpdate: staying on page');
                    return;
                }
            }

            if (canProceed) {
                console.log('📄 onPagerUpdate: proceeding with navigation');
                return this.model.load({ resId: params.resIds[params.offset] });
            }
        } finally {
            this._processingPagerUpdate = false;
        }
    },

    /**
     * Método que se llama antes de abandonar la vista
     * Intercepta el comportamiento original y usa nuestro diálogo personalizado
     */
    async beforeLeave() {
        // If leaving through the main menu, the menu_service patch handles confirmation
        if (this.isLeavingViaMenu) {
            return this._super(...arguments);
        }
        console.log('🚪 beforeLeave called (patched)');

        if (this.stayOnPage) {
            this.stayOnPage = false;
            console.log('🚪 beforeLeave: staying on page flag was set');
            return false;
        }

        if (this.model.root.isDirty) {
            console.log('🚪 beforeLeave: model is dirty, asking confirmation');
            const proceed = await this._askConfirmation();

            // Si se seleccionó "Permanecer aquí", no abandonar
            if (this.stayOnPage) {
                this.stayOnPage = false;
                console.log('🚪 beforeLeave: staying on page after confirmation');
                return false;
            }

            console.log('🚪 beforeLeave: proceed =', proceed);
            // Si el usuario eligió guardar o descartar, ya se hizo en _askConfirmation
            // No llamar al _super porque ya manejamos el guardado/descarte
            return proceed;
        }

        console.log('🚪 beforeLeave: model is clean, calling super');
        // Si no hay cambios, llamar al comportamiento original
        return this._super(...arguments);
    },

            /**
     * Detecta si hay cambios pendientes (después de procesar campos activos)
     */
    _hasUnsavedChanges() {
        // Después de procesar los campos activos, verificar si el modelo está dirty
        if (this.model && this.model.root && this.model.root.isDirty) {
            console.log('🔄 Model is dirty, has unsaved changes');
            return true;
        }

        console.log('🔄 No unsaved changes detected');
        return false;
    },

    /**
     * Método que se llama cuando el usuario recarga o cierra la página
     * Solo se activa si hay cambios pendientes (Punto 3 corregido)
     */
    beforeUnload(ev) {
        console.log('🔄 beforeUnload called, checking for changes...');

        const hasChanges = this._hasUnsavedChanges();

        if (hasChanges) {
            console.log('🔄 beforeUnload: changes detected, showing warning');
            const message = this._getUnsavedMessage();

            // Establecer tanto preventDefault como returnValue para máxima compatibilidad
            ev.preventDefault();
            ev.returnValue = message;

            // Algunos navegadores requieren que se retorne el mensaje
            return message;
        }

        console.log('🔄 beforeUnload: no changes, allowing navigation');
        // Si no hay cambios, no hacer nada (permitir recarga sin aviso)
        return undefined;
    },

    /**
     * Método de limpieza para remover event listeners
     */
    willUnmount() {
        if (this._beforeUnloadHandler) {
            window.removeEventListener('beforeunload', this._beforeUnloadHandler);
            console.log('🌐 beforeUnload handler removed');
        }

        if (this._super.willUnmount) {
            this._super(...arguments);
        }
    }
});
