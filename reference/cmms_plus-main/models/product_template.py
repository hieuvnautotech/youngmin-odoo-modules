import ast
from datetime import date, datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from psycopg2 import IntegrityError


class ProductProduct(models.Model):
    _inherit = 'product.template'

    
    is_machine = fields.Boolean(string="Is Machine")
    is_jig = fields.Boolean(string="Is Jig")

    # maintenance_equipment_id =  fields.Many2one('maintenance.equipment', default=False,string="Equipment")
    
    # equipment_category =  fields.Char('Category', related="maintenance_equipment_id.category_id.name", readonly=True)
    # equipment_team =  fields.Char('Team', related="maintenance_equipment_id.maintenance_team_id.name", readonly=True)

    product_model_id = fields.Many2one('equipment.model', 'Product Model')


