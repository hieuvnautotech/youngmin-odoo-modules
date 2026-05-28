# -*- coding: utf-8 -*-

from odoo import fields, models


class StandardProcess(models.Model):
    _name = 'standard.process'
    _description = 'Standard Process'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Process Code must be unique!'),
    ]

    name = fields.Char(string='Process Name', required=True, tracking=True)
    code = fields.Char(string='Process Code', required=True, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    line_ids = fields.One2many(
        'standard.process.line',
        'process_id',
        string='Process Lines',
    )


class StandardProcessLine(models.Model):
    _name = 'standard.process.line'
    _description = 'Process Line'
    _order = 'sequence, id'

    process_id = fields.Many2one(
        'standard.process',
        string='Process',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Line Name', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center')
    duration = fields.Float(string='Duration (hours)')
    note = fields.Text(string='Note')
