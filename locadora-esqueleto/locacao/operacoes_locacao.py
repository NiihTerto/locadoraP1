"""DONO: P9 - Grupo 3 (Telas)
Casos de uso UC04 e UC05.

TODO:
  registrar_retirada(reserva, funcionario, km_saida, combustivel_saida, caucao)   (e a versão de balcão, sem reserva)
        RN13, RN14, RN15: reserva -> CONVERTIDA, veículo -> LOCADO, cria Locacao EM_ANDAMENTO
        SNAPSHOT DE PREÇO: copia valor_diaria e valor_caucao da categoria para a locação
  previa_devolucao(locacao, devolucao_real, km_retorno, combustivel_retorno)
        calcula o extrato SEM gravar (para mostrar antes de confirmar)
  registrar_devolucao(locacao, devolucao_real, km_retorno, combustivel_retorno, avaria="")
        RN16-RN19: grava valores, finaliza a locação, veículo -> DISPONIVEL
        (ou MANUTENCAO se houve avaria; nesse caso a caução é retida)
"""
from django.db import transaction  # noqa: F401

from . import rules, services  # noqa: F401

from .excecoes import RegraNegocioError

# Provisório: quando o P4 entregar o enum NivelCombustivel, troque por ele.
QUARTOS = {"VAZIO": 0, "UM_QUARTO": 1, "METADE": 2, "TRES_QUARTOS": 3, "CHEIO": 4}


def calcular_extrato(
    valor_diaria,
    valor_tanque_cheio,
    data_retirada,
    devolucao_prevista,
    devolucao_real,
    combustivel_saida,
    combustivel_retorno,
):
    """Calcula o extrato da devolução SEM gravar nada. Usa só as fórmulas do P4."""
    diarias = services.diarias_contratadas(data_retirada, devolucao_prevista)
    previsto = services.valor_previsto(diarias, valor_diaria)
    dias_de_atraso = services.diarias_de_atraso(devolucao_prevista, devolucao_real)
    multa = services.valor_multa(dias_de_atraso, valor_diaria)
    combustivel = services.taxa_combustivel(
        QUARTOS[combustivel_saida], QUARTOS[combustivel_retorno], valor_tanque_cheio
    )
    total = services.valor_total(previsto, multa, combustivel)
    return {
        "diarias": diarias,
        "valor_previsto": previsto,
        "dias_de_atraso": dias_de_atraso,
        "valor_multa": multa,
        "taxa_combustivel": combustivel,
        "valor_total": total,
    }




def previa_devolucao(locacao, devolucao_real, km_retorno, combustivel_retorno):
    """Mostra o extrato antes de confirmar. Não grava nada."""
    rules.validar_km_retorno(locacao.km_saida, km_retorno)
    return calcular_extrato(
        valor_diaria=locacao.valor_diaria_aplicado,
        valor_tanque_cheio=locacao.veiculo.categoria.valor_tanque_cheio,
        data_retirada=locacao.data_retirada,
        devolucao_prevista=locacao.devolucao_prevista,
        devolucao_real=devolucao_real,
        combustivel_saida=locacao.combustivel_saida,
        combustivel_retorno=combustivel_retorno,
    )


@transaction.atomic
def registrar_retirada(reserva, funcionario, km_saida, combustivel_saida):
    """UC04: transforma uma reserva ATIVA em locação EM_ANDAMENTO."""
    # Importados aqui dentro até os modelos do grupo 1 chegarem na main.
    from django.utils import timezone

    from .models import Locacao, Reserva, Veiculo

    # Trava a reserva e o veículo para ninguém mexer neles ao mesmo tempo.
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    veiculo = Veiculo.objects.select_for_update().get(pk=reserva.veiculo_id)

    rules.validar_reserva_convertivel(reserva.status)                          # RN13
    rules.validar_dados_saida(km_saida, combustivel_saida, veiculo.km_atual)   # RN14

    categoria = veiculo.categoria
    locacao = Locacao.objects.create(
        reserva=reserva,
        cliente=reserva.cliente,
        veiculo=veiculo,
        atendente=funcionario,
        data_retirada=timezone.now(),
        devolucao_prevista=reserva.devolucao_prevista,
        km_saida=km_saida,
        combustivel_saida=combustivel_saida,
        valor_diaria_aplicado=categoria.valor_diaria,   # snapshot do preço
        valor_caucao=categoria.valor_caucao,            # snapshot da caução
        status="EM_ANDAMENTO",
    )

    veiculo.status = "LOCADO"                                                  # RN15
    veiculo.km_atual = km_saida
    veiculo.save()
    reserva.status = "CONVERTIDA"
    reserva.save()
    return locacao


@transaction.atomic
def registrar_devolucao(locacao, devolucao_real, km_retorno, combustivel_retorno, avaria=""):
    """UC05: finaliza a locação, grava o extrato e libera o veículo."""
    # Importados aqui dentro até os modelos do grupo 1 chegarem na main.
    from .models import Locacao, Veiculo

    # Trava a locação e o veículo.
    locacao = Locacao.objects.select_for_update().get(pk=locacao.pk)
    veiculo = Veiculo.objects.select_for_update().get(pk=locacao.veiculo_id)

    if locacao.status == "FINALIZADA":                                         # RN19
        raise RegraNegocioError("RN19", "locação finalizada não pode ser alterada.")

    # Valida o km (RN16) e calcula o extrato, com a mesma função da prévia.
    extrato = previa_devolucao(locacao, devolucao_real, km_retorno, combustivel_retorno)

    tem_avaria = bool(avaria.strip())

    locacao.devolucao_real = devolucao_real
    locacao.km_retorno = km_retorno
    locacao.combustivel_retorno = combustivel_retorno
    locacao.avaria = avaria
    locacao.valor_multa = extrato["valor_multa"]
    locacao.valor_total = extrato["valor_total"]
    locacao.status = "FINALIZADA"
    locacao.save()

    veiculo.km_atual = km_retorno
    veiculo.status = "MANUTENCAO" if tem_avaria else "DISPONIVEL"              # RN18
    veiculo.save()

    # A caução é tratada à parte do total: volta ao cliente, exceto se houve avaria.
    extrato["caucao_devolvida"] = 0 if tem_avaria else locacao.valor_caucao
    return extrato