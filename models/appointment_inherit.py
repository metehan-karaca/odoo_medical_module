from odoo import models, fields, api

class HospitalAppointment(models.Model):
    _inherit = 'hospital.appointment'  # inherits my appointment.py

    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total_amount', store=True)
    pending_amount = fields.Monetary(string='Pending Amount', compute='_compute_pending_amount', store=True)
    order_line_ids = fields.One2many('sale.order.line', 'appointment_id', string='Sale Order Lines')
    #!!!! get appointment_id from inherited sale.order.line here

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)

    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.order_line_ids.mapped('price_subtotal'))

    def _compute_pending_amount(self):
        for rec in self:
            invoices = self.env['account.move'].search([('invoice_origin', '=', rec.code), ('state', '=', 'posted')])
            paid = sum(invoices.mapped('amount_residual'))
            rec.pending_amount = paid

    # Smart buttons actions
    def action_view_sale_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Orders',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('appointment_id', '=', self.id)],
            'context': {'default_appointment_id': self.id},
        }

    def action_view_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('invoice_origin', '=', self.code)],
        }

    def action_view_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('ref', '=', self.code)],
        }
