from odoo import models, fields, api

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _inherit = 'hospital.appointment'

    total_amount = fields.Char(string="Total Amount")
    pending_amount = fields.Char(string="Pending Amount")

    sale_order_lines = fields.One2many('sale.order.line', 'appointment_id', string="Sale Order Lines")
    sale_orders = fields.One2many('sale.order', 'appointment_id', string="Sale Orders")



    sale_order_count = fields.Integer(string="Sale Order Count", compute="_compute_sale_order_count")
    invoice_count = fields.Integer(string="Invoice Count", default=10)

    @api.depends('sale_orders')
    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = len(record.sale_orders)
            

    def sale_orders_smart_button(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Orders',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('appointment_id', '=', self.id)],
            'context': {'default_appointment_id': self.id},
        }

    def invoice_smart_button(self):
        return True

    def payment_smart_button(self):
        return True

    def create_sale_order_button(self):
        self.ensure_one()
        sale_order = self.env['sale.order'].create({
            'partner_id': self.patient_id.id,  # assumes appointment has patient_id
            'appointment_id': self.id,
            'origin': f"Appointment #{self.id}",
        })

        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'appointment_id': self.id,
            'name': f"Service for appointment {self.code or self.id}",
            'product_uom_qty': 1,
            'price_unit': 100.0,
            'product_id': self.env.ref('product.product_product_4').id,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Created Sale Order',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
        }
    


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
