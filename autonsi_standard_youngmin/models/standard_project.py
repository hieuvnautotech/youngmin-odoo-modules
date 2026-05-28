from odoo import models, fields


class StandardProject(models.Model):
    _name = "standard.project"
    _description = "Standard Project"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    alias = fields.Char(string="Alias")
    project_start = fields.Date(string="Start Date")
    project_end = fields.Date(string="End Date")
    project_period = fields.Char(string="Period")
    project_status = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("closed", "Closed"),
    ], string="Status", default="draft", tracking=True)
    developer_charger = fields.Char(string="Developer In Charge")
    development_status = fields.Selection([
        ("developing", "Developing"),
        ("released", "Released"),
        ("discontinued", "Discontinued"),
    ], string="Development Status", default="developing")
    check_drawing_consistency = fields.Boolean(string="Check Drawing Consistency")
    image = fields.Binary(string="Image")
    remark = fields.Text(string="Remark")

    process_line_ids = fields.One2many(
        comodel_name="standard.process.line",
        inverse_name="project_id",
        string="Process Lines",
    )
