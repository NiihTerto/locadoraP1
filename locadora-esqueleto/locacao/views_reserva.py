"""DONO: P8 - Grupo 3 (Telas)
TODO: UC03 - busca de disponibilidade, nova reserva, confirmação com o código e
cancelamento. Capture RegraNegocioError e mostre a mensagem com django.contrib.messages.
"""
from django.contrib.auth.decorators import login_required  # noqa: F401
from django.http import request
from django.shortcuts import render, get_object_or_404, redirect, render  # noqa: F401
from django.contrib import messages  # noqa: F401
from django.utils import timezone  # noqa: F401
from django.utils.formats import number_format  # noqa: F401

from .forms_reserva import BuscaDisponibilidadeForm, NovaReservaForm  # noqa: F401
from . import operacoes_reserva, services  # noqa: F401
from .excecoes import RegraNegocioError  # noqa: F401
from .models import Reserva, Veiculo  # noqa: F401  
from .enums import StatusReserva  # noqa: F401

@login_required
def disponibilidade(request):
    # Põe os status temporais de reserva em dia, antes de consultar a disponibilidade (RN09 e RN17)
    operacoes_reserva.atualizar_status_temporais()

    # None = ainda não foi feita a busca, lista vazia = buscou e nao encontrou veículos disponíveis
    veiculos = None

    if request.GET:
        form = BuscaDisponibilidadeForm(request.GET)
        if form.is_valid():
            veiculos = operacoes_reserva.veiculos_disponiveis(
                form.cleaned_data["retirada"],
                form.cleaned_data["devolucao"],
                form.cleaned_data["categoria"],
            )

    else:
        form = BuscaDisponibilidadeForm()

    contexto = {
        "form": form,
        "veiculos": veiculos,
        "consulta": request.GET.urlencode(),
    }
    return render(request, "locacao/disponibilidade.html", contexto)

@login_required
def criar_reserva(request, veiculo_id):
    operacoes_reserva.atualizar_status_temporais()  # RN09 e RN17
    veiculo = get_object_or_404(Veiculo, pk=veiculo_id)

    # O período vem na URL (?retirada=...&devolucao=...). Reaproveitamos o formulário de busca para conferir e converter as datas.
    periodo = BuscaDisponibilidadeForm(request.GET)
    if not periodo.is_valid():
        messages.error(request, "Período inválido. Por favor, faça a busca novamente.")
        return redirect("locacao:disponibilidade")
    retirada = periodo.cleaned_data["retirada"]
    devolucao = periodo.cleaned_data["devolucao"]

    if request.method == "POST":
        form = NovaReservaForm(request.POST)
        if form.is_valid():
            try:
                reserva = operacoes_reserva.criar_reserva(form.cleaned_data["cliente"], veiculo, retirada, devolucao)
            except RegraNegocioError as erro:
            # Ex: "RN06: veículo não disponível no período selecionado"
                messages.error(request, str(erro))
            else:
                return redirect("reserva_confirmacao", codigo=reserva.codigo)

    else:
        form = NovaReservaForm()

    diarias = services.diarias_contratadas(retirada, devolucao)
    contexto = {
        "form": form,
        "veiculo": veiculo,
        "retirada": retirada,
        "devolucao": devolucao,
        "diarias": diarias,
        "valor_estimado": services.valor_previsto(veiculo.categoria.valor_diaria, diarias),
        "consulta": request.GET.urlencode(),
    }
    return render(request, "locacao/criar_reserva.html", contexto)
@login_required
def reserva_confirmacao(request, codigo):
    reserva = get_object_or_404(Reserva, codigo=codigo)
    return render(request, "locacao/reserva_confirmacao.html", {"reserva": reserva})

@login_required
def cancelar_reserva(request, pk):
    operacoes_reserva.atualizar_status_temporais()  # RN09 e RN17
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == "POST":
        try:
            multa = operacoes_reserva.cancelar_reserva(reserva)
        except RegraNegocioError as erro:
            messages.error(request, str(erro))
        else:
            texto = f"Reserva {reserva.codigo} cancelada com sucesso."
            if multa > 0:
                texto += f" Multa de cancelamento: R$ {number_format(multa, 2)}"
            messages.success(request, texto)
        return redirect("locacao:disponibilidade")

    # Prévia de multa: a mesma fórmula usada no cancelamento.
    multa = services.multa_cancelamento(
        reserva.valor_estimado, reserva.retirada_prevista, timezone.now()
    )
    contexto = {
        "reserva": reserva,
        "multa": multa,
        "pode_cancelar": reserva.status == StatusReserva.ATIVA,
    }
    return render(request, "locacao/reserva_cancelamento.html", contexto)