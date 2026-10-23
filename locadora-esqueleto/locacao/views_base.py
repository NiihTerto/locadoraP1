"""DONO: P1 - Grupo 1 (Fundação)
TODO (todas com @login_required, exceto o login):
  painel(request)        RF15: livres, em andamento, atrasadas, manutenção, faturado hoje,
                         retiradas e devoluções do dia
  reserva_lista / reserva_detalhe      RF14 (filtro por status)
  locacao_lista / locacao_detalhe      RF14 (filtro por status)
O login e o logout usam as views prontas do Django (django.contrib.auth.views).
Chame operacoes.atualizar_status_temporais() no início das telas.
"""


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# TODO P1: quando models e operacoes dos colegas estiverem na develop,
# trocar os valores vazios abaixo por consultas reais e chamar
# operacoes.atualizar_status_temporais() no início de cada view.


@login_required
def painel(request):
    return render(request, "locacao/painel.html", {})


@login_required
def reserva_lista(request):
    return render(request, "locacao/reserva_lista.html", {"reservas": []})


@login_required
def reserva_detalhe(request, pk):
    return render(request, "locacao/reserva_detalhe.html", {"reserva": None})


@login_required
def locacao_lista(request):
    return render(request, "locacao/locacao_lista.html", {"locacoes": []})


@login_required
def locacao_detalhe(request, pk):
    return render(request, "locacao/locacao_detalhe.html", {"locacao": None})