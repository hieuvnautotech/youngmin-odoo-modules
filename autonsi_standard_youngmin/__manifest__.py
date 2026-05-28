# -*- coding: utf-8 -*-

{
    'name': 'Standard Information',
    'version': '17.0.1.0.0',
    'author': 'Youngmin Hi-Tech Vina',
    'license': 'OPL-1',
    'category': 'Manufacturing',
    'summary': 'Standard master data management for Youngmin',
    'depends': ['base', 'mail', 'product', 'mrp', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/standard_project_views.xml',
        'views/standard_process_views.xml',
        'views/standard_common_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
}
