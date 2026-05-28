# -*- coding: utf-8 -*-
# Copyright 2024 Sveltware Solutions

{
    'name': 'Adaptive Filter Bar',
    'category': 'Tools',
    'summary': 'It is made up of input controls that filter objects according to various criteria with just one click, such as status or date. Expanded filter bar, search bar, dropdown filter, quick filtering, column filter, fast search, fast filter, smart filter bar, quick sort, smart list group, contextual filter, list view search, quick search, field search, advanced search odoo, list view manager, multiple search queries, easy search, searchbar, product search, custom search, advance search, datetime search, date range search, number search, search by product, lazy search, smart search, header search, header-integrated filtering, global search, search record by column, search engine, advance search & quick search list edit view, tree view advanced search / direct filter in list, bryntum, treegrid',
    'version': '1.1.5',
    'license': 'OPL-1',
    'author': 'Sveltware Solutions',
    'website': 'linkedin.com/in/sveltware',
    'images': [
        'static/description/banner.png',
    ],
    'depends': [
        'omux_state_manager',
        'omux_view_action',
    ],
    'assets': {
        'web.assets_backend': [
            (
                'before',
                'web/static/src/views/list/list_renderer.js',
                'udoo_web_filter_bar/static/src/editor/*',
            ),
            (
                'after',
                'web/static/src/views/list/list_renderer.js',
                'udoo_web_filter_bar/static/src/patch/list_renderer.js',
            ),
            (
                'after',
                'web/static/src/model/relational_model/dynamic_list.js',
                'udoo_web_filter_bar/static/src/patch/model/dynamic_list.js',
            ),
            (
                'after',
                'web/static/src/model/relational_model/static_list.js',
                'udoo_web_filter_bar/static/src/patch/model/static_list.js',
            ),
            (
                'after',
                'web/static/src/search/search_model.js',
                'udoo_web_filter_bar/static/src/patch/search/search_model.js',
            ),
            (
                'after',
                'web/static/src/search/search_bar/search_bar.xml',
                'udoo_web_filter_bar/static/src/search/search_bar.xml',
            ),
            (
                'after',
                'web/static/src/search/search_bar/search_bar.xml',
                'udoo_web_filter_bar/static/src/search/search_bar.js',
            ),
            (
                'after',
                'web/static/src/views/list/list_renderer.xml',
                'udoo_web_filter_bar/static/src/patch/list_renderer.xml',
            ),
            (
                'after',
                'omux_view_action/static/src/control_panel.xml',
                'udoo_web_filter_bar/static/src/search/control_panel.js',
            ),
            (
                'after',
                'omux_view_action/static/src/control_panel.xml',
                'udoo_web_filter_bar/static/src/search/control_panel.xml',
            ),
            'udoo_web_filter_bar/static/src/list_renderer.scss',
        ]
    },
    'price': 87,
    'currency': 'EUR',
}
