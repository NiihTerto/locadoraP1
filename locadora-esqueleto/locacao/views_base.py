"""DONO: P1 - Grupo 1 (Fundação)
Versão parcial: painel de veículos e telas de reservas (RF14/RF15).
As partes de locação entram quando o Locacao do P3 estiver alinhado.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .enums import StatusReserva, StatusVeiculo
from .models import Reserva, Veiculo

# TODO P1: chamar operacoes.atualizar_status_temporais() no início das telas
# quando o P8 corrigir a função.


@login_required
def painel(request):
    cartoes = [
        ("Veículos livres", Veiculo.objects.filter(status=StatusVeiculo.DISPONIVEL).count(), "success"),
        ("Veículos locados", Veiculo.objects.filter(status=StatusVeiculo.LOCADO).count(), "primary"),
        ("Em manutenção", Veiculo.objects.filter(status=StatusVeiculo.MANUTENCAO).count(), "warning"),
        ("Reservas ativas", Reserva.objects.filter(status=StatusReserva.ATIVA).count(), "info"),
    ]
    return render(request, "locacao/painel.html", {"cartoes": cartoes})


@login_required
def reserva_lista(request):
    status = request.GET.get("status", "")
    reservas = Reserva.objects.select_related("cliente", "veiculo").order_by("-retirada_prevista")
    if status in StatusReserva.values:
        reservas = reservas.filter(status=status)
    return render(request, "locacao/reserva_lista.html", {
        "reservas": reservas,
        "status_atual": status,
        "status_opcoes": StatusReserva.choices,
    })


@login_required
def reserva_detalhe(request, pk):
    reserva = get_object_or_404(Reserva.objects.select_related("cliente", "veiculo"), pk=pk)
    return render(request, "locacao/reserva_detalhe.html", {"reserva": reserva})


@login_required
def locacao_lista(request):
    return render(request, "locacao/locacao_lista.html", {"locacoes": []})


@login_required
def locacao_detalhe(request, pk):
    return render(request, "locacao/locacao_detalhe.html", {"locacao": None})