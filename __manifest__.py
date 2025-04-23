# -*- coding: utf-8 -*-
{
    'name': "medical_appointment_system",

    'summary': """
        Hospital Management System""",

    'description': """
        Work in progress
    """,

    'author': "My Company",
    'website': "https://github.com/metehan-karaca/odoo_medical_module",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale', #added to pull sale.order.line in appointment
        'mail',  # added to use message_follower_ids, activity_ids, and message_ids all for chatter view
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',


        'views/menu_views.xml',
        'views/templates.xml',
        'views/hospital_doctor_views.xml',
        'views/hospital_patient_views.xml',
        'views/hospital_department_views.xml',
        'views/hospital_appointment_views.xml',
        'views/hospital_treatment_views.xml',
        'views/hospital_appointment_wizard_views.xml',
        'views/hospital_appointment_inherit_views.xml',


        'data/hospital_sequence.xml', 
        

    ],
    # only loaded in demonstration mode, not working yet
    'demo': [
        'demo/demo.xml',

    ],



    'application': True,
    'installable': True,
}
