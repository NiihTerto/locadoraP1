"""DONO: P2 - Grupo 1 (Fundação)
TODO: modelos Categoria, Veiculo e Reserva.
Toda ForeignKey: related_name e on_delete=models.PROTECT.
Dinheiro: DecimalField(max_digits=10, decimal_places=2).

  Categoria  nome, valor_diaria, valor_caucao, valor_tanque_cheio, descricao
  Veiculo    placa (unique), chassi (unique), marca, modelo, ano_fabricacao, cor,
             km_atual, status (StatusVeiculo), categoria (FK)
  Reserva    codigo (unique), cliente (FK "locacao.Cliente" - texto, pois o modelo é do P3),
             veiculo (FK), retirada_prevista, devolucao_prevista,
             valor_estimado, status (StatusReserva)
"""
from django.db import models  # noqa: F401

from .enums import *  # noqa: F401,F403  (feito pelo P4)
from .validators_veiculo import validar_chassi, validar_placa



class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    valor_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    valor_caucao = models.DecimalField(max_digits=10, decimal_places=2)
    valor_tanque_cheio = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Veiculo(models.Model):
    placa = models.CharField(max_length=8, unique=True, validators=[validar_placa])
    chassi = models.CharField(max_length=17, unique=True, validators=[validar_chassi])
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=80)
    ano_fabricacao = models.PositiveSmallIntegerField()
    cor = models.CharField(max_length=30)
    km_atual = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20, choices=StatusVeiculo.choices, default=StatusVeiculo.DISPONIVEL
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="veiculos"
    )

    def save(self, *args, **kwargs):
        self.placa = self.placa.upper().replace("-", "")
        self.chassi = self.chassi.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.modelo} ({self.placa})"


class Reserva(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(
        "locacao.Cliente", on_delete=models.PROTECT, related_name="reservas"
    )
    veiculo = models.ForeignKey(
        Veiculo, on_delete=models.PROTECT, related_name="reservas"
    )
    retirada_prevista = models.DateTimeField()
    devolucao_prevista = models.DateTimeField()
    valor_estimado = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=StatusReserva.choices, default=StatusReserva.ATIVA
    )

    def __str__(self):
        return self.codigo
    