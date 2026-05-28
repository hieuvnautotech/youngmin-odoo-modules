from odoo import models, fields, api

class StandardProcessLine(models.Model):
    _name = 'standard.process.line'
    _description = 'Process Line'
    _order = 'process_id, name'

    process_id = fields.Many2one('standard.process', string='Process', required=True, ondelete='cascade')
    location_ids = fields.One2many(related='process_id.location_ids', string='Locations', readonly=True)
    number_of_lines = fields.Char(string='Number of Lines', required=True)
    name = fields.Char(string='Line #', compute='_compute_name', store=True)
    remark = fields.Char(string='Remark')
    location_id = fields.Many2one('stock.location', string='Location', required=True,
                                  domain="[('id', 'in', location_ids)]")
    
    @api.onchange('process_id')
    def _onchange_process_id(self):
        for line in self:
            line.location_id = line.process_id.location_ids[0] if len(line.process_id.location_ids) == 1 else False

    @api.depends('process_id', 'number_of_lines', 'location_id')
    def _compute_name(self):
        for line in self:
            location_name = line.location_id.name or ''
            if "Stock" in location_name:
                location_name = location_name.replace("Stock", "").strip()
            line.name = f"{location_name or ''} - {line.number_of_lines or ''}"
