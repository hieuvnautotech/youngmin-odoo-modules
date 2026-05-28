from odoo import api, fields, models, _

from odoo.exceptions import UserError


class MrpMaterial(models.Model):
    _inherit = 'mrp.material'

    item_qc_form_id = fields.Many2one('mes.qc_form', string='Item QC Form')

    def button_qc(self):
        for record in self:

            history_id = self.env["mes.qc_form.history"].search([('mrp_material_id', '=', record.id)])
            if history_id:
                print(history_id)
                return history_id.action_open_item_qc_form_history()
            res = super().button_qc()

            # record.item_qc_form_id = self.env.ref("autonsi_qms.item_qc_form_item_check").id
            form_id = self.env["mes.qc_form"].search([('form_type', '=', 'item_qc'), ('state', '=', 'confirm')], order='confirm_date desc', limit=1)
            if not form_id:
                raise UserError(_("There is no confirmed QC form of type 'item_qc'."))
            record.item_qc_form_id = form_id

            context_data = {
                "title": record.item_qc_form_id.name,
                'category_material': record.material_id.categ_id.name,
                # 'supplier': record.partner_id.name,
                'material_code': record.material_id.code,
                'material_name': record.material_id.name,
                'spec': record.material_id.spec,
                'lot': record.lot_id.name,
                'qty_uom': record.material_id.uom_id.name,
                'isHistory': False,
                'isPreview': False,

                'employee_list': record.item_qc_form_id.get_employee_list(),
                'self_id': record.item_qc_form_id.get_self_id(),
                'doc_list': record.item_qc_form_id.get_doc_ids_list(),
                'staff_id': record.item_qc_form_id.env.user.id,
                'staff_name': record.item_qc_form_id.env.user.name,
                # 'check_date': "",
                # 'final_result': "OK",
                'columns': record.item_qc_form_id.get_pqc_column_config(),
                'check_list': record.item_qc_form_id.prepare_check_list_data(),
                'form_id': record.item_qc_form_id.id,
                'mrp_material_id': record.id,
                'qty': record.received_qty,

            }

            tag = "qms_question_item_qc_action"
            name = _(f"QMS Item QC - {record.item_qc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }


class MrpMOMaterial(models.Model):
    _inherit = 'mrp.mo.material'

    item_qc_form_id = fields.Many2one('mes.qc_form', string='Item QC Form')

    def button_qc(self):
        for record in self:

            history_id = self.env["mes.qc_form.history"].search([('mrp_mo_material_id', '=', record.id)])
            if history_id:
                print(history_id)
                return history_id.action_open_item_qc_form_history()
            res = super().button_qc()

            # record.item_qc_form_id = self.env.ref("autonsi_qms.item_qc_form_item_check").id
            form_id = self.env["mes.qc_form"].search([('form_type', '=', 'item_qc'), ('state', '=', 'confirm')], order='confirm_date desc', limit=1)
            if not form_id:
                raise UserError(_("There is no confirmed QC form of type 'item_qc'."))
            record.item_qc_form_id = form_id

            context_data = {
                "title": record.item_qc_form_id.name,
                'category_material': record.material_id.categ_id.name,
                # 'supplier': record.partner_id.name,
                'material_code': record.material_id.code,
                'material_name': record.material_id.name,
                'spec': record.material_id.spec,
                'lot': record.lot_id.name,
                'qty_uom': record.material_id.uom_id.name,
                'isHistory': False,
                'isPreview': False,

                'employee_list': record.item_qc_form_id.get_employee_list(),
                'self_id': record.item_qc_form_id.get_self_id(),
                'doc_list': record.item_qc_form_id.get_doc_ids_list(),
                'staff_id': record.item_qc_form_id.env.user.id,
                'staff_name': record.item_qc_form_id.env.user.name,
                # 'check_date': "",
                # 'final_result': "OK",
                'columns': record.item_qc_form_id.get_pqc_column_config(),
                'check_list': record.item_qc_form_id.prepare_check_list_data(),
                'form_id': record.item_qc_form_id.id,
                'mrp_mo_material_id': record.id,
                'qty': record.received_qty,

            }

            tag = "qms_question_item_qc_action"
            name = _(f"QMS Item QC - {record.item_qc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }