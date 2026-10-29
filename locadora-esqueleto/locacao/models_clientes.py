from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .validators_cpf import validar_cpf

class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=11, unique=True, validators=[validar_cpf])
    telefone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    
    cnh_numero = models.CharField(max_length=20, unique=True)
    cnh_categoria = models.CharField(max_length=5)
    cnh_validade = models.DateField()
    
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} (CPF: {self.cpf})"

class Funcionario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Locacao(models.Model):
    veiculo = models.ForeignKey('locacao.Veiculo', on_delete=models.PROTECT, related_name='locacoes', null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='locacoes')
    funcionario_retirada = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='retiradas', null=True, blank=True)
    
    data_retirada = models.DateTimeField()
    data_devolucao_prevista = models.DateTimeField()
    data_devolucao_efetiva = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(
        max_length=20, 
        choices=[
            ('PENDENTE', 'Pendente'), 
            ('RETIRADA', 'Retirada'), 
            ('FINALIZADA', 'Finalizada'), 
            ('ATRASADA', 'Atrasada')
        ], 
        default='PENDENTE'
    )
    
    valor_diaria_contratada = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Regra RN19: Locação finalizada não pode ser modificada[span_2](start_span)[span_2](end_span)
        if self.pk:
            original = Locacao.objects.get(pk=self.pk)
            if original.status == 'FINALIZADA':
                raise ValidationError("RN19: Não é permitido alterar uma locação com status FINALIZADA.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Locação #{self.pk} - Cliente: {self.cliente.nome}"