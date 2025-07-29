/** @odoo-module */

import { Dialog } from "@web/core/dialog/dialog";
import { _lt } from "@web/core/l10n/translation";
import { useChildRef } from "@web/core/utils/hooks";

import { Component } from "@odoo/owl";

export class CustomConfirmationDialog extends Component {
    setup() {
        // No registrar close handler ya que no hay X para cerrar
        this.modalRef = useChildRef();
        this.isConfirmedOrCancelled = false; // ensures we do not confirm and/or cancel twice
    }

    async _cancel() {
        if (this.isConfirmedOrCancelled) {
            return;
        }
        this.isConfirmedOrCancelled = true;
        this.disableButtons();
        if (this.props.cancel) {
            try {
                await this.props.cancel();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
    }

    async _confirm() {
        if (this.isConfirmedOrCancelled) {
            return;
        }
        this.isConfirmedOrCancelled = true;
        this.disableButtons();
        if (this.props.confirm) {
            try {
                await this.props.confirm();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
    }

    async _stayHere() {
        if (this.isConfirmedOrCancelled) {
            return;
        }
        this.isConfirmedOrCancelled = true;
        this.disableButtons();
        if (this.props.stayHere) {
            try {
                await this.props.stayHere();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
    }

    disableButtons() {
        if (!this.modalRef.el) {
            return; // safety belt for stable versions
        }
        for (const button of [...this.modalRef.el.querySelectorAll(".modal-footer button")]) {
            button.disabled = true;
        }
    }
}

CustomConfirmationDialog.template = "auto_save_extend.CustomConfirmationDialog";
CustomConfirmationDialog.components = { Dialog };
CustomConfirmationDialog.props = {
    close: Function,
    title: {
        validate: (m) => {
            return (
                typeof m === "string" || (typeof m === "object" && typeof m.toString === "function")
            );
        },
        optional: true,
    },
    body: String,
    confirm: { type: Function, optional: true },
    confirmLabel: { type: String, optional: true },
    cancel: { type: Function, optional: true },
    cancelLabel: { type: String, optional: true },
    stayHere: { type: Function, optional: true },
    stayLabel: { type: String, optional: true },
};

CustomConfirmationDialog.defaultProps = {
    confirmLabel: _lt("Save"),
    cancelLabel: _lt("Discard"),
    stayLabel: _lt("Stay Here"),
    title: _lt("Unsaved Changes"),
};
