# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Process(models.Model):
    _name = "standard.process"
    _description = "Process Model"
    _order = "sequence"
    _sql_constraints = [
        ("unique_model_code", "unique(name)", "Duplicated Process"),
    ]

    sequence = fields.Integer("Sequence")
    name = fields.Char("Name")
    code = fields.Char("Code")
    remark = fields.Char("Remark")
    location_id = fields.Many2one("stock.location", "Location",store=True)
    location_ids = fields.One2many(
        "stock.location",
        "process_id",
        string="Locations",
        store=True,
    )
    is_need_jig = fields.Boolean("Need Jig", default=False)
