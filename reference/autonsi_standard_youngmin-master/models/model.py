# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Model(models.Model):
    _name = 'standard.model'
    _description = 'Product Model'
    _order = 'create_date desc'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    description = fields.Char(string='Description')
    remark = fields.Char(string='Remark')

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            if record.name:
                duplicate_records = self.search(
                    [('id', '!=', record.id), ('name', '=', record.name)])
                if duplicate_records:
                    raise UserError(_('Duplicate Name'))
