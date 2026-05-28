from odoo import models, fields


class StandardProcess(models.Model):
    _name = "standard.process"
    _description = "Standard Process"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    line_ids = fields.One2many(
        comodel_name="standard.process.line",
        inverse_name="process_id",
        string="Process Lines",
    )


class StandardProcessLine(models.Model):
    _name = "standard.process.line"
    _description = "Standard Process Line"

    process_id = fields.Many2one(comodel_name="standard.process", string="Process", required=True, ondelete="cascade")
    project_id = fields.Many2one(comodel_name="standard.project", string="Project", ondelete="set null")
    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Char(string="Name", required=True)
    workcenter_id = fields.Many2one(comodel_name="mrp.workcenter", string="Workcenter")
    duration = fields.Float(string="Duration (hours)")
    note = fields.Text(string="Note")
