from odoo import models, fields, api


class Common(models.Model):
    _name = 'standard.common'
    _description = 'Common'
    _order = 'sequence desc'
    _sql_constraints = [('unique_common_code', 'unique(name)', "Duplicated Common Code"), ]

    sequence = fields.Integer('Sequence')
    name = fields.Char('name', required=True, index=True)
    description = fields.Char('Description')
    remark = fields.Char('Remark')
    detail = fields.One2many('standard.common.detail', 'master', index=True)
    is_packing = fields.Boolean('Is Packing', default=False)

    def unlink(self):
        for item in self:
            item.detail.unlink()

        return super(Common, self).unlink()


class CommonDetail(models.Model):
    _name = 'standard.common.detail'
    _description = 'CommonDetail'
    _order = 'create_date desc'
    _sql_constraints = [('unique_commondetail_code', 'unique(name, master)', "Duplicated Detail Code"), ]

    name = fields.Char('name', required=True, index=True)
    code = fields.Char('Code')
    description = fields.Char('Description')
    remark = fields.Char('Remark')
    master = fields.Many2one('standard.common', 'master', required=True, index=True, ondelete='cascade')
    small_packing = fields.Boolean('Small Packing')
    big_packing = fields.Boolean('Big Packing')
    pallet_packing = fields.Boolean('Pallet Packing')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('name', operator, name), ('code', operator, name)]
        records = self.search(domain + args, limit=limit)
        return [(rec.id, rec.display_name) for rec in records]

    @api.model
    def default_get(self, fields_list):
        res = super(CommonDetail, self).default_get(fields_list)
        master_name = self.env.context.get("master_name", False)
        if master_name:
            master = self.env["standard.common"].search([("name", "=", master_name)], limit=1)
            if master:
                res["master"] = master.id
        return res
