/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService, useChildRef } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
const actionRegistry = registry.category("actions");
import { _t } from '@web/core/l10n/translation';
import { download } from "@web/core/network/download";

class QMSQuestionPQCDialog extends Component {
    static template = "qms_question_pqc_dialog_template";
    static components = { Dialog };
   
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.action = useService("action");
        this.data = useState(this.env.dialogData);
        this.dialogRef = useChildRef()
       
        const { context } = this.props;

        this.state = useState({
            "title": context.title || "",
            'category_material': context.category_material || "",
            'supplier': context.supplier || "",
            'material_code': context.material_code || "",
            'material_name': context.material_name || "",
            'line_no': context.line_no || "",
            'lot': context.lot || "",
            'qty_uom': context.qty_uom || "",
            'isHistory': context.isHistory,
            'isPreview': context.isPreview,
            'shop_floor': context.shop_floor,
            'type_roll': context.type_roll || "first",

            'doc_list': context.doc_list || [],
            'staff_id': context.staff_id ?? context.employee_list[0].id,
            'staff_name': context.staff_name || "",
            'final_result': context.final_result || "OK",
            'check_date': context.check_date ? new Date(context.check_date + "Z").toLocaleString('sv-SE', { hour12: false }).replace('T', ' ').split('.')[0] : new Date().toLocaleString('sv-SE', { hour12: false }).replace('T', ' ').split('.')[0],
            'check_list': context.check_list || [],
            'form_id': context.form_id,
            'mrp_production_id': context.mrp_production_id,
            'qty': Math.round(Number(context.qty ?? 1.0) * 100) / 100,

            'process': context.process,
            'process_id': context.process_id,
            'qty_sampling': context.qty_sampling || 1.0,
            'defect_ratio': context.defect_ratio ?? 0.0,
            'ok_qty': context.ok_qty ?? context.qty ?? 1.0,
            'ng_qty': context.ng_qty ?? 0.0,


        });
        this.state.columns = this.props.context.columns.map(col => ({
            ...col,
            title: _t(col.title) // Dịch title
        }));
        this.tableRef = useRef("qmsTable");
        const self = this
        onMounted(() => {
            document.querySelectorAll('.modal-header')[1]?.classList.add('justify-content-center');
            const dialog = this.dialogRef.el;
            // find '.modal-dialog'
            const modalDialog = dialog.querySelector('.modal-dialog');
            // remove modal-xl
            modalDialog.classList.remove('modal-xl');
            // add modal-lg
            modalDialog.classList.add('modal-fs');
            // add width 100%
            modalDialog.style.width = '100%';
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

    _onChangeQtySampling(ev) {
        const value = Number(ev.target.value);

        if (isNaN(value)) {
            this.state.qty_sampling = 1.0;
        }

        if (value > this.state.qty) {
            this.state.qty_sampling = this.state.qty;
        } else if (value < 1.0) {
            this.state.qty_sampling = 1.0;
        } else {
            this.state.qty_sampling = value;
        }

        this.state.defect_ratio = (this.state.ng_qty / this.state.qty_sampling) * 100.0
    }

    _onChangeNGQty(ev) {
        const value = Number(ev.target.value);

        if (isNaN(value)) {
            this.state.ng_qty = 0.0;
        }

        if (value > this.state.qty_sampling) {
            this.state.ng_qty = this.state.qty_sampling;
        }
        else if (value < 0.0) {
            this.state.ng_qty = 0.0;
        }
        else {
            this.state.ng_qty = value;
        }


        this.state.ok_qty = (this.state.qty - this.state.ng_qty);
        this.state.defect_ratio = (this.state.ng_qty / this.state.qty_sampling) * 100.0
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
            url: "/pms/print/pqc",
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

            await this.orm.call('mes.qc_form.history', 'create_history_pqc', [], {inspectionData: this.state});

            this.env.bus.trigger("Reload:StockMoveLine", {})

            this.props.close();

        // } catch (error) {
        //     console.error('Error saving data:', error);
        //     // this.notification.add("Error saving data: " + error.message, { type: "danger" });
        //     this.notification.add("Error saving data: You must provide the ng quantity before saving.", { type: "danger" });
        // } finally {
        //     this.state.isLoading = false;
        // }
    }
}
// Register client action
function mesQcPreviewPQCAction(env, action) {
    const dialog = env.services.dialog;

    const test = dialog.add(QMSQuestionPQCDialog, {
        context: action.context,
    });
    console.log('test', test)
}


actionRegistry.add("qms_question_pqc_action", mesQcPreviewPQCAction);