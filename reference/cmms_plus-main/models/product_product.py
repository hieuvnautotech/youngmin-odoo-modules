from datetime import date, datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, tools, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from psycopg2 import IntegrityError
from collections import defaultdict
from odoo.osv.expression import AND
import json
import base64
from math import ceil
import logging
import os
_logger = logging.getLogger(__name__)

page_units_size = 6

class ProductProduct(models.Model):
    _inherit = 'product.product'
    _order = "id desc"

    

    def getJigFormViewId(self):
        return  self.env.ref('cmms_plus.cmms_plus_equipment_view_form').id
    
    def getMachineFormViewId(self):
        return  self.env.ref('cmms_plus.cmms_plus_equipment_view_machine_form').id
    
    def getMachineListViewId(self):
        return  self.env.ref('cmms_plus.cmms_plus_equipment_view_tree_machine').id
    
    def getJigListViewId(self):
        return  self.env.ref('cmms_plus.cmms_plus_equipment_view_tree').id
    
    def getSearchViewHistoryId(self):
        return  self.env.ref('cmms_plus.view_jig_history_search').id
    
    
    
    def getKanbanViewId(self):
        return  self.env.ref('cmms_plus.view_product_product_kanban_custom').id
    
    def getSearchView(self):
        return  self.env.ref('cmms_plus.cmms_plus_product_product_search_view').id
        

    equip_lot_name=fields.Char("Equip Lot Name")
    asset_code=fields.Char('Code')
    
    asset_custom_declaration=fields.Char('Custom Declaration')
    asset_inv_number=fields.Char('INV Number')
    asset_serial_number=fields.Char('Serial Number')
    asset_price=fields.Float('Unit Price')

    equip_name = fields.Char('Equipment Name', )
    equip_used_in_location_id = fields.Many2one('stock.location', string="Used in Location")
    equip_department = fields.Many2one('hr.department', string="Department")

    equip_employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
    )
 

    equip_active = fields.Boolean(default=True)
    equip_technician_user_id = fields.Many2one('res.users', string='Technician', tracking=True)
    equip_owner_user_id = fields.Many2one('res.users', string='Owner', tracking=True)
    equip_category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category',
                                  tracking=True, group_expand='_read_group_category_ids')
    
    is_equipment_mold = fields.Boolean(string="Is Mold", related="equip_category_id.is_mold", readonly=True)

    equip_partner_id = fields.Many2one('res.partner', string='Vendor')

    jig_product_id = fields.Many2one('product.product', domain=[('product_type','=','fg product'),('is_jig','=', False),('is_machine','=', False)], string="Product")

    process_id = fields.Many2one("standard.process", string="Process",  ondelete="set null",)

    jig_accumulated = fields.Integer("Accumulated", readonly=True) 

    jig_used_in_location_id = fields.Many2one('stock.location', string="Location")
    
    jig_used_in_location_id_2 = fields.Selection([('swh', 'SW.H'),
                                    ('sh', 'S.H'), 
                               
                                   ], default="swh", index=True)
                                   
                                   
    die_lifetime =  fields.Integer("Die Lifetime", default=100000)

    remaining_strokes =  fields.Integer("Remaining Strokes", readonly=True)

    rev = fields.Char("Rev")
    remark = fields.Char("Remark")


    position = fields.Char("Position")

    jig_status_qc =  fields.Selection([('not_yet', 'Not Yet'),
                                    ('ng', 'NG'), 
                                     ('ok', 'OK'), 
                                   ], default="not_yet", index=True)

    status = fields.Selection([('in_use', 'In Use'),
                                    ('stock', 'Stock'), 
                                     ('scrap​', 'Scrap​'), 
                                   ], default="stock", index=True)
    

    jig_type_import   = fields.Char("Jig Type Import")
    vender_import   = fields.Char("Vender Import")
    location_import  = fields.Char("Location Import")
    product_name_import = fields.Char("Product Name Import")
    process_name_import = fields.Char("Process Name")

    
    # image_company_logo = fields.Text("Company Logo", compute="_compute_hex_image_company_logo", store=True)
    # @api.depends('image_1920') 
    # def _compute_hex_image_company_logo(self):
    #     for record in self:
    #             data  ="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"
    #             record.image_company_logo ="__zpl_image__" + data


    @api.model
    def init(self):
        # 1. Tạo phòng ban nếu chưa tồn tại
        department = self.env['hr.department'].search([('code', '=', 'D001')], limit=1)
        if not department:
            department = self.env['hr.department'].create({
                'code': 'D001',
                'name': 'Đội quản lý sản xuất'
            })

        # 2. Tạo hoặc lấy user NHƯỜNG
        user_1 = self._create_user_with_employee(
            name="NHƯỜNG",
            login="nhuong",
            password="123456",
            department=department
        )

        # 3. Tạo hoặc lấy user DŨNG
        user_2 = self._create_user_with_employee(
            name="DŨNG",
            login="dung",
            password="123456",
            department=department
        )

        #4. Create partner
        if not self.env['res.partner'].search([('alias', '=', 'HƯNG THỊNH')], limit=1):
             self.env['res.partner'].create({
                'name':'HƯNG THỊNH','alias':'HƯNG THỊNH'
            })

        #5. create process
        if not self.env['standard.process'].search([('name', '=', 'Tape')], limit=1):
            self.env['standard.process'].create({
                    'code':'tape','name':'Tape'
                })
        
        if not self.env['standard.process'].search([('name', '=', 'Forming')], limit=1):
            self.env['standard.process'].create({
                    'code':'forming','name':'Forming'
                })
            

        if not self.env['stock.location'].search([('name','=','1')], limit= 1):
            parent_id =  self.env['stock.location'].search([('name','=','WIP')], limit= 1)
            record = self.env['stock.location'].create({'name':'1', 'location_id':parent_id.id})

    # =============================
    # Hàm tiện ích tạo user + employee
    # =============================
    def _create_user_with_employee(self, name, login, password, department):
        Users = self.env['res.users']
        Employee = self.env['hr.employee']

        # Nếu user đã tồn tại → lấy nó
        user = Users.search([('login', '=', login)], limit=1)
        if not user:
            user = Users.create({
                'name': name,
                'login': login,
                'password': password,
            })

        # 1. Gán quyền system admin (tùy bạn)
        admin_group = self.env.ref('base.group_system', raise_if_not_found=False)
        if admin_group:
            admin_group.sudo().write({'users': [(4, user.id)]})

        # 2. Nếu employee chưa tồn tại → tạo
        employee = Employee.search([('work_email', '=', login)], limit=1)
        if not employee:
            employee = Employee.create({
                'name': name,
                'work_email': login,
                'user_id': user.id,        # liên kết employee → user
                'department_id': department.id
            })
        else:
            # cập nhật lại nếu thiếu
            employee.write({
                'user_id': user.id,
                'department_id': department.id
            })

        # 3. Gán employee vào user (2 chiều)
        if not user.employee_ids:
            user.employee_ids = [(4, employee.id)]

        return user

    @staticmethod
    def _encode_image_to_base64(image_path):
        """
        Encode an image file to a base64 string.
        :param image_path: Path to the image file.
        :return: Base64 string of the image.
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            _logger.error(f"Error reading image {image_path}: {e}")
            return None
        
    @api.model
    def create(self, vals):
        if vals.get('jig_type_import'):
            #la t6n của type nhu Wood visual​
            record = self.env['maintenance.equipment.category'].search(['name','=',vals.get('jig_type_import')], limit=1)
            vals['equip_category_id'] = record.id

        if vals.get('vender_import'):
            #la name nhu: Hung Thinh
            record = self.env['res.partner'].search([('alias', '=', vals.get('vender_import'))], limit=1)
            vals['equip_partner_id'] = record.id

        

        if vals.get('location_import'):
            record = False
            if vals.get('process_name_import')=='Forming' and vals.get('location_import')=="WH/WIP 1":
                record = self.env['stock.location'].search([('name', '=', 'Forming Stock 1')], limit=1)

            if vals.get('process_name_import')=='Forming' and vals.get('location_import')=="WH/WIP 2":
                record = self.env['stock.location'].search([('name', '=', 'Forming Stock 2')], limit=1)

            if vals.get('process_name_import')=='Tape' and vals.get('location_import')=="WH/WIP 1":
                record = self.env['stock.location'].search([('name', '=', 'Tape Stock 1')], limit=1)

            if vals.get('process_name_import')=='Tape' and vals.get('location_import')=="WH/WIP 2":
                record = self.env['stock.location'].search([('name', '=', 'Tape Stock 2')], limit=1)


        if vals.get('product_name_import'):
            product=  self.env['product.product'].search([('name', '=', vals.get('product_name_import'))], limit=1)
            if not  product:
                product = self.env['product.product'].create({'name':vals.get('product_name_import'), 'code':vals.get('product_name_import')})
          
            vals['jig_product_id'] = product.id
        



        if vals.get('is_machine_import'):
            vals['is_machine'] =True if vals.get('is_machine_import') =="TRUE" else False
        else:
            vals['is_machine']=  self.env.context.get('is_machine', False)


        if vals.get('is_jig_import'):
            vals['is_jig'] =True if vals.get('is_jig_import') =="TRUE" else False
        else:
            vals['is_jig']= self.env.context.get('is_jig', False)


        if not vals.get('asset_code') and vals['is_jig']:
            # Fetch the next sequence value
            sequence = self.env['ir.sequence'].next_by_code('jig.code.sequence')
            vals['asset_code'] = sequence or '/'
        

        if not vals.get('machine_code') and vals['is_machine']:
            # Fetch the next sequence value
            sequence = self.env['ir.sequence'].next_by_code('machine.code.sequence')
            vals['machine_code'] = sequence or '/'
            vals['asset_code'] = sequence or '/'
            
        if vals['is_machine']:
            vals['name']=vals['machine_name']


        if 'image_1920' not in vals and vals.get('is_machine'):
            module_path = os.path.dirname(os.path.abspath(__file__))
             # Navigate to the root of the module
            module_root_model_path = os.path.abspath(os.path.join(module_path, '..'))
           # module_root_path = os.path.abspath(os.path.join(module_root_model_path, '..'))
            img1_path = os.path.join(module_root_model_path, "static/src/img/m_logo.png")
            vals['image_1920'] = self._encode_image_to_base64(img1_path)


        record = super(ProductProduct, self).create(vals)

        if vals['is_jig']:
            #tạo history jig
            self.env["jig.history"].create({
                'jig_id':record.id
            })
            
            
        return record
    
    def unlink(self):
        # Tìm và xóa các history tương ứng
        for rec in self:
            if rec.is_jig:
                histories = self.env['jig.history'].search([('jig_id', '=', rec.id)])
                if histories:
                    histories.unlink()
        # Sau đó mới xóa product
        return super(ProductProduct, self).unlink()
    

    def get_machine_units(self, domain, page=1):
        # Base domain mặc định
        base_domain = [('is_machine', '=', True)]
        
        # Gộp domain người dùng gửi vào (AND)
        full_domain = AND([base_domain, domain])

        # Tính tổng số record hợp lệ
        total_count = self.env['product.product'].search_count(full_domain)
        total_pages = ceil(total_count / page_units_size)

        # Tính toán offset cho phân trang
        offset = (page - 1) * page_units_size

        # Lấy dữ liệu theo trang
        machines = self.env['product.product'].search(full_domain, offset=offset, limit=page_units_size)

        # Build response
        result = [{
            'id': m.id,
            'name': m.machine_name,
            'code': m.machine_code,
            'no_number': m.no_number,
            'is_lazy': False,
        } for m in machines]



        return {
            'items': result,
            'total_count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'next_page': page + 1 if page < total_pages else page,  
        }
    

    def get_jig_units(self, jtype_id, domain, page):
        domain_base = [('equip_category_id', '=', jtype_id),('is_jig', '=', True)]
        
        # Merge base domain with client-provided domain
        full_domain = AND([domain_base, domain])

        # Count total records for this filter
        total_count = self.env['product.product'].search_count(full_domain)
        total_pages = ceil(total_count / page_units_size)

        # Pagination logic
        offset = (page-1 ) * page_units_size
        jigs = self.env['product.product'].search(full_domain, offset=offset, limit=page_units_size)

        result = []
        for jig in jigs:
            result.append({
                'id': jig.id,
                'name': jig.name,
                'code': jig.asset_code,
                'is_lazy': False
            })

        return {
            'items': result,
            'total_count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'next_page': page + 1 if page < total_pages else page
            
        }
    
    
    def get_jig_info(self, jig_id):
        jigs = self.env['product.product'].search([('id','=',jig_id)], limit=1)
        result = []
        for jig in jigs:
          
            result.append({
                'id': jig.id,
                'name': jig.name,
                'code':jig.asset_code,
                'jig_product_id':jig.jig_product_id,
                'process_id':jig.process_id,
                'jig_accumulated':jig.jig_accumulated,
                'jig_used_in_location_id':jig.jig_used_in_location_id,
                'die_lifetime':jig.die_lifetime,
                'remaining_strokes':jig.remaining_strokes,
                'rev':jig.rev,
                'remark':jig.remark,
                'jig_status_qc':jig.jig_status_qc,
                'status':jig.status,

                'is_lazy':False
            })

        return result


    def get_category_equipment_types(self):
        categories = self.env['maintenance.equipment.category'].search([('type', '=', 'machine')])
        result = []

        for category in categories:
            # Count total products in this category
            product_model = self.env['product.product']
            domain = [('equip_category_id', '=', category.id)]
            total_count = product_model.search_count(domain)

            

            # Calculate pagination info
            total_pages = ceil(total_count / page_units_size)
           

            # Query paginated products (if needed for frontend)
            # products = product_model.search(domain, offset=(nextpage - 1) * page_size, limit=page_size)

            result.append({
                'id': category.id,
                'name': category.name,
                'has_products': total_count > 0,
                'total_count': total_count,
                'total_pages': total_pages,
              
            })

        return result
    

    def action_check_jig(self):
        pass

    def action_print_qr_code(self):
        active_ids = self.env.context.get("active_ids", [])
        return self.env["zld.label"].show_print_dialog("AssetsQR", active_ids)

        