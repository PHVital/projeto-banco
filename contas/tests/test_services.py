# Esse programa segue o padrão de testes Arrange-Act-Assert (AAA)

import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from contas.models import Cliente, ContaBancaria, Transacao
from contas.services.cliente_services import depositar_valor, criar_cliente_e_conta, sacar_valor
from contas.services.transferencia_service import transferir_valor


@pytest.fixture
def cliente_generico(db):
    cliente, _, _ = criar_cliente_e_conta(
        cpf='00000000000',
        nome='Cliente Fixture Teste',
        email='fixture.cliente@example.com',
        senha='password123',
        data_nascimento='1990-01-01'
    )
    return cliente


@pytest.fixture
def conta_generica(cliente_generico):
    conta = ContaBancaria.objects.get(cliente=cliente_generico)
    return conta


@pytest.fixture
def cliente_origem(db):
    cliente, _, _ = criar_cliente_e_conta(
        cpf='11111111111',
        nome='Cliente Origem',
        email='origem.fixture@example.com',
        senha='password123'
    )
    return cliente


@pytest.fixture
def conta_origem_com_saldo(cliente_origem):
    conta = ContaBancaria.objects.get(cliente=cliente_origem)
    conta.saldo = Decimal('500.00')
    conta.save()
    return conta


@pytest.fixture
def cliente_destino(db):
    cliente, _, _ = criar_cliente_e_conta(
        cpf='22222222222',
        nome='Cliente Destino',
        email='destino.fixture@example.com',
        senha='password123'
    )
    return cliente


@pytest.fixture
def conta_destino_com_saldo(cliente_destino):
    conta = ContaBancaria.objects.get(cliente=cliente_destino)
    conta.saldo = Decimal('100.00')
    conta.save()
    return conta


@pytest.mark.django_db
def test_depositar_valor_sucesso(conta_generica):
    # 1. Preparação (Arrange) - Configura tudo que é necessário para o teste
    conta_mock = conta_generica

    valor_deposito_inicial_na_conta = Decimal('0.00')
    if conta_mock.saldo != valor_deposito_inicial_na_conta:
        conta_mock.saldo = valor_deposito_inicial_na_conta
        conta_mock.save()

    valor_a_depositar = Decimal('50.00')

    # 2. Ação (Act) - Execução da unidade de código a ser testada
    conta_atualizada = depositar_valor(
        numero_conta=conta_mock.numero_conta,
        valor=valor_a_depositar
    )

    # 3. Verificação (Assert) - Verificação dos resultados
    assert conta_atualizada is not None
    assert conta_atualizada.numero_conta == conta_mock.numero_conta
    assert conta_atualizada.saldo == valor_deposito_inicial_na_conta + valor_a_depositar
    
    transacao_criada = Transacao.objects.filter(conta=conta_mock, tipo='D').first()
    assert transacao_criada is not None
    assert transacao_criada.valor == valor_a_depositar


# Vou deixar para comparação
# @pytest.mark.django_db
# def test_depositar_valor_sucesso():
#     # 1. Preparação (Arrange) - Configura tudo que é necessário para o teste
#     cliente_mock, conta_mock, _ = criar_cliente_e_conta(
#         cpf='12345678901',
#         nome='Cliente Teste Deposito',
#         email='deposito@teste.com',
#         senha='senhaforte123',
#         data_nascimento='1990-01-01'
#     )

#     valor_deposito_inicial = Decimal('100.00')
#     conta_mock.saldo = valor_deposito_inicial
#     conta_mock.save()

#     valor_a_depositar = Decimal('50.00')

#     # 2. Ação (Act) - Execução da unidade de código a ser testada
#     conta_atualizada = depositar_valor(
#         numero_conta=conta_mock.numero_conta,
#         valor=valor_a_depositar
#     )

#     # 3. Verificação (Assert) - Verificação dos resultados
#     assert conta_atualizada is not None
#     assert conta_atualizada.numero_conta == conta_mock.numero_conta
#     assert conta_atualizada.saldo == valor_deposito_inicial + valor_a_depositar

#     transacao_criada = Transacao.objects.filter(conta=conta_mock, tipo='D').first()
#     assert transacao_criada is not None
#     assert transacao_criada.valor == valor_a_depositar


@pytest.mark.django_db
def test_depositar_valor_negativo_ou_zero(conta_generica):
    conta_mock = conta_generica
    saldo_antes = conta_mock.saldo

    with pytest.raises(ValueError, match='O valor do depósito deve ser maior que zero.'):
        depositar_valor(numero_conta=conta_mock.numero_conta, valor=Decimal('0.00'))

    with pytest.raises(ValueError, match='O valor do depósito deve ser maior que zero.'):
        depositar_valor(numero_conta=conta_mock.numero_conta, valor=Decimal('-50.00'))

    conta_mock.refresh_from_db()
    assert conta_mock.saldo == saldo_antes
    assert Transacao.objects.filter(conta=conta_mock, tipo='D').count() == 0


@pytest.mark.django_db
def test_sacar_valor_sucesso(conta_generica):
    conta_mock = conta_generica
    conta_mock.saldo = Decimal('200.00')
    conta_mock.save()

    valor_a_sacar = Decimal('50.00')

    conta_atualizada = sacar_valor(
        numero_conta=conta_mock.numero_conta,
        valor=valor_a_sacar
    )

    assert conta_atualizada.saldo == Decimal('150.00')
    transacao_saque = Transacao.objects.filter(conta=conta_mock, tipo='S').first()
    assert transacao_saque is not None
    assert transacao_saque.valor == valor_a_sacar


@pytest.mark.django_db
def test_sacar_valor_insuficiente(conta_generica):
    conta_mock = conta_generica
    conta_mock.saldo = Decimal('30.00')
    conta_mock.save()
    saldo_antes = conta_mock.saldo

    valor_a_sacar = Decimal('50.00')

    with pytest.raises(ValueError, match='Saldo insuficiente'):
        sacar_valor(numero_conta=conta_mock.numero_conta, valor=valor_a_sacar)

    conta_mock.refresh_from_db()
    assert conta_mock.saldo == saldo_antes
    assert Transacao.objects.filter(conta=conta_mock, tipo='S').count() == 0


@pytest.mark.django_db
def test_sacar_valor_negativo_ou_zero(conta_generica):
    conta_mock = conta_generica
    conta_mock.saldo = Decimal('100.00')
    conta_mock.save()
    saldo_antes = conta_mock.saldo

    with pytest.raises(ValueError, match='O valor do saque deve ser maior que zero.'):
        sacar_valor(numero_conta=conta_mock.numero_conta, valor=Decimal('0.00'))

    with pytest.raises(ValueError, match='O valor do saque deve ser maior que zero.'):
        sacar_valor(numero_conta=conta_mock.numero_conta, valor=Decimal('-50.00'))

    conta_mock.refresh_from_db()
    assert conta_mock.saldo == saldo_antes
    assert Transacao.objects.filter(conta=conta_mock, tipo='S').count() == 0


@pytest.mark.django_db
def test_transferir_valor_sucesso(conta_origem_com_saldo, conta_destino_com_saldo):
    valor_transferencia = Decimal('75.00')

    conta_origem_atualizada, conta_destino_atualizada = transferir_valor(
        conta_origem_numero=conta_origem_com_saldo.numero_conta,
        conta_destino_numero=conta_destino_com_saldo.numero_conta,
        valor_transferencia=valor_transferencia
    )

    assert conta_origem_atualizada.saldo == Decimal('425.00')
    assert conta_destino_atualizada.saldo == Decimal('175.00')

    trans_enviada = Transacao.objects.get(conta=conta_origem_com_saldo, tipo='TE')
    trans_recebida = Transacao.objects.get(conta=conta_destino_com_saldo, tipo='TR')

    assert trans_enviada.valor == valor_transferencia
    assert trans_recebida.valor == valor_transferencia


@pytest.mark.django_db
def test_transferir_valor_saldo_insuficiente_origem(conta_origem_com_saldo, conta_destino_com_saldo):
    
    conta_origem_com_saldo.saldo = Decimal('50.00')
    conta_origem_com_saldo.save()

    saldo_origem_antes = conta_origem_com_saldo.saldo
    saldo_destino_antes = conta_destino_com_saldo.saldo

    with pytest.raises(ValueError, match='Saldo insuficiente para transferência'):
        transferir_valor(
            conta_origem_numero=conta_origem_com_saldo.numero_conta,
            conta_destino_numero=conta_destino_com_saldo.numero_conta,
            valor_transferencia=Decimal('75.00')
        )

    conta_origem_com_saldo.refresh_from_db()
    conta_destino_com_saldo.refresh_from_db()
    assert conta_origem_com_saldo.saldo == saldo_origem_antes
    assert conta_destino_com_saldo.saldo == saldo_destino_antes


@pytest.mark.django_db
def test_transferir_para_mesma_conta(conta_origem_com_saldo):
    with pytest.raises(ValueError, match='Conta de origem e destino não podem ser iguais.'):
        transferir_valor(
            conta_origem_numero=conta_origem_com_saldo.numero_conta,
            conta_destino_numero=conta_origem_com_saldo.numero_conta,
            valor_transferencia=Decimal('50.00')
        )


@pytest.mark.django_db
def test_transferir_valor_negativo_ou_zero(conta_origem_com_saldo, conta_destino_com_saldo):
    with pytest.raises(ValueError, match="O valor da transferência deve ser positivo."):
        transferir_valor(
            conta_origem_numero=conta_origem_com_saldo.numero_conta,
            conta_destino_numero=conta_destino_com_saldo.numero_conta,
            valor_transferencia=Decimal('0.00')
        )
    with pytest.raises(ValueError, match='O valor da transferência deve ser positivo.'):
        transferir_valor(
            conta_origem_numero=conta_origem_com_saldo.numero_conta,
            conta_destino_numero=conta_destino_com_saldo.numero_conta,
            valor_transferencia=Decimal('-50.00')
        )


@pytest.mark.django_db
def test_transferir_conta_origem_nao_encontrada(conta_destino_com_saldo):
    with pytest.raises(ValueError, match='Conta de origem NUMERO_FALSO não encontrada.'):
        transferir_valor(
            conta_origem_numero='NUMERO_FALSO',
            conta_destino_numero=conta_destino_com_saldo.numero_conta,
            valor_transferencia=Decimal('50.00')
        )