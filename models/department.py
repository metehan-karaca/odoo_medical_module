from odoo import models, fields


class Department(models.Model):
    _name = 'hospital.department'
    _description = 'Hospital Department'
    _rec_name = 'code'

    name = fields.Char(string="Name", required=True, store=True)
    code = fields.Char(string="Code", required=True, store=True)    

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'The department code must be unique.')
    ]
