from odoo import models, fields


class StandardCommon(models.Model):
    _name = "standard.common"
    _description = "Standard Common"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    active = fields.Boolean(string="Active", default=True)
    detail_ids = fields.One2many(
        comodel_name="standard.common.detail",
        inverse_name="common_id",
        string="Details",
    )


class StandardCommonDetail(models.Model):
    _name = "standard.common.detail"
    _description = "Standard Common Detail"

    common_id = fields.Many2one(comodel_name="standard.common", string="Common", required=True, ondelete="cascade")
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)
