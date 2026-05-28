from datetime import date, datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from psycopg2 import IntegrityError
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)

class ProductMachine(models.Model):
    _inherit = 'product.product'

    def getMachineFormViewId(self):
        return  self.env.ref('cmms_plus.cmms_plus_equipment_view_machine_form').id

    machine_code = fields.Char('Machine Code', )
    machine_name = fields.Char('Machine Name', )
  
    process_id = fields.Many2one("standard.process", string="Process",  ondelete="set null",)
    line_id = fields.Many2one("mrp.workcenter","Line")
    no_number = fields.Char("No#")
    process_name = fields.Char("Description2")
    date_of_manufacture = fields.Date("Date of manufacture",  )
    date_of_entry = fields.Date("Date of Entry",  )
    amount = fields.Float("Amount",  )

    #Local -> jig_used_in_location_id
    machine_department_id = fields.Many2one(
    "hr.department",
    string="Department",
    compute="_compute_machine_department_id",
    inverse="_inverse_machine_department_id",
    store=True
)
    @api.depends("department_code_import")
    def _compute_machine_department_id(self):
        for rec in self:
            if rec.department_code_import:
                dept = self.env["hr.department"].search([
                    ("code", "=", rec.department_code_import)
                ], limit=1)
                rec.machine_department_id = dept.id if dept else False

    def _inverse_machine_department_id(self):
        for rec in self:
            # Nếu user chọn Department trên UI thì không cập nhật code_import
            pass

    company_manufactor_id =  fields.Many2one('res.partner',"Company Name")
    company_name =  fields.Char("Company")
    seller_responsible =  fields.Char("Responsible Person​")
    seller_contact=  fields.Char("Contact​")

    #For import function
    lead_name_import = fields.Char("Phu Trach Chinh Import")
    deputy_name_import = fields.Char("Phu Trach Phu Import")
    department_code_import = fields.Char("Department Import")
    is_machine_import = fields.Char("Is Machine Import")
    is_jig_import = fields.Char("Is jig Import")



    deputy_id= fields.Many2one("hr.employee",string="Deputy" ,  compute="_compute_deputy_id",
        inverse="_inverse_deputy_id",store=True )
    def _inverse_deputy_id(self):
        for rec in self:
            pass

    @api.depends('deputy_name_import')
    def _compute_deputy_id(self):
        for rec in self:
            employee = self.env['hr.employee'].search([
                ('name', '=', rec.deputy_name_import)
            ], limit=1)
            rec.deputy_id = employee.id if employee else False


    lead_id = fields.Many2one(
        "hr.employee",
        string="Lead",
        compute="_compute_lead_id",
        inverse="_inverse_lead_id",
        store=True
    )
    def _inverse_lead_id(self):
        for rec in self:
            pass

    @api.depends('lead_name_import')
    def _compute_lead_id(self):
        for rec in self:
            employee = self.env['hr.employee'].search([
                ('name', '=', rec.lead_name_import)
            ], limit=1)
            rec.lead_id = employee.id if employee else False









    















  


