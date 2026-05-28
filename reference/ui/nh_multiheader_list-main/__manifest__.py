# -*- coding: utf-8 -*-
{
    'name': "Multi List Header",
    'version': '1.0.0',
    'author': 'MrHieu- nnhieu.htb@gmailmcon',
    'category': 'Base',
    'license': 'OPL-1',
    'sequence': 2,
    'summary': """
Multi Header List
    """,
    'price': 0.00,
    'currency': 'EUR',
    'depends': [
        'web',
        'account',
        'udoo_web_list_view'
    ],
    'data': [
        'views/inherited.xml'
    ],
    'assets': {
        'web.assets_backend': [
             (
                'after',
                'web/static/src/views/list/list_renderer.xml',
                'nh_multiheader_list/static/src/js/list_renderer.xml',
            ),
            'nh_multiheader_list/static/src/css/style.css',
            'nh_multiheader_list/static/src/js/multiheader_list.js',

        ],
    },
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
