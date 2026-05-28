from odoo import api, fields, models, _

from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    jig_form_id = fields.Many2one('mes.qc_form', string='JIG Form')

    def action_check_jig(self):
        for record in self:
            if record.jig_status_qc != 'not_yet':
                # raise UserError(_("Jig has already been QC."))
                history_id = self.env["mes.qc_form.history"].search([('jig_id', '=', record.id)])
                if history_id:
                    print(history_id)
                    return history_id.action_open_jig_form_history()
            res = super().action_check_jig()

            # record.jig_form_id = self.env.ref("autonsi_qms.item_qc_form_pqc_jig_new").id
            form_id = self.env["mes.qc_form"].search([('form_type', '=', 'jig'), ('state', '=', 'confirm'), ('jig_state', '=', 'new')], order='confirm_date desc', limit=1)
            if not form_id:
                raise UserError(_("There is no confirmed QC form of type 'jig new check'."))
            record.jig_form_id = form_id

            context_data = {
                'title': record.jig_form_id.name,
                'product_code': record.jig_product_id.code,
                'supplier': record.equip_partner_id.name,
                'jig_code': record.asset_code,
                'jig_name': record.name,
                'process': record.process_id.name,
                'rev': record.rev,
                'remark': record.remark,
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
                'jig_id': record.id,
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


        