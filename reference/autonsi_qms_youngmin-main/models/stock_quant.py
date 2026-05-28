from odoo import models, api,fields, _

from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    re_use_form_id = fields.Many2one('mes.qc_form', string='Re-Use Form')

    def button_open_iqc_form(self):
        for record in self:
            # if record.disposal_date:
                # history_id = self.env["mes.qc_form.history"].search([('stock_quant_id', '=', record.id)])
                # if history_id:
                #     print(history_id)
                #     return history_id.action_open_re_use_form_history()
            res = super().button_open_iqc_form()

            # record.re_use_form_id = self.env.ref("autonsi_qms.item_qc_form_re_use").id
            form_id = self.env["mes.qc_form"].search([('form_type', '=', 're_use'), ('state', '=', 'confirm'), ('item_group', '=', 'material')], order='confirm_date desc', limit=1)
            if not form_id:
                raise UserError(_("There is no confirmed QC form of type 're-use'."))
            record.re_use_form_id = form_id

            context_data = {
                "title": record.re_use_form_id.name,
                "item_group": record.re_use_form_id.item_group,
                'remaining_days': record.remaining_days,
                'life_days': record.material_life,
                'category_material': record.material_category_id.name,
                'supplier': record.partner_id.name,
                'material_code': record.product_id.code,
                'material_name': record.product_name,
                'lot': record.lot_id.name,
                'qty_uom': record.product_id.uom_id.name,
                'isHistory': False,
                'isPreview': False,

                'employee_list': record.re_use_form_id.get_employee_list(),
                'self_id': record.re_use_form_id.get_self_id(),
                'doc_list': record.re_use_form_id.get_doc_ids_list(),
                'staff_id': record.re_use_form_id.env.user.id,
                'staff_name': record.re_use_form_id.env.user.name,
                # 'check_date': "",
                # 'final_result': "OK",
                'columns': record.re_use_form_id.get_pqc_column_config(),
                'check_list': record.re_use_form_id.prepare_check_list_data(),
                'form_id': record.re_use_form_id.id,
                'stock_quant_id': record.id,
                'qty': record.available_quantity,

            }

            tag = "qms_question_re_use_action"
            name = _(f"QMS Re-Use - {record.re_use_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }

    def button_open_qc_semi_wip(self):
        for record in self:
            # if record.disposal_date:
            #     history_id = self.env["mes.qc_form.history"].search([('stock_quant_id', '=', record.id)])
            #     if history_id:
            #         print(history_id)
            #         return history_id.action_open_re_use_form_history()
            res = super().button_open_iqc_form()

            # record.re_use_form_id = self.env.ref("autonsi_qms.item_qc_form_re_use").id
            form_id = self.env["mes.qc_form"].search([('form_type', '=', 're_use'), ('state', '=', 'confirm'), ('item_group', '=', 'semi')], order='confirm_date desc', limit=1)
            if not form_id:
                raise UserError(_("There is no confirmed QC form of type 're-use'."))
            record.re_use_form_id = form_id

            context_data = {
                "title": record.re_use_form_id.name,
                "item_group": record.re_use_form_id.item_group,
                'remaining_days': record.remaining_days,
                'life_days': record.material_life,
                'category_material': record.material_category_id.name,
                'supplier': record.partner_id.name,
                'material_code': record.product_id.code,
                'material_name': record.product_name,
                'lot': record.lot_id.name,
                'qty_uom': record.product_id.uom_id.name,
                'isHistory': False,
                'isPreview': False,

                'employee_list': record.re_use_form_id.get_employee_list(),
                'self_id': record.re_use_form_id.get_self_id(),
                'doc_list': record.re_use_form_id.get_doc_ids_list(),
                'staff_id': record.re_use_form_id.env.user.id,
                'staff_name': record.re_use_form_id.env.user.name,
                # 'check_date': "",
                # 'final_result': "OK",
                'columns': record.re_use_form_id.get_pqc_column_config(),
                'check_list': record.re_use_form_id.prepare_check_list_data(),
                'form_id': record.re_use_form_id.id,
                'stock_quant_id': record.id,
                'qty': record.available_quantity,

            }

            tag = "qms_question_re_use_action"
            name = _(f"QMS Re-Use - {record.re_use_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }

    def button_open_qc_fg(self):
        for record in self:
            # if record.disposal_date:
            #     history_id = self.env["mes.qc_form.history"].search([('stock_quant_id', '=', record.id)])
            #     if history_id:
            #         print(history_id)
            #         return history_id.action_open_re_use_form_history()
            res = super().button_open_iqc_form()

            # record.re_use_form_id = self.env.ref("autonsi_qms.item_qc_form_re_use").id
            form_id = self.env["mes.qc_form"].search([('form_type', '=', 're_use'), ('state', '=', 'confirm'), ('item_group', '=', 'fg')], order='confirm_date desc', limit=1)
            if not form_id:
                raise UserError(_("There is no confirmed QC form of type 're-use'."))
            record.re_use_form_id = form_id

            context_data = {
                "title": record.re_use_form_id.name,
                "item_group": record.re_use_form_id.item_group,
                'remaining_days': record.remaining_days,
                'life_days': record.material_life,
                'category_material': record.material_category_id.name,
                'supplier': record.partner_id.name,
                'material_code': record.product_id.code,
                'material_name': record.product_name,
                'lot': record.lot_id.name,
                'qty_uom': record.product_id.uom_id.name,
                'isHistory': False,
                'isPreview': False,

                'employee_list': record.re_use_form_id.get_employee_list(),
                'self_id': record.re_use_form_id.get_self_id(),
                'doc_list': record.re_use_form_id.get_doc_ids_list(),
                'staff_id': record.re_use_form_id.env.user.id,
                'staff_name': record.re_use_form_id.env.user.name,
                # 'check_date': "",
                # 'final_result': "OK",
                'columns': record.re_use_form_id.get_pqc_column_config(),
                'check_list': record.re_use_form_id.prepare_check_list_data(),
                'form_id': record.re_use_form_id.id,
                'stock_quant_id': record.id,
                'qty': record.available_quantity,

            }

            tag = "qms_question_re_use_action"
            name = _(f"QMS Re-Use - {record.re_use_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }



    def button_open_re_use_material(self, quants):
        print(quants)
        quant_ids = self.env["stock.quant"].search([('id', 'in', quants)])
        form_id = self.env["mes.qc_form"].search([('form_type', '=', 're_use'), ('state', '=', 'confirm'), ('item_group', '=', 'material')], order='confirm_date desc', limit=1)
        if not form_id:
            raise UserError(_("There is no confirmed QC form of type 're-use'."))

        for quant_id in quant_ids:
            quant_id.re_use_form_id = form_id

        context_data = {
            "title": form_id.name,
            "item_group": form_id.item_group,

            'isHistory': False,
            'isPreview': False,

            'employee_list': form_id.get_employee_list(),
            'self_id': form_id.get_self_id(),
            'doc_list': form_id.get_doc_ids_list(),
            'staff_id': form_id.env.user.id,
            'staff_name': form_id.env.user.name,
            'columns': form_id.get_pqc_column_config(),
            'check_list': form_id.prepare_check_list_data(),
            'form_id': form_id.id,
            'stock_quant_ids': quant_ids.ids,

        }

        tag = "qms_question_multi_re_use_action"
        name = _(f"QMS Re-Use - {form_id.name}")
        return {
            "type": "ir.actions.client",
            "tag": tag,
            "name": name,
            "context": context_data,
            "target": "new",
        }

    def button_open_re_use_semi(self, quants):
        quant_ids = self.env["stock.quant"].search([('id', 'in', quants)])
        form_id = self.env["mes.qc_form"].search([('form_type', '=', 're_use'), ('state', '=', 'confirm'), ('item_group', '=', 'semi')], order='confirm_date desc', limit=1)
        if not form_id:
            raise UserError(_("There is no confirmed QC form of type 're-use'."))

        for quant_id in quant_ids:
            quant_id.re_use_form_id = form_id

        context_data = {
            "title": form_id.name,
            "item_group": form_id.item_group,

            'isHistory': False,
            'isPreview': False,

            'employee_list': form_id.get_employee_list(),
            'self_id': form_id.get_self_id(),
            'doc_list': form_id.get_doc_ids_list(),
            'staff_id': form_id.env.user.id,
            'staff_name': form_id.env.user.name,
            'columns': form_id.get_pqc_column_config(),
            'check_list': form_id.prepare_check_list_data(),
            'form_id': form_id.id,
            'stock_quant_ids': quant_ids.ids,

        }

        tag = "qms_question_multi_re_use_action"
        name = _(f"QMS Re-Use - {form_id.name}")
        return {
            "type": "ir.actions.client",
            "tag": tag,
            "name": name,
            "context": context_data,
            "target": "new",
        }

    def button_open_re_use_fg(self, quants):
        quant_ids = self.env["stock.quant"].search([('id', 'in', quants)])
        form_id = self.env["mes.qc_form"].search([('form_type', '=', 're_use'), ('state', '=', 'confirm'), ('item_group', '=', 'fg')], order='confirm_date desc', limit=1)
        if not form_id:
            raise UserError(_("There is no confirmed QC form of type 're-use'."))

        for quant_id in quant_ids:
            quant_id.re_use_form_id = form_id

        context_data = {
            "title": form_id.name,
            "item_group": form_id.item_group,

            'isHistory': False,
            'isPreview': False,

            'employee_list': form_id.get_employee_list(),
            'self_id': form_id.get_self_id(),
            'doc_list': form_id.get_doc_ids_list(),
            'staff_id': form_id.env.user.id,
            'staff_name': form_id.env.user.name,
            'columns': form_id.get_pqc_column_config(),
            'check_list': form_id.prepare_check_list_data(),
            'form_id': form_id.id,
            'stock_quant_ids': quant_ids.ids,

        }

        tag = "qms_question_multi_re_use_action"
        name = _(f"QMS Re-Use - {form_id.name}")
        return {
            "type": "ir.actions.client",
            "tag": tag,
            "name": name,
            "context": context_data,
            "target": "new",
        }


