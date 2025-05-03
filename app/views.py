import logging
import re
from django.shortcuts import render, get_object_or_404, redirect
from .models import User
import uuid
from .forms import   RegistroUserForm
from .forms import ProductoForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Producto, Categoria, Cart, CartItem
import os
from django.conf import settings  # Añadir esta línea

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from decimal import Decimal
from transbank.error.transaction_create_error import TransactionCreateError
from transbank.error.transaction_commit_error import TransactionCommitError



# Create your views here.
def inicio(request):
    return render(request, 'app/inicio.html')

def home(request):
    return render(request, 'app/home.html')

def alimentos(request):
    categoria = Categoria.objects.get(nom_categoria='Singles')
    products = Producto.objects.filter(id_categoria=categoria)[:8]
    return render(request, 'app/alimentos.html', {'products':products})


def accesorios(request):
    categoria = Categoria.objects.get(nom_categoria='Accesorios')
    products = Producto.objects.filter(id_categoria=categoria)[:8]
    return render(request, 'app/accesorios.html', {'products':products})

def farmacia(request):
    categoria = Categoria.objects.get(nom_categoria='Productos Sellados')
    products = Producto.objects.filter(id_categoria=categoria)[:8]
    return render(request, 'app/farmacia.html', {'products':products})

def user_login(request):
    return render(request, 'registration/login.html')


@login_required
def editarProductos(request):
    return render(request, 'app/editarProductos.html')


def registro(request):
    data = {
        'form': RegistroUserForm()
    }

    if request.method == 'POST':
        user_creation_form = RegistroUserForm(data=request.POST)

        if user_creation_form.is_valid():
            user_creation_form.save()

            user = authenticate(username=user_creation_form.cleaned_data['username'],
                                password=user_creation_form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
                return redirect('home')
    
    return render(request, 'registration/registro.html', data)




def salir(request):
    logout(request)
    return redirect('home')


# Vista para listar productos
@login_required
def producto_list(request):
    productos = Producto.objects.all()
    return render(request, 'app/producto_list.html', {'productos': productos})


# Vista para crear un nuevo producto
@login_required
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('producto_list')
    else:
        form = ProductoForm()
    return render(request, 'app/producto_form.html', {'form': form})

# Vista para actualizar un producto existente
@login_required
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('producto_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'app/producto_form.html', {'form': form})

# Vista para eliminar un producto
@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('producto_list')
    return render(request, 'app/producto_confirm_delete.html', {'producto': producto})



#CARRITO
@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    template_path = os.path.join(settings.BASE_DIR, 'app/templates/app/cart_detail.html')
    print(f"Looking for template at: {template_path}")  # Línea de depuración
    return render(request, 'app/cart_detail.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    # Busca el producto
    product = get_object_or_404(Producto, id_producto=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart_detail')

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Producto, id_producto=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def update_cart_item(request, product_id):
    product = get_object_or_404(Producto, id_producto=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    
    # Obtener la cantidad desde el POST
    quantity = int(request.POST.get('quantity', 0))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart_detail')

# Configurar el logger
logger = logging.getLogger(__name__)


@login_required
def iniciar_pago(request):
    total = get_cart_total_from_db(request)
    
    if total <= 0:
        return redirect('cart_detail')  # Puedes mostrar error si prefieres

    # Crear parámetros de transacción
    buy_order = uuid.uuid4().hex[:20]
    session_id = str(uuid.uuid4())
    return_url = request.build_absolute_uri('/webpay/respuesta/')

    print("buy_order:", buy_order, flush=True)
    print("session_id:", session_id, flush=True)
    print("return_url:", return_url, flush=True)

    try:
        # Crear transacción con Transbank
        response = Transaction.create(
            buy_order, session_id, int(total), return_url
        )

        # Redirigir a Webpay usando plantilla redirect.html
        return render(request, 'webpay/redirect.html', {
            'url': response.url,
            'token': response.token
        })

    except TransactionCreateError as e:
        # Mostrar página de error con mensaje
        return render(request, 'webpay/error.html', {
            'message': f"Error al crear la transacción: {e.message}"
        })



def parse_price(raw_price: str) -> Decimal:

    # Quita todo excepto dígitos, puntos y comas
    cleaned = re.sub(r"[^\d\.,]", "", raw_price)
    # Si tiene un solo separador coma y varios puntos: asume formato XX.XXX,YY
    if cleaned.count(',') == 1 and cleaned.count('.') > 1:
        cleaned = cleaned.replace('.', '').replace(',', '.')
    # Si tiene varios separadores de coma: asume miles con coma
    elif cleaned.count(',') > 1:
        cleaned = cleaned.replace(',', '')
    # Si tiene una sola coma sin puntos: coma decimal
    elif cleaned.count(',') == 1 and cleaned.count('.') == 0:
        cleaned = cleaned.replace(',', '.')
    try:
        return Decimal(cleaned)
    except Exception:
        return Decimal('0.0')


def get_cart_total_from_db(request):
    """Recorre el Cart y suma precio * cantidad de cada CartItem."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    total = Decimal('0.0')
    items = CartItem.objects.filter(cart=cart).select_related('product')
    for item in items:
        price = parse_price(str(item.product.precio))
        total += price * item.quantity
    return total

@login_required
def respuesta_pago(request):
    # Ya no bloqueamos GET
    token = request.POST.get('token_ws') or request.GET.get('token_ws')
    print("🔔 Token recibido:", token, flush=True)

    if not token:
        print("⚠️ No se recibió token", flush=True)
        return render(request, 'webpay/error.html', {
            'message': 'No se recibió un token válido.',
        })

    try:
        print("🔄 Confirmando transacción con token:", token, flush=True)
        response = Transaction.commit(token)
        print("📤 Respuesta completa:", response.__dict__, flush=True)

        if response.status == 'AUTHORIZED':
            print("✅ Pago AUTORIZADO", flush=True)
            cart = Cart.objects.get(user=request.user)
            CartItem.objects.filter(cart=cart).delete()
            return render(request, 'webpay/exito.html', {'response': response})
        else:
            print(f"❌ Pago rechazado. Estado: {response.status}", flush=True)
            return render(request, 'webpay/error.html', {
                'message': f"Pago rechazado. Estado: {response.status}",
                'response': response
            })

    except TransactionCommitError as e:
        print("🚨 TransactionCommitError:", str(e), flush=True)
        return render(request, 'webpay/error.html', {
            'message': f"Error al confirmar la transacción: {str(e)}"
        })

    except Exception as e:
        print("🔥 Error inesperado:", str(e), flush=True)
        return render(request, 'webpay/error.html', {
            'message': f"Error inesperado: {str(e)}"
        })
