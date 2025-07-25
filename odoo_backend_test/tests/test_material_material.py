from odoo.tests.common import HttpCase
from odoo.exceptions import ValidationError
from odoo.tests import tagged
import json
import requests


@tagged('odoo_backend_material_registration')
class TestMaterialRegistration(HttpCase):
    
    def setUp(self):
        """ Fungsi SetUP """
        super(TestMaterialRegistration, self).setUp()
        self.base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        self.url = self.base_url + '/api/materials'
        self.Material = self.env['material.material'].sudo()
        self.Partner = self.env['res.partner'].sudo()
        self.supplier_id = self.Partner.create({
            'name': 'Test Supplier 1',
        })
        self.test_material = self.env['material.material'].create({
            'code': 'TEST001',
            'name': 'Test Material',
            'types': 'fabric',
            'buy_price': 120.0,
            'partner_id': self.supplier_id.id,
        })
    
    
    def test_create_supplier(self):
        """ Fungsi Test untuk membuat supplier/kontak baru """
        supplier_id = self.Partner.create({
            'name': 'New Supplier 1',
        })
        self.assertTrue(supplier_id.id, "Supplier should be created with an ID")
        self.assertEqual(supplier_id.name, 'New Supplier 1', "Supplier name should match")
    
    
    def test_create_material_fabric(self):
        """ Fungsi Test untuk membuat data Material dengan type Fabric """
        material = self.Material.create({
            'partner_id': self.supplier_id.id,
            'code': 'MAT001',
            'name': 'Test Material Fabric',
            'types': 'fabric',
            'buy_price': 200.0,
        })
        self.assertTrue(material.id, "Material should be created with an ID")
        self.assertEqual(material.code, 'MAT001', "Material code should match")
        self.assertEqual(material.name, 'Test Material Fabric', "Material name should match")
        self.assertEqual(material.types, 'fabric', "Material type should match")
        self.assertEqual(material.buy_price, 200.0, "Material buy price should match")
        self.assertEqual(material.partner_id.id, self.supplier_id.id, "Supplier ID should match")
    
    
    def test_create_material_jeans(self):
        """ Fungsi Test untuk membuat data Material dengan type Jeans """
        material = self.Material.create({
            'partner_id': self.supplier_id.id,
            'code': 'MAT002',
            'name': 'Test Material Jeans',
            'types': 'jeans',
            'buy_price': 300.0,
        })
        self.assertTrue(material.id, "Material should be created with an ID")
        self.assertEqual(material.code, 'MAT002', "Material code should match")
        self.assertEqual(material.name, 'Test Material Jeans', "Material name should match")
        self.assertEqual(material.types, 'jeans', "Material type should match")
        self.assertEqual(material.buy_price, 300.0, "Material buy price should match")
        self.assertEqual(material.partner_id.id, self.supplier_id.id, "Supplier ID should match")
    
    
    def test_create_material_cotton(self):
        """ Fungsi Test untuk membuat data Material dengan type Katun """
        material = self.Material.create({
            'partner_id': self.supplier_id.id,
            'code': 'MAT003',
            'name': 'Test Material Cotton',
            'types': 'cotton',
            'buy_price': 400.0,
        })
        self.assertTrue(material.id, "Material should be created with an ID")
        self.assertEqual(material.code, 'MAT003', "Material code should match")
        self.assertEqual(material.name, 'Test Material Cotton', "Material name should match")
        self.assertEqual(material.types, 'cotton', "Material type should match")
        self.assertEqual(material.buy_price, 400.0, "Material buy price should match")
        self.assertEqual(material.partner_id.id, self.supplier_id.id, "Supplier ID should match")
    
    
    def test_material_buy_price_invalid(self):
        """ Fungsi Test untuk membuat data Material dengan harga beli < 100 """
        with self.assertRaises(ValidationError, msg="Should fail if buy price < 100"):
            self.Material.create({
                'code': 'MAT004',
                'name': 'Test Material Fabric 2',
                'types': 'fabric',
                'buy_price': 50.0,
                'partner_id': self.supplier_id.id,
            })
    
    
    def test_material_type_invalid(self):
        """ Fungsi Test untuk membuat data Material dengan type yang belum di define """
        with self.assertRaises(Exception, msg="Should fail if material_type is invalid"):
            self.Material.create({
                'code': 'MAT005',
                'name': 'Test Material Invalid',
                'types': 'silk',
                'buy_price': 150.0,
                'partner_id': self.supplier_id.id,
            })
    
    
    def test_create_material_API(self):
        """ Fungsi Test untuk membuat data Material melalui controller """
        payload = {
            'code': 'MAT006',
            'name': 'Test Material Fabric API',
            'types': 'fabric',
            'buy_price': 150.0,
            'partner_id': self.supplier_id.id,
        }

        response = requests.post(
            self.url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json().get('result')
        
        self.assertEqual(response_data.get('status'), 'success', "API should return success")
        self.assertEqual(response_data['data']['code'], 'MAT006', "Material code should match")
        self.assertEqual(response_data['data']['types'], 'fabric', "Material type should match")
        self.assertEqual(response_data['data']['partner_id'], self.supplier_id.id, "Supplier ID should match")
    
    
    def test_get_fabric_materials_API(self):
        """ Fungsi Test untuk mengambil data Material Fabric melalui controller """
        payload = {
            'material_type': 'fabric',
        }
        response = requests.get(
            self.url,
            headers={'Content-Type': 'application/json'},
            json=payload
        )

        print("Response >>>>x:", response.text)
        self.assertEqual(response.status_code, 200)
        response_data = response.json().get('result')
        
        self.assertEqual(response_data['status'], 'success')
        self.assertIsInstance(response_data['data'], list) 
    
    
    def test_update_material_API(self):
        """ Fungsi Test untuk mengubah/mengupdate data Material melalui controller """
        payload = {
            'buy_price': 533.00,
            'types': 'cotton', 
            'partner_id': self.supplier_id.id,
        }
        response = requests.put(
            f"{self.url}/{self.test_material.id}",
            headers={'Content-Type': 'application/json'},
            json=payload
        )
        self.assertEqual(response.status_code, 200, "API should return 200 on success")
        response_data = response.json().get('result')
        self.assertEqual(response_data['status'], 'success', "API should return success")
        updated_data = response_data['data']
        self.assertEqual(updated_data['buy_price'], 533.0, "Buy Price should be updated")
        self.assertEqual(updated_data['types'], 'cotton', "Material Type should be updated")
        self.assertEqual(updated_data['partner_id'], self.supplier_id.id, "Supplier should be updated")
    
    
    def test_delete_material_API(self):
        """ Fungsi Test untuk menghapus data Material melalui controller """
        test_material = self.env['material.material'].create({
            'code': 'DEL_TEST_001',
            'name': 'Material to Delete',
            'types': 'fabric',
            'buy_price': 100.0,
            'partner_id': self.supplier_id.id,
        })
        
        response = requests.delete(
            f"{self.url}/{self.test_material.id}",
            headers={'Content-Type': 'application/json'},
            data='{}'
        )
        self.assertEqual(response.status_code, 200, "API should return 200 on success")
        
        response_data = response.json().get('result')
        self.assertEqual(response_data['status'], 'success', "API should return success")
        self.assertEqual(
            response_data['message'],
            'Material telah dihapus.',
            "Confirm deletion message"
        )
        deleted_material = self.env['material.material'].browse(test_material.id)
        self.assertFalse(deleted_material.exists(), "Material sudah terhapus di Database.")
