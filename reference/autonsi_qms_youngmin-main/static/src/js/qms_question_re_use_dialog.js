/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
const actionRegistry = registry.category("actions");
import { _t } from '@web/core/l10n/translation';
import { download } from "@web/core/network/download";

class QMSQuestionREUSEDialog extends Component {
    static template = "qms_question_re_use_dialog_template";
    static components = { Dialog };
   
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.action = useService("action");
        this.data = useState(this.env.dialogData);
       
        const { context } = this.props;

        console.log("Props:" + this.props)
        console.log(context.qty)

        this.state = useState({
            "title": context.title || "",
            'category_material': context.category_material || "",
            'supplier': context.supplier || "",
            'material_code': context.material_code || "",
            'material_name': context.material_name || "",
            'lot': context.lot || "",
            'qty_uom': context.qty_uom || "",
            'isHistory': context.isHistory,
            'isPreview': context.isPreview,
            'type_roll': context.type_roll,
            'item_group': context.item_group,
            'remaining_days': context.remaining_days,
            'life_days': context.life_days,

            'doc_list': context.doc_list || [],
            'staff_id': context.staff_id ?? context.employee_list[0].id,
            'staff_name': context.staff_name || "",
            'final_result': context.final_result || "OK",
            'check_date': context.check_date ? new Date(context.check_date + "Z").toLocaleString('sv-SE', { hour12: false }).replace('T', ' ').split('.')[0] : new Date().toLocaleString('sv-SE', { hour12: false }).replace('T', ' ').split('.')[0],
            'check_list': context.check_list || [],
            'form_id': context.form_id,
            'stock_quant_id': context.stock_quant_id,
            'qty': Math.round(Number(context.qty ?? 0) * 100) / 100
        });
        this.state.columns = this.props.context.columns.map(col => ({
            ...col,
            title: _t(col.title) // Dịch title
        }));
        this.tableRef = useRef("qmsTable");
        onMounted(() => {
            document.querySelectorAll('.modal-header')[1]?.classList.add('justify-content-center');
        })
    }

    async action_view_file(ev) {
        const id = ev.target.dataset.id;
        try {
            const result = await this.orm.call(
                'mes.qc_doc',
                'action_view_file',
                [parseInt(id)],
                {}
            );

            if (result) {
                this.action.doAction(result);
            }

        } catch (error) {
            console.error('Error saving data:', error);
            // this.notification.add("Error saving data: You must provide the final result before saving.", { type: "danger" });
        }
    }

    formatDateForInput(dateValue) {
        if (!dateValue) return "";
        
        // Nếu là string (format YYYY-MM-DD) - trả về trực tiếp
        if (typeof dateValue === 'string') {
            return dateValue;
        }
        
        // Nếu là Date object - convert về YYYY-MM-DD
        if (dateValue instanceof Date) {
            return dateValue.toISOString().split('T')[0];
        }
        
        // Nếu là moment object (một số version cũ)
        if (dateValue.format) {
            return dateValue.format('YYYY-MM-DD');
        }
        
        return dateValue;
    }

    async downloadExcel() {
        await download({
            url: "/pms/print/re_use",
            data: {
                state: JSON.stringify(this.state),
            },
        });
    }


    onStaffChange(ev) {
        const selectedId = parseInt(ev.target.value);
        const employee = this.props.context.employee_list.find(e => e.id === selectedId);

        if (employee) {
            this.state.staff_id = employee.id;
            this.state.staff_name = employee.name;
        } else {
            this.state.staff_id = null;
            this.state.staff_name = "";
        }
    }

    onCellChange(rowIndex, columnField, value) {
        if (this.state.isPreview) return;
        const row = this.state.check_list[rowIndex];
        if (row) {
            row[columnField] = value;
        }
    }


    async saveData() {
        // try {
            console.log(this.state)
            if (this.state.isPreview) return
            this.state.isLoading = true;

            await this.orm.call('mes.qc_form.history', 'create_history_re_use', [], {inspectionData: this.state});

            this.env.bus.trigger("Reload:StockMoveLine", {})

            this.props.close();

        // } catch (error) {
        //     console.error('Error saving data:', error);
        //     // this.notification.add("Error saving data: " + error.message, { type: "danger" });
        //     this.notification.add("Error saving data: You must provide the final result before saving.", { type: "danger" });
        // } finally {
        //     this.state.isLoading = false;
        // }
    }
}
// Register client action
function mesQcPreviewREUSEAction(env, action) {
    const dialog = env.services.dialog;

    dialog.add(QMSQuestionREUSEDialog, {
        context: action.context,
    });
}


actionRegistry.add("qms_question_re_use_action", mesQcPreviewREUSEAction);