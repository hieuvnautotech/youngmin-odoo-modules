from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND, OR

class BomLine(models.Model):
    _inherit = 'mrp.bom.line'

    qty_no_loss = fields.Float("Quantity", default=1, digits="Product Unit of Measure")
    level = fields.Integer('Level', default=0)
    loss = fields.Float('Loss %', default=0, digits="Product Unit of Measure")
    source_location_id = fields.Many2one(
        "stock.location", string="Source Location")
    destination_location_id = fields.Many2one(
        "stock.location", string="Destination Location")
    process_id = fields.Many2one('standard.process', 'Process Code')

    product_type = fields.Selection(related='product_id.product_type', string='Product Type')

    @api.onchange('qty_no_loss', 'loss')
    def _compute_qty(self):
        for rec in self:
            rec.product_qty = (rec.qty_no_loss or 0) * ( 1 + rec.loss or 0)

class BOMProcess(models.Model):
    _name = 'mrp.bom.process'
    _description = 'Bom Process'
    _order = 'sequence,create_date'

    name = fields.Many2one(
        'standard.process', 'Process Name', required=True, index=True)
    process_code = fields.Char(related='name.code', string='Process Code')
    bom_id = fields.Many2one(
        'mrp.bom', 'bom', required=True, index=True, ondelete='cascade')
    material_ids = fields.One2many(
        'mrp.bom.process.material', 'bomprocess_id', index=True)
    duration = fields.Integer('Duration')
    durationComputation = fields.Integer('Duration Computation')
    tool_ids = fields.Many2many('standard.common.detail', index=True, domain=[
        ('master.name', '=', 'MoldType')])
    parent_id = fields.Many2one('standard.process', 'Parent Code')
    sequence = fields.Integer('Sequence', default=1)
    level = fields.Integer('Level', compute='compute_level')
    state = fields.Selection(related="bom_id.state", string="State")
    source_location_id = fields.Many2one(
        "stock.location", string="Source Location")
    destination_location_id = fields.Many2one(
        "stock.location", string="Destination Location")

    # inherit
    target_product_id = fields.Many2one('product.product', 'Target Product')
    target_image = fields.Binary('Target Image', attachment=True)
    target_image_name = fields.Char('Target Image Name')

    def compute_level(self):
        for record in self:
            record.level = record.sequence

    @api.model
    def _default_level(self):
        max_level = self.env['mrp.bom.process'].search(
            [('bom_id', '=', self.bom_id.id)], order='level desc', limit=1).level
        return max_level + 1 if max_level else 1

    @api.constrains('name', 'parent_id')
    def _check_parent_id_not_same_as_name(self):
        for record in self:
            if record.name == record.parent_id:
                raise ValidationError(
                    f"Next Process cannot be the same as the Process Code: {record.parent_id.name}")

    def action_open_material_popup(self):
        return {
            'target': 'new',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'name': _('Add Material List'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom.process',
            'views': [(self.env.ref('autonsi_standard_youngmin.view_bom_material_popup_form').id, 'form')],
        }

    def unlink(self):
        for process in self:
            process.material_ids.unlink()
        return super(BOMProcess, self).unlink()


class BOMProcessMaterial(models.Model):
    _name = 'mrp.bom.process.material'
    _description = 'Bom Process Material'
    _order = 'name'
    # _sql_constraints = [
    #     ('unique_bpm_code', 'unique(name, bomprocess_id)', "Duplicated Material"),]
    # _sql_constraints = [
    #     ('unique_bpm_code', 'unique(name, bomprocess_id)', "Duplicated Material"),]

    name = fields.Many2one('product.product', 'Material', required=True, index=True, domain=[
        '|', ('product_type', '=', 'semi product'), ('product_type', '=', 'material'),
        ('product_sub_type', '=', 'manual')])
    product_name = fields.Char(related='name.name', string='Product Name')
    product_spec = fields.Char(related='name.spec', string='Spec')
    quantity = fields.Float(string='Quantity', default=1, digits="Product Unit of Measure")
    unit = fields.Many2one('uom.uom', 'Unit')
    weight_value = fields.Float('Weight Value', default=1, digits="Product Unit of Measure")
    loss_percent = fields.Float('Loss %', digits="Product Unit of Measure")
    bomprocess_id = fields.Many2one(
        'mrp.bom.process', 'bomprocess', required=True, index=True, ondelete='cascade')
    product_type = fields.Selection(related='name.product_type', string='Item Group')
    required_qty = fields.Float('Required Quantity', compute='_compute_required_qty', digits="Product Unit of Measure")
    process_id = fields.Many2one('standard.process', related="bomprocess_id.name", string="Process")
    source_location_id = fields.Many2one(
        "stock.location", string="Source Location", related="bomprocess_id.source_location_id")
    destination_location_id = fields.Many2one(
        "stock.location", string="Destination Location", related="bomprocess_id.destination_location_id")
    bom_id = fields.Many2one("mrp.bom", related="bomprocess_id.bom_id")

    @api.depends('quantity', 'loss_percent')
    def _compute_required_qty(self):
        for rec in self:
            rec.required_qty = (rec.quantity or 0) * ( 1 + rec.loss_percent or 0)


    def _find_target_bom(self):
        """Tìm BOM của target_product_id được tạo từ BOM FG gốc"""
        if not self.bomprocess_id or not self.bomprocess_id.target_product_id:
            return False

        target_product = self.bomprocess_id.target_product_id

        # Tìm BOM gốc (FG) tạo ra BOM hiện tại
        current_bom = self.bom_id
        root_fg_bom = current_bom
        while root_fg_bom.create_by_bom_id:
            root_fg_bom = root_fg_bom.create_by_bom_id

        # Tìm BOM của target_product được tạo từ BOM FG gốc
        target_bom = self.env['mrp.bom'].search([
            ('product_id', '=', target_product.id),
            ('create_by_bom_id', '=', root_fg_bom.id)
        ], limit=1)

        return target_bom

    def _update_target_bom_line(self, operation='create'):
        """Cập nhật bom line trong BOM target tương ứng"""
        target_bom = self._find_target_bom()
        
        
        if self.bom_id.state != "confirmed":
            return
        if self.bom_id.process_ids and self.bomprocess_id == self.bom_id.process_ids[-1]:
            target_bom = self.bom_id
        if not target_bom:
            return

        if operation == 'create':
            # Thêm bom line mới
            target_bom.write({
                'bom_line_ids': [(0, 0, {
                    'product_id': self.name.id,
                    'qty_no_loss': self.quantity,
                    'loss': self.loss_percent,
                    'product_qty': self.required_qty,
                    'product_uom_id': self.unit.id if self.unit else self.name.uom_id.id,
                    'process_id': self.process_id.id,
                    'source_location_id': self.source_location_id.id,
                    'destination_location_id': self.destination_location_id.id,
                })]
            })
        elif operation == 'write':
            # Tìm và cập nhật bom line hiện có
            existing_line = target_bom.bom_line_ids.filtered(
                lambda line: line.product_id.id == self.name.id
            )
            if existing_line:
                existing_line.write({
                    'qty_no_loss': self.quantity,
                    'loss': self.loss_percent,
                    'product_qty': self.required_qty,
                    'product_uom_id': self.unit.id if self.unit else self.name.uom_id.id,
                    'process_id': self.process_id.id,
                    'source_location_id': self.source_location_id.id,
                    'destination_location_id': self.destination_location_id.id,
                })
        elif operation == 'unlink':
            # Xóa bom line tương ứng
            existing_line = target_bom.bom_line_ids.filtered(
                lambda line: line.product_id.id == self.name.id
            )
            if existing_line:
                existing_line.unlink()

    @api.model
    def create(self, vals_list):
        record = super().create(vals_list)
        record._update_target_bom_line('create')
        return record

    def write(self, vals):
        result = super().write(vals)
        for record in self:
            record._update_target_bom_line('write')
        return result

    def unlink(self):
        for record in self:
            record._update_target_bom_line('unlink')
        return super().unlink()

class BOM(models.Model):
    _inherit = 'mrp.bom'
    _order = 'create_date desc'

    model_id = fields.Many2one('standard.model', 'Model')
    spec_no = fields.Char("Spec No")
    description = fields.Char("Description")
    process_ids = fields.One2many('mrp.bom.process', 'bom_id', index=True)
    duration_ids = fields.One2many('mrp.bom.process', 'bom_id', index=True)
    tool_ids = fields.One2many('mrp.bom.process', 'bom_id', index=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
        string="State"
    )
    fg_bom_is = fields.Boolean('FG Bom', compute='_compute_fg_bom_is', store=True)
    material_status = fields.Char('Materials', compute='compute_Materials')
    bom_type = fields.Selection(
        [('basic', 'Basic'), ('manufacturing', 'Manufacturing')], index=True, default='basic', string='BOM Type')

    # bom_inherit
    project_id = fields.Many2one('standard.project', string='Project Name', related="product_tmpl_id.project_id")
    # default_code = fields.Char(related='product_tmpl_id.default_code', string='Product Code')
    default_name = fields.Char(related='product_tmpl_id.name', string='Product Name')

    name = fields.Char('BOM Name')
    bom_version = fields.Integer('BOM Ver', default=0)
    project_code = fields.Char(related='project_id.code', string='Project Code')
    create_by_bom_id = fields.Many2one('mrp.bom', 'Created By BOM', index=True)

    is_vision_inspection = fields.Boolean(string="Vision Insp", default=False, compute='_compute_inspection_fields')
    is_double_inspection_and_packing = fields.Boolean(string="Double Insp", default=False,
                                                      compute='_compute_inspection_fields')
    file_imported = fields.Binary(string="File Imported")
    filename_imported = fields.Char(string="Filename Imported")
    bom_process_material_ids = fields.One2many('mrp.bom.process.material', compute='_compute_bom_process_material_ids', readonly=False)
    product_type = fields.Selection(related='product_tmpl_id.product_type', string='Item Group')

    def _compute_bom_process_material_ids(self):
        for rec in self:
            rec.bom_process_material_ids = rec.process_ids.sorted('sequence').mapped('material_ids')

    def _compute_inspection_fields(self):
        for rec in self:
            vision_inspection = self.env.ref('autonsi_standard_youngmin.common_record_process_480_vision_inspection')
            double_inspection = self.env.ref('autonsi_standard_youngmin.common_record_process_510_double_insp_packing')
            if vision_inspection in rec.process_ids.mapped('name'):
                rec.is_vision_inspection = True
            else:
                rec.is_vision_inspection = False
            if double_inspection in rec.process_ids.mapped('name'):
                rec.is_double_inspection_and_packing = True
            else:
                rec.is_double_inspection_and_packing = False

    @api.depends('product_tmpl_id', 'product_tmpl_id.product_type')
    def _compute_fg_bom_is(self):
        for record in self:
            if record.product_tmpl_id.product_type == 'fg product':
                record.fg_bom_is = True
            else:
                record.fg_bom_is = False
    
    def find_semi_target_qty(self, process: BOMProcess, process_list: BOMProcess):
        """
        Tìm kiếm trong material_ids của các process trong process_list,
        xem có field product_id == process.target_product_id thì lấy target_qty = product_qty,
        không tìm ra thì trả về 1.
        """
        target_product = process.target_product_id
        for proc in process_list:
            for material in proc.material_ids:
                if material.name.id == target_product.id:
                    return material.quantity
        return 1


    def action_confirm(self):
        for record in self:
            if record.state == 'draft':
                record.connect_process()

                # process_list = record.process_ids.sorted(
                #     key=lambda r: r.sequence, reverse=True)
                process_list = record.process_ids

                if process_list:
                    index = 0
                    # if process_list[index]:
                    #     record.create_component(process_list, index, False)

                    for process in process_list:
                        component_list = []
                        if process == process_list[-1]:
                            continue
                        for material in process.material_ids:
                            component_list.append((0, 0, {
                                'product_id': material.name.id,
                                'qty_no_loss': material.quantity,
                                'loss': material.loss_percent,
                                'product_qty': material.required_qty,
                                'product_uom_id': material.unit.id if material.unit else material.name.uom_id.id,
                                'process_id': process.name.id,
                                'source_location_id': process.source_location_id.id,
                                'destination_location_id': process.destination_location_id.id,
                            }))
                        if len(component_list) == 0:
                            raise ValidationError(
                                _('Please add material for process %s' % (process.name.name)))
                        # if process.target_product_id.bom_ids:
                        #     process.target_product_id.bom_ids.unlink()

                        bom_process = self.env['mrp.bom'].create({
                            'product_tmpl_id': process.target_product_id.product_tmpl_id.id,
                            'state': 'confirmed',
                            'bom_line_ids': component_list,
                            'create_by_bom_id': record.id,
                            'product_id': process.target_product_id.id,
                            'product_qty': self.find_semi_target_qty(process, process_list)
                        })

                    # last process
                    last_process = process_list[-1]
                    component_list = []
                    for material in last_process.material_ids:
                        component_list.append((0, 0, {
                            'product_id': material.name.id,
                            'qty_no_loss': material.quantity,
                            'loss': material.loss_percent,
                            'product_qty': material.required_qty,
                            'product_uom_id': material.unit.id if material.unit else material.name.uom_id.id,
                            'process_id': last_process.name.id,
                            'source_location_id': last_process.source_location_id.id,
                            'destination_location_id': last_process.destination_location_id.id,
                        }))

                    record.write({'bom_line_ids': component_list})

                record.state = 'confirmed'

    def create_component(self, process_list, index, bom):
        process = process_list[index]
        if process:
            # create new product semi
            fg_product = self.env['product.product'].search(
                [('product_tmpl_id', '=', self.product_tmpl_id.id)])
            if index == 0:  # last process
                fg_product.process_id = process.name.id
            if bom:
                # remove context
                if 'default_product_tmpl_id' in self.env.context:
                    mutable_context = dict(self.env.context)
                    mutable_context['default_product_tmpl_id'] = False
                    mutable_context['default_product_id'] = False
                    self.env.context = mutable_context

                # create new semi for process
                # new_product = self.env['product.product'].create({
                #     'name': f"{self.product_tmpl_id.name}_{process.name.name}",
                #     # 'product_sub_type': 'semi product',
                #     'process_id': process.name.id,
                #     # 'product_sub_type': 'auto',
                #     #'part_no_product_id': fg_product.id,
                #     # 'create_by_bom_id': self.id,
                #     'uom_id': fg_product.uom_id.id,
                # })
                new_product = process.target_product_id

                # create new bom 1-1 product
                new_bom = self.env['mrp.bom'].create({
                    'product_tmpl_id': new_product.product_tmpl_id.id,
                    'product_id': new_product.id,
                    'fg_bom_is': True,
                    'product_uom_id': new_product.uom_id.id,
                    'state': 'confirmed',
                    'name': new_product.name,
                    # 'item_id': new_product.id
                    # 'create_by_bom_id': self.id,

                })

                # create component
                bom.write({'bom_line_ids': [(0, 0, {
                    'product_id': new_product.id,
                    'process_id': process.name.id,
                    'level': process.level,
                    'source_location_id': process.source_location_id.id,
                    'destination_location_id': process.destination_location_id.id,
                    # 'model_ids': process.model_ids
                })]})

                component_list = []
                for material in process.material_ids:
                    component_list.append((0, 0, {
                        'product_id': material.name.id,
                        'qty_no_loss': material.quantity,
                        'loss': material.loss_percent,
                        'product_qty': material.quantity * (1 + material.loss_percent / 100),
                        'product_uom_id': material.unit.id if material.unit else material.name.uom_id.id,
                        # 'process_id': material.process_id.id if material.process_id else False,
                        # 'source_location_id': material.source_location_id.id if material.source_location_id else False,
                        # 'destination_location_id': material.destination_location_id.id if material.destination_location_id else False,
                    }))

                if len(component_list) > 0:
                    new_bom.write({'bom_line_ids': component_list})

                if (index + 1) < len(process_list):
                    self.create_component(process_list, index + 1, new_bom)
            else:
                component_list = []
                for material in process.material_ids:
                    component_list.append((0, 0, {
                        'product_id': material.name.id,
                        'qty_no_loss': material.quantity,
                        'loss': material.loss_percent,
                        'product_qty': material.quantity * (1 + material.loss_percent / 100),
                        'product_uom_id': material.unit.id if material.unit else material.name.uom_id.id,
                        'process_id': process.name.id,
                        'source_location_id': process.source_location_id.id,
                        'destination_location_id': process.destination_location_id.id,
                    }))

                if len(component_list) > 0:
                    self.write({'bom_line_ids': component_list})

                if (index + 1) < len(process_list):
                    self.create_component(process_list, index + 1, self)

    def connect_process(self):
        process_list = self.process_ids.sorted(key=lambda r: r.sequence)
        if process_list:
            for index, process in enumerate(process_list):
                if index != len(process_list) - 1:
                    next_process = process_list[index + 1]
                    if next_process:
                        process.parent_id = next_process.name

            self.process_ids = process_list

    @api.onchange('model_id')
    def onchange_model_id(self):
        domain = ['|', ('product_type', '=', 'fg product'), '&', ('product_type',
                                                                  '=', 'semi product'),
                  ('product_sub_type', '=', 'manual')]
        if self.model_id:
            domain = ['&', '|', ('product_type', '=', 'fg product'), '|', ('product_type', '=', 'semi product'), (
                'product_sub_type', '=', 'manual'), ('product_model_id.id', '=', self.model_id.id)]
        return {'domain': {'product_tmpl_id': domain}}

    def compute_Materials(self):
        tamp = 'Not yet'
        for bom in self:
            for process in bom.process_ids:
                for material in process.material_ids:
                    tamp = 'Selected'
            bom.material_status = tamp

    @api.onchange('process_ids')
    def compute_levels(self):
        if not self._origin:
            for index, process in enumerate(self.process_ids, start=1):
                process.level = index
                process.sequence = index

    @api.constrains('spec_no')
    def _check_unique_spec_no(self):
        for record in self:
            if record.spec_no:
                duplicate_records = self.search([('id', '!=', record.id), (
                    'spec_no', '=', record.spec_no), ('product_tmpl_id', '=', record.product_tmpl_id.id)])
                if duplicate_records:
                    raise ValidationError(_('Duplicate Spec no'))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        # copy new bom
        bom = super(BOM, self).copy(default)
        bom.bom_version += 1

        # Duplicate the processes and materials
        for process in self.process_ids:
            process.copy(default={'bom_id': bom.id,
                                  'material_ids': [(0, 0, {
                                      'name': material.name.id,
                                      'quantity': material.quantity,
                                      'loss_percent': material.loss_percent,
                                      'unit': material.unit.id,
                                      'weight_value': material.weight_value,
                                  }) for material in process.material_ids]
                                  })

        # remove old component
        # if 'active' not in default:
        #     bom.bom_line_ids.unlink()
        return bom

    @api.model
    def create(self, vals_list):
        res = super(BOM, self).create(vals_list)
        bom = self.search([('product_tmpl_id', '=', res.product_tmpl_id.id)], order='bom_version desc', limit=1)
        bom_version = 0
        if bom:
            bom_version = bom.bom_version + 1

        res.bom_version = bom_version
        if not res.name:
            res.name = f"{res.product_tmpl_id.default_code} - V{str(res.bom_version)}"

        return res

    def unlink(self):
        for bom in self:
            child_boms = self.search([('create_by_bom_id', '=', bom.id)])
            child_boms.unlink()
        return super(BOM, self).unlink()



class BOMLine(models.Model):
    _inherit = 'mrp.bom.line'


    @api.depends('product_id', 'bom_id')
    def _compute_child_bom_id(self):
        products = self.product_id
        bom_by_product = self.env['mrp.bom']._bom_find(products)
        for line in self:
            
            if not line.product_id:
                line.child_bom_id = False
            elif line.bom_id.create_by_bom_id or line.bom_id.product_tmpl_id.product_type == 'fg product':
                domain = self.env['mrp.bom']._bom_find_domain(line.product_id)
                if line.bom_id.create_by_bom_id :
                    domain = AND([domain, [('create_by_bom_id', '=', line.bom_id.create_by_bom_id.id)]])
                else:
                    domain = AND([domain, [('create_by_bom_id', '=', line.bom_id.id)]])
                bom = self.env['mrp.bom'].search(domain, limit=1)
                if bom:
                    line.child_bom_id = bom
                else:
                    line.child_bom_id = bom_by_product.get(line.product_id, False)
            else:
                line.child_bom_id = bom_by_product.get(line.product_id, False)
