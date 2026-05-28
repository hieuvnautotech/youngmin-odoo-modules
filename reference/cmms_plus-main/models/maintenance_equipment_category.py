from odoo import models, fields, api

class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    type = fields.Selection([('machine', 'Machine'),('mold', 'Mold')], default='machine', string="Type")
    is_mold = fields.Boolean(
        "Is Mold",
        compute="_compute_is_mold",
        store=True 
    )
    @api.depends('type')
    def _compute_is_mold(self):
        """ Compute whether the category type is 'mold'. """
        for record in self:
            record.is_mold = (record.type == "mold")


    @api.model
    def init(self):
        # Nếu chưa có dữ liệu nào thì tự động tạo mẫu
        if not self.search_count([]):
            default_items = [
                {"name": "Film"},
                 {"name": "Wood visual​"},
                  {"name": "Contour"},
                {"name": "Lamination"},
                 {"name": "Press"},

            ]
            self.create(default_items)


            


