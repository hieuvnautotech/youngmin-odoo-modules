from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class ProductCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char("Code")
    active = fields.Boolean("Active", default=True)
    mps_factory = fields.Selection([('swh', 'SW.H'), ('sh', 'S.H')], string="MPS Factory")
    display_name2 = fields.Char("Product Categories", related="display_name")

    @api.depends('name')
    def _compute_complete_name(self):
        for category in self:
            category.complete_name = category.name


class ProductPackingQty(models.Model):
    _name = 'product.packaging.qty'

    product_id = fields.Many2one('product.product', string='Product')
    packing_type = fields.Char('Packing Type')
    max_qty = fields.Integer('Max Qty')
    uom_id = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_id')


class Product(models.Model):
    _inherit = 'product.product'
    _order = 'create_date desc'

    uom_id2 = fields.Many2one('uom.uom', '2nd Unit of Measure')
    process_id = fields.Many2one('standard.process', 'Process Code', index=True)
    file = fields.Binary('File')
    description = fields.Char('Description')
    remark = fields.Char('Remark')
    supplier_material_ids = fields.Many2many('res.partner', index=True, domain=[('supplier_rank', '>', '0')])
    product_model_category = fields.Many2one('standard.model')
    product_type = fields.Selection(related='product_tmpl_id.product_type', string='Item Group', store=True, readonly=False)

    # _inherit
    project_id = fields.Many2one('standard.project', string='Project', related="product_tmpl_id.project_id", store=True, readonly=False)
    project_name = fields.Char(related='project_id.name', string='Project Name')
    product_category_id = fields.Many2one('standard.common.detail', string='Product Category', domain=[('master.name', '=', 'Product Category')])
    spec = fields.Char('Spec')
    item_use = fields.Selection([('y', 'Y'), ('n', 'N')], string='Item Use', default='n')
    sorting_qc = fields.Selection([('y', 'Y'), ('n', 'N')], string='Sorting QC', default='n')
    file_upload = fields.Binary('File', attachment=True, )
    file_upload_name = fields.Char('File Name')

    expire = fields.Integer('Life Day(s)', default=365)
    label_cost = fields.Float('Labor Cost')
    outsourcing_cost = fields.Float('Outsourcing Cost')
    price = fields.Float('Price', compute='_compute_price', store=True)
    semi_price = fields.Float('Price', related="list_price", readonly=False)
    material_price = fields.Float('Price', related="list_price", readonly=False)

    supplier_material = fields.Many2one('res.partner', string='Supplier', domain=[('supplier_rank', '>', '0')])
    material_category_id = fields.Many2one('standard.common.detail', string='Material Category', domain=[('master.name', '=', 'Material Category')])
    id_in_korea = fields.Char('ID In KOREA')

    douzone_erp_create_date = fields.Datetime(string="Douzone ERP Create Date")
    douzone_erp_update_date = fields.Datetime(string="Douzone ERP Update Date")
    is_vision_inspection = fields.Boolean(string="Vision Insp", default=False, compute='_compute_inspection_fields')
    is_double_inspection_and_packing = fields.Boolean(string="Double Insp", default=False, compute='_compute_inspection_fields')
    standard_qty = fields.Float('Standard Qty', default=0.0)
    wire_strand = fields.Float('Wire Strand', default=0.0)
    material_category_name = fields.Char(related='categ_id.name', string='Material Category Name', store=True)
    is_sample = fields.Boolean("Sample")
    product_category_domain = fields.Char(string='Product Category Domain', compute='_compute_product_category_domain')

    # packing
    product_packing_id = fields.Many2one('standard.common.detail', string='Packing Step',
                                         domain=[('master.name', '=', 'Product Packing')])
    packing_qty_ids = fields.One2many('product.packaging.qty', 'product_id', string='Packing Quantities')

    shipping_country_ids = fields.Many2many('standard.common.detail', string='Shipping Country', domain=[('master.name', '=', 'Shipping Country')])

    @api.onchange("product_packing_id")
    def _onchange_product_packing_id(self):
        if self.product_packing_id:
            self.packing_qty_ids = [(5, 0, 0)]
            if self.product_packing_id.small_packing:
                self.packing_qty_ids = [(0, 0, {'packing_type': 'Small Packs', 'max_qty': 0})]
            if self.product_packing_id.big_packing:
                self.packing_qty_ids = [(0, 0, {'packing_type': 'Big Packs', 'max_qty': 0})]
            if self.product_packing_id.pallet_packing:
                self.packing_qty_ids = [(0, 0, {'packing_type': 'Pallet', 'max_qty': 0})]
        else:
            self.packing_qty_ids = [(5, 0, 0)]

    def _compute_product_category_domain(self):
        common_record_product_category = self.env.ref('autonsi_standard_youngmin.product_category_fg')
        common_record_material_category = self.env.ref('autonsi_standard_youngmin.product_category_material')
        for rec in self:
            if rec.product_type == 'material':
                rec.product_category_domain = f"[('parent_id', '=', {common_record_material_category.id})]"
            elif rec.product_type == 'semi product':
                rec.product_category_domain = f"[]"
            elif rec.product_type == 'fg product':
                rec.product_category_domain = f"[('parent_id', '=', {common_record_product_category.id})]"
            else:
                rec.product_category_domain = f"[]"

    @api.constrains('id_in_korea')
    def _check_unique_id_in_korea(self):
        for record in self:
            if record.id_in_korea:
                existing_record = self.search([
                    ('id_in_korea', '=', record.id_in_korea),
                    ('id', '!=', record.id)
                ])
                if existing_record:
                    raise ValidationError(_('ID In Korea "%s" already exists! Please use a different value.') % record.id_in_korea)

    def _compute_inspection_fields(self):
        for rec in self:
            bom = rec.env['mrp.bom'].search([('product_id', '=', rec.id)], order='id desc', limit=1)
            if bom:
                rec.is_vision_inspection = bom.is_vision_inspection
                rec.is_double_inspection_and_packing = bom.is_double_inspection_and_packing
            else:
                rec.is_vision_inspection = False
                rec.is_double_inspection_and_packing = False

    @api.depends('label_cost', 'outsourcing_cost')
    def _compute_price(self):
        for rec in self:
            rec.price = (rec.label_cost or 0.0) + (rec.outsourcing_cost or 0.0)

    @api.depends('name', 'default_code', 'product_tmpl_id')
    @api.depends_context('display_default_code', 'seller_id', 'company_id', 'partner_id', 'use_partner_name')
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for rec in self.sudo():
            if rec.product_type in ['fg product', 'material', 'semi product'] and rec.default_code:
                rec.display_name = rec.default_code
        return res

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        res = super()._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)
        if not res and name:
            domain = domain or []
            match = re.search(r'(.+)\((.+)\)', name)
            if match:
                clean_name = match.group(1).strip()
                variant_part = match.group(2).strip()
                if not clean_name or not variant_part:
                    return res
                product_ids = list(self._search([('name', operator, clean_name)] + domain, limit=limit, order=order))
                if not product_ids:
                    return res
                products = self.browse(product_ids)
                filtered = products.filtered(
                    lambda p: variant_part.lower() in
                              (p.product_template_attribute_value_ids._get_combination_name() or '').lower()
                )
                if not filtered:
                    return res
                filtered = filtered[:limit] if limit else filtered
                res = filtered.ids

        return res

    def write(self, vals):
        if 'product_packing_id' in vals:
            for product in self:
                stock = self.env['stock.quant'].search([('product_id', '=', product.id), ('quantity', '>', 0)])
                if stock:
                    raise ValidationError("The Packing Type cannot be changed because the product is already in stock!")

        return super().write(vals)


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _order = 'create_date desc'

    create_by_bom_id = fields.Many2one('mrp.bom')
    product_model_id = fields.Many2one('standard.model', 'Model')
    product_type = fields.Selection([('material', 'MATERIAL'),
                                     ('semi product', 'SEMI'),
                                     ('fg product', 'FG')], index=True, string='Item Group')
    product_sub_type = fields.Selection([('auto', 'Auto'), ('manual', 'Manual')], index=True, string='Sub Type', default='manual')
    product_type_label = fields.Selection([('material', 'Material'), ('semi product', 'Semi Product')], index=True, string='Product Type Label')
    detailed_type = fields.Selection(default="product")
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')],
        string="Tracking", required=True, default='lot',
        # Not having a default value here causes issues when migrating.
        compute='_compute_tracking', store=True, readonly=False, precompute=True,
        help="Ensure the traceability of a storable product in your warehouse.")

    @api.depends('default_code')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.default_code}" if rec.default_code else ""

    project_id = fields.Many2one('standard.project', string='Project')
