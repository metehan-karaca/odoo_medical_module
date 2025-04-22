from odoo import models, fields, api

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Hospital Appointment'
    _rec_name = 'code'

    appointment_date = fields.Datetime(string="Appointment Date", required=True, store=True)
    code = fields.Char(string="Code", readonly=True, copy=False, store=True)
    doctor_id = fields.Many2many('hospital.doctor', string="Doctors", store=True)
    patient_id = fields.Many2one('hospital.patient', string="Patient", store=True)
    stage = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string="Stage", default='draft', store=True)
    treatment_id = fields.One2many('hospital.treatment', 'appointment_id', string="Treatments", store=True)


    # generate patient id from hospital_sequence.xml
    @api.model
    def create(self, vals):

        vals['code'] = self.env['ir.sequence'].next_by_code('Appointment.id.seq')
        return super(HospitalAppointment, self).create(vals)
    
    #added for states change buttons part
    def set_to_in_progress(self):
        self.write({'stage': 'in_progress'})

    def set_to_done(self):
        self.write({'stage': 'done'})

    def set_to_draft(self):
        self.write({'stage': 'draft'})

    def set_to_cancel(self):
        self.write({'stage': 'cancel'})


