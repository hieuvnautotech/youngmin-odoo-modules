# -*- coding: utf-8 -*-

from odoo import fields, models


class StandardCommon(models.Model):
    _name = 'standard.common'
    _description = 'Common Master Data'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)
    detail_ids = fields.One2many(
        'standard.common.detail',
        'common_id',
        string='Details',
    )


class StandardCommonDetail(models.Model):
    _name = 'standard.common.detail'
    _description = 'Common Detail'
    _order = 'sequence, id'

    common_id = fields.Many2one(
        'standard.common',
        string='Common',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
