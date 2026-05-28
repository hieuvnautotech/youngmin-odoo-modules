from odoo import fields, models, api


class Package(models.Model):
    _inherit = 'stock.quant.package'
    _order = 'sequence desc'

    ym_type = fields.Selection([
        ('big', 'Big Packing'),
        ('pallet_no_1', 'Pallet No'),
        ('pallet_no_2', 'Pallet No'),
        ('pallet_no_3', 'Pallet No'),
        ('pallet_1', 'Pallet Packing'),
        ('pallet_2', 'Pallet Packing'),
        ('pallet_3', 'Pallet Packing'),
        ('pallet', 'Pallet')
    ], string='YM Package Type')
    packing_state = fields.Selection(
        selection=[('not_yet', 'Not yet Packing'), ('packed', 'Packed'), ('shipped', 'Shipped')],
        string="Packing State", default='not_yet')
    total_qty = fields.Float(string="Total Qty")

    sequence = fields.Integer('Sequence')
    remark = fields.Char('Remark')

    @api.model
    def create(self, vals):

        package_type_name = self._context.get('package_type_name')
        if package_type_name:

            package_type = self.env['stock.package.type'].search([('name', '=', package_type_name)], limit=1)
            if package_type:
                vals['package_type_id'] = package_type.id

        return super(Package, self).create(vals)
