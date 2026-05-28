from odoo import api, fields, models, _

from odoo.exceptions import ValidationError


class HistoryStock(models.Model):
    _inherit = "history.stock"

    re_use_history = fields.Many2one('mes.qc_form.history')

    def button_detail(self):
        for record in self:
            return record.re_use_history.action_open_re_use_form_history()
