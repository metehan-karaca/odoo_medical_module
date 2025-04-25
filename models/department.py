import os
import base64
from odoo import models, fields, tools


class Department(models.Model):
    _name = 'hospital.department'
    _inherit = ['mail.thread', 'mail.activity.mixin'] #chatter
    _description = 'Hospital Department'
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, store=True, tracking=True)
    code = fields.Char(string="Code", required=True, store=True, tracking=True)
    icon = fields.Image(string="Icon", store=True, tracking=True, default= lambda self: self._get_default_image())    

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'The department code must be unique.')
    ]


    def _get_default_image(self):
        module_path = tools.config['addons_path'].split(',')[0]  # Adjust if you have multiple paths
        image_path = os.path.join(module_path, 'odoo_medical_module', 'static', 'description', 'icon.png')
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read())
        return False
