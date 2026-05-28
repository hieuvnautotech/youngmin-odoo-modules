from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    jig_form_id = fields.Many2one('mes.qc_form', string='JIG Form')

    def button_jig_check(self):
        for record in self:
            history_id = self.env["mes.qc_form.history"].search([('mrp_workorder_id', '=', record.id)])
            if history_id and record.jig_status == 'done':
                return history_id.action_open_jig_form_history()
            res = super().button_jig_check()

            # record.jig_form_id = self.env.ref("autonsi_qms.item_qc_form_pqc_jig").id
            form_id = self.env["mes.qc_form"].search([('form_type', '=', 'jig'), ('state', '=', 'confirm'), ('jig_state', '=', 'jig')], order='confirm_date desc', limit=1)
            if not form_id:
                raise UserError(_("There is no confirmed QC form of type 'jig check'."))
            record.jig_form_id = form_id

            context_data = {
                'title': record.jig_form_id.name,
                'product_code': record.jig_code.jig_product_id.code,
                'supplier': record.jig_code.equip_partner_id.name,
                'jig_code': record.jig_code.asset_code,
                'jig_name': record.jig_code.name,
                'process': record.jig_code.process_id.name,
                'rev': record.jig_code.rev,
                'remark': record.jig_code.remark,
                'create_date': record.create_date,
                'isHistory': False,
                'isPreview': False,

                'employee_list': record.jig_form_id.get_employee_list(),
                'self_id': record.jig_form_id.get_self_id(),
                'doc_list': record.jig_form_id.get_doc_ids_list(),
                'staff_id': record.jig_form_id.env.user.id,
                'staff_name': record.jig_form_id.env.user.name,
                # 'check_date': "",
                # 'final_result': "OK",
                'columns': record.jig_form_id.get_pqc_column_config(),
                'check_list': record.jig_form_id.prepare_check_list_data(),
                'form_id': record.jig_form_id.id,
                'mrp_workorder_id': record.id,
                # 'qty': record.quantity,

            }

            tag = "qms_question_jig_action"
            name = _(f"QMS JIG - {record.jig_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }


