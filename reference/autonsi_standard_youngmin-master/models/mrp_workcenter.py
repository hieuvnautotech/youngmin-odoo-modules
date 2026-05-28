from odoo import models, fields, api


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    process_id = fields.Many2one('standard.process', string='Process')
    factory = fields.Selection([('fac1', 'Factory 1'), ('fac2', 'Factory 2')], string='Factory')