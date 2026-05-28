# -*- coding: utf-8 -*-
{
    "name": "Auto&SI QMS Extend",
    "summary": "Auto&SI QMS Extend",
    "website": "https://www.autonsi.com",
    "support": "https://www.autonsi.com",
    "category": "Manufacturing",
    "description": """ Auto&SI QMS Extend """,
    "author": "AUTONSI",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["autonsi_qms", "cmms_plus", "autonsi_pms_youngmin", "autonsi_wms_ym", "autonsi_mms_youngmin"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        # views
        "views/jig_history_views.xml",
        "views/mes_qc_form.xml",
        "views/mes_qc_form_history.xml",
        "views/mes_qc_hold_release.xml",
        "views/mes_qc_form_log.xml",
        "views/mes_qc_report.xml",
    ],
    "application": True,
    "assets": {
        "web.assets_backend": [
            "autonsi_qms_youngmin/static/src/js/*.js",
            # "autonsi_qms_youngmin/static/src/css/*.css",
            "autonsi_qms_youngmin/static/src/scss/*.scss",
            "autonsi_qms_youngmin/static/src/xml/*.xml",
        ]
    },
}
