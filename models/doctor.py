from odoo import models, fields, api, tools
import os
import base64
from datetime import date


class Doctor(models.Model):
    _name = 'hospital.doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Doctor Information'
    _rec_name = 'full_name'

    first_name = fields.Char(string="First Name*", required=True, tracking=True)
    last_name = fields.Char(string="Last Name*", required=True, tracking=True)
    full_name = fields.Char(string="Full Name", compute="_compute_full_name", store=True, tracking=True, readonly=True)
    date_of_birth = fields.Date(string="Date of Birth", tracking=True)
    age = fields.Integer(string="Age", readonly=True, compute="_compute_age", store=True, tracking=True)
    phone = fields.Char(string="Phone", tracking=True, default="+90 555 555 55 66")
    email = fields.Char(string="Email*", required=True, tracking=True)
    department_id = fields.Many2one('hospital.department', string="Department*", tracking=True, ondelete='cascade')
    shift_start = fields.Float(string="Shift Start", tracking=True, default=8.0)
    shift_end = fields.Float(string="Shift End", tracking=True, default=17.0)
    portrait = fields.Image(string="Portrait", tracking=True, default=lambda self: self._get_default_image())
    user_id = fields.Many2one('res.users', string="Related User", tracking=True, readonly=True, ondelete='cascade')

    # Address Fields (for invoice partner)
    street = fields.Char(string="Street", default="Istanbul")
    street2 = fields.Char(string="Street2")
    city = fields.Char(string="City", default="Istanbul")
    state_id = fields.Many2one('res.country.state', string="State")
    zip = fields.Char(string="ZIP", default="34000")
    country_id = fields.Many2one('res.country', string="Country", default=lambda self: self.env.ref('base.tr'))
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)

    _sql_constraints = [
        ('unique_email', 'unique(email)', 'Email is already used.')
    ]

    @api.onchange('first_name', 'last_name')
    def _onchange_name_fields(self):
        for record in self:
            if record.first_name and record.last_name and not record.email:
                record.email = f"{record.first_name.lower()}@{record.last_name.lower()}.com"

    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = f"{rec.first_name or ''} {rec.last_name or ''}".strip()

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = date.today()
                rec.age = today.year - rec.date_of_birth.year - (
                    (today.month, today.day) < (rec.date_of_birth.month, rec.date_of_birth.day)
                )
            else:
                rec.age = 0

    def _get_default_image(self):
        module_path = tools.config['addons_path'].split(',')[0]
        image_path = os.path.join(module_path, 'odoo_medical_module', 'static', 'description', 'doctor.png')
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read())
        return False

    @api.model
    def create(self, vals):
        doctor = super().create(vals)

        if not doctor.user_id and doctor.email:
            group_doctor = self.env.ref('odoo_medical_module.group_hospital_doctor')
            group_internal = self.env.ref('base.group_user')
            group_sales = self.env.ref('sales_team.group_sale_salesman')
            group_invoicing = self.env.ref('account.group_account_invoice')

            user = self.env['res.users'].sudo().create({
                'name': doctor.full_name,
                'login': doctor.email,
                'email': doctor.email,
                'password': doctor.email,
                'image_1920': doctor.portrait,
                'company_id': doctor.company_id.id,
                'street': doctor.street,
                'street2': doctor.street2,
                'city': doctor.city,
                'state_id': doctor.state_id.id,
                'zip': doctor.zip,
                'country_id': doctor.country_id.id,
                'currency_id': doctor.country_id.currency_id.id,  # Set the currency based on country

                'groups_id': [(6, 0, [group_internal.id, group_doctor.id, group_sales.id, group_invoicing.id])],
            })

            doctor.user_id = user.id

        return doctor

    @api.model
    def unlink(self):
        for record in self:
            # Delete related user and partner when the doctor is deleted
            if record.user_id:
                record.user_id.unlink()
            if record.partner_id:
                record.partner_id.unlink()

    # Smart button to open the user form view
    def action_view_user(self):
        for doctor in self:
            if doctor.user_id:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Related User',
                    'res_model': 'res.users',
                    'view_mode': 'form',
                    'view_id': self.env.ref('base.view_users_form').id,
                    'res_id': doctor.user_id.id,
                    'target': 'current',
                }
        return {}  # In case there's no linked user
