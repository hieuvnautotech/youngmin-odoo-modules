# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # todo: 后续处理 Lazy
    app_default_superbar_and_search = fields.Boolean('Search And', config_parameter='app_default_superbar_and_search',
                                                     help="Press 'shift' key to Use And filter for same field. Search result must fix all keyword input.")
    app_default_superbar_lazy_search = fields.Boolean('Lazy Search in Sidebar', config_parameter='app_default_superbar_lazy_search',
                                                      help='Set up all filter first, then click search to get filter data.')
