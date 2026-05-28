{
    'name': 'Autonsi Access Right Management',
    'version': '17.0.0.1',
    'summary': 'Access Right Management for Odoo',
    'description': 'This module provides a comprehensive solution for managing access rights in Odoo, ensuring that users have the appropriate permissions to perform their tasks while maintaining data security and integrity.',
    'category': 'Tools',
    'author': 'Autonsi',
    'license': 'OPL-1',
    'depends': ['base', 'auth_signup', 'mail', 'spreadsheet_dashboard', 'autonsi_sale_ym', 'autonsi_qms_youngmin',
                'cmms_plus', 'mrp_workorder', 'autonsi_wms_ym'],
    'data': [
        "data/ir_module_category_data.xml",
        'views/user_views.xml',
        'views/menus_views.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_rule_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}
