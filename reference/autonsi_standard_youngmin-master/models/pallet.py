from odoo import models, fields, api


class Pallet(models.Model):
    _name = 'standard.pallet'
    _description = 'Pallet'
    _order = 'create_date desc'

    name = fields.Char('Pallet No', index=True)
    description = fields.Char('Description')
    remark = fields.Char('Remark')

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('standard.pallet.pallet_no')
        return super().create(vals)