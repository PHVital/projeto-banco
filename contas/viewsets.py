from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import ContaBancaria, Transacao
from .serializers import (
    ContaBancariaSerializer,
    TransacaoSerializer,
    OperacaoSerializer,
    TransferenciaInternaSerializer,
)
from .services.cliente_services import depositar_valor, sacar_valor
from .services.transferencia_service import transferir_valor


class ContaViewSet(viewsets.GenericViewSet):
    queryset = ContaBancaria.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ContaBancaria.objects.filter(cliente=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ContaBancariaSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        conta = self.get_object()
        serializer = ContaBancariaSerializer(conta)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def extrato(self, request, pk=None):
        conta = self.get_object()
        transacoes = conta.transacoes.all()
        serializer = TransacaoSerializer(transacoes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], serializer_class=OperacaoSerializer)
    def deposito(self, request, pk=None):
        conta = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        depositar_valor(
            numero_conta=conta.numero_conta,
            valor=serializer.validated_data['valor']
        )
        conta_atualizada = self.get_object()
        conta_data = ContaBancariaSerializer(conta_atualizada).data
        return Response({'mensagem': 'Depósito realizado com sucesso.', 'conta': conta_data})

    @action(detail=True, methods=['post'], serializer_class=OperacaoSerializer)
    def saque(self, request, pk=None):
        conta = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sacar_valor(
            numero_conta=conta.numero_conta,
            valor=serializer.validated_data['valor']
        )
        conta_atualizada = self.get_object()
        conta_data = ContaBancariaSerializer(conta_atualizada).data
        return Response({'mensagem': 'Saque realizado com sucesso.', 'conta': conta_data})

    @action(detail=True, methods=['post'], serializer_class=TransferenciaInternaSerializer)
    def transferencia(self, request, pk=None):
        conta_origem = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dados_validados = serializer.validated_data

        transferir_valor(
            conta_origem_numero=conta_origem.numero_conta,
            conta_destino_numero=dados_validados['conta_destino'],
            valor_transferencia=dados_validados['valor']
        )
        return Response({'mensagem': 'Transferência realizada com sucesso.'})
