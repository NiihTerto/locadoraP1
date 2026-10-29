"""DONO: P4 - Grupo 2 (Domínio)
TODO: criar as enumerações como django.db.models.TextChoices.
ENTREGAR NO PRIMEIRO DIA: P2 e P3 dependem deste arquivo.

  StatusVeiculo    DISPONIVEL, LOCADO, MANUTENCAO, INATIVO
  StatusReserva    ATIVA, CONVERTIDA, CANCELADA, EXPIRADA
  StatusLocacao    EM_ANDAMENTO, FINALIZADA, ATRASADA
  CategoriaCNH     A, B, C, D, E
  NivelCombustivel VAZIO(0), UM_QUARTO(1), METADE(2), TRES_QUARTOS(3), CHEIO(4)
                   -> precisa de um jeito de obter o valor em quartos
  PerfilUsuario    ATENDENTE, GERENTE
"""
from django.db import models  # noqa: F401

class StatusVeiculo(models.TextChoices):
    DISPONIVEL = "DISPONIVEL", "Disponível"
    LOCADO = "LOCADO", "Locado"
    MANUTENCAO = "MANUTENCAO", "Em manutenção"
    INATIVO = "INATIVO", "Inativo"

class StatusReserva(models.TextChoices):
    ATIVA = "ATIVA", "Ativa"
    CONVERTIDA = "CONVERTIDA", "Convertida em locação"
    CANCELADA = "CANCELADA", "Cancelada"
    EXPIRADA = "EXPIRADA", "Expirada"

class StatusLocacao(models.TextChoices):
    EM_ANDAMENTO = "EM_ANDAMENTO", "Em andamento"
    FINALIZADA = "FINALIZADA", "Finalizada"
    ATRASADA = "ATRASADA", "Atrasada"

class CategoriaCNH(models.TextChoices):
    A = "A", "Categoria A"
    B = "B", "Categoria B"
    C = "C", "Categoria C"
    D = "D", "Categoria D"
    E = "E", "Categoria E"

class NivelCombustivel(models.IntegerChoices):
    VAZIO = 0, "Vazio"
    UM_QUARTO = 1, "1/4"
    METADE = 2, "Metade"
    TRES_QUARTOS = 3, "3/4"
    CHEIO = 4, "Cheio"

class PerfilUsuario(models.TextChoices):
    ATENDENTE = "ATENDENTE", "Atendente"
    GERENTE = "GERENTE", "Gerente"
