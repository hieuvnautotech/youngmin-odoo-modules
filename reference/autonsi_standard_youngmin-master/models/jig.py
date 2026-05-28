from odoo import models, fields, api


class StandardJig(models.Model):
    _name = 'standard.jig'
    _description = 'Jig'
    _order = 'create_date desc'

    type = fields.Selection(
        [('film', 'Film'),
        ('contour', 'Contour'),
        ('wood', 'Wood'),
        ('lamination', 'Lamination'),
        ('press', 'Press'),], default='film', string='Type Jig')

    code = fields.Char('Jig Code', index=True)
    name = fields.Char('Jig Name')
    supplier = fields.Many2one('res.partner', string='Supplier', domain=[('supplier_rank', '>', '0')])
    product_id = fields.Many2one('product.product', string='Product', domain=[('product_type', '=', 'fg product')])
    process_id = fields.Many2one('mrp.bom.process', string='Process')
    location_id = fields.Many2one('stock.location', string='Location')
    accumulated = fields.Float(string='Accumulated', default=0.0)
    die_lifetime = fields.Float(string='Die Lifetime', default=100000.0)
    remaining_strokes = fields.Float(string='Remaining Strokes', compute='_compute_remaining_strokes')
    remark = fields.Char('Remark')
    REV = fields.Integer('REV', default=0)

    status = fields.Selection(
        [('in_use', 'In Use'),
         ('stock', 'Stock'),
         ('scrap', 'Scrap'), ], default='in_use', string='Type Status')

    qc_status = fields.Selection(
        [('ok', 'OK'),
         ('ng', 'NG'),], default='ok', string='QC Status')

    @api.depends('die_lifetime', 'accumulated')
    def _compute_remaining_strokes(self):
        for rec in self:
            rec.remaining_strokes = (rec.die_lifetime or 0.0) - (rec.accumulated or 0.0)
