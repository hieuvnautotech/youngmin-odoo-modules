# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(IrHttp, self).session_info()
        config_parameter = request.env['ir.config_parameter'].sudo()
        # By default, it's not retrieved False
        result['app_superbar_pro_enable'] = True
        result['app_default_superbar_and_search'] = config_parameter.get_param('app_default_superbar_and_search', False)
        result['app_default_superbar_lazy_search'] = config_parameter.get_param('app_default_superbar_lazy_search', False)
        result = super(IrHttp, self).session_info()
        return result
