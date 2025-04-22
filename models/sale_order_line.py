from odoo import models, fields
#this is inherited odoo model
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    #adding my appointment id to odoo sale order
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment')
