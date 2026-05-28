/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { useBus, useService } from "@web/core/utils/hooks";



export class CMMSKanbanController extends KanbanController {
    static template = "cmms_plus.CMMSKanbanView";

      setup() {
        super.setup();
        this.ui= useService('ui')
        this.orm = useService('orm')
        this.actionService = useService("action");
        this.state={}


    
        // 👇 Gán controller vào props của renderer
         this.ui.controller = this;

         
    }

    
    async callEvents(payload) {
        // if (payload.type=="jigtype") {
        //     const jig_type_id = payload.data;
        //     alert(jig_type_id)
        // }
    }

     /**
     * Mở form view cmms_plus_equipment_view_form (model: product.product)
     * trong chế độ tạo mới (create mode)
     */
     async createJigRecord() {
                    // 🟢 Gọi Python method để lấy view_id
                   const view_id = await this.orm.call(
                            "product.product",
                            "getJigFormViewId",
                            [[]] 
                        );
                  

                    // 🟢 Mở form view đã chỉ định
                    await this.actionService.doAction({
                        type: "ir.actions.act_window",
                        res_model: "product.product",
                        name: "Create Equipment",
                        views: [[view_id, "form"]],
                        view_mode: "form",
                        target: "current",
                        context: {
                            is_jig: true,
                        },
                    });
    }

    async createMachineRecord() {
                    // 🟢 Gọi Python method để lấy view_id
                   const view_id = await this.orm.call(
                            "product.product",
                            "getMachineFormViewId",
                            [[]] 
                        );
                  

                    // 🟢 Mở form view đã chỉ định
                    await this.actionService.doAction({
                        type: "ir.actions.act_window",
                        res_model: "product.product",
                        name: "Create Machine",
                        views: [[view_id, "form"]],
                        view_mode: "form",
                        target: "current",
                        context: {
                            is_machine: true,
                        },
                    });
    }

    async refreshTree() {
        const { root } = this.model;
        await this.actionService.doAction("cmms_plus.create_from_template_action", { additionalContext: root.context });
    }
};
