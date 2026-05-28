from odoo import models, fields, api


class Staff(models.Model):
    _inherit = 'hr.employee'
    _order = 'sequence desc'

    sequence = fields.Integer('Sequence')
    staff_code = fields.Char(string='Code')
    remark = fields.Char('Remark')
    address = fields.Char('Address')

    @api.model
    def create(self, vals):
        if not vals.get('staff_code'):
            vals['staff_code'] = self.env['ir.sequence'].next_by_code('hr.employee.staff_code')
        return super().create(vals)
