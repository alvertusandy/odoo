# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    """ Inherit Model Sale Order """
    _inherit = 'sale.order'
    
    
    @api.model
    def _default_booking_order(self):
        """ Fungsi default untuk assign value pada is_booking_order """
        return bool(self.env.context.get('from_booking_order_menu'))
    
    
    is_booking_order = fields.Boolean(default=_default_booking_order, copy=False)
    service_team_id = fields.Many2one('service.team', 'Team', copy=False)
    service_leader_id = fields.Many2one('res.users', 'Team Leader', copy=False)
    service_member_ids = fields.Many2many('res.users', string='Team Members', copy=False)
    start_book = fields.Datetime(copy=False)
    end_book = fields.Datetime(copy=False)
    work_orders_count = fields.Integer(string="Work Orders",
                                    compute='compute_work_orders_count',
                                    default=0)
    
    
    @api.multi
    def compute_work_orders_count(self):
        """ Fungsi Compute untuk mengambil data work orders dan ditampilkan di smart button """
        for record in self:
            record.work_orders_count = self.env['work.order'].sudo().search_count([('order_id', '=', self.id)])
    
    
    @api.multi
    def action_get_work_orders(self):
        """ Fungsi untuk menampilkan Work orders dari smart button """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Work Orders',
            'view_mode': 'tree,form',
            'res_model': 'work.order',
            'domain': [('order_id', '=', self.id)],
            'context': "{'create': False, 'edit': False, 'delete': False}"
        }
    
    
    def _update_service_fields(self, leader_id, member_ids):
        """ Fungsi untuk assign value pada field services """
        self.update({
            'service_leader_id' : leader_id,
            'service_member_ids' : member_ids
        })
    
    
    @api.onchange('service_team_id')
    def _onchange_service_team(self):
        """ Fungsi Onchange untuk merubah field services berdasarkan value service_team_id """
        leader_id = self.service_team_id.leader_id.id if self.service_team_id else False
        member_ids = self.service_team_id.member_ids.ids if self.service_team_id else False
        self._update_service_fields(leader_id, member_ids)
    
    
    @api.constrains('start_book', 'end_book')
    def _check_booking_dates(self):
        """ Validate start and end book dates """
        today = fields.Datetime.now()
        
        for order in self:
            today_convert = fields.Datetime.from_string(fields.Datetime.now())
            today_str = today_convert.strftime("%d-%m-%Y %H:%M:%S")
            
            if order.start_book and order.start_book < today:
                raise ValidationError(_
                    ("Start Book cannot be in the past. Please select a future date larger than Today (%s) for Start Book.") 
                    % today_str)
            if order.end_book and order.end_book < today:
                raise ValidationError(_
                    ("End Book cannot be in the past. Please select a future date larger than Today (%s) for End Book.") 
                    % today_str)
            if order.start_book and order.end_book and order.end_book < order.start_book:
                raise ValidationError(_("End Book cannot be earlier than Start Book."))
    
    
    @api.multi
    def _get_work_orders(self, team_id, leader_id, start_book, end_book):
        """ Fungsi untuk mendapatkan work order yang overlap dengan SQL query """
        self.ensure_one()
        start_book_str = start_book if isinstance(start_book, str) else start_book.strftime('%Y-%m-%d %H:%M:%S')
        end_book_str = end_book if isinstance(end_book, str) else end_book.strftime('%Y-%m-%d %H:%M:%S')
        
        sql_query = """
            SELECT wo.id, wo.name, so.name as order_name
            FROM work_order wo
            LEFT JOIN sale_order so 
                ON wo.order_id = so.id
            WHERE wo.state NOT IN ('cancel')
                AND wo.team_id = %s
                AND wo.leader_id = %s
                AND (
                    (%s < wo.start_plan AND %s > wo.start_plan AND %s <= wo.end_plan)
                    OR
                    (%s >= wo.start_plan AND %s <= wo.end_plan)
                    OR
                    (%s >= wo.start_plan AND %s < wo.end_plan AND %s > wo.start_plan)
                    OR
                    (%s <= wo.start_plan AND %s >= wo.end_plan)
                )
                AND wo.start_plan IS NOT NULL
                AND wo.end_plan IS NOT NULL
            ORDER BY wo.start_plan
        """
        
        self.env.cr.execute(sql_query, (
            team_id, leader_id,
            start_book_str, end_book_str, end_book_str,
            start_book_str, end_book_str,
            start_book_str, start_book_str, start_book_str,
            start_book_str, end_book_str
        ))
        
        results = self.env.cr.dictfetchall()
        
        if results:
            work_order_ids = self.env['work.order'].browse([r['id'] for r in results])
            return work_order_ids
        else:
            return False
    
    
    @api.model
    def _check_assigned_work_orders(self, is_from_confirm=False):
        """ Fungsi untuk mengecek work order yang sudah di assign """
        self.ensure_one()
        work_order_ids = self._get_work_orders(
            self.service_team_id.id, 
            self.service_leader_id.id, 
            self.start_book, 
            self.end_book
        )
        
        if work_order_ids:
            work_id = work_order_ids[0]
            so_name = work_id.order_id.name if work_id.order_id else "Unknown SO"
            raise UserError(_("Team already has work order during that period on %s") % so_name)
        if not is_from_confirm:
            raise UserError(_("Team is available for booking"))
    
    
    @api.one
    def action_check_team(self):
        """ Fungsi untuk mengecek availability dari work order dari team dan leader """
        if not self.start_book or not self.end_book:
            raise UserError(_("Please set Booking Start and Booking End before checking availability."))
        self._check_assigned_work_orders(False)
    
    
    @api.model
    def _create_work_order(self):
        """ Fungsi untuk membuat Work Order """
        self.ensure_one()
        self.env['work.order'].sudo().create({
            'order_id' : self.id,
            'team_id' : self.service_team_id.id,
            'leader_id' : self.service_leader_id.id,
            'member_ids' : [(6, 0, self.service_member_ids.ids)],
            'start_plan' : self.start_book,
            'end_plan' : self.end_book
        })
    
    
    @api.multi
    def action_confirm(self):
        """ Inherit Fungsi Action Confirm untuk mengecek availability dari work order team dan leader """
        self._check_assigned_work_orders(True)
        res = super(SaleOrder, self).action_confirm()
        self._create_work_order()
        return res
    
    
    @api.multi
    def unlink(self):
        """ Fungsi unlink untuk membatasi ketika user delete sale order saat work order masih progress """
        for sale_id in self:
            if self.env.context.get('from_booking_order_menu'):
                existing_work_orders_id = self.env['work.order'].sudo().search([('order_id', '=', sale_id.id), 
                                                                                ('state', '=', 'in_progress')],
                                                                                limit=1)
                if existing_work_orders_id:
                    raise ValidationError(_('You cannot delete this Sale Order %s because there is In Progress Work Order %s.')
                                        % (sale_id.name, existing_work_orders_id.name))
        return super(SaleOrder, self).unlink()
