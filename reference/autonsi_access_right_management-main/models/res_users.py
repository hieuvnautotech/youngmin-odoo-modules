from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    team = fields.Char("Team")
    position = fields.Char("Position")
    x_user_category = fields.Selection([('admin', 'Admin'), ('manager', 'Manager'), ('user', 'User')],
                                       string="User Category", default="user")

    discuss_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User')], string="Discuss Rights", default="user")
    calendar_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User')], string="Calendar Rights",
                                       default="user")
    document_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User')], string="Document Rights",
                                       default="user")
    standard_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User')], string="Standard Rights",
                                       default="user")
    sales_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User')], string="Sales Rights", default="user")
    purchase_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User')], string="Purchase Rights",
                                       default="user")
    m_wms_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User'), ('manager', 'Manager')],
                                    string="M-WMS Rights", default="user")
    wip_wms_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User'), ('manager', 'Manager')],
                                      string="WIP-WMS Rights", default="user")
    fg_wms_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User'), ('manager', 'Manager')],
                                     string="FG-WMS Rights", default="user")
    mps_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User')], string="MPS Rights", default="user")
    pms_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User')], string="PMS Rights", default="user")
    cmms_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User')], string="CMMS Rights", default="user")
    mms_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User')], string="MMS Rights", default="user")
    qms_rights = fields.Selection([('viewer', 'Viewer'), ('user', 'User'), ('manager', 'Manager')], string="QMS Rights",
                                  default="user")

    hide_menu_ids = fields.Many2many('ir.ui.menu', 'hide_menu_rel', 'user_id',
                                     'menu_id', 'Hide Menu')
    user_mng_rights = fields.Selection([('user', 'User'), ('viewer', 'Viewer'), ('manager', 'Manager')],
                                       string="User Mng Rights")
    team_id = fields.Many2one('hr.department', string="Team")
    mms_shop_floor_rights = fields.Selection([('user', 'User'), ('manager', 'Manager')],
                                             string="MMS Shop Floor Rights")
    pms_shop_floor_rights = fields.Selection([('user', 'User'), ('manager', 'Manager')],
                                             string="PMS Shop Floor Rights")

    @api.onchange('x_user_category')
    def _onchange_x_user_category(self):
        if self.x_user_category == 'admin':
            self.write({
                'discuss_rights': 'user',
                'calendar_rights': 'user',
                'document_rights': 'user',
                'standard_rights': 'user',
                'sales_rights': 'user',
                'purchase_rights': 'user',
                'm_wms_rights': 'manager',
                'wip_wms_rights': 'manager',
                'fg_wms_rights': 'manager',
                'mps_rights': 'user',
                'pms_rights': 'user',
                'cmms_rights': 'user',
                'mms_rights': 'user',
                'qms_rights': 'manager',
                'user_mng_rights': 'user',
                'mms_shop_floor_rights': 'manager',
                'pms_shop_floor_rights': 'manager',
            })
        elif self.x_user_category == 'manager':
            self.write({
                'discuss_rights': 'user',
                'calendar_rights': 'user',
                'document_rights': 'user',
                'standard_rights': 'user',
                'sales_rights': 'user',
                'purchase_rights': 'user',
                'm_wms_rights': 'manager',
                'wip_wms_rights': 'manager',
                'fg_wms_rights': 'manager',
                'mps_rights': 'user',
                'pms_rights': 'user',
                'cmms_rights': 'user',
                'mms_rights': 'user',
                'qms_rights': 'manager',
                'user_mng_rights': False,
                'mms_shop_floor_rights': 'manager',
                'pms_shop_floor_rights': 'manager',
            })
        elif self.x_user_category == 'user':
            self.write({
                'discuss_rights': 'user',
                'calendar_rights': 'user',
                'document_rights': 'user',
                'standard_rights': 'user',
                'sales_rights': 'user',
                'purchase_rights': 'user',
                'm_wms_rights': 'user',
                'wip_wms_rights': 'user',
                'fg_wms_rights': 'user',
                'mps_rights': 'user',
                'pms_rights': 'user',
                'cmms_rights': 'user',
                'mms_rights': 'user',
                'qms_rights': 'user',
                'user_mng_rights': False,
                'mms_shop_floor_rights': 'user',
                'pms_shop_floor_rights': 'user',
            })

    def action_open_change_password(self):
        action = self.env["ir.actions.actions"]._for_xml_id('base.change_password_wizard_action')
        return action

    @api.model
    def create(self, vals):
        # Validate user type limits before creating
        user = super().create(vals)
        user.assign_hide_menu()
        user.action_apply_menu_when_create()
        if not user.employee_id:
            user.action_create_employee()

        self.env.registry.clear_cache()

        return user

    def assign_hide_menu(self):
        Menus = self.env['ir.ui.menu'].with_context({'ir.ui.menu.full_list': True})
        menu_ids_to_hide = self.env['ir.ui.menu']

        def get_menu(xml_id):
            return self.env.ref(xml_id, raise_if_not_found=False)

        def get_all_menus_under(menu):
            if not menu:
                return self.env['ir.ui.menu']

            all_menus = self.env['ir.ui.menu'].browse()

            def recurse(m):
                nonlocal all_menus
                children = Menus.search([('parent_id', '=', m.id)])
                all_menus |= children
                for child in children:
                    recurse(child)

            recurse(menu)
            return all_menus | menu  # Bao gồm cả menu cha

        # Main logic
        for user in self:
            if user.login == 'admin':
                user.hide_menu_ids = [(5, 0, 0)]  # Clear all hidden menus for admin
                continue
            hide_menus = self.env['ir.ui.menu']
            if user.x_user_category == 'admin':
                if not user.discuss_rights:
                    hide_menus |= get_menu("mail.menu_root_discuss")
                if not user.calendar_rights:
                    hide_menus |= get_menu("calendar.mail_menu_calendar")
                if not user.document_rights:
                    hide_menus |= get_menu("documents.menu_root")
                    # hide_menus |= get_menu("document_knowledge.menu_document_root")
                if not user.standard_rights:
                    hide_menus |= get_menu("autonsi_standard_youngmin.autonsi_standard_standard_menu")
                if not user.sales_rights:
                    hide_menus |= get_menu("autonsi_sale_ym.menu_erp_root")
                if not user.purchase_rights:
                    hide_menus |= get_menu("purchase.menu_purchase_root")
                if not user.m_wms_rights:
                    hide_menus |= get_menu("autonsi_wms_ym.menu_erp_root")
                if not user.wip_wms_rights:
                    hide_menus |= get_menu("autonsi_wms_ym.menu_erp_root")
                if not user.fg_wms_rights:
                    hide_menus |= get_menu("autonsi_wms_ym.menu_erp_root")
                if not user.mps_rights:
                    hide_menus |= get_menu("autonsi_mps_youngmin.menu_mps_main")
                if not user.pms_rights:
                    hide_menus |= get_menu("autonsi_pms_youngmin.pms_menu_root")
                if not user.cmms_rights:
                    hide_menus |= get_menu("cmms_plus.menu_cmms_plus_root")
                if not user.mms_rights:
                    hide_menus |= get_menu("autonsi_mms_youngmin.menu_mrp_mmo_root")
                if not user.qms_rights:
                    hide_menus |= get_menu("autonsi_qms.menu_qms_main")
                if not user.user_mng_rights:
                    hide_menus |= get_menu("autonsi_access_right_management.menu_user_management_root")
            else:
                all_root_menus = Menus.search(
                    [('parent_id', '=', False), ('id', '!=', self.env.ref('autonsi_wms_ym.menu_erp_root').id)])
                wms_menu_root = Menus.search([('id', 'in', [self.env.ref('autonsi_wms_ym.m_wms_menu_root').id,
                                                            self.env.ref('autonsi_wms_ym.w_wms_menu_root').id,
                                                            self.env.ref('autonsi_wms_ym.fg_wms_menu_root').id])])
                hide_menus |= wms_menu_root
                hide_menus |= all_root_menus
                if user.discuss_rights:
                    hide_menus -= get_menu("mail.menu_root_discuss")
                if user.calendar_rights:
                    hide_menus -= get_menu("calendar.mail_menu_calendar")
                if user.document_rights:
                    hide_menus -= get_menu("documents.menu_root")
                    # hide_menus -= get_menu("document_knowledge.menu_document_root")
                if user.standard_rights:
                    hide_menus -= get_menu("autonsi_standard_youngmin.autonsi_standard_standard_menu")
                if user.sales_rights:
                    hide_menus -= get_menu("autonsi_sale_ym.menu_erp_root")
                if user.purchase_rights:
                    hide_menus -= get_menu("purchase.menu_purchase_root")
                if user.m_wms_rights:
                    hide_menus -= get_menu("autonsi_wms_ym.m_wms_menu_root")
                if user.wip_wms_rights:
                    hide_menus -= get_menu("autonsi_wms_ym.w_wms_menu_root")
                if user.fg_wms_rights:
                    hide_menus -= get_menu("autonsi_wms_ym.fg_wms_menu_root")
                if user.mps_rights:
                    hide_menus -= get_menu("autonsi_mps_youngmin.menu_mps_main")
                if user.pms_rights:
                    hide_menus -= get_menu("autonsi_pms_youngmin.pms_menu_root")
                if user.cmms_rights:
                    hide_menus -= get_menu("cmms_plus.menu_cmms_plus_root")
                if user.mms_rights:
                    hide_menus -= get_menu("autonsi_mms_youngmin.menu_mrp_mmo_root")
                if user.qms_rights:
                    hide_menus -= get_menu("autonsi_qms.menu_qms_main")
                if user.user_mng_rights:
                    hide_menus -= get_menu("autonsi_access_right_management.menu_user_management_root")

            # Gán kết quả vào trường hide_menu_ids
            print("hide_menus", [hide_menus.complete_name for hide_menus in hide_menus])
            user.hide_menu_ids = [(6, 0, hide_menus.ids)]

    def write(self, vals):

        # Store old values before updating

        result = super().write(vals)
        if "discuss_rights" in vals or "calendar_rights" in vals or "document_rights" in vals \
             or "standard_rights" in vals or "sales_rights" in vals or "purchase_rights" in vals \
                 or "m_wms_rights" in vals or "wip_wms_rights" in vals or "fg_wms_rights" in vals \
                     or "mps_rights" in vals or "pms_rights" in vals or "cmms_rights" in vals or "mms_rights" in vals \
                        or "qms_rights" in vals or "user_mng_rights" in vals or "x_user_category" in vals or "mms_shop_floor_rights" in vals or "pms_shop_floor_rights" in vals:
            self.assign_hide_menu()

        self.env.registry.clear_cache()
        return result

    def action_apply_menu_when_create(self):
        for user in self:
            group_erp_manager = self.env.ref("base.group_erp_manager", raise_if_not_found=False)

            # check if user not in group_erp_manager then add user to group_erp_manager
            no_reset_password = self._context.get("no_reset_password", False)
            if group_erp_manager and not user.has_group('base.group_erp_manager') and not no_reset_password:
                group_erp_manager.users += user
            cmms_group = self.env.ref("cmms_plus.group_cmms_plus_manager", raise_if_not_found=False)
            if cmms_group and not user.has_group('cmms_plus.group_cmms_plus_manager'):
                cmms_group.users += user
            ams_group = self.env.ref("autonsi_ams.group_ams_plus_manager", raise_if_not_found=False)
            if ams_group and not user.has_group('autonsi_ams.group_ams_plus_manager'):
                ams_group.users += user

            user_setting = self.env['res.users.settings']._find_or_create_for_user(user)
            ps_fav_menus = '["calendar.mail_menu_calendar","mail.menu_root_discuss","documents.menu_root","autonsi_standard_youngmin.autonsi_standard_standard_menu","autonsi_sale_ym.menu_erp_root","purchase.menu_purchase_root","autonsi_wms_ym.menu_erp_root","autonsi_mps_youngmin.menu_mps_main","autonsi_pms_youngmin.pms_menu_root","cmms_plus.menu_cmms_plus_root","autonsi_qms.menu_qms_main","autonsi_access_right_management.menu_user_management_root","autonsi_mms_youngmin.menu_mrp_mmo_root","autonsi_ams.menu_ams_view_root","autonsi_package_youngmin.menu_packing_main","autonsi_dashboard.menu_indoor_dashboard_root","nhtivi.menu_tivi_root","spreadsheet_dashboard.spreadsheet_dashboard_menu_root"]'
            user_setting.set_res_users_settings({
                'ps_fav_menus': ps_fav_menus})

    @api.onchange('mms_shop_floor_rights')
    def _onchange_mms_shop_floor_rights(self):
        group_mms_shop_floor_manager = self.env.ref("mrp_workorder.group_mms_shop_floor_manager",
                                                    raise_if_not_found=False)
        group_mms_shop_floor_user = self.env.ref("mrp_workorder.group_mms_shop_floor_user", raise_if_not_found=False)
        if self.mms_shop_floor_rights == 'manager':
            self.groups_id = [(4, group_mms_shop_floor_manager.id)]
        elif self.mms_shop_floor_rights == 'user':
            self.groups_id = [(3, group_mms_shop_floor_manager.id), (4, group_mms_shop_floor_user.id)]
        else:
            self.groups_id = [(3, group_mms_shop_floor_manager.id), (3, group_mms_shop_floor_user.id)]

    @api.onchange('pms_shop_floor_rights')
    def _onchange_pms_shop_floor_rights(self):
        group_pms_shop_floor_manager = self.env.ref("mrp_workorder.group_pms_shop_floor_manager",
                                                    raise_if_not_found=False)
        group_pms_shop_floor_user = self.env.ref("mrp_workorder.group_pms_shop_floor_user", raise_if_not_found=False)
        if self.pms_shop_floor_rights == 'manager':
            self.groups_id = [(4, group_pms_shop_floor_manager.id)]
        elif self.pms_shop_floor_rights == 'user':
            self.groups_id = [(3, group_pms_shop_floor_manager.id), (4, group_pms_shop_floor_user.id)]
        else:
            self.groups_id = [(3, group_pms_shop_floor_manager.id), (3, group_pms_shop_floor_user.id)]

    @api.onchange('fg_wms_rights')
    def _onchange_fg_wms_rights(self):
        if self.fg_wms_rights == 'manager':
            self.groups_id = [(4, self.env.ref("autonsi_access_right_management.group_fg_wms_manager").id)]
        elif self.fg_wms_rights == 'user':
            self.groups_id = [(3, self.env.ref("autonsi_access_right_management.group_fg_wms_manager").id), (4, self.env.ref("autonsi_access_right_management.group_fg_wms_user").id)]
        else:
            self.groups_id = [(3, self.env.ref("autonsi_access_right_management.group_fg_wms_manager").id), (3, self.env.ref("autonsi_access_right_management.group_fg_wms_user").id)]