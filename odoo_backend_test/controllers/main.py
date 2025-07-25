from odoo import http
from odoo.http import request


class MaterialController(http.Controller):
    """ Controller Material """
    
    def _prepare_create_material(self, data):
        """ Fungsi Untuk Prepare data pembuatan material """
        return {
            'code': data['code'],
            'name': data['name'],
            'types': data['types'],
            'buy_price': data['buy_price'],
            'partner_id': data['partner_id'],
        }
    
    
    def _prepare_material(self, material):
        """ Fungsi Untuk Menyiapkan data get, update dan delete material """
        return {
            'id': material.id,
            'code': material.code,
            'name': material.name,
            'types': material.types,
            'buy_price': material.buy_price,
            'partner_id': material.partner_id.id,
        }
    
    
    def _check_material_data(self, data):
        """ Fungsi untuk mengecek material data beserta field """
        required_fields = ['code', 'name', 'types', 'buy_price', 'partner_id']
        if not all(field in data for field in required_fields):
            return {'status': 'error', 'message': 'Seluruh Field Mandatory.'}
        
        if data['buy_price'] < 100:
            return {'status': 'error', 'message': 'Harga Buy Price Material harus diatas 100.'}
        
        if data['types'] not in ['fabric', 'jeans', 'cotton']:
            return {'status': 'error', 'message': 'Material Type tidak ditemukan.'}
    
    
    @http.route('/api/materials', type='json', auth='public', csrf=False, methods=['POST'])
    def create_material(self, **kwargs):
        """ Fungsi Untuk Membuat data pembuatan material """
        try:
            data = request.jsonrequest
            self._check_material_data(data)
            
            partner = request.env['res.partner'].sudo().browse(data['partner_id'])
            
            if not partner.exists():
                return {'status': 'error', 'message': 'Supplier tidak ditemukan.'}
            
            material = request.env['material.material'].sudo().create(self._prepare_create_material(data))
            
            return {
                'status': 'success',
                'data': self._prepare_material(material)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    
    @http.route('/api/materials', type='json', auth='public', csrf=False, methods=['GET'])
    def get_materials(self, material_type=None):
        """ Fungsi Untuk Mengambil data material berdasarkan type """
        try:
            domain = []
            if material_type and material_type in ['fabric', 'jeans', 'cotton']:
                domain.append(('types', '=', material_type))
            
            materials = request.env['material.material'].sudo().search(domain)
            material_list = [self._prepare_material(material) for material in materials]
            return {'status': 'success', 'data': material_list}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    
    @http.route('/api/materials/<int:material_id>', type='json', auth='public', csrf=False, methods=['PUT'])
    def update_material(self, material_id, **kwargs):
        """ Fungsi Untuk Mengupdate data material berdasarkan ID """
        try:
            material = request.env['material.material'].sudo().browse(material_id)
            if not material.exists():
                return {'status': 'error', 'message': 'Material tidak ditemukan.'}
            
            data = request.jsonrequest
            if 'buy_price' in data and data['buy_price'] < 100:
                return {'status': 'error', 'message': 'Harga Buy Price Material harus diatas 100.'}
            
            if 'types' in data and data['types'] not in ['fabric', 'jeans', 'cotton']:
                return {'status': 'error', 'message': 'Material Type tidak ditemukan.'}
            
            if 'partner_id' in data:
                partner = request.env['res.partner'].sudo().browse(data['partner_id'])
                if not partner.exists():
                    return {'status': 'error', 'message': 'Supplier tidak ditemukan.'}
            
            material.write(data)
            return {
                'status': 'success',
                'data': self._prepare_material(material)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    
    @http.route('/api/materials/<int:material_id>', type='json', auth='public', csrf=False, methods=['DELETE'])
    def delete_material(self, material_id):
        """ Fungsi Untuk Menghapus data material berdasarkan ID """
        try:
            material_id = request.env['material.material'].sudo().browse(material_id)
            if not material_id.exists():
                return {'status': 'error', 'message': 'Material tidak ditemukan.'}
            
            material_id.unlink()
            return {'status': 'success', 'message': 'Material telah dihapus.'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
