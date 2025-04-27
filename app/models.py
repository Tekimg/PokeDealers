from django.db import models
#Regex para validar que tengan los formatos de registro
from django.core.validators import RegexValidator, EmailValidator
import datetime
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Producto(models.Model):
    id_producto =models.AutoField(db_column="id_producto", primary_key=True)
    id_categoria= models.ForeignKey('Categoria',on_delete=models.CASCADE, db_column='id_categoria')
    foto= models.ImageField('Imagen',upload_to='fotosProductos/',max_length=255,null=False, blank=True)
    nom_producto=models.CharField(max_length=200, blank=False, null=False)
    descripcion =models.TextField(max_length=500)
    cantidad=models.CharField(max_length=5, blank=False, null=False)
    precio =models.CharField(max_length=45, blank=False, null=False)

    def __str__(self):
        return self.nom_producto
    

class Categoria(models.Model):
    id_categoria =models.AutoField(db_column="id_categoria", primary_key=True)
    nom_categoria=models.CharField(max_length=100, blank=False, null=False)
    
    def __str__(self):
        return self.nom_categoria
    



# Orden del Cliente
class Order(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    Usuario =  models.ForeignKey(User, on_delete=models.CASCADE)
    Cantidad = models.IntegerField(default=1) 
    Direccion = models.CharField(max_length=100, default='', blank=True)
    Fecha = models.DateField(default=datetime.datetime.today)

    def __str__(self):
        return self.producto
    


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart {self.id} for {self.user}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Producto, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.nom_producto} in cart {self.cart.id}'

    def get_total_price(self):
        # Limpiar la cadena de texto del precio
        precio_limpio = self.product.precio.replace('$', '').replace('.', '').replace(',', '.')
        return self.quantity * float(precio_limpio)