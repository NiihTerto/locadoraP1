"""DONO: P1 - Grupo 1 (Fundação)
Junta as rotas de todos. Cada grupo de telas edita só o seu urls_*.py.
Em config/urls.py (P1): path("", include("locacao.urls"))
"""


from django.urls import include, path

from . import views_base

urlpatterns = [
    path("", views_base.painel, name="painel"),
    path("reservas/", views_base.reserva_lista, name="reserva_lista"),
    path("reservas/<int:pk>/", views_base.reserva_detalhe, name="reserva_detalhe"),
    path("locacoes/", views_base.locacao_lista, name="locacao_lista"),
    path("locacoes/<int:pk>/", views_base.locacao_detalhe, name="locacao_detalhe"),
    path("", include("locacao.urls_cadastro")),
    path("", include("locacao.urls_reserva")),
    path("", include("locacao.urls_locacao")),
]