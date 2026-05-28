from odoo import api, fields, models, tools


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug', 'self.env.user.hide_menu_ids')
    def _visible_menu_ids(self, debug=False):
        visible_menus = super(IrUiMenu, self)._visible_menu_ids(debug)
        hide_menus = self.env.user.mapped('hide_menu_ids')
        visible_menus = visible_menus - set(hide_menus.ids)
        return visible_menus
