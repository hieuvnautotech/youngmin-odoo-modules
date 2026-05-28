# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Department(models.Model):
    _inherit = 'hr.department'
    _order = 'sequence desc'

    sequence = fields.Integer('Sequence')
    description = fields.Char('Description')
    code = fields.Char('Code', index=True)

