/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";


export class HistoryController extends ListController {
    setup() {
        super.setup();
    }
    async openRecord(record) {
        console.log(record)
        var action = "action_open_iqc_form_history"
        if (record.data.form_type == "iqc")
            action = "action_open_iqc_form_history"
        else if (record.data.form_type == "pqc")
            action = "action_open_pqc_form_history"
        else if (record.data.form_type == "oqc")
            action = "action_open_oqc_form_history"
        else if (record.data.form_type == "item_qc")
            action = "action_open_item_qc_form_history"
        else if (record.data.form_type == "pallet_qc")
            action = "action_open_pallet_qc_form_history"
        const result = await this.env.services.orm.call('mes.qc_form.history',
            action,
            [record._config.resId],
            {}
        )
        this.env.services.action.doAction(
            result
        );
    }
}

export const formHistory = {
    ...listView,
    Controller: HistoryController,
};

registry.category("views").add("history_controller", formHistory);
