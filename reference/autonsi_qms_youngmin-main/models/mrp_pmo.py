from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError

from odoo.fields import Datetime


class MrpPmo(models.Model):
    _inherit = 'mrp.pmo'

    def button_pass_pqc(self):
        res = super().button_pass_pqc()

        selected_ids = self.env.context.get('selected_ids')
        if not selected_ids:
            raise ValidationError(_("No Manufacturing Orders selected for PQC Pass."))
        operation_ids = self.env['mrp.production'].browse(selected_ids)
        # form_id = self.env.ref("autonsi_qms.item_qc_form_pqc_cutting")
        form = self.env["mes.qc_form"].search([('form_type', '=', 'pqc'), ('state', '=', 'confirm'), ('process_ids', 'in', self.env.ref('autonsi_standard_youngmin.common_record_process_020_fabric_cutting').id)], order='confirm_date desc', limit=1)
        if not form:
            raise UserError(_("There is no confirmed QC form of type 'pqc fabric cutting'."))
        form_id = form

        for record in operation_ids:
            record.pqc_cut_form_id = form_id
            history_vals = {
                'name': form_id.name,
                'mes_qc_form_id': form_id.id,
                'mrp_production_id': record.id,

                'process_id': self.env.ref('autonsi_standard_youngmin.common_record_process_020_fabric_cutting').id,

                'process': "Cutting",
                'qty_sampling': record.product_qty,
                'defect_ratio': 0.0,
                'lot_id': record.lot_producing_id.id,
                'ok_qty': record.product_qty,
                'ng_qty': 0.0,
                'type_roll': "first",

                'staff_id': record.env.user.id,
                'check_date': Datetime.now(),
                'staff_name': record.env.user.name,

            }
            history = self.env["mes.qc_form.history"].create(history_vals)
            history.form_type = history.mes_qc_form_id.form_type

            for item in form_id.prepare_check_list_data():
                line_vals = {
                    'history_id': history.id,
                    'mes_qc_form_question_id': item.get('id'),
                    # 'X1': item.get('X1'),
                    # 'X2': item.get('X2'),
                    # 'X3': item.get('X3'),
                    # 'X4': item.get('X4'),
                    # 'X5': item.get('X5'),
                    'result': item.get('result'),
                    'remark': item.get('remark'),
                }
                self.env["mes.qc_form.history.line"].create(line_vals)

        return res

