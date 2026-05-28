from odoo import api, fields, models, _

from odoo.exceptions import UserError


class PickingExpireWizardLine(models.Model):
    _inherit = "picking.wizard.line"

    pallet_qc_form_id = fields.Many2one('mes.qc_form', string='Pallet Form')

    def button_pallet_qc(self):
        for record in self:
            history_id = self.env["mes.qc_form.history"].search([('picking_wizard_id', '=', record.id)])
            if history_id:
                return history_id.action_open_pallet_qc_form_history()
            res = super().button_pallet_qc()

            form_id = self.env["mes.qc_form"].search(
                [('form_type', '=', 'pallet_qc'), ('state', '=', 'confirm')],
                order='confirm_date desc', limit=1)
            if not form_id:
                raise UserError(_("There is no confirmed QC form of type 'jig new check'."))
            record.pallet_qc_form_id = form_id

            context_data = {
                'title': record.pallet_qc_form_id.name,
                'pallet_no': record.pallet_no_id.name,
                'project_code': record.product_id.project_id.name,
                'material_code': record.product_id.code,
                'material_name': record.product_id.name,
                'lot': record.total_lot_qty,
                'qty_uom': record.product_id.uom_id.name,
                'isHistory': False,
                'isPreview': False,

                'employee_list': record.pallet_qc_form_id.get_employee_list(),
                'self_id': record.pallet_qc_form_id.get_self_id(),
                'doc_list': record.pallet_qc_form_id.get_doc_ids_list(),
                'staff_id': record.pallet_qc_form_id.env.user.id,
                'staff_name': record.pallet_qc_form_id.env.user.name,
                # 'check_date': "",
                # 'final_result': "OK",
                'columns': record.pallet_qc_form_id.get_pqc_column_config(),
                'check_list': record.pallet_qc_form_id.prepare_check_list_data(),
                'form_id': record.pallet_qc_form_id.id,
                'picking_wizard_id': record.id,
                'qty': record.total_qty,

            }

            tag = "qms_question_pallet_qc_action"
            name = _(f"QMS Pallet QC - {record.pallet_qc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }
