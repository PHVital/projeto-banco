from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

# from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from contas.models import Cliente, ContaBancaria, Transacao
from contas.services.cliente_services import (
    criar_cliente_e_conta,
    depositar_valor,
    sacar_valor,
)
from contas.services.transferencia_service import transferir_valor

from .serializers import (
    ClienteSerializer,
    ClienteCreateSerializer,
    LoginSerializer,
    ContaBancariaSerializer,
    TransacaoSerializer,
    DepositoSaqueSerializer,
    TransferenciaSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def registrar_cliente(request):
    serializer = ClienteCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            cliente, conta, token = criar_cliente_e_conta(
                nome=serializer.validated_data["nome"],
                cpf=serializer.validated_data["cpf"],
                email=serializer.validated_data["email"],
                data_nascimento=serializer.validated_data.get("data_nascimento"),
                senha=serializer.validated_data["password"],
            )

            cliente_data = ClienteSerializer(cliente).data
            return Response(
                {
                    "mensagem": "Cliente criado com sucesso!",
                    "cliente": cliente_data,
                    "numero_conta": conta.numero_conta,
                    "token": token.key,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"erro": "Ocorreu um erro ao criar o cliente."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def autenticar_cliente(request):
    serializer = LoginSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        user_data = ClienteSerializer(user).data

        return Response(
            {
                "mensagem": "Autenticado com sucesso!",
                "token": token.key,
                "usuario": user_data,
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deposito(request):
    serializer = DepositoSaqueSerializer(data=request.data)
    if serializer.is_valid():
        numero_conta_req = serializer.validated_data["numero_conta"]
        valor_req = serializer.validated_data["valor"]

        try:
            conta_bancaria = get_object_or_404(
                ContaBancaria, numero_conta=numero_conta_req
            )
            if conta_bancaria.cliente != request.user:
                return Response(
                    {"erro": "Você não tem permissão para depositar nesta conta."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            conta_atualizada = depositar_valor(numero_conta_req, valor_req)

            conta_data = ContaBancariaSerializer(conta_atualizada).data
            return Response(
                {
                    "mensagem": f"Depósito de R${valor_req} realizado com sucesso.",
                    "conta": conta_data,
                },
                status=status.HTTP_200_OK,
            )

        except ObjectDoesNotExist:
            return Response(
                {"erro": f"Conta {numero_conta_req} não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"erro": "Ocorreu um erro ao processar o depósito"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def saque(request):
    serializer = DepositoSaqueSerializer(data=request.data)
    if serializer.is_valid():
        numero_conta_req = serializer.validated_data["numero_conta"]
        valor_req = serializer.validated_data["valor"]

        try:
            conta_bancaria = get_object_or_404(
                ContaBancaria, numero_conta=numero_conta_req
            )
            if conta_bancaria.cliente != request.user:
                return Response(
                    {"erro": "Você não tem permissão para sacar nesta conta."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            conta_atualizada = sacar_valor(numero_conta_req, valor_req)

            conta_data = ContaBancariaSerializer(conta_atualizada).data
            return Response(
                {
                    "mensagem": f"Saque de R${valor_req} realizado com sucesso.",
                    "conta": conta_data,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"erro": "Ocorreu um erro ao processar o saque"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def consultar_saldo(request):
    try:
        conta = ContaBancaria.objects.get(cliente=request.user)
        serializer = ContaBancariaSerializer(conta)
        return Response(serializer.data)
    except ContaBancaria.DoesNotExist:
        return Response(
            {"erro": "Nenhuma conta bancária encontrada para este cliente."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ContaBancaria.MultipleObjectsReturned:
        return Response(
            {"erro": "Múltiplas contas encontradas. Especifique a conta."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        return Response(
            {"erro": "Ocorreu um erro ao consultar o saldo."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def extrato_transacoes(request):
    try:
        conta = ContaBancaria.objects.get(cliente=request.user)
        transacoes = conta.transacoes.all()  # type: ignore

        transacoes_data = TransacaoSerializer(transacoes, many=True).data
        conta_data = ContaBancariaSerializer(conta).data

        return Response(
            {
                "conta": {
                    "numero_conta": conta_data["numero_conta"],
                    "saldo_atual": conta_data["saldo"],
                },
                "extrato": transacoes_data,
            }
        )
    except ContaBancaria.DoesNotExist:
        return Response(
            {"erro": "Nenhuma conta bancária encontrada para este cliente."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception:
        return Response(
            {"erro": "Ocorreu um erro ao buscar o extrato."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def transferencia(request):
    serializer = TransferenciaSerializer(data=request.data)
    if serializer.is_valid():
        conta_origem_num = serializer.validated_data["conta_origem"]
        conta_destino_num = serializer.validated_data["conta_destino"]
        valor_transf = serializer.validated_data["valor"]

        try:
            conta_origem_obj = get_object_or_404(
                ContaBancaria, numero_conta=conta_origem_num
            )
            if conta_origem_obj.cliente != request.user:
                return Response(
                    {"erro": "Você só pode transferir a partir da sua própria conta."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            _, _ = transferir_valor(
                conta_origem_numero=conta_origem_num,
                conta_destino_numero=conta_destino_num,
                valor_transferencia=valor_transf,
            )

            return Response(
                {
                    "mensagem": f"Transferência de R%{valor_transf} de {conta_origem_num} para {conta_destino_num} realizada com sucesso."
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"erro": "Ocorreu um erro ao processar a transferência."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
