from rest_framework import serializers
from django.contrib.auth import authenticate
from decimal import Decimal

from .models import Cliente, ContaBancaria, Transacao


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "cpf", "nome", "email", "data_nascimento", "date_joined"]
        read_only_fields = ["id", "cpf", "email", "date_joined"]


class ClienteCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    nome = serializers.CharField(required=True)
    data_nascimento = serializers.DateField(
        required=False, allow_null=True, input_formats=["%Y-%m-%d"]
    )
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = Cliente
        fields = ["cpf", "nome", "email", "data_nascimento", "password"]

    def validate_cpf(self, value):
        if Cliente.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("Um cliente com este CPF já existe.")
        return value

    def validate_email(self, value):
        if Cliente.objects.filter(email=value).exists():
            raise serializers.ValidationError("Um cliente com este email já existe.")
        return value


class LoginSerializer(serializers.Serializer):
    cpf = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, data):
        cpf = data.get("cpf")
        password = data.get("password")

        if cpf and password:
            user = authenticate(
                request=self.context.get("request"), cpf=cpf, password=password
            )
            if not user:
                raise serializers.ValidationError(
                    "Credenciais inválidas. Verifique CPF e senha.",
                    code="authorization",
                )
        else:
            raise serializers.ValidationError(
                "CPF e senha são obrigatórios.", code="authorization"
            )

        data["user"] = user
        return data


class ContaBancariaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)

    class Meta:
        model = ContaBancaria
        fields = ["id", "cliente", "numero_conta", "saldo"]
        read_only_fields = fields


class TransacaoSerializer(serializers.ModelSerializer):
    tipo_descricao = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Transacao
        fields = ["id", "conta", "tipo", "tipo_descricao", "valor", "data"]
        read_only_fields = fields


class DepositoSaqueSerializer(serializers.Serializer):
    numero_conta = serializers.CharField(max_length=12, required=True)
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_valor(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("O valor da operação deve ser positivo.")
        return value


class TransferenciaSerializer(serializers.Serializer):
    conta_origem = serializers.CharField(
        max_length=12, required=True, help_text="Número da sua conta de origem"
    )
    conta_destino = serializers.CharField(
        max_length=12, required=True, help_text="Número da conta de destino"
    )
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_valor(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "O valor da transferência deve ser positivo."
            )
        return value

    def validate(self, data):
        if data.get("conta_origem") == data.get("conta_destino"):
            raise serializers.ValidationError(
                "A conta de origem e destino não podem ser iguais."
            )
        return data


class OperacaoSerializer(serializers.Serializer):
    valor = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.01")
    )


class TransferenciaInternaSerializer(serializers.Serializer):
    conta_destino = serializers.CharField(max_length=12)
    valor = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.01")
    )

    def validate_conta_destino(self, value):
        if not ContaBancaria.objects.filter(numero_conta=value).exists():
            raise serializers.ValidationError("A conta de destino não existe.")
        return value
