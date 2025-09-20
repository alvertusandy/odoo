# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WorkOrder(models.Model):
    """ New Model Work Order """
    _name = "work.order"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Work Order"
    
    
    name = fields.Char('WO Number', readonly=True, copy=False, default=lambda self: _('New'))
    order_id = fields.Many2one('sale.order', 'Booking Order Reference', readonly=True, copy=False)
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', readonly=True, copy=False)
    team_id = fields.Many2one('service.team', 'Team', required=True, copy=False)
    leader_id = fields.Many2one('res.users', 'Team Leader', required=True, copy=False)
    member_ids = fields.Many2many('res.users', string='Team Members', copy=False)
    start_plan = fields.Datetime('Planned Start', required=True, copy=False)
    end_plan = fields.Datetime('Planned End', required=True, copy=False)
    start_date = fields.Datetime('Date Start', readonly=True, copy=False)
    end_date = fields.Datetime('Date End', readonly=True, copy=False)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Order Status', copy=False, store=True, default='pending')
    note = fields.Text(copy=False, readonly=True)
    
    
    @api.model
    def create(self, vals):
        """ Fungsi untuk assign sequence pada nama work order """
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('work.order') or _('New')
        result = super(WorkOrder, self).create(vals)
        return result
    
    
    @api.model
    def _update_work_order(self, state, start_date, end_date):
        """ Fungsi untuk mengubah state dan date pada work order """
        self.ensure_one()
        self.write({
            'state' : state,
            'start_date' : start_date,
            'end_date' : end_date
        })
    
    
    @api.multi
    def action_start(self):
        """ Fungsi untuk mengubah work order ke In progress """
        for work_id in self:
            work_id._update_work_order('in_progress', fields.Datetime.now(), False)
    
    
    @api.multi
    def action_end(self):
        """ Fungsi untuk mengubah work order ke Done """
        for work_id in self:
            work_id._update_work_order('done', work_id.start_date, fields.Datetime.now())
    
    
    @api.multi
    def action_reset(self):
        """ Fungsi untuk mereset work order """
        for work_id in self:
            work_id._update_work_order('pending', False, False)
    
    
    @api.multi
    def action_cancel(self):
        """ Fungsi action cancel untuk meredirect ke popup wizard cancel guna menulis reason """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reason for cancellation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'work.order.cancel',
            'context' : {'work_order_id' : self.id},
            'target': 'new',
        }
    
    
    @api.multi
    def unlink(self):
        """ Fungsi unlink untuk membatasi ketika user delete work order saat masih progress """
        for work_id in self:
            if work_id.state == 'in_progress':
                raise ValidationError(_('You cannot delete this Work Order in state Progress.'))
        return super(WorkOrder, self).unlink()
