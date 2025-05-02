from odoo import models, fields, api
from datetime import date


class Patient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'full_name'

    # Fields
    patient_id = fields.Char(string="Patient ID", readonly=True, copy=False, store=True, tracking=True)
    
    first_name = fields.Char(string="First Name*", required=True, store=True, tracking=True)
    last_name = fields.Char(string="Last Name", required=True, store=True, tracking=True)
    full_name = fields.Char(string="Full Name", compute="_compute_full_name", store=True, tracking=True)
    date_of_birth = fields.Date(string="Date of Birth", store=True, tracking=True)
    age = fields.Integer(string="Age", readonly=True, compute="_compute_age", store=True, tracking=True)
    
    phone = fields.Char(string="Phone", store=True, tracking=True, default="+90 555 555 55 55")
    email = fields.Char(string="Email", store=True, tracking=True)
    national_id_no = fields.Char(string="National ID No", store=True, tracking=True)

    user_id = fields.Many2one('res.users', string="Related User", store=True, tracking=True, readonly=True)
    partner_id = fields.Many2one('res.partner', string="Related Partner", readonly=True, store=True, tracking=True) 

    # Address fields
    street = fields.Char(string="Street", default="Istanbul")
    street2 = fields.Char(string="Street2")
    city = fields.Char(string="City", default="Istanbul")
    state_id = fields.Many2one('res.country.state', string="State")
    zip = fields.Char(string="ZIP", default="34000")
    country_id = fields.Many2one('res.country', string="Country", default=lambda self: self.env.ref('base.tr'))
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)

    _sql_constraints = [
        ('unique_national_id', 'unique(national_id_no)', 'National ID No must be unique.')
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

    @api.model
    def create(self, vals):
        vals['patient_id'] = self.env['ir.sequence'].next_by_code('patient.id.seq')
        patient = super().create(vals)

        if not patient.user_id and patient.email:
            group_patient = self.env.ref('odoo_medical_module.group_hospital_patient')
            group_internal = self.env.ref('base.group_user')

            partner = self.env['res.partner'].sudo().create({
                'name': patient.full_name,
                'email': patient.email,
                'street': patient.street,
                'street2': patient.street2,
                'city': patient.city,
                'state_id': patient.state_id.id,
                'zip': patient.zip,
                'country_id': patient.country_id.id,
                'type': 'invoice',
                'company_id': patient.company_id.id,
                'phone': patient.phone,
            })

            user = self.env['res.users'].sudo().create({
                'name': patient.full_name,
                'login': patient.email,
                'email': patient.email,
                'password': patient.email,
                'company_id': patient.company_id.id,
                'currency_id': patient.country_id.currency_id.id,
                'partner_id': partner.id,
                'groups_id': [(6, 0, [group_internal.id, group_patient.id])]
            })

            patient.user_id = user.id
            patient.partner_id = partner.id

        return patient

    def unlink(self):
        for record in self:
            if record.user_id:
                record.user_id.unlink()
            if record.partner_id:
                record.partner_id.unlink()
        return super().unlink()

    def action_view_patient_user(self):
        self.ensure_one()
        if self.user_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Related User',
                'res_model': 'res.users',
                'view_mode': 'form',
                'view_id': self.env.ref('base.view_users_form').id,
                'res_id': self.user_id.id,
                'target': 'current',
            }
        return {}

    def action_add_invoice_contact_popup(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Child Contact',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_parent_id': self.partner_id.id,
                'default_type': 'invoice',
                'default_use_parent_address': True,  # inherits address if desired
                'form_view_initial_mode': 'edit',
            }
        }





