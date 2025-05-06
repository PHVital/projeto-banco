from contas.models import ContaBancaria, Transacao
from decimal import Decimal
from django.db import transaction
from datetime import datetime

def transferir_valor(conta_origem_numero, conta_destino_numero, valor):
    with transaction.atomic():
        conta_origem = ContaBancaria.objects.select_for_update().get(numero_conta=conta_origem_numero)
        conta_destino = ContaBancaria.objects.get(numero_conta=conta_destino_numero)

        if conta_origem.saldo < valor:
            raise ValueError("Saldo insuficiente para transferência")
        
        conta_origem.saldo -= valor
        conta_destino.saldo += valor

        conta_origem.save()
        conta_destino.save()

        Transacao.objects.create(conta=conta_origem, tipo='transferencia_saida', valor=-valor, date=datetime.now())
        Transacao.objects.create(conta=conta_destino, tipo='transferencia_entrada', valor=valor, date=datetime.now())

        return conta_origem, conta_destino