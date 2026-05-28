# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"
    _order = 'create_date desc'

    operation_type = fields.Selection([
        ('manufacturing', 'Manufacturing'),
        ('pre_manufacturing', 'Pre-Manufacturing'),
        ('m_receiving', 'Material Receiving'),
        ('m_putaway', 'Material Put Away'),
        ('m_shipping', 'Material Shipping'),
        ('m_return', 'Material Return'),
        ('m_ng', 'Material NG'),
        ('m_repair', 'Material Repair'),
        ('m_return_remain', 'Return Remain'),
        ('w_receiving', 'WIP Receiving'),
        ('w_shipping', 'WIP Shipping'),
        ('w_return', 'WIP Return'),
        ('a_return', 'Alloy Return'),
        ('w_ng', 'WIP NG'),
        ('w_repair', 'WIP Repair'),
        ('f_receiving', 'FG Receiving'),
        ('f_shipping', 'FG Shipping'),
        ('f_return', 'FG Return'),
        ('f_ng', 'FG NG'),
        ('f_repair', 'FG Repair'),
        ('f_packing', 'FG Packing'),
        ('f_oqc', 'FG OQC'),
        ('f_oqc_ng', 'FG OQC NG'),
        ('virtual_reserve_material', 'Virtual reserve material'),
        ('f_repair', 'FG Repair'),
        ('repair', 'Repair'),
        ('repair_ng', 'Repair NG'),
    ], string='Operation Type')
    operation_category = fields.Selection([
        ('material', 'Material'),
        ('wip', 'WIP'),
        ('fg', 'FG'),
        ('mold', 'Mold'),
        ('silver', 'Silver'),
        ('repair', 'Repair'),
        ('maf', 'Manufacturing'),
    ],
        string='Operation Type',
        required=True,
        default='material')
    is_qc = fields.Boolean('Is QC', default=False)
    create_lot = fields.Boolean('Create Lot', default=False)
    description = fields.Char('Description')


class StandbySetting(models.Model):
    _name = 'standard.standbysetting'
    _description = 'Standby Setting Model'
    _order = 'create_date desc'
    _sql_constraints = [('unique_model_code', 'unique(name, process_id)',
                         "Duplicated Operation Type and Process"),]

    name = fields.Many2one("stock.picking.type",
                           'Operation Type', required=True, index=True)
    process_id = fields.Many2one('standard.process', 'Process')

    step_ids = fields.One2many(
        'standard.standbysetting.step', 'standbysetting_id', index=True)
    type_ids = fields.One2many(
        'standard.standbysetting.type', 'standbysetting_id', index=True)

    confirm_is = fields.Boolean("Confirm", default=False)
    level = fields.Integer('Level', compute='compute_level')
    step = fields.Char('Step', compute='compute_step')
    type = fields.Char('Type', compute='compute_type')

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        Standby = super(StandbySetting, self).copy(
            default={'process_id': False})

        # Duplicate step
        for step in self.step_ids:
            step.copy(default={'standbysetting_id': Standby.id})

        # Duplicate type
        for type in self.type_ids:
            type.copy(default={'standbysetting_id': Standby.id})

        return Standby

    def compute_level(self):
        for record in self:
            if record.step_ids:
                record.level = len(record.step_ids)
            else:
                record.level = 0

    def compute_step(self):
        for record in self:
            stt = ''
            if record.step_ids:
                for dt in record.step_ids:
                    if stt == '':
                        stt = stt + dt.name
                    else:
                        stt = stt + ', ' + dt.name
                record.step = stt
            else:
                record.step = ''

    def compute_type(self):
        for record in self:
            stt = ''
            if record.type_ids:
                for dt in record.type_ids:
                    if stt == '':
                        stt = stt + dt.name.name
                    else:
                        stt = stt + ', ' + dt.name.name
                record.type = stt
            else:
                record.type = ''

    def confirm_registration(self):
        self.confirm_is = not self.confirm_is


class StandbySettingStep(models.Model):
    _name = 'standard.standbysetting.step'
    _description = 'Standby Step Model'
    _order = 'sequence'

    name = fields.Char('Step', required=True, index=True)
    level = fields.Integer('Level', compute='compute_Level')
    description = fields.Char('Description')
    default_is = fields.Boolean('Default', default=True)
    check_report_is = fields.Boolean('Check Report')
    check_disposal_is = fields.Boolean('Check Disposal')
    standbysetting_id = fields.Many2one(
        'standard.standbysetting', 'step', required=True, index=True)
    sequence = fields.Integer('Sequence', default=1)

    def compute_Level(self):
        stt = 0
        for bom in self:
            stt = stt + 1
            bom.level = stt


class StandbySettingType(models.Model):
    _name = 'standard.standbysetting.type'
    _description = 'Standby Type Model'
    _order = 'sequence'

    name = fields.Many2one("standard.standbytype",
                           'Type', required=True, index=True)
    default_is = fields.Boolean('Default', default=True)
    standbysetting_id = fields.Many2one(
        'standard.standbysetting', 'type', required=True, index=True)
    sequence = fields.Integer('Sequence', default=1)


class StandbyType(models.Model):
    _name = 'standard.standbytype'
    _description = 'Standby Type Model'
    _sql_constraints = [
        ('unique_standbytype_name', 'unique(name)', "Duplicated Type Name"),]

    name = fields.Char('Name', required=True, index=True)
    type = fields.Selection([('man', 'man'), ('mold', 'mold'),
                            ('machine', 'machine')], string='Type', required=True)
