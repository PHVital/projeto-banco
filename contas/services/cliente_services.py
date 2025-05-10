from contas.models import Cliente, ContaBancaria, Transacao
from rest_framework.authtoken.models import Token
from decimal import Decimal


def criar_cliente_e_conta(
    cpf: str, nome: str, email: str, senha: str, data_nascimento=None
):
    if not all([cpf, nome, email, senha]):
        raise ValueError("CPF, nome, email e senha são obrigatórios.")

    cliente = Cliente.objects.create_user(
        cpf=cpf, email=email, nome=nome, data_nascimento=data_nascimento, password=senha
    )

    conta = ContaBancaria.objects.create(cliente=cliente)
    token, _ = Token.objects.get_or_create(user=cliente)

    return cliente, conta, token


def depositar_valor(numero_conta, valor):
    conta = ContaBancaria.objects.get(numero_conta=numero_conta)
    valor_decimal = Decimal(str(valor))

    if valor_decimal <= 0:
        raise ValueError("O valor do depósito deve ser maior que zero.")

    conta.saldo += valor_decimal
    conta.save()
    Transacao.objects.create(conta=conta, tipo="D", valor=valor_decimal)
    return conta


def sacar_valor(numero_conta, valor):
    conta = ContaBancaria.objects.get(numero_conta=numero_conta)
    valor_decimal = Decimal(str(valor))

    if valor_decimal <= 0:
        raise ValueError("O valor do saque deve ser maior que zero.")
    if conta.saldo < valor_decimal:
        raise ValueError("Saldo insuficiente")

    conta.saldo -= valor_decimal
    conta.save()
    Transacao.objects.create(conta=conta, tipo="S", valor=valor_decimal)
    return conta


def transferir_valor(conta_origem_numero, conta_destino_numero, valor):
    from contas.models import ContaBancaria, Transacao
    from decimal import Decimal

    if conta_origem_numero == conta_destino_numero:
        raise ValueError("Conta de origem e destino devem ser diferentes.")

    conta_origem = ContaBancaria.objects.get(numero_conta=conta_origem_numero)
    conta_destino = ContaBancaria.objects.get(numero_conta=conta_destino_numero)
    valor_decimal = Decimal(str(valor))

    if conta_origem.saldo < valor_decimal:
        raise ValueError("Saldo insuficiente para a trasferência.")

    conta_origem.saldo -= valor_decimal
    conta_destino.saldo += valor_decimal

    conta_origem.save()
    conta_destino.save()

    Transacao.objects.create(
        conta=conta_origem, tipo="Transferência enviada", valor=valor_decimal
    )
    Transacao.objects.create(
        conta=conta_destino, tipo="Transferência recebida", valor=valor_decimal
    )

    return conta_origem, conta_destino
