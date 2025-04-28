from django.contrib import admin
from .models import Cliente, ContaBancaria, Transacao

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'email')
    search_fields = ('nome', 'cpf')

@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ('numero_conta', 'cliente', 'saldo')
    search_fields = ('numero_conta', 'cliente__nome')

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('conta', 'tipo', 'valor', 'data')
    search_fields = ('conta__numero_conta',)
    list_filter = ('tipo',)