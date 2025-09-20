# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ServiceTeam(models.Model):
    """ New Model Service Team """
    _name = "service.team"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Service Team"
    
    
    name = fields.Char('Team Name', required=True, copy=False)
    leader_id = fields.Many2one('res.users', 'Team Leader', required=True, copy=False)
    member_ids = fields.Many2many('res.users', string='Team Members', copy=False)
