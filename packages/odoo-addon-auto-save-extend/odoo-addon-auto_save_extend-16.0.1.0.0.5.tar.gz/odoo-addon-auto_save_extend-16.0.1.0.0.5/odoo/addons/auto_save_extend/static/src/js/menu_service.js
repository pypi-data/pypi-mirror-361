/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { menuService } from "@web/webclient/menus/menu_service";

/**
 * This patch intercepts menu navigation to provide a custom confirmation dialog
 * when there are unsaved changes in a form or list view.
 *
 * It coordinates with the form and list controllers using the `isLeavingViaMenu` flag
 * to avoid showing duplicate dialogs.
 */
patch(menuService, "auto_save_extend.menuService", {
    start(env, { user }) {
        const originalStart = this._super.bind(this, ...arguments);

        // The actual menu service that will be returned
        const service = {
            ...originalStart(),

            /**
             * Overridden `selectMenu` method to handle unsaved changes.
             */
            selectMenu: async function(menu) {
                const actionService = env.services.action;
                const currentController = actionService.currentController;

                // Check if the current controller is a form or list view with unsaved changes
                const hasUnsavedChanges = this._hasUnsavedChanges(currentController);

                if (hasUnsavedChanges) {
                    // Set a flag on the controller to indicate that we are handling the confirmation
                    currentController.component.isLeavingViaMenu = true;

                    // Ask for confirmation before proceeding
                    const proceed = await currentController.component._askConfirmation();

                    // Reset the flag after confirmation
                    currentController.component.isLeavingViaMenu = false;

                    // If the user chose to stay, prevent navigation
                    if (!proceed || currentController.component.stayOnPage) {
                        currentController.component.stayOnPage = false; // Reset stay flag
                        return; // Stop navigation
                    }
                }

                // If no unsaved changes or if the user chose to proceed, call the original method
                return originalStart().selectMenu.call(this, menu);
            },

            /**
             * Helper method to check for unsaved changes in the current controller.
             * @param {Object} controller - The current controller from the action service.
             * @returns {boolean} - True if there are unsaved changes, false otherwise.
             */
            _hasUnsavedChanges(controller) {
                if (!controller || !controller.component || !controller.component.model) {
                    return false;
                }

                // For Form Views
                if (controller.component.model.root && typeof controller.component.model.root.isDirty === 'boolean') {
                    return controller.component.model.root.isDirty;
                }

                // For List Views (and other editable views)
                if (controller.component.model.root && controller.component.model.root.editedRecord) {
                    return true;
                }

                return false;
            }
        };

        return service;
    }
});