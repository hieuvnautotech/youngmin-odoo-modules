# -*- coding: utf-8 -*-
"""
Example models and views to test X2Many Enhanced widget
"""

from odoo import models, fields, api

# =====================================================
# Parent Model
# =====================================================
class TestParent(models.Model):
    _name = 'test.parent'
    _description = 'Test Parent Model'
    
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    
    # One2Many field để test widget
    line_ids = fields.One2many(
        'test.line',
        'parent_id',
        domain=[('id','!=',0)],
        string='Lines'
    )
    
    # Many2Many field để test widget  
    tag_ids = fields.Many2many(
        'test.tag',
        string='Tags'
    )


# =====================================================
# Line Model (One2Many)
# =====================================================
class TestLine(models.Model):
    _name = 'test.line'
    _description = 'Test Line Model'
    
    # Parent reference
    parent_id = fields.Many2one(
        'test.parent',
        string='Parent',
        required=True,
        ondelete='cascade'
    )
    
    # Basic fields
    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Numeric fields
    quantity = fields.Float(string='Quantity', digits=(12, 2), default=1.0)
    price = fields.Float(string='Price', digits=(12, 2))
    amount = fields.Float(
        string='Amount',
        compute='_compute_amount',
        store=True
    )
    
    # Relational fields (để test group by)
    category_id = fields.Many2one(
        'test.category',
        string='Category'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product'
    )
    
    # Selection field (để test group by)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')
    
    # Date fields (để test group by)
    date = fields.Date(string='Date', default=fields.Date.today)
    datetime = fields.Datetime(string='Date Time')
    
    # Boolean field (để test group by)
    is_active = fields.Boolean(string='Active', default=True)
    
    # Text fields
    note = fields.Text(string='Notes')
    
    @api.depends('quantity', 'price')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.price


# =====================================================
# Category Model (Master data)
# =====================================================
class TestCategory(models.Model):
    _name = 'test.category'
    _description = 'Test Category'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    color = fields.Integer(string='Color Index')


# =====================================================
# Tag Model (Many2Many)
# =====================================================
class TestTag(models.Model):
    _name = 'test.tag'
    _description = 'Test Tag'
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
