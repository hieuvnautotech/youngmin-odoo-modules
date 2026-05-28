# -*- coding: utf-8 -*-

# Created on 2019-01-04
# author: 欧度智能，https://www.odooai.cn
# email: 300883@qq.com
# resource of odooai
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# Odoo12在线用户手册（长期更新）
# https://www.odooai.cn/documentation/user/12.0/en/index.html

# Odoo12在线开发者手册（长期更新）
# https://www.odooai.cn/documentation/12.0/index.html

# Odoo10在线中文用户手册（长期更新）
# https://www.odooai.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.odooai.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.odooai.cn/odoo10_developer_document_offline/

# todo: view A有关联字段B，如果AB都有superbar，那么A->B->A，此时toggle会不显示，superbar也不显示，要调整
{
    'name': "Advance Search sidebar for every odoo App",
    'version': '24.11.20',
    'author': 'odooai.cn',
    'category': 'Base',
    'website': 'https://www.odooai.cn',
    'live_test_url': 'https://demo.odooapp.cn',
    'license': 'OPL-1',
    'sequence': 2,
    'summary': """
    odoo Advance Search, Advance Filter for list search, kanban search. search bar.datetime search, date range search. number search. instant and lazy mode. .
    Easy to navigator and browse any data.
    ztree superbar.
    """,
    'description': """
    Advance Filter with Hierarchy Parent Children tree
    1. Can Add search sidebar in any odoo app. Easy to navigator and browse any data. 
    2. Provide over 10 free search app like Like Product, CRM, Sale order, Purchase order, MRP, Inventory, Accounting vouchers, Mrp order, HR etc.
    3. Support variety of field type like many2one relation, many2many relation, date and datetime, number and money search.
    date search, datetime search, date range search, datetime rang search, number search, number range search, boolean search.
    4. Fully compatible with all odoo apps and odoo search. like search build inside
    5. 【Not Ready】Support instant or lazy search. Instant for just one click to search. Lazy for set all filter then click to search, good perform for big data.
    6. Support lot kind of view like list / tree, kanban, pivot, graph view. 
    7. Support search more view, easy to find product for sale / purchase order. (Only for instant mode)
    8. Show Advance Search, Advance Filter with Parent Children Tree.
    9. Mobile ok for Adaptive responsive view. also optimize for big screen hd view > 992px; 
    10. Easy to customize or add advance search sidebar to 3rd apps. Follow reference.
    11. Multi-language Support.
    12. Multi-Company Support.
    13. Support Odoo 13, Enterprise and Community Edition. Also you can find app_web_superbar for odoo 12,11,10
        
    Customize reference: 
    searchpanel: view_types, class
    field: name, select, icon, groupby, groups, string, color, domain, text
    context: searchpanel_default_xxx,
    context: searchpanel_domain,
    
    超级方便的查询，树状视图导航。可用在任何模块中。
    可动态设置的domain参数，以 searchpanel_domain 开头，如：
            action['context'] = {
            'searchpanel_domain_group_id': "[('root_sale', '=', " + str(self.id) + ")]"
        }
        todo: 直接用 active id
        domain: 原生的searchpanel处理写法只能在联动子集中处理是 domain="[['customer', '=', 'True']]"，
        在普通的处理中改成 filter_domain="{[domain]}"    
    """,
    'price': 68.00,
    'currency': 'EUR',
    'depends': [
        'app_web_superbar',
    ],
    'images': ['static/description/superbar_pro.gif'],
    'data': [
        'data/ir_config_parameter_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'app_web_superbar_pro/static/src/js/list_controller.js',
            'app_web_superbar_pro/static/src/js/search_bar.js',
            'app_web_superbar_pro/static/src/js/search_arch_parser.js',
            'app_web_superbar_pro/static/src/js/search_panel_follow_service.js',
            'app_web_superbar_pro/static/src/js/search_panel.js',
            'app_web_superbar_pro/static/src/js/loading.js',
            'app_web_superbar_pro/static/src/js/list_renderer.js',
            'app_web_superbar_pro/static/src/js/search_model.js',
            'app_web_superbar_pro/static/src/js/model.js',
        ],
    },
    'demo': [
    ],
    'test': [
    ],
    'css': [
    ],
    'js': [
    ],
    'post_load': None,
    'installable': True,
    'application': True,
    'auto_install': False,
}
