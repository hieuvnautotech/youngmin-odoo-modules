from odoo import models, fields, api

class EquipmentModel(models.Model):
    _name = 'equipment.model'

    name = fields.Char('Name')

    equip_category_id = fields.Many2one('maintenance.equipment.category', string="Category")

    remark = fields.Char('Remark')
    
    model_type = fields.Selection([
        ('product', 'Product'),
        ('mold', 'Mold'),
        ('machine', 'Machine'),
        ('tool', 'Tool'),

    ], string='Model Type', default='product')


   
            


