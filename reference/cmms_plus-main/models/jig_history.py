from datetime import date, datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from psycopg2 import IntegrityError
from collections import defaultdict
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)

class JigHistory(models.Model):
    _name = 'jig.history'

    mo= fields.Char("MO")
    jig_id = fields.Many2one("product.product", domain=[('is_jig','=',True)], string="Jig", ondelete='cascade')

    jig_code = fields.Char(related="jig_id.asset_code", string="Jig Code", store=True)

    jig_type = fields.Many2one(related="jig_id.equip_category_id", string="Type", store=True)

    jig_name =  fields.Char(related="jig_id.name", string="Jig Name", store=True)
    product_name =  fields.Char(related="jig_id.jig_product_id.name", string="Product Name", store=True)

    factory_name = fields.Char(related="jig_id.jig_used_in_location_id.name", string="Factory", store=True)

    process = fields.Char(related="jig_id.process_id.name", string="Process", store=True)

    die_lifetime = fields.Integer(related="jig_id.die_lifetime", string="Die Lifetime", store=True)

    current_stroke_count = fields.Float( string="Current Stroke Count", store=True)

    operation_time= fields.Datetime( string="Operation Time", store=True,compute="_compute_operation_time")
    @api.depends('current_stroke_count')
    def _compute_operation_time(self):
        for rec in self:
            rec.operation_time = datetime.now()


    accumulated = fields.Float( string="Accumulated", store=True, compute="_compute_accumulated")
    @api.depends('current_stroke_count')
    def _compute_accumulated(self):
        for rec in self:
            rec.accumulated =rec.accumulated  + rec.current_stroke_count
            rec.jig_id.jig_accumulated = rec.accumulated


    #= die lifetime – Accumulated​
    #if remaining strokes =< 1,000 then change red color to warning.
    remaining_strokes = fields.Float( string="Remaining Strokes", compute="_compute_remaining_strokes", store=True)


    @api.depends('accumulated','die_lifetime')
    def _compute_remaining_strokes(self):
        for rec in self:
            rec.remaining_strokes =max( rec.die_lifetime  - rec.accumulated,0)
            rec.jig_id.remaining_strokes = rec.remaining_strokes
            
            #neu remaining_strokes <= 0, change status to scrap
            
            if rec.remaining_strokes <=0:
            
                rec.jig_id.status = 'scrap'
            


    def action_result_qc(self):
        pass

    def action_check_1(self):
        self.env['product.product'].search([]).write({'process_id': False})


    # @api.model
    # def init(self):
    #     # Nếu chưa có dữ liệu nào thì tự động tạo mẫu
    #     jigs = self.env["product.product"].search([('is_jig','=',True)])

    #     for jig in jigs:

    #         self.create({
    #             'jig_id':jig.id
    #         })
