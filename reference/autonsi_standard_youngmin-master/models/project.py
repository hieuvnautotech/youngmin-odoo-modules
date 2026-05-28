from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Project(models.Model):
    _name = 'standard.project'
    _description = 'Project'
    _rec_name = 'code'

    image = fields.Binary("Image")
    code = fields.Char("Code", copy=False, index=True)
    name = fields.Char("Name")
    project_alias = fields.Char("Project Alias")
    project_status = fields.Selection([
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('not_used', 'Not Used'),
    ], string="Project Status", default="not_used")

    project_start = fields.Date(string="Start Date")
    project_end = fields.Date(string="End Date")
    project_period = fields.Char("Project Period", compute="_compute_project_period", store=True)

    remark = fields.Char("Remark")

    developer_charger = fields.Char("Developer Charger")
    check_drawing_consistency = fields.Char("Check Drawing Consistency")
    development_status = fields.Char("Developer Status")


    @api.depends('project_start', 'project_end')
    def _compute_project_period(self):
        for rec in self:
            if rec.project_start and rec.project_end:
                rec.project_period = f"{rec.project_start} ~ {rec.project_end}"
            else:
                rec.project_period = ""


    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('standard.project.code')
        return super().create(vals)

