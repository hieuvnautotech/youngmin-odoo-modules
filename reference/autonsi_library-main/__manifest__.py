{
	'name': 'Auto&SI Library',
	"author": "Auton&SI",
	"website": "https://www.autonsi.com",
	"support": "https://www.autonsi.com",
	"category": "",
	'depends': ["web",'stock'],
	"data": [
        "security/ir.model.access.csv",
        "views/test_xmany.xml",
	],
	'assets': {
		'web.assets_backend': [
			'autonsi_library/static/lib/suite/codebase/suite.css',
			'autonsi_library/static/lib/suite/codebase/suite.js',

			'autonsi_library/static/lib/gantt/codebase/dhtmlxgantt.js',
			'autonsi_library/static/lib/gantt/codebase/dhtmlxgantt.css',

			'autonsi_library/static/lib/scheduler/codebase/dhtmlxscheduler_material.css',
			'autonsi_library/static/lib/scheduler/codebase/dhtmlxscheduler_conn.js',

			'autonsi_library/static/src/**/*',
		],
		
	}
}
