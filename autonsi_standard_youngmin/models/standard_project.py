# -*- coding: utf-8 -*-

from odoo import fields, models


class StandardProject(models.Model):
    _name = 'standard.project'
    _description = 'Standard Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Project Code must be unique!'),
    ]

    name = fields.Char(string='Project Name', required=True, tracking=True)
    code = fields.Char(string='Project Code', required=True, tracking=True)
    alias = fields.Char(string='Alias')
    project_start = fields.Date(string='Project Start')
    project_end = fields.Date(string='Project End')
    project_period = fields.Char(string='Project Period')
    project_status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ], string='Project Status', default='draft', tracking=True)
    developer_charger = fields.Char(string='Developer Charger')
    development_status = fields.Selection([
        ('developing', 'Developing'),
        ('released', 'Released'),
        ('discontinued', 'Discontinued'),
    ], string='Development Status')
    check_drawing_consistency = fields.Boolean(string='Check Drawing Consistency')
    image = fields.Binary(string='Image')
    remark = fields.Text(string='Remark')
