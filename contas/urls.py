from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('login/', views.autenticar_cliente, name='autenticar_cliente'),
    path('deposito/', views.deposito, name='deposito'),
    path('saque/', views.saque),
    path('saldo/', views.consultar_saldo, name='consultar_saldo'),
    path('extrato/', views.extrato_transacoes),
    path('transferencia/', views.transferencia, name='transferencia'),
]
