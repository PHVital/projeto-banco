from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_cliente),
    path('login/', views.autenticar_cliente),
    path('deposito/', views.deposito),
    path('saque/', views.saque),
    path('saldo/', views.consultar_saldo),
    path('extrato/', views.extrato_transacoes),
    path('transferencia/', views.transferencia, name='transferencia'),
]
