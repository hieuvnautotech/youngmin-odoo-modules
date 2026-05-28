from odoo import fields, models, api, _

from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    pqc_cut_form_id = fields.Many2one('mes.qc_form', string='Cut Form')

    def button_pqc(self):
        for record in self:
            if record.pqc_date:
                # raise UserError(_("Material has already been IQC on %s.") % record.qc_date.date())
                history_id = self.env["mes.qc_form.history"].search([('mrp_production_id', '=', record.id)])
                if history_id and history_id.form_type=='oqc':
                    return history_id.action_open_oqc_form_history()
                elif history_id and history_id.form_type=='pqc':
                    return history_id.action_open_pqc_form_history()
            res = super().button_pqc()

            if record.mo_id.is_oqc_process:
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

                form_id = self.env["mes.qc_form"].search(
                    [('form_type', '=', 'oqc'), ('state', '=', 'confirm'), ('oqc_process', '=', oqc_process)],
                    order='confirm_date desc', limit=1)
                if not form_id:
                    raise UserError(_("There is no confirmed QC form of type 'process'."))
                record.pqc_cut_form_id = form_id

                context_data = {
                    "title": record.pqc_cut_form_id.name,
                    'material_code': record.product_id.code,
                    'material_name': record.product_id.name,
                    'line_no': record.workorder_ids[:1].name or "",
                    'lot': record.lot_producing_id.name,
                    'qty_uom': record.product_id.uom_id.name,
                    'isHistory': False,
                    'isPreview': False,
                    'is_resistance': oqc_process == "resistance",
                    'is_final_process': False,

                    'employee_list': record.pqc_cut_form_id.get_employee_list(),
                    'self_id': record.pqc_cut_form_id.get_self_id(),
                    'doc_list': record.pqc_cut_form_id.get_doc_ids_list(),
                    'staff_id': record.pqc_cut_form_id.env.user.id,
                    'staff_name': record.pqc_cut_form_id.env.user.name,
                    'columns': record.pqc_cut_form_id.get_pqc_column_config(),
                    'check_list': record.pqc_cut_form_id.prepare_check_list_data(),
                    'form_id': record.pqc_cut_form_id.id,
                    'mrp_production_id': record.id,
                    'qty': record.actual_qty,

                }

                tag = "qms_question_oqc_action"
                name = _(f"QMS PQC Cutting - {record.pqc_cut_form_id.name}")
            else:
                if not record.process_id:
                    record.process_id = self.env.ref('autonsi_standard_youngmin.common_record_process_020_fabric_cutting')

                form_id = self.env["mes.qc_form"].search([('form_type', '=', 'pqc'), ('state', '=', 'confirm'), ('process_ids', 'in', record.process_id.id)],
                                                         order='confirm_date desc', limit=1)
                if not form_id:
                    raise UserError(_("There is no confirmed QC form of type 'process'."))
                record.pqc_cut_form_id = form_id

                context_data = {
                    "title": record.pqc_cut_form_id.name,
                    'category_material': record.semi_product_id.categ_id.name,
                    # 'supplier': record.partner_id.name,
                    'material_code': record.semi_product_id.code,
                    'material_name': record.semi_product_id.name,
                    'line_no': record.workorder_ids[:1].name or "",
                    'lot': record.lot_producing_id.name,
                    'qty_uom': record.semi_product_id.uom_id.name,
                    'isHistory': False,
                    'isPreview': False,

                    'employee_list': record.pqc_cut_form_id.get_employee_list(),
                    'self_id': record.pqc_cut_form_id.get_self_id(),
                    'doc_list': record.pqc_cut_form_id.get_doc_ids_list(),
                    'staff_id': record.pqc_cut_form_id.env.user.id,
                    'staff_name': record.pqc_cut_form_id.env.user.name,
                    # 'check_date': "",
                    # 'final_result': "OK",
                    'columns': record.pqc_cut_form_id.get_pqc_column_config(),
                    'check_list': record.pqc_cut_form_id.prepare_check_list_data(),
                    'form_id': record.pqc_cut_form_id.id,
                    'mrp_production_id': record.id,
                    'qty': record.actual_qty,

                    'process': record.process_id.name,
                    'process_id': record.process_id.id,

                }

                tag = "qms_question_pqc_action"
                name = _(f"QMS PQC Cutting - {record.pqc_cut_form_id.name}")


            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }


