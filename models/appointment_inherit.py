from odoo import models, fields, api

#I chose to inherit appointment model to make the additions instructed in chapter 2
class HospitalAppointment(models.Model):
    _inherit = 'hospital.appointment'  # inherits my appointment.py

    total_amount = fields.Char(string="Total Amount")
    pending_amount = fields.Char(string="Pending Amount")

    sale_order_lines = fields.One2many('sale.order.line', 'appointment_id', string="Sale Order Lines")

    def sale_orders_smart_button(self):
        sale_orders = self.env['sale.order'].search([('order_line.appointment_id', 'in', self.ids)])
        return {
            'name': 'Sale Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',

        }
    
    def invoice_smart_button(self):
        return True
    
    def payment_smart_button(self):
        return True





class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")







