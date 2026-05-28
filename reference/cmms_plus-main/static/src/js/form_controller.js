/* @odoo-module */

import { patch } from '@web/core/utils/patch';
import { FormController } from '@web/views/form/form_controller';
import { onMounted, onPatched } from '@odoo/owl';
import { useBus,useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
patch(FormController.prototype, {
    setup() {
        super.setup();

        this.ui = useService("ui");
        this.orm = useService("orm");
        this.dialog = useService("dialog");

        const addStatusBadge = () => {
            if (!this.model.config.context.cmms_quick_form) return;

            const jigStatus = this.model.root.data.jig_status_qc;
            const badgeConfig = {
                "not_yet": { text: "Not Yet", class: "badge-not-yet" },
                "ok": { text: "  OK   ", class: "badge-ok" },
                "ng": { text: "NG", class: "badge-ng" },
            };

           

            const config = badgeConfig[jigStatus];
            if (config) {
                const formSheet = document.querySelector(".o_form_sheet");
                if (formSheet) {
                    // Remove existing badge
                    const existingBadge = formSheet.querySelector(".cmms-form-status-badge");
                    if (existingBadge) existingBadge.remove();

                     $('.o_form_sheet').css({'overflow': 'hidden'})

                    // Add new badge
                    const badge = document.createElement("div");
                    badge.className = `cmms-form-status-badge ${config.class}`;
                    badge.textContent = config.text;
                    formSheet.appendChild(badge);
                }
            }
        };

        onMounted(addStatusBadge);
        onPatched(addStatusBadge);
    },

    
    /**
     * @override
     */
    getStaticActionMenuItems() {
        const { activeActions } = this.archInfo;
        

        if (!this.model.config.context.from_cmms_quick_form)
        {
            
             return super.getStaticActionMenuItems()
        }
           
        else {
                
                return {
                // duplicate: {
                //     isAvailable: () => activeActions.create && activeActions.duplicate,
                //     sequence: 30,
                //     icon: "fa fa-clone",
                //     description: _t("Duplicate"),
                //     callback: () => this.duplicateRecord(),
                // },
                // unarchive: {
                //     isAvailable: () => !this.model.root.data.active,
                //     sequence: 20,
                //     icon: "fa fa-history",
                //     description: _t("Restore"),
                //     callback: () => this.model.root.unarchive(),
                // },
                delete: {
                    isAvailable: () =>
                        activeActions.delete && !this.model.root.isNew,
                    sequence: 40,
                    icon: "fa fa-trash-o",
                    description: "Delete",
                    callback: async () => {
                       
                       this.dialog.add(ConfirmationDialog, {
                                title: "Delete",
                                body: (
                                    "Are you sure ?"
                                ),

                                confirmLabel: ("Move to trash"),
                                confirm: async () => {
                                    await this.orm.call(
                                        this.props.resModel,
                                        "action_archive",
                                        [this.model.root.resId]
                                    );

                                   this.ui.jtree && this.ui.jtree._reloadTree()
                                   this.env.config.historyBack();

                                },
                                cancel: () => {},

                            });


                         //   console.log(this.ui,'..............')
                            // this.ui.jtree._reloadTree()
                    },
                    skipSave: true,
                },
            };
        } 
    }

  

});
