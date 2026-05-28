from odoo import fields, models, api, _

from odoo.exceptions import ValidationError,UserError

from odoo.fields import Datetime


class MrpMO(models.Model):
    _inherit = 'mrp.mo'

    oqc_form_id = fields.Many2one('mes.qc_form', string='OQC Form')

    def button_oqc(self):
        selected_ids = self.env.context.get('selected_ids', [])
        if len(selected_ids) != 1:
            raise UserError(_("Please select exactly one record."))
        selected_id = selected_ids[0] if selected_ids else None
        mrp_production_id = self.env["mrp.production"].search([('id', '=', selected_id)])
        for record in self:
            history_id = self.env["mes.qc_form.history"].search([('mrp_production_id', '=', selected_id)])
            if history_id:
                return history_id.action_open_oqc_form_history()
            res = super().button_oqc()

            # record.oqc_form_id = self.env.ref("autonsi_qms.item_qc_form_pqc_cutting").id
            # "resistance","double_insp","visual"
            oqc_process = "visual"
            if record.process_id.id == self.env.ref(
                    "autonsi_standard_youngmin.common_record_process_510_double_insp_packing").id:
                oqc_process = "double_insp"
            elif record.process_id.id == self.env.ref(
                    "autonsi_standard_youngmin.common_record_process_500_circuit_insp_packing").id:
                oqc_process = "resistance"
            elif record.process_id.id == self.env.ref(
                    "autonsi_standard_youngmin.common_record_process_480_vision_inspection").id:
                oqc_process = "vision"

            form_id = self.env["mes.qc_form"].search([('form_type', '=', 'oqc'), ('state', '=', 'confirm'), ('oqc_process', '=', oqc_process)],
                                                     order='confirm_date desc', limit=1)
            print(form_id)
            if not form_id:
                raise UserError(_("There is no confirmed QC form of type 'oqc_process'."))
            record.oqc_form_id = form_id

            context_data = {
                "title": record.oqc_form_id.name,
                'material_code': mrp_production_id.product_id.code,
                'material_name': mrp_production_id.product_id.name,
                'line_no': mrp_production_id.workorder_ids[:1].name or "",
                'lot': mrp_production_id.lot_producing_id.name,
                'qty_uom': mrp_production_id.product_id.uom_id.name,
                'isHistory': False,
                'isPreview': False,
                'is_resistance': oqc_process == "resistance",
                'is_final_process': True,

                'employee_list': record.oqc_form_id.get_employee_list(),
                'self_id': record.oqc_form_id.get_self_id(),
                'doc_list': record.oqc_form_id.get_doc_ids_list(),
                'staff_id': record.oqc_form_id.env.user.id,
                'staff_name': record.oqc_form_id.env.user.name,
                'columns': record.oqc_form_id.get_pqc_column_config(),
                'check_list': record.oqc_form_id.prepare_check_list_data(),
                'form_id': record.oqc_form_id.id,
                'mrp_production_id': mrp_production_id.id,
                'qty': mrp_production_id.actual_qty,

            }

            tag = "qms_question_oqc_action"
            name = _(f"QMS PQC Cutting - {record.oqc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }

    def button_pass_pqc(self):
        res = super().button_pass_pqc()

        selected_ids = self.env.context.get('selected_ids')
        if not selected_ids:
            raise ValidationError(_("No Manufacturing Orders selected for PQC Pass."))
        operation_ids = self.env['mrp.production'].browse(selected_ids)
        # form_id = self.env.ref("autonsi_qms.item_qc_form_pqc_cutting")
        form = self.env["mes.qc_form"].search([('form_type', '=', 'pqc'), ('state', '=', 'confirm'), ('process_ids', 'in', self.process_id.id)], order='confirm_date desc', limit=1)
        if not form:
            raise UserError(_("There is no confirmed QC form of type 'pqc'."))
        form_id = form

        shop_floor = self.env.context.get('shop_floor', False)
        staff_name = self.env.user.name
        if shop_floor and self.env.context.get('staff_name', False):
            if staff_name:
                staff_name = self.env.context.get('staff_name')
            

        for record in operation_ids:
            record.pqc_cut_form_id = form_id

            record.write(
                {
                    "ok_qty": record.product_qty,
                    "ng_qty": 0.0,
                    "pqc_date": Datetime.now(),
                }
            )
            record.action_reserved_semi_product_qty(record.product_qty, 0.0)

            history_vals = {
                'name': form_id.name,
                'mes_qc_form_id': form_id.id,
                'mrp_production_id': record.id,

                'process_id': self.process_id.id,

                'process': "Cutting",
                'qty_sampling': record.product_qty,
                'defect_ratio': 0.0,
                'lot_id': record.lot_producing_id.id,
                'ok_qty': record.product_qty,
                'ng_qty': 0.0,
                'type_roll': "first",

                'staff_id': record.env.user.id,
                'check_date': Datetime.now(),
                'staff_name': staff_name,

            }
            history = self.env["mes.qc_form.history"].create(history_vals)
            history.form_type = history.mes_qc_form_id.form_type
            history.lot_id = history.mrp_production_id.lot_producing_id
            history.mes_qc_form_id.used = True

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

    def button_pass_oqc(self):
        res = super().button_pass_oqc()

        selected_ids = self.env.context.get('selected_ids')
        if not selected_ids:
            raise ValidationError(_("No Manufacturing Orders selected for OQC Pass."))
        operation_ids = self.env['mrp.production'].browse(selected_ids)

        oqc_process = "visual"
        if self.process_id.id == self.env.ref("autonsi_standard_youngmin.common_record_process_510_double_insp_packing").id:
            oqc_process = "double_insp"
        elif self.process_id.id == self.env.ref("autonsi_standard_youngmin.common_record_process_500_circuit_insp_packing").id:
            oqc_process = "resistance"
        elif self.process_id.id == self.env.ref("autonsi_standard_youngmin.common_record_process_480_vision_inspection").id:
            oqc_process = "vision"

        form_id = self.env["mes.qc_form"].search(
            [('form_type', '=', 'oqc'), ('state', '=', 'confirm'), ('oqc_process', '=', oqc_process)],
            order='confirm_date desc', limit=1)

        for record in operation_ids:
            record.pqc_cut_form_id = form_id

            record.action_callback_oqc()
            record.write({
                "ok_qty": record.actual_qty,
                "ng_qty": 0,
                "pqc_date": Datetime.now(),
            })
            record.action_reserved_semi_product_qty(record.actual_qty,0)

            history_vals = {
                'name': form_id.name,
                'mes_qc_form_id': form_id.id,
                'mrp_production_id': record.id,

                'is_resistance': oqc_process == "resistance",
                'is_final_process': True,

                'qty_sampling': 1,
                'defect_ratio': 0.0,
                'ok_qty': record.actual_qty,
                'ng_qty': 0.0,
                'type_roll': "first",
                'qty': record.actual_qty,

                'staff_id': record.env.user.id,
                'check_date': Datetime.now(),
                'staff_name': record.env.user.name,
            }
            history = self.env["mes.qc_form.history"].create(history_vals)
            history.form_type = history.mes_qc_form_id.form_type
            history.lot_id = history.mrp_production_id.lot_producing_id
            history.mes_qc_form_id.used = True

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
