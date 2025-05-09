from contas.models import ContaBancaria, Transacao
from django.db import transaction
from decimal import Decimal
from django.utils import timezone


def transferir_valor(conta_origem_numero, conta_destino_numero, valor_transferencia):
    try:
        valor_decimal = Decimal(str(valor_transferencia))
    except Exception:
        raise ValueError('Valor de transferência inválido.')
    
    if valor_decimal <= Decimal('0.00'):
        raise ValueError('O valor da transferência deve ser positivo.')
    
    if conta_origem_numero == conta_destino_numero:
        raise ValueError('Conta de origem e destino não podem ser iguais.')
    
    with transaction.atomic():
        try:
            conta_origem = ContaBancaria.objects.select_for_update().get(numero_conta=conta_origem_numero)
        except ContaBancaria.DoesNotExist:
            raise ValueError(f'Conta de origem {conta_origem_numero} não encontrada.')
        
        try:
            conta_destino = ContaBancaria.objects.get(numero_conta=conta_destino_numero)
        except ContaBancaria.DoesNotExist:
                    raise ValueError(f'Conta de destino {conta_destino_numero} não encontrada.')
        
        if conta_origem.saldo < valor_transferencia:
            raise ValueError("Saldo insuficiente para transferência")
        
        conta_origem.saldo -= valor_transferencia
        conta_destino.saldo += valor_transferencia

        conta_origem.save()
        conta_destino.save()

        Transacao.objects.create(
            conta=conta_origem, 
            tipo='TE', 
            valor=valor_decimal, 
        )
        Transacao.objects.create(
            conta=conta_destino, 
            tipo='TR', 
            valor=valor_decimal,
        )

        return conta_origem, conta_destino