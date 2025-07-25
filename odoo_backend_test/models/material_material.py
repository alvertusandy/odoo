from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MaterialMaterial(models.Model):
    """ Material Object """
    _name = "material.material"
    _description = "Material"
    _rec_name = 'name'
    
    
    name = fields.Char(string="Material Name", required=True, copy=False)
    code = fields.Char(string="Material Code", required=True, copy=False)
    types = fields.Selection(selection=[('fabric', 'Fabric'), ('jeans', 'Jeans'), ('cotton', 'Cotton')],
                            default='fabric', string="Material Type", required=True,  copy=False)
    buy_price = fields.Float(copy=False)
    partner_id = fields.Many2one('res.partner', string="Supplier", required=True,  copy=False)
    
    
    @api.constrains('buy_price')
    def _check_buy_price(self):
        """ Fungsi Constrain untuk limit harga beli ketika create/write """
        for record in self:
            if record.buy_price < 100:
                raise ValidationError('Material Buy Price harus di atas 100.')
