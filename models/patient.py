from odoo import models, fields, api
from datetime import date


class Patient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient Information'


    # Patient Fields
    patient_id = fields.Char(string="Patient ID", required=True, readonly=True, copy=False, default='New', store=True)
    
    first_name = fields.Char(string="First Name", required=True, store=True)
    last_name = fields.Char(string="Last Name", required=True, store=True)
    full_name = fields.Char(string="Full Name", compute="_compute_full_name", store=True)
    date_of_birth = fields.Date(string="Date of Birth", store=True)
    age = fields.Integer(string="Age", readonly=True, compute="_compute_age", store=True)
    address = fields.Text(string="Address", store=True)

    phone = fields.Char(string="Phone", store=True)
    email = fields.Char(string="Email", store=True)
    national_id_no = fields.Char(string="National ID No", store=True)

    # sql constraints
    _sql_constraints = [
        ('unique_national_id', 'unique(national_id_no)', 'National ID No must be unique.')
    ]

    # generate patient id
    @api.model
    def create(self, vals):
        if vals.get('patient_id', 'New') == 'New':

            vals['patient_id'] = self.env['ir.sequence'].next_by_code('hospital.patient') or 'New'

        return super(Patient, self).create(vals)

    # first + last name
    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = f"{rec.first_name or ''} {rec.last_name or ''}".strip()

    # compute age
    @api.depends('date_of_birth') #I think depends work better than onchange here??
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = date.today()
                rec.age = today.year - rec.date_of_birth.year - (
                        (today.month, today.day) < (rec.date_of_birth.month, rec.date_of_birth.day)
                )
            else:
                rec.age = 0
