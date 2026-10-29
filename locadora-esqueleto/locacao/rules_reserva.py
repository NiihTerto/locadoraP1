"""DONO: P5 - Grupo 2 (Domínio)
Regras de cliente, período e reserva. Funções PURAS: recebem números, datas e
textos simples (nunca objetos do banco). Ao violar, levantam
RegraNegocioError("RNxx", "mensagem").

TODO (teste primeiro, em tests/test_rules_reserva.py):

  validar_idade(data_nascimento, data_retirada)            RN01  mínimo 21 anos na retirada
  validar_cnh(categoria, validade, devolucao_prevista)     RN02  categoria B ou superior e válida até a devolução
  validar_cliente_ativo(ativo)                             RN03  cliente inativo não reserva
  validar_sem_atraso(tem_locacao_atrasada)                 RN04  cliente com locação ATRASADA não reserva
  validar_periodo(retirada, devolucao, agora)              RN08  mínimo 1 diária, máximo 30 dias
                                                           RN09  retirada não pode ser no passado
                                                           RN10  devolução depois da retirada
  cancelamento_com_multa(retirada_prevista, agora)         RN11  True se faltar menos de 24 h
  reserva_expirada(retirada_prevista, agora)               RN12  True se passou mais de 4 h da hora prevista
"""
from datetime import datetime, timedelta, timezone

from .excecoes import RegraNegocioError  # noqa: F401


def validar_idade(data_nascimento, data_retirada):
    idade = data_retirada.year - data_nascimento.year
    if (data_retirada.month, data_retirada.day) < (data_nascimento.month, data_nascimento.day):
        idade = idade-1
    if idade < 21:
        raise RegraNegocioError("RN01", "O cliente deve possuir pelo menos 21 anos")


def validar_cnh(categoria, validade, devolucao_prevista):
    if categoria not in ["B", "C", "D", "E"]:
        raise RegraNegocioError("RN02", "Categoria precisa ser B ou superior") 
    if validade < devolucao_prevista:
        raise RegraNegocioError("RN02", "CNH inválida, o vencimento ocorrerá antes da devolução prevista")


def validar_cliente_ativo(ativo):
    if not ativo:
        raise RegraNegocioError("RN03", "O cadastro do cliente está inativo")


def validar_sem_atraso(tem_locacao_atrasada):
    if tem_locacao_atrasada:
        raise RegraNegocioError("RN04", "Este cliente possui uma locação atrasada")


def validar_periodo(retirada, devolucao, agora):
    if devolucao <= retirada:
        raise RegraNegocioError("RN10", "A devolução deve ser posterior à retirada")
    if retirada < agora:
        raise RegraNegocioError("RN09", "A retirada deve ser posterior à reserva")
    duracao = devolucao - retirada
    if duracao < timedelta(hours=24) or duracao > timedelta(days=30):
        raise RegraNegocioError("RN08", "Limite de tempo não permitido")

def cancelamento_com_multa(retirada_prevista, agora):
    cancelamento = retirada_prevista - agora
    return cancelamento < timedelta(hours=24)


def reserva_expirada(retirada_prevista, agora):
    expiracao = agora - retirada_prevista
    return expiracao > timedelta(hours=4)
