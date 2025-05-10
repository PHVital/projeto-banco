from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from contas.models import Cliente


@api_view(["POST"])
def autenticar_cliente_token(request):
    cpf = request.data.get("cpf")
    senha = request.data.get("senha")

    user = authenticate(request, cpf=cpf, password=senha)

    if user is None:
        return Response({"erro": "Credenciais inválidas"}, status=401)

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "mensagem": "Autenticado com sucesso!",
            "token": token.key,
            "cliente_id": user.id,
            "nome": user.nome,
        }
    )
