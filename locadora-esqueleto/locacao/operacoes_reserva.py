"""DONO: P8 - Grupo 3 (Telas)
Casos de uso UC03: une modelos + regras + fórmulas, dentro de transações.

TODO:
  veiculos_disponiveis(retirada, devolucao, categoria=None)
        RN05: só status DISPONIVEL; RN07: fora MANUTENCAO e INATIVO;
        RN06: sem reserva ATIVA nem locação EM_ANDAMENTO sobrepostas (use rules.ha_sobreposicao)
  criar_reserva(cliente, veiculo, retirada, devolucao)
        @transaction.atomic + select_for_update no veículo; valida RN01-RN04, RN06, RN08-RN10;
        gera código único; calcula valor_estimado (services); cria a reserva ATIVA
  cancelar_reserva(reserva, agora)
        RN11: grátis até 24 h antes; depois, multa de 20%
  atualizar_status_temporais(agora=None)
        RN12: reservas ATIVAS vencidas -> EXPIRADA; RN17: locações vencidas -> ATRASADA
"""
import secrets  # noqa: F401
import string  # noqa: F401
from django.db import transaction  # noqa: F401
from django.utils import timezone  # noqa: F401
from . import rules, services  # noqa: F401
from .enums import StatusLocacao, StatusReserva, StatusVeiculo
from .models import Locacao, Reserva, Veiculo
from .excecoes import RegraNegocioError

def periodos_ocupados(veiculo):
    """Retorna uma lista de tuplas (inicio, fim) com os períodos ocupados do veículo."""
    periodos = []

    reservas = Reserva.objects.filter(veiculo=veiculo, status=StatusReserva.ATIVA)
    for reserva in reservas:
        periodos.append((reserva.retirada_prevista, reserva.devolucao_prevista))

    locacoes = Locacao.objects.filter(veiculo=veiculo, status=StatusLocacao.EM_ANDAMENTO)
    for locacao in locacoes:
        periodos.append((locacao.data_retirada, locacao.devolucao_prevista))

    return periodos

def veiculos_disponiveis(retirada, devolucao, categoria=None):
    # RN055 e RN07: só entra quem está DISPONIVEL
    # (isso deixa de fora manutenções e inativos, e locados)
    candidatos = Veiculo.objects.filter(status=StatusVeiculo.DISPONIVEL)

    # se o usuário especificou uma categoria, filtra por ela
    if categoria is not None:
        candidatos = candidatos.filter(categoria=categoria)

    disponiveis = []
    for veiculo in candidatos:
        #junta todos os períodos "ocupados" do veículo
        periodos = []
        ocupados = periodos_ocupados(veiculo)
        locacoes = Locacao.objects.filter(veiculo=veiculo, status=StatusLocacao.EM_ANDAMENTO)

        for locacao in locacoes:
            periodos.append((locacao.data_retirada, locacao.devolucao_prevista))

        # RN06: se houver sobreposição, não está disponível
        if not rules.ha_sobreposicao(periodos, retirada, devolucao):
            disponiveis.append(veiculo)

    return disponiveis
 
def _gerar_codigo_reserva():
    caracteres = string.ascii_uppercase + string.digits
    while True:
        # Sorteia 8 caracteres e junta tudo num texto só
        sufixo = "".join(secrets.choice(caracteres) for _ in range(8))
        codigo = f"RES-{sufixo}"
        # Se por azar esse código já existir, o laço sorteia outro
        if not Reserva.objects.filter(codigo=codigo).exists():
            return codigo

@transaction.atomic
def criar_reserva(cliente, veiculo, retirada, devolucao, valor_estimado, agora=None):
    # se não foi passado, pega o horário atual
    if agora is None:
        agora = timezone.now()
    # RN08, RN09, RN10: periodos válidos (uma função do P5 cuida das 3)
    rules.validar_periodo(retirada, devolucao, agora)

    # RN01: idade mínima do cliente
    rules.validar_idade(cliente.data_nascimento, retirada.date())

    # RN02: CNH categoria B ou superior e válida até a data de devolução
    rules.validar_cnh(cliente.cnh_categoria, cliente.cnh_validade, devolucao.date())

    # RN03: o cliente precisa estar ativo
    rules.validar_cliente_ativo(cliente.ativo)

    # RN04: o cliente não pode ter locações atrasadas
    tem_atrasadas = Locacao.objects.filter(cliente=cliente, status=StatusLocacao.ATRASADA).exists()
    rules.validar_sem_atraso(tem_atrasadas)

    # Trava o carro no banco ate o fim da transação
    veiculo = Veiculo.objects.select_for_update().get(pk=veiculo.pk)    

    # RN05 e RN07: só entra quem está DISPONIVEL (isso deixa de fora manutenções e inativos, e locados). O starus pode ter mudado desde a busca, e o id também pode ter sido digitado direto na url
    if veiculo.status != StatusVeiculo.DISPONIVEL:
        raise RegraNegocioError("Veículo não disponível no período solicitado.")

    # RN06: só depois de travar é que conferimos se o veículo está disponível no período
    ocupados = periodos_ocupados(veiculo)
    if rules.ha_sobreposicao(retirada, devolucao, ocupados):
        raise RegraNegocioError("Veículo não disponível no período solicitado.")

    # Grava e devolve a reserva, para a view mostrar o código ao usuário
    return Reserva.objects.create(
        codigo=_gerar_codigo_reserva(),
        cliente=cliente,
        veiculo=veiculo,
        retirada_prevista=retirada,
        devolucao_prevista=devolucao,
        valor_estimado=valor_estimado,
        status=StatusReserva.ATIVA,
    )

def cancelar_reserva(reserva, agora=None):
    # se não foi passado, pega o horário atual
    if agora is None:
        agora = timezone.now()

    # só é possível cancelar reservas ATIVAS
    if reserva.status != StatusReserva.ATIVA:
        raise RegraNegocioError("Só é possível cancelar reservas ATIVAS.")

    # RN11: grátis até 24 h antes; depois, multa de 20%
    multa = services.multa_cancelamento(reserva.valor_estimado, reserva.retirada_prevista, agora)

    with transaction.atomic():
        # atualiza o status da reserva para CANCELADA
        reserva.status = StatusReserva.CANCELADA
        reserva.save()

        return multa

def atualizar_status_temporais(agora=None):
    if agora is None:
        agora = timezone.now() 

    reservas_expiradas = 0
    locações_atrasadas = 0

    with transaction.atomic():
        # RN12: a regra do P5 diz se a reserva está vencida
        for reserva in Reserva.objects.filter(status=StatusReserva.ATIVA):
            if rules.reserva_expirada(reserva, agora):
                reserva.status = StatusReserva.EXPIRADA
                reserva.save()
                reservas_expiradas += 1

        # RN17: a regra do P4 conta as diarias de atraso
        # se der pelo menos 1, a locação está vencida
        for locacao in Locacao.objects.filter(status=StatusLocacao.EM_ANDAMENTO):
            if services.diarias_de_atraso(locacao.devolucao_prevista, agora) > 0:
                locacao.status = StatusLocacao.ATRASADA
                locacao.save()
                locações_atrasadas += 1
    return {
        "reservas_expiradas": reservas_expiradas,
        "locacoes_atrasadas": locações_atrasadas,
    }