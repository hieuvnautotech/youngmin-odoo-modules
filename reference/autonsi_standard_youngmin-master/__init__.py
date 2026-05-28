# -*- coding: utf-8 -*-
from . import models, wizards
from odoo import api, SUPERUSER_ID

def set_config_params(env):
    # env là cái env registry / database context
    # Bạn cần môi trường có sudo để update param
    param = env["ir.config_parameter"]

    print("__post_init_set_group_lot is called")
    # Cách 1: lưu param
    param.set_param("stock.group_production_lot", True)

    config = env["res.config.settings"].create({})
    config.write({
        'group_stock_production_lot': True,
        'group_stock_multi_locations': True,
        'group_stock_adv_location': True,
    })
    config.sudo().set_values()

    DecimalPrecision = env['decimal.precision']

    print(">>> Running update_decimal_precision...")

    # Tìm record cần update
    record = DecimalPrecision.search([('name', '=', 'Product Unit of Measure')], limit=1)
    if record:
        record.write({'digits': 5})
        print(">>> Updated Product Unit of Measure to 5 digits")
    else:
        print(">>> Record not found: Product Unit of Measure")