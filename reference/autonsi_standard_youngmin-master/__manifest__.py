# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    "name": "Autonsi Standard Young Min",
    "version": "17.0.0.7",
    # "category": "Autonsi",
    "sequence": 1,
    "description": """
       Standard
    """,
    "author": "Autonsi",
    "maintainer": "Autonsi",
    "website": "https://autonsi.com/",
    "license": "OPL-1",
    "depends": ["web", "hr_skills", "base", "stock", "mrp", "account"],
    "data": [
        # security
        "security/ir.model.access.csv",
        # data
        "data/data.xml",
        "data/init_commom.xml",
        "data/init_location.xml",
        "data/init_process.xml",
        # wizard
        "wizards/autonsi_standard_bom_import_wizard.xml",
        "wizards/material_import_korea_id_wizard.xml",
        # view
        "views/standbystep.xml",
        "views/operationtype.xml",
        "views/model.xml",
        "views/bom.xml",
        "views/bom_inherit.xml",
        "views/bomMaterialPopup.xml",
        "views/common.xml",
        "views/location.xml",
        "views/process.xml",
        "views/product.xml",
        "views/product_inherit.xml",
        "views/material.xml",
        "views/package.xml",
        "views/partner.xml",
        "views/partner_inherit.xml",
        "views/employee.xml",
        "views/department.xml",
        "views/project.xml",
        "views/pallet.xml",
        "views/jig.xml",
        "views/process_line.xml",
        "views/mrp_workcenter.xml",
        "views/product_category_views.xml",
        # menu
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "autonsi_standard_youngmin/static/src/css/standard_style.css",
        ],
    },
    "post_init_hook": "set_config_params",
}
