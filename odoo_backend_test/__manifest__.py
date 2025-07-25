{
    'name': 'Odoo Backend Test Material',
    'version': '14.0.0.1',
    'author': 'Albertus Andy Setyaputra',
    'depends': [
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/material_material_views.xml',
        'views/menuitem.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
