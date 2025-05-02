from odoo import models, fields, api

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Appointment'
    _rec_name = 'code'

    appointment_date = fields.Datetime(string="Appointment Date", required=True, store=True, tracking=True)
    code = fields.Char(string="Code", readonly=True, copy=False, store=True, tracking=True)
    doctor_id = fields.Many2many('hospital.doctor', string="Doctors", store=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string="Patient", store=True, tracking=True)
    stage = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string="Stage", default='draft', store=True, tracking=True)
    treatment_id = fields.One2many('hospital.treatment', 'appointment_id', string="Treatments", store=True, tracking=True)

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", store=True, currency_field='currency_id')
    pending_amount = fields.Monetary(string="Pending Amount", compute="_compute_total_amount", store=True, currency_field='currency_id')

    sale_order_lines = fields.One2many('sale.order.line', 'appointment_id', string="Sale Order Lines")
    sale_order_ids = fields.One2many('sale.order', 'appointment_id', string="Sale Orders")
    invoice_ids = fields.One2many('account.move', 'appointment_id', string="Invoices")
    payment_ids = fields.One2many('account.payment', 'appointment_id', string="Payments")

    sale_order_count = fields.Integer(string="Sale Order Count", compute="_compute_sale_order_count")
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_invoice_count")
    payment_count = fields.Integer(string="Payment Count", compute="_compute_payment_count")

    @api.depends('sale_order_lines.price_unit', 'sale_order_lines.product_uom_qty')
    def _compute_total_amount(self):
        for record in self:
            total = sum(line.price_unit * line.product_uom_qty for line in record.sale_order_lines)
            record.total_amount = total

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
            record.invoice_count = len(record.invoice_ids)

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
            'domain': [('appointment_id', '=', self.id)],
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




class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")

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
    
        
    def action_make_payment(self):
        self.ensure_one()
        payment_vals = {
            'partner_id': self.partner_id.id,
            'amount': self.amount_total,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
            
        }
        payment = self.env['account.payment'].create(payment_vals)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Payment',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'res_id': payment.id,
            'target': 'current',
        }




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

    @api.model
    def create(self, vals):
        # Link payment to appointment via invoice
        if not vals.get('appointment_id') and vals.get('invoice_ids'):
            invoices = self.env['account.move'].browse(vals['invoice_ids'][0][2])  # [0][2] = list of invoice IDs
            if invoices:
                appointment = invoices[0].appointment_id
                if appointment:
                    vals['appointment_id'] = appointment.id
        return super(AccountPayment, self).create(vals)
    
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

