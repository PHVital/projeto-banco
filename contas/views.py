from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cliente, ContaBancaria, Transacao
import json

@csrf_exempt
def criar_cliente_conta(request):
    if request.method == 'POST':
        dados = json.loads(request.body)
        nome = dados.get('nome')
        cpf = dados.get('cpf')
        email = dados.get('email')
        data_nascimento = dados.get('data_nascimento')

        if Cliente.objects.filter(cpf=cpf).exists():
            return JsonResponse({'erro': 'Cliente com esse CPF já existe'}, status=400)
        
        cliente = Cliente.objects.create(nome=nome, cpf=cpf, email=email, data_nascimento=data_nascimento)
        conta = ContaBancaria.objects.create(cliente=cliente)

        return JsonResponse({
            'mensagem': 'Cliente e Conta criados!',
            'cliente_id': cliente.id,
            'numero_conta': conta.numero_conta,
            'saldo_inicial': str(conta.saldo)
        })
    
@csrf_exempt
def depositar(request):
    if request.method == 'POST':
        dados = json.loads(request.body)
        numero_conta = dados.get('numero_conta')
        valor = float(dados.get('valor'))

    try:
        conta = ContaBancaria.objects.get(numero_conta=numero_conta)
        conta.saldo += valor
        conta.save()
        Transacao.objects.create(conta=conta, tipo='D', valor=valor)

        return JsonResponse({'mensagem': f'Depósito de R${valor:.2f} realizado com sucesso.'})
    except ContaBancaria.DoesNotExist:
        return JsonResponse({'erro': 'Conta não encontrada.'}, status=404)
    
@csrf_exempt
def sacar(request):
    if request.method == 'POST':
        dados = json.loads(request.body)
        numero_conta = dados.get('numero_conta')
        valor = float(dados.get('valor'))

    try:
        conta = ContaBancaria.objects.get(numero_conta=numero_conta)
        if conta.saldo >= valor:
            conta.saldo -= valor
            conta.save()
            Transacao.objects.create(conta=conta, tipo='S', valor=valor)

            return JsonResponse({'mensagem': f'Saque de R${valor:.2f} realizado com sucesso.'})
        else:
            return JsonResponse({'erro': 'Saldo insulficiente.'}, status=400)
    except ContaBancaria.DoesNotExist:
        return JsonResponse({'erro': 'Conta não encontrada.'}, status=404)
    

def consultar_saldo(request, numero_conta):
    try:
        conta = ContaBancaria.objects.get(numero_conta=numero_conta)
        return JsonResponse({
            'numero_conta': conta.numero_conta,
            'saldo': str(conta.saldo)
        })
    except ContaBancaria.DoesNotExist:
        return JsonResponse({'erro': 'Conta não encontrada.'}, status=404)