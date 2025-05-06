from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
import uuid


class ClienteManager(BaseUserManager):
    def create_user(self, cpf, email, nome, data_nascimento=None, password=None):
        if not cpf or not email:
            raise ValueError('CPF e email são obrigatórios')
        
        email = self.normalize_email(email)
        cliente = self.model(
            cpf=cpf,
            email=email,
            nome=nome,
            data_nascimento=data_nascimento,
        )
        cliente.set_password(password)
        cliente.save(using=self._db)
        return cliente
    
    def create_superuser(self, cpf, email, nome, password=None):
        cliente = self.create_user(cpf, email, nome, password=password)
        cliente.is_staff = True
        cliente.is_superuser = True
        cliente.save(using=self._db)
        return cliente


def validar_cpf(cpf):
    if not cpf.isdigit() or len(cpf) != 11:
        raise ValidationError('CPF deve conter 11 dígitos numéricos.')


class Cliente(AbstractBaseUser, PermissionsMixin, models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, unique=True, validators=[validar_cpf])
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['email', 'nome']

    objects = ClienteManager()

    def __str__(self):
        return f'{self.nome} ({self.cpf})'


class ContaBancaria(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    numero_conta = models.CharField(max_length=12, unique=True, blank=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # type: ignore

    def save(self, *args, **kwargs):
        if not self.numero_conta:
            self.numero_conta = str(uuid.uuid4().int)[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Conta {self.numero_conta} - {self.cliente.nome}'
    

class Transacao(models.Model):
    TIPO_TRANSACAO = [
        ('D', 'Depósito'),
        ('S', 'Saque'),
    ]

    conta = models.ForeignKey(ContaBancaria, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10)  # 'deposito' ou 'saque'
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_tipo_display()} de R${self.valor} - {self.conta.numero_conta}' # type: ignore
    
