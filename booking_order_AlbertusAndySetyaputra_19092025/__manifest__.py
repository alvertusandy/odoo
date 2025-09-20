# -*- coding: utf-8 -*-
{
    'name': 'Booking Order Albertus Andy Setyaputra 19-09-2025',
    'version': '1.0',
    'category': 'Booking Order',
    'sequence': 1,
    'author': 'Albertus Andy Setyaputra',
    'summary': 'Hashmicro Odoo Developer Test Booking Order',
    'description': """
Hashmicro Odoo Developer Test Booking Order
""",
    'depends': ['sale'],
    'data': [
        'reports/work_order_template.xml',
        'reports/work_order_report.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizards/work_order_cancel_views.xml',
        'views/sale_order_views.xml',
        'views/service_team_views.xml',
        'views/work_order_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
