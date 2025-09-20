# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class WorkOrderCancel(models.TransientModel):
    """ Wizard Work Order Cancel """
    _name = "work.order.cancel"
    _description = "Work Order Cancel Reason"
    
    
    reason = fields.Text(required=True)
    
    
    @api.one
    def action_confirm(self):
        """ Fungsi untuk assign reason pada note di koresponding work order """
        work_id = self.env.context.get('work_order_id')
        if work_id:
            work_order_id = self.env['work.order'].sudo().browse(work_id)
            work_order_id.write({'note' : self.reason, 'state' : 'cancel'})
