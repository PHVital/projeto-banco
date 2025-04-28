from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()
    email = models.EmailField()

    def __str__(self):
        return self.nome


class ContaBancaria(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    numero_conta = models.CharField(max_length=10, unique=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # type: ignore

    def __str__(self):
        return f'Conta {self.numero_conta} - {self.cliente.nome}'
    

class Transacao(models.Model):
    TIPO_TRANSACAO_CHOICES = (
        ('DEPOSITO', 'Depósito'),
        ('SAQUE', 'Saque'),
    )

    conta = models.ForeignKey(ContaBancaria, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_TRANSACAO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tipo} de R$ {self.valor} na conta {self.conta.numero_conta}'