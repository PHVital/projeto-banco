import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from contas.models import Cliente, ContaBancaria, Transacao
from rest_framework.authtoken.models import Token
from contas.services.cliente_services import criar_cliente_e_conta


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def usuario_teste_data():
    return {
        'cpf': '33300011122',
        'nome': 'Usuario View Teste',
        'email': 'viewuser@example.com',
        'data_nascimento': '1995-05-15',
        'password': 'securepassword123'
    }


@pytest.fixture
def cliente_registrado_para_views(db, usuario_teste_data):
    data = usuario_teste_data.copy()
    password = data.pop('password')
    cliente = Cliente.objects.create_user(**data, password=password) # type: ignore
    return cliente


@pytest.fixture
def cliente_autenticado_com_conta(db, cliente_registrado_para_views):
    cliente = cliente_registrado_para_views
    conta, _ = ContaBancaria.objects.get_or_create(cliente=cliente)
    
    token, _ = Token.objects.get_or_create(user=cliente)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client, cliente, conta


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


@pytest.mark.django_db
class TestRegistroClienteView:
    def test_registrar_cliente_sucesso(self, api_client, usuario_teste_data):
        url = reverse('registrar_cliente')

        payload = usuario_teste_data.copy()

        response = api_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'mensagem' in response.data
        assert response.data['mensagem'] == 'Cliente criado com sucesso!'
        assert 'token' in response.data
        assert 'numero_conta' in response.data
        assert 'cliente' in response.data
        assert response.data['cliente']['cpf'] == payload['cpf']

        assert Cliente.objects.filter(cpf=payload['cpf']).exists()
        cliente_criado = Cliente.objects.get(cpf=payload['cpf'])
        assert ContaBancaria.objects.filter(cliente=cliente_criado).exists()
        assert Token.objects.filter(user=cliente_criado).exists()

    def test_registrar_cliente_cpf_duplicado(self, api_client, cliente_registrado_para_views, usuario_teste_data):
        url = reverse('registrar_cliente')
        payload_duplicado = usuario_teste_data.copy()
        payload_duplicado['cpf'] = cliente_registrado_para_views.cpf
        payload_duplicado['email'] = 'novoemailunico@example.come'

        response = api_client.post(url, payload_duplicado, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cpf' in response.data
        assert 'cliente com este cpf já existe.' in str(response.data['cpf'][0])

    def test_registrar_cliente_campo_obrigatorio_faltando(self, api_client, cliente_registrado_para_views, usuario_teste_data):
        url = reverse('registrar_cliente')
        payload_incompleto = usuario_teste_data.copy()
        del payload_incompleto['password']

        response = api_client.post(url, payload_incompleto, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
        assert 'Este campo é obrigatório.' in response.data['password'][0]


@pytest.mark.django_db
class TestLoginClienteView:
    def test_login_sucesso(self, api_client, cliente_registrado_para_views, usuario_teste_data):
        url = reverse('autenticar_cliente')

        payload = {
            'cpf': cliente_registrado_para_views.cpf,
            'password': usuario_teste_data['password']
        }

        response = api_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'mensagem' in response.data
        assert response.data['mensagem'] == 'Autenticado com sucesso!'
        assert 'token' in response.data
        assert Token.objects.filter(key=response.data['token'], user=cliente_registrado_para_views).exists()

    def test_login_credenciais_invalidas_senha(self, api_client, cliente_registrado_para_views):
        url = reverse('autenticar_cliente')
        payload = {
            'cpf': cliente_registrado_para_views.cpf,
            'password': 'senhaincorreta'
        }

        response = api_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'non_field_errors' in response.data
        assert 'Credenciais inválidas' in str(response.data['non_field_errors'][0])

    def test_login_usuario_nao_existe(self, api_client):
        url = reverse('autenticar_cliente')
        payload = {
            'cpf': 'cpf_inexistente_000',
            'password': 'qualquersenha'
        }

        response = api_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'non_field_errors' in response.data
        assert 'Credenciais inválidas' in str(response.data['non_field_errors'][0])


@pytest.mark.django_db
class TestOperacoesContaView:
    def test_deposito_sucesso(self, cliente_autenticado_com_conta):
        client, cliente_obj, conta_obj = cliente_autenticado_com_conta
        url = reverse('deposito')

        saldo_anterior = conta_obj.saldo
        valor_deposito = Decimal('100.00')
        payload = {
            'numero_conta': conta_obj.numero_conta,
            'valor': str(valor_deposito),
        }

        response = client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'mensagem' in response.data
        assert 'Depósito' in response.data['mensagem']
        assert 'conta' in response.data
        assert Decimal(response.data['conta']['saldo']) == saldo_anterior + valor_deposito


        conta_obj.refresh_from_db()
        assert conta_obj.saldo == saldo_anterior + valor_deposito
        assert Transacao.objects.filter(conta=conta_obj, tipo='D', valor=valor_deposito).exists()


    def test_deposito_sem_autenticacao(self, api_client, conta_generica):
        url = reverse('deposito')
        payload = {
            'numero_conta': conta_generica.numero_conta,
            'valor': '50.00',
        }

        response = api_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'As credenciais de autenticação não foram fornecidas' in response.data['detail']

    
    def test_consultar_saldo_sucesso(self, cliente_autenticado_com_conta):
        client, cliente_obj, conta_obj = cliente_autenticado_com_conta
        url = reverse('consultar_saldo')

        saldo_esperado = Decimal('123.45')
        conta_obj.saldo = saldo_esperado
        conta_obj.save()

        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['numero_conta'] == conta_obj.numero_conta
        assert Decimal(response.data['saldo']) == saldo_esperado

    
    def test_consultar_saldo_sem_autenticacao(self, api_client):
        url = reverse('consultar_saldo')

        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED