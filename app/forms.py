from django import forms 
from .models import User
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Producto



# Formulario para manejar el modelo Producto
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['id_categoria', 'foto', 'nom_producto', 'descripcion', 'cantidad', 'precio']



class RegistroUserForm(UserCreationForm):
  
    class Meta: 
        model = User
        fields = [ 'username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels={
            'username':'Nombre de usuario',
            'first_name':'Nombre',
            'last_name':'Apellidos',
            'email':'Correo',
            'password1':'Ingrese una contraseña',
            'password2':'Repita la contraseña',
        }
