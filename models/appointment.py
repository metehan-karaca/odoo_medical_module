from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Appointment'
    _rec_name = 'code'

    appointment_date = fields.Datetime(string="Appointment Date", required=True, store=True, tracking=True)
    code = fields.Char(string="Code", readonly=True, copy=False, store=True, tracking=True)
    doctor_id = fields.Many2many('hospital.doctor', string="Doctors", store=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string="Patient", store=True, tracking=True, ondelete='cascade')
    stage = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string="Stage", default='in_progress', store=True, tracking=True)
    treatment_id = fields.One2many('hospital.treatment', 'appointment_id', string="Treatments", store=True, tracking=True, ondelete='cascade')

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, store=True, tracking=True, ondelete='cascade')
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", store=True, currency_field='currency_id')
    pending_amount = fields.Monetary(string="Pending Amount", compute="_compute_pending_amount", store=True, currency_field='currency_id')

    sale_order_lines = fields.One2many('sale.order.line', 'appointment_id', string="Sale Order Lines", store=True, tracking=True, ondelete='cascade')
    sale_order_ids = fields.One2many('sale.order', 'appointment_id', string="Sale Orders", store=True, tracking=True, ondelete='cascade')
    invoice_ids = fields.One2many('account.move', 'appointment_id', string="Invoices", store=True, tracking=True, ondelete='cascade')
    payment_ids = fields.One2many('account.payment', 'appointment_id', string="Payments", store=True, tracking=True, ondelete='cascade')

    sale_order_count = fields.Integer(string="Sale Order Count", compute="_compute_sale_order_count", store=True, tracking=True)
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_invoice_count", store=True, tracking=True)
    payment_count = fields.Integer(string="Payment Count", compute="_compute_payment_count", store=True, tracking=True)

    @api.depends('sale_order_ids.amount_total')
    def _compute_total_amount(self):
        for record in self:
            total = sum(order.amount_total for order in record.sale_order_ids)
            record.total_amount = total

    @api.depends('payment_ids.amount')
    def _compute_pending_amount(self):
        for record in self:
            total_paid = sum(payment.amount for payment in record.payment_ids)
            record.pending_amount = record.total_amount - total_paid

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('Appointment.id.seq')
        return super().create(vals)

    def set_to_in_progress(self):
        self.stage = 'in_progress'

    def set_to_done(self):
        self.stage = 'done'

    def set_to_draft(self):
        self.stage = 'draft'

    def set_to_cancel(self):
        self.stage = 'cancel'

    @api.depends('sale_order_ids')
    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = len(record.sale_order_ids)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            # Count invoices with the same domain used in the smart button
            valid_invoices = record.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice')
            record.invoice_count = len(valid_invoices)

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for record in self:
            record.payment_count = len(record.payment_ids)

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
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('appointment_id', '=', self.id),
                       ('move_type', '=', 'out_invoice')],
        }

    def payment_smart_button(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('appointment_id', '=', self.id)],
        }

    def create_sale_order_button(self):
        self.ensure_one()
        if not self.patient_id.partner_id:
            raise UserError("This patient has no linked contact. Please create or link a res.partner first.")

        sale_order = self.env['sale.order'].create({
            'partner_id': self.patient_id.partner_id.id,
            'appointment_id': self.id,
            'origin': f"Appointment #{self.code or self.id}",
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    #validations
    def write(self, vals):
        if vals.get('stage') == 'done':
            for record in self:
                if record.pending_amount > 0:
                    raise ValidationError("cannot be marked as done with unpaid money")

                sale_orders = self.env['sale.order'].search([('appointment_id', '=', record.id)])
                if not sale_orders:
                    raise ValidationError("cannot be marked as done without a sale order")

                invoices = self.env['account.move'].search([
                    ('appointment_id', '=', record.id),
                    ('move_type', '=', 'out_invoice'),
                    ('state', '!=', 'cancel')
                ])
                if not invoices:
                    raise ValidationError("cannot be marked as done without invoice.")
        return super(HospitalAppointment, self).write(vals)





class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")

    @api.model
    def create(self, vals):
        if 'order_id' in vals:
            sale_order = self.env['sale.order'].browse(vals['order_id'])
            if sale_order.appointment_id:
                vals['appointment_id'] = sale_order.appointment_id.id

        # Call the super method to create the record
        return super(SaleOrderLine, self).create(vals)



class SaleOrder(models.Model):
    _inherit = 'sale.order'
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")

    def action_open_appointment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointment',
            'res_model': 'hospital.appointment',
            'view_mode': 'form',
            'res_id': self.appointment_id.id,
            'context': {'default_appointment_id': self.appointment_id.id},
        }
    
    # for make payment button in sale order form
    def action_make_payment(self):
        self.ensure_one()
        payment_vals = {
            'partner_id': self.partner_id.id,
            'amount': self.amount_total,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
            'appointment_id': self.appointment_id.id,
            'sale_order_id': self.id,
            
            
        }
        payment = self.env['account.payment'].create(payment_vals)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Payment',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'res_id': payment.id,
            'target': 'new',
        }
    
    
    
    #link payment to invoice and validation
    def action_create_invoice(self):
        res = super(SaleOrder, self).action_create_invoice()

        for order in self:
            invoices = self.env['account.move'].search([
                ('invoice_origin', '=', order.name),
                ('move_type', '=', 'out_invoice')
            ])

            payments = self.env['account.payment'].search([
                ('appointment_id', '=', order.appointment_id.id),
                ('state', '=', 'posted')
            ])

            for invoice in invoices:
                for payment in payments:
                    if invoice.state != 'posted':
                        invoice.action_post()

                    # Assign payment to invoice
                    payment_move_line = payment.line_ids.filtered(lambda line: line.account_id == invoice.line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'receivable').account_id and line.credit > 0)

                    if payment_move_line:
                        invoice.js_assign_outstanding_line(payment_move_line.id)

        return res
    

    def action_confirm(self):
        for order in self:
            if order.appointment_id:
                payments = self.env['account.payment'].search([('appointment_id', '=', order.appointment_id.id)])
                if not payments:
                    raise ValidationError("Cannot confirm the sale order before at least one payment is made for the associated appointment.")
        return super(SaleOrder, self).action_confirm()
    


    #adding to show paid amounts at the bottom
    payment_ids = fields.One2many('account.payment', 'sale_order_id', string="Payments")

    amount_paid = fields.Monetary(string="Amount Paid", compute='_compute_payment_amounts', store=True)
    amount_due = fields.Monetary(string="Amount Due", compute='_compute_payment_amounts', store=True)

    @api.depends('amount_total', 'payment_ids.amount', 'payment_ids.state')
    def _compute_payment_amounts(self):
        for order in self:
            payments = self.env['account.payment'].search([
                ('sale_order_id', '=', order.id),
                ('state', '=', 'posted')
            ])
            total_paid = sum(payments.mapped('amount'))
            order.amount_paid = total_paid
            order.amount_due = order.amount_total - total_paid




class AccountMove(models.Model):
    _inherit = 'account.move'
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")

    @api.model
    def create(self, vals):
        # Automatically link invoice to appointment via sale order
        if not vals.get('appointment_id') and vals.get('invoice_origin'):
            sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
            if sale_order and sale_order.appointment_id:
                vals['appointment_id'] = sale_order.appointment_id.id
        return super(AccountMove, self).create(vals)
    
    def action_open_appointment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointment',
            'res_model': 'hospital.appointment',
            'view_mode': 'form',
            'res_id': self.appointment_id.id,
            'context': {'default_appointment_id': self.appointment_id.id},
        }

    


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment", store=True)

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", store=True)

    
    def action_open_appointment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointment',
            'res_model': 'hospital.appointment',
            'view_mode': 'form',
            'res_id': self.appointment_id.id,
            'context': {'default_appointment_id': self.appointment_id.id},
        }

