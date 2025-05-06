from django.test import TestCase
from django.urls import reverse 
from decimal import Decimal
from contas.models import Cliente, ContaBancaria
import json


class BancoTests(TestCase):
    def setUp(self):
        self.cliente_data = {
            'nome': 'João Teste',
            'cpf': '12345678900',
            'email': 'joao@email.com',
            'data_nascimento': '2000-01-01',
        }
        response = self.client.post('/criar/', data=self.cliente_data, content_type='application/json')
        self.conta_numero = response.json().get('numero_conta')

    def test_deposito(self):
        data = {
            'numero_conta': self.conta_numero,
            'valor': '100.00'
        }
        response = self.client.post('/depositar/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('mensagem', response.json())

        conta = ContaBancaria.objects.get(numero_conta=self.conta_numero)
        self.assertEqual(conta.saldo, Decimal('100.00'))

    def test_saque_sucesso(self):
        self.client.post('/depositar/', data={
            'numero_conta': self.conta_numero,
            'valor': '100.00'
        }, content_type='application/json')

        response = self.client.post('/sacar/', data=json.dumps({
            'numero_conta': self.conta_numero,
            'valor': '50.00'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('mensagem', response.json())

        conta = ContaBancaria.objects.get(numero_conta=self.conta_numero)
        self.assertEqual(conta.saldo, Decimal('50.00'))

    def test_saque_insuficiente(self):
        response = self.client.post('/sacar/', data={
            'numero_conta': self.conta_numero,
            'valor': '999.00'
        }, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('erro', response.json())