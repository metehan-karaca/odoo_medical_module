from odoo import models, fields, api

class AppointmentWizard(models.TransientModel):
    _name = 'hospital.appointment.wizard'
    _description = 'Appointment Wizard'

    patient_id = fields.Many2one('hospital.patient', string="Patient", required=True)
    doctor_id = fields.Many2many('hospital.doctor', string="Doctors", required=True)
    appointment_date = fields.Datetime(string="Appointment Date", required=True)
    

    def create_appointment(self):
        for wizard in self:
            appointment = self.env['hospital.appointment'].create({
                'patient_id': wizard.patient_id.id,
                'doctor_id': [(6, 0, wizard.doctor_id.ids)],
                'appointment_date': wizard.appointment_date,
                
                'stage': 'draft',
            })
        return {'type': 'ir.actions.act_window_close'}
