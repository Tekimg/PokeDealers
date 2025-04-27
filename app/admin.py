from django.contrib import admin
from .models import Producto, Categoria, Order

# Register your models here.
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Order) 