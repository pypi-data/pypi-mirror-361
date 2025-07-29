/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { CustomConfirmationDialog } from "./custom_confirmation_dialog";

/**
 * Este módulo mejora el comportamiento de auto-guardado de Odoo
 * añadiendo diálogos de confirmación con más opciones para vistas de lista
 */
patch(ListController.prototype, 'auto_save_extend.ListController', {
    setup() {
        this._super(...arguments);
        this.dialogService = useService("dialog");
        this.stayOnPage = false;

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
            console.log('🌐 window beforeunload event triggered (list)');
            // Forzar que se procesen los cambios pendientes antes de verificar
            this._processActiveFieldChanges();
            return this.beforeUnload(ev);
        };

        // Registrar el handler
        window.addEventListener('beforeunload', this._beforeUnloadHandler);
        console.log('🌐 beforeUnload handler registered (list)');
    },

    /**
     * Procesa los cambios en el campo activo para asegurar que se marque como dirty
     */
    _processActiveFieldChanges() {
        try {
            let activeElement = document.activeElement;

            // Handle fields inside iframes (e.g., rich text editors)
            if (activeElement && activeElement.tagName === 'IFRAME' && activeElement.contentDocument) {
                activeElement = activeElement.contentDocument.activeElement || activeElement.contentDocument.body;
            }

            if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA' || activeElement.isContentEditable)) {
                // Forcing blur and change events to ensure the model is updated
                activeElement.blur();
                activeElement.dispatchEvent(new Event('change', { bubbles: true, cancelable: false }));
                activeElement.dispatchEvent(new Event('input', { bubbles: true, cancelable: false }));
                console.log('🔄 Processed active field changes on (list):', activeElement.tagName);
            }
        } catch (error) {
            // Avoid crashing the unload event, just log the error
            console.warn('🔄 Error processing active field changes (list):', error);
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

    _getDialogMessages() {
        const lang = this.env.services.user.lang || 'en_US';

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
                title: _t("Unsaved Changes"),
                body: _t("You have unsaved changes, what do you want to do?"),
                saveLabel: _t("Save and Leave"),
                discardLabel: _t("Leave without Saving"),
                stayLabel: _t("Stay Here")
            };
        }
    },

        async _askConfirmation() {
        if (!this.model.root.editedRecord) {
            return true;
        }

        const messages = this._getDialogMessages();
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
                    await this.model.root.save();
                    resolve(true);
                },
                cancel: async () => {
                    userChoice = 'discard';
                    await this.onClickDiscard();
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
     * Método que se llama antes de abandonar la vista
     * Intercepta el comportamiento original y usa nuestro diálogo personalizado
     */
    async beforeLeave() {
        // If leaving through the main menu, the menu_service patch handles confirmation
        if (this.isLeavingViaMenu) {
            return this._super(...arguments);
        }
        if (this.stayOnPage) {
            this.stayOnPage = false;
            return false;
        }

        if (this.model.root.editedRecord) {
            const proceed = await this._askConfirmation();
            if (this.stayOnPage) {
                this.stayOnPage = false;
                return false;
            }
            // Si el usuario eligió guardar o descartar, ya se hizo en _askConfirmation
            // No llamar al _super porque ya manejamos el guardado/descarte
            return proceed;
        }

        // Si no hay cambios, llamar al comportamiento original
        return this._super(...arguments);
    },

    /**
     * Detecta si hay cambios pendientes en la vista de lista
     */
    _hasUnsavedChanges() {
        // Después de procesar los campos activos, verificar si hay registro editado
        if (this.model.root.editedRecord) {
            console.log('🔄 List has edited record, has unsaved changes');
            return true;
        }

        console.log('🔄 No unsaved changes detected (list)');
        return false;
    },

    /**
     * Método que se llama cuando el usuario recarga o cierra la página
     * Solo se activa si hay cambios pendientes
     */
    beforeUnload(ev) {
        console.log('🔄 beforeUnload called (list), checking for changes...');

        const hasChanges = this._hasUnsavedChanges();

        if (hasChanges) {
            console.log('🔄 beforeUnload (list): changes detected, showing warning');
            const message = this._getUnsavedMessage();

            // Establecer tanto preventDefault como returnValue para máxima compatibilidad
            ev.preventDefault();
            ev.returnValue = message;

            // Algunos navegadores requieren que se retorne el mensaje
            return message;
        }

        console.log('🔄 beforeUnload (list): no changes, allowing navigation');
        // Si no hay cambios, no hacer nada (permitir recarga sin aviso)
        return undefined;
    },

    /**
     * Método de limpieza para remover event listeners
     */
    willUnmount() {
        if (this._beforeUnloadHandler) {
            window.removeEventListener('beforeunload', this._beforeUnloadHandler);
            console.log('🌐 beforeUnload handler removed (list)');
        }

        if (this._super.willUnmount) {
            this._super(...arguments);
        }
    }
});
