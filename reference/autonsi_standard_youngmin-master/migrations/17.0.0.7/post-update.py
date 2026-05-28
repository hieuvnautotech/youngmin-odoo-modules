import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

def print_log(message):
    _logger.info(message)
    print(message)

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    print_log("Running post-update autonsi_standard_youngmin")

    # env['product.product'].search([('shipping_country', '=', 'korea')]).write({'shipping_country': False})

