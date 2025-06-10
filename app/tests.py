from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Producto, Categoria, Cart, CartItem
from django.core.files.uploadedfile import SimpleUploadedFile


class AppViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='usuarioP', password='12345')
        self.client.login(username='usuarioP', password='12345')


        self.categoria = Categoria.objects.create(nom_categoria='Singles')


        image = SimpleUploadedFile(
        name='test_image.jpg',
        content=b'\x47\x49\x46\x38\x39\x61',  
        content_type='image/gif'
        )


        self.producto = Producto.objects.create(
            id_categoria=self.categoria,
            nom_producto='ProductoP',
            descripcion='DescripciónP',
            cantidad='5',
            precio='500',
            foto=image,
        )
       
        self.cart = Cart.objects.create(user=self.user)


    def test_add_to_cart(self):
        response = self.client.get(reverse('add_to_cart', args=[self.producto.id_producto]))
        self.assertRedirects(response, reverse('cart_detail'))


        cart_item = CartItem.objects.get(cart=self.cart, product=self.producto)
        self.assertEqual(cart_item.quantity, 1)


    def test_cart_detail_view(self):
        response = self.client.get(reverse('cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/cart_detail.html')


    def test_remove_from_cart(self):
       
        CartItem.objects.create(cart=self.cart, product=self.producto, quantity=2)


        response = self.client.get(reverse('remove_from_cart', args=[self.producto.id_producto]))
        self.assertRedirects(response, reverse('cart_detail'))


       
        self.assertFalse(CartItem.objects.filter(cart=self.cart, product=self.producto).exists())


    def test_update_cart_item_quantity(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.producto, quantity=2)


       
        response = self.client.post(reverse('update_cart_item', args=[self.producto.id_producto]), {'quantity': 5})
        self.assertRedirects(response, reverse('cart_detail'))


        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)


       
        response = self.client.post(reverse('update_cart_item', args=[self.producto.id_producto]), {'quantity': 0})
        self.assertRedirects(response, reverse('cart_detail'))
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())


    def test_producto_list_view(self):
        response = self.client.get(reverse('producto_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/producto_list.html')
        self.assertIn(self.producto, response.context['productos'])


    def test_producto_create_view(self):
        url = reverse('producto_create')
       
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/producto_form.html')


       
       
        response = self.client.post(url, {
                'id_categoria': self.categoria.id_categoria,
                'nom_producto': 'Nuevo Producto',
                'descripcion': 'Nueva descripción',
                'cantidad': '3',
                'precio': '300',
               
            })
       
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Producto.objects.filter(nom_producto='Nuevo Producto').exists())


    def test_producto_update_view(self):
        url = reverse('producto_update', args=[self.producto.id_producto])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/producto_form.html')


        response = self.client.post(url, {
            'id_categoria': self.categoria.id_categoria,
            'nom_producto': 'Producto Actualizado',
            'descripcion': 'Desc Actualizada',
            'cantidad': '10',
            'precio': '1000',
        })
        self.assertEqual(response.status_code, 302)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nom_producto, 'Producto Actualizado')


    def test_producto_delete_view(self):
        url = reverse('producto_delete', args=[self.producto.id_producto])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/producto_confirm_delete.html')


        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Producto.objects.filter(id_producto=self.producto.id_producto).exists())


    def test_registro_view(self):
        url = reverse('registro')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registro.html')


        response = self.client.post(url, {
            'username': 'nuevo_usuario',
            'password1': 'SuperSecret123',
            'password2': 'SuperSecret123',
        })
       
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())


    def test_alimentos_view(self):
        url = reverse('alimentos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/alimentos.html')