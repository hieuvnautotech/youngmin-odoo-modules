from odoo import models, fields, api,  _
from odoo.exceptions import UserError, ValidationError

from odoo.fields import Datetime


class MESQCFormLog(models.Model):
    _name = "mes.qc_form.log"
    _order = "id DESC"

    history_id = fields.Many2one('mes.qc_form.history', string="History")
    type_material = fields.Char(related='history_id.type_material')
    material_code = fields.Char(related='history_id.material_code')
    material_name = fields.Char(related='history_id.material_name')
    lot_id = fields.Many2one(related='history_id.lot_id')
    stock_move_line_id = fields.Many2one(related='history_id.stock_move_line_id')
    form_type = fields.Selection(related='history_id.form_type')
    item_group = fields.Selection(related='history_id.item_group')
    status = fields.Selection(related='history_id.status')
    result = fields.Char(related='history_id.result')
    check_date = fields.Datetime(related='history_id.check_date')
    staff_name = fields.Char(related='history_id.staff_name')
    qty = fields.Float(related='history_id.qty')
    qty_uom = fields.Char(related='history_id.qty_uom')

    log_result = fields.Char(string="Overall Result")

    reason = fields.Char(string="Reason")

    file_upload = fields.Binary('File', attachment=True, )
    file_upload_name = fields.Char('File Name')



    @api.model
    def create(self, vals):
        history_ids = self.env.context.get("default_history_ids")

        if history_ids:
            logs = self.env[self._name]
            for history_id in history_ids:
                new_vals = vals.copy()
                new_vals["history_id"] = history_id
                log = super().create(new_vals)
                logs |= log

                if log.history_id.status == 'hold':
                    log.history_id.create_picking_shipping({
                        "lot_id": log.history_id.lot_id,
                        "from_location": log.history_id.ng_location,
                        "to_location": log.history_id.ok_location,
                        "quantity": log.history_id.qty,
                    })._action_done()
                    log.history_id.status = 'release'
                    log.history_id.result = 'OK'
                    log.log_result = log.history_id.result
                    log.history_id.ng_location = False
                    # if log.history_id.form_type == "item_qc":
                    #     log.history_id.ng_location = self.env.ref("autonsi_standard_youngmin.location_ng_stock_1")

                elif log.history_id.status == 'release':

                    if log.history_id.form_type == "item_qc":
                        self.env['stock.quant']._update_reserved_quantity(
                            log.history_id.product_id,
                            log.history_id.ok_location,
                            - log.history_id.qty,
                            lot_id=log.history_id.lot_id,
                            strict=True
                        )
                        log.history_id.mrp_material_id.qc_status = 'not_yet'

                        log.history_id.create_picking_shipping({
                            "lot_id": log.history_id.lot_id,
                            "from_location": log.history_id.ok_location,
                            "to_location": log.history_id.ng_location,
                            "quantity": log.history_id.qty,
                        })._action_done()
                        log.history_id.status = 'hold'
                        log.history_id.result = 'NG'
                        log.log_result = log.history_id.result
                        log.history_id.ok_location = False

                    if log.history_id.form_type == "iqc":
                        quants = self.env["stock.quant"].search([
                            ("lot_id", "=", log.history_id.lot_id.id),
                            ("location_id.check_type", "in", ["m_stock", "m_stock_2"]),
                            ("quantity", ">", 0),
                        ])

                        if not quants:
                            raise UserError(_("No available quantity to hold for this lot."))

                        for quant in quants:
                            log.history_id.create_picking_shipping({
                                "lot_id": quant.lot_id,
                                "from_location": quant.location_id,
                                "to_location": log.history_id.ng_location,
                                "quantity": quant.quantity,
                            })._action_done()

                        log.history_id.status = 'hold'
                        log.history_id.result = 'OK'
                        log.log_result = log.history_id.result
                        log.history_id.ok_location = False

            return logs
        else:
            raise UserError(_("Please select a history before creating this form."))















