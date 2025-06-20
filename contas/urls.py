from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import viewsets
from . import views

router = DefaultRouter()
router.register(r"contas", viewsets.ContaViewSet, basename="conta")

function_based_urls = [
    path("registrar/", views.registrar_cliente, name="registrar_cliente"),
    path("login/", views.autenticar_cliente, name="autenticar_cliente"),
]

urlpatterns = [
    path("", include(router.urls)),
    path("", include(function_based_urls)),
]
