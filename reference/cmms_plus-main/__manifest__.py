# -*- coding: utf-8 -*-
{
    'name': "CMMS",
    'version': '1.0.0',
    'author': 'MrHieu',
    'category': 'Base',
    'license': 'LGPL-3',
    'sequence': 2,
    'summary': """
        CMMS
    """,
    "depends": ["base","maintenance","stock","autonsi_standard_youngmin"],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'security/sequence.xml',
        
        'views/maintenance_equiment_category.xml',
        'views/equipment_model_views.xml',
        'views/product_product_kanban.xml',
        'views/jig_history_views.xml',
        'views/menus.xml'
    ],
    'assets': {
        'web.assets_backend': [
            "cmms_plus/static/src/css/style.css",
             "cmms_plus/static/src/css/cmms_kanban.scss",

             # "cmms_plus/static/src/js/store.js",
            
            "cmms_plus/static/src/js/kanban/cmms_kanban_controller.js",
            "cmms_plus/static/src/js/kanban/cmms_kanban_controller.xml",
            "cmms_plus/static/src/js/kanban/cmms_kanban_dynamic_list.js",
            "cmms_plus/static/src/js/kanban/cmms_kanban_model.js",
            "cmms_plus/static/src/js/kanban/cmms_kanban_record.js",
            "cmms_plus/static/src/js/kanban/cmms_kanban_record.xml",
            "cmms_plus/static/src/js/kanban/cmms_kanban_renderer.js",
            "cmms_plus/static/src/js/kanban/cmms_kanban_renderer.xml",
             "cmms_plus/static/src/js/kanban/cmms_search_model.js",
             "cmms_plus/static/src/js/form_controller.js",

            
            "cmms_plus/static/src/js/kanban/cmms_kanban_view.js",
            "cmms_plus/static/src/js/custom_list_view.js",
            
            "cmms_plus/static/src/js/kanban/cmms_jstree_container/cmms_jstree_container.js",
            "cmms_plus/static/src/js/kanban/cmms_jstree_container/cmms_jstree_container.xml",

            "cmms_plus/static/src/js/kanban/cmms_formview_container/cmms_formview_container.js",
            "cmms_plus/static/src/js/kanban/cmms_formview_container/cmms_formview_container.xml",

             "cmms_plus/static/src/js/kanban/cmms_navigation/cmms_navigation.js",
            "cmms_plus/static/src/js/kanban/cmms_navigation/cmms_navigation.xml",
            
        ],
    },
   
    'installable': True,
    'application': False,
    'auto_install': False,
}
