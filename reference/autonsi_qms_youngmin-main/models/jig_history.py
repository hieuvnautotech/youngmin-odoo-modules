from odoo import api, fields, models, _

class JigHistory(models.Model):
    _inherit = 'jig.history'

    history_id = fields.Many2one("mes.qc_form.history", string="History")

    def action_result_qc(self):
        for record in self:
            if record.history_id:
                return record.history_id.action_open_jig_form_history()

