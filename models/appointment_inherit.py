from odoo import models, fields, api

#I chose to inherit appointment model to make the additions instructed in chapter 2
class HospitalAppointment(models.Model):
    _inherit = 'hospital.appointment'  # inherits my appointment.py

    total_amount = fields.Char(string="Total Amount")
    pending_amount = fields.Char(string="Pending Amount")

    sale_order_lines = fields.One2many('sale.order.line', 'appointment_id', string="Sale Order Lines")

    def sale_orders_smart_button(self):
        return True
    
    def invoice_smart_button(self):
        return True
    
    def payment_smart_button(self):
        return True





class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")







