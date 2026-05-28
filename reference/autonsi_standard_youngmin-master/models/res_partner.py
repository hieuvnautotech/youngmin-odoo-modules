from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    code = fields.Char("Code", copy=False, index=True)
    alias = fields.Char("Alias")
    business_reg_number = fields.Char("Business Reg. Number")
    business_category = fields.Char("Business Category")
    business_type = fields.Char("Business Type")
    representative_name = fields.Char("Representative Name")
    fax = fields.Char("Fax")
    description = fields.Char("Description")
    douzone_erp_create_date = fields.Datetime(string="Douzone ERP Create Date")
    douzone_erp_update_date = fields.Datetime(string="Douzone ERP Update Date")


    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            if record.code:
                if record.customer_rank > 0:
                    duplicate_records = self.search([('id', '!=', record.id), (
                        'code', '=', record.code), ('customer_rank', '>', 0)])
                    if duplicate_records:
                        raise ValidationError(_('Duplicate Buyer Code'))
                if record.supplier_rank > 0:
                    duplicate_records = self.search([('id', '!=', record.id), (
                        'code', '=', record.code), ('supplier_rank', '>', 0)])
                    if duplicate_records:
                        raise ValidationError(_('Duplicate Supplier Code'))

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('res.partner.code')
        return super().create(vals)