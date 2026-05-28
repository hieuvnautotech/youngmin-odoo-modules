from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_done_receiving(self):
        res = super().button_done_receiving()
        for picking in self:
            for line in picking.move_line_ids:
                if line.iqc_state == "ng":
                    rec = self.env["mes.qc_form.history"].search(
                        [("stock_move_line_id", "=", line.id)], limit=1
                    )
                    rec.status = "hold"
                    rec.ng_location = rec.stock_move_line_id.location_dest_id
                elif line.iqc_state == "ok":
                    rec = self.env["mes.qc_form.history"].search(
                        [("stock_move_line_id", "=", line.id)], limit=1
                    )
                    rec.status = "release"
                    rec.ok_location = rec.stock_move_line_id.location_dest_id

        return res
