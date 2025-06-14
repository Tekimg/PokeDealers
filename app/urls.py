from django.urls import path, include
from . import views
from .views import producto_list, producto_create, producto_update, producto_delete
from . import views as webpay_views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('home.html', views.home, name='home'),
    path('singles.html', views.singles, name='singles'),
    path('accesorios.html', views.accesorios, name='accesorios'),
    path('productos_sellados.html', views.productos_sellados, name='productos_sellados'),
    path('registration/login.html', views.user_login, name='login'),
    path('registro', views.registro, name='registro'),
    path('editarProductos.html', views.editarProductos, name='editarProductos'),

     # Nuevas URLs para las vistas CRUD de Producto
    path('productos/', producto_list, name='producto_list'),
    path('productos/new/', producto_create, name='producto_create'),
    path('productos/<int:pk>/edit/', producto_update, name='producto_update'),
    path('productos/<int:pk>/delete/', producto_delete, name='producto_delete'),


    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/',views.salir,name="salir"),


    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_item, name='update_cart_item'),
    path('webpay/iniciar/', views.iniciar_pago, name='iniciar_pago'),
    path('webpay/respuesta/', views.respuesta_pago, name='respuesta_pago'),
    


]



