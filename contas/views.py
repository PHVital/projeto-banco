from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from contas.models import Cliente, ContaBancaria, Transacao
from contas.services.cliente_services import criar_cliente_e_conta, depositar_valor, sacar_valor, transferir_valor

@api_view(['POST'])
def registrar_cliente(request):
    if request.method == 'POST':
        try:
            nome = request.data.get('nome')
            cpf = request.data.get('cpf')
            email = request.data.get('email')
            data_nascimento = request.data.get('data_nascimento')
            senha = request.data.get('senha')

            cliente, conta, token = criar_cliente_e_conta(
                nome=nome, 
                cpf=cpf, 
                email=email,
                data_nascimento=data_nascimento,
                senha=senha
            )
            
            return Response({
                'mensagem': 'Cliente criado com sucesso!',
                'cliente_id': conta.numero_conta,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def autenticar_cliente(request):
    cpf = request.data.get('cpf')
    senha = request.data.get('senha')

    user = authenticate(request, cpf=cpf, password=senha)

    if user is None:
        return Response({'erro': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'mensagem': 'Autenticado com sucesso!',
        'token': token.key,
        'cliente_id': user.id,
        'nome': user.nome
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposito(request):
    try:
        numero_conta = request.data.get('numero_conta')
        valor = request.data.get('valor')

        conta = get_object_or_404(ContaBancaria, numero_conta=numero_conta)

        if conta.cliente != request.user:
            return Response({'erro': 'Você não tem permissão para depositar nesta conta.'}, status=status.HTTP_403_FORBIDDEN)

        conta = depositar_valor(numero_conta, valor)

        return Response({
            'mensagem': f'Depósito de R${valor} realizado com sucesso.',
            'saldo_atual': float(conta.saldo)
        })
    
    except Exception as e:
        return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saque(request):
    try:
        numero_conta = request.data.get('numero_conta')
        valor = request.data.get('valor')

        conta = get_object_or_404(ContaBancaria, numero_conta=numero_conta)

        if conta.cliente != request.user:
            return Response({'erro': 'Você não tem permissão para depositar nesta conta.'}, status=status.HTTP_403_FORBIDDEN)

        conta = sacar_valor(numero_conta, valor)

        return Response({
            'mensagem': f'Saque de R${valor} realizado com sucesso.',
            'saldo_atual': float(conta.saldo)
        })
    
    except Exception as e:
        return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultar_saldo(request):
    conta = ContaBancaria.objects.get(cliente=request.user)
    return Response({
        'numero_conta': conta.numero_conta,
        'saldo': float(conta.saldo)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def extrato_transacoes(request):
    conta = ContaBancaria.objects.get(cliente=request.user)
    transacoes = Transacao.objects.filter(conta=conta).order_by('-data')

    extrato = [
        {
            'tipo': t.tipo,
            'valor': float(t.valor),
            'data': t.data.strftime('%d/%m/%Y %H:%M')
        } for t in transacoes
    ]

    return Response({
        'numero_conta': conta.numero_conta,
        'extrato': extrato
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transferencia(request):
    try:
        conta_origem_numero = request.data.get('conta_origem')
        conta_destino_numero = request.data.get('conta_destino')
        valor = request.data.get('valor')

        conta_origem = get_object_or_404(ContaBancaria, numero_conta=conta_origem_numero)

        if conta_origem.cliente != request.user:
            return Response({'erro': 'Você só pode transferir a partir da sua própria conta.'}, status=status.HTTP_403_FORBIDDEN)
        
        transferir_valor(conta_origem_numero, conta_destino_numero, valor)

        return Response({
            'mensagem': f'Transferência de R${valor} realizada com sucesso.',
        })
    
    except Exception as e:
        return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)