from django.urls import path
from . import views

urlpatterns = [
    path('criar/', views.criar_cliente_conta, name='criar_cliente_conta'), # type: ignore
    path('depositar/', views.depositar, name='depositar'),
    path('sacar/', views.sacar, name='sacar'),
    path('saldo/<str:numero_conta>/', views.consultar_saldo, name='consultar_saldo')
]
