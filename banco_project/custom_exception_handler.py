# banco_project/custom_exception_handler.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

def custom_api_exception_handler(exc, context):
    # Primeiro, chame o handler de exceção padrão do DRF para obter a resposta base.
    response = exception_handler(exc, context)

    # Se o handler padrão do DRF já forneceu uma resposta, nós a usamos.
    if response is not None:
        # Você pode adicionar customizações aqui se quiser mudar o formato padrão do DRF
        # Por exemplo, para garantir que todos os erros tenham uma chave 'errors'
        if isinstance(response.data, dict) and not ('errors' in response.data or any(isinstance(v, list) for v in response.data.values())):
            # Se for um erro de detalhe simples, envolva em 'errors'
            if 'detail' in response.data:
                 response.data = {'errors': {'detail': [response.data['detail']]}}
            # else: # Se já for um dict de erros de validação, pode já estar bom
                 # response.data = {'errors': response.data} # Ou deixe como está
        elif isinstance(response.data, list):
            response.data = {'errors': {'detail': response.data}}
    else:
        # Se o DRF não tratou a exceção, podemos tratar algumas exceções do Django aqui
        if isinstance(exc, Http404): # Http404 é um tipo de ObjectDoesNotExist
            response = Response(
                {'errors': {'detail': ["Recurso não encontrado."]}},
                status=status.HTTP_404_NOT_FOUND
            )
        elif isinstance(exc, ObjectDoesNotExist): # Genérico
             response = Response(
                {'errors': {'detail': ["Objeto não encontrado."]}},
                status=status.HTTP_404_NOT_FOUND
            )
        elif isinstance(exc, ValueError): # Se seus services levantarem ValueError
            response = Response(
                {'errors': {'detail': [str(exc)]}},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Para qualquer outra exceção não tratada que não seja do DRF
        # e que você não queira expor detalhes, retorne um 500 genérico.
        # Em produção, você DEVE logar a exceção 'exc' aqui!
        else:
            # print(f"Erro não tratado no custom_exception_handler: {type(exc).__name__} - {exc}") # Para debug
            response = Response(
                {'errors': {'server_error': ['Ocorreu um erro inesperado no servidor.']}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return response