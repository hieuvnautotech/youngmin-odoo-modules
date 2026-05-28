from odoo import models, api, fields, _

from odoo.exceptions import UserError

from odoo.fields import Datetime


class StockMove(models.Model):
    _inherit = "stock.move"

    def button_pass_iqc(self):
        selected_line_ids = self.env.context.get('selected_ids', [])

        # form_id = self.env.ref("autonsi_qms.item_qc_form_material_incoming")
        form = self.env["mes.qc_form"].search([('form_type', '=', 'iqc'), ('state', '=', 'confirm')], order='confirm_date desc', limit=1)
        if not form:
            raise UserError(_("There is no confirmed QC form of type 'iqc'."))
        form_id = form

        if selected_line_ids:
            lines = self.env['stock.move.line'].browse(selected_line_ids)
            for record in lines:
                self.env["mes.qc_form.history"].search([('stock_move_line_id', '=', record.id)]).unlink()
                history_vals = {
                    'name': form_id.name,
                    'mes_qc_form_id': form_id.id,
                    'stock_move_line_id': record.id,

                    'type_material': record.material_category_id.name,
                    'supplier': record.picking_id.partner_id.name,
                    'material_code': record.product_id.code,
                    'material_name': record.product_name,
                    'lot_id': record.lot_id.id,
                    'qty_uom': record.product_id.uom_id.name,

                    'staff_id': record.env.user.id,
                    'confirm_staff_id': record.env.user.id,
                    'check_date': Datetime.now(),
                    'staff_name': record.env.user.name,
                    'confirm_staff_name': record.env.user.name,
                    'overall_result': "OK",
                    'qty': record.quantity,
                    'item_group': 'material',
                    'is_history': True,

                }
                history = self.env["mes.qc_form.history"].create(history_vals)
                history.form_type = history.mes_qc_form_id.form_type

                for item in form_id.prepare_check_list_data():
                    line_vals = {
                        'history_id': history.id,
                        'mes_qc_form_question_id': item.get('id'),
                        'X1': item.get('X1'),
                        'X2': item.get('X2'),
                        'X3': item.get('X3'),
                        'X4': item.get('X4'),
                        'X5': item.get('X5'),
                        'result': item.get('result'),
                        'remark': item.get('remark'),
                    }
                    self.env["mes.qc_form.history.line"].create(line_vals)

        return super().button_pass_iqc()

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    iqc_form_id = fields.Many2one('mes.qc_form', string='IQC Form')

    def button_open_iqc_form(self):
        for record in self:
            history_id = self.env["mes.qc_form.history"].search([('stock_move_line_id', '=', record.id)])
            if history_id:
                print(history_id)
                return history_id.action_open_iqc_form_history()
            res = super().button_open_iqc_form()

            # record.iqc_form_id = self.env.ref("autonsi_qms.item_qc_form_material_incoming").id
            form_id = self.env["mes.qc_form"].search([('form_type', '=', 'iqc'), ('state', '=', 'confirm')], order='confirm_date desc', limit=1)
            if not form_id:
                raise UserError(_("There is no confirmed QC form of type 'iqc'."))
            record.iqc_form_id = form_id

            context_data = {
                "title": record.iqc_form_id.name,
                'category_material': record.product_id.categ_id.name,
                'supplier': record.picking_id.partner_id.name,
                'material_code': record.product_id.code,
                'material_name': record.product_name,
                'lot': record.lot_id.name,
                'qty_uom': record.product_id.uom_id.name,
                'isHistory': False,
                'isPreview': False,

                'employee_list': record.iqc_form_id.get_employee_list(),
                'self_id': record.iqc_form_id.get_self_id(),
                'doc_list': record.iqc_form_id.get_doc_ids_list(),
                'staff_id': record.iqc_form_id.env.user.id,
                'staff_name': record.iqc_form_id.env.user.name,
                # 'check_date': "",
                # 'final_result': "OK",
                'columns': record.iqc_form_id.get_iqc_column_config(),
                'check_list': record.iqc_form_id.prepare_check_list_data(),
                'form_id': record.iqc_form_id.id,
                'stock_move_line_id': record.id,
                'qty': record.quantity,

            }

            tag = "qms_question_iqc_action"
            name = _(f"QMS IQC - {record.iqc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }




    
