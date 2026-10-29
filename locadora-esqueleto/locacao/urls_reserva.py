"""DONO: P8 - Grupo 3 (Telas)
"""
from django.urls import path  # noqa: F401

from . import views_reserva  # noqa: F401

urlpatterns = [
    path("disponibilidade/", views_reserva.disponibilidade, name="disponibilidade"),
    path("reserva/nova/<int:veiculo_id>/", views_reserva.reserva_nova, name="reserva_nova"),
    path("reserva/confirmacao/<str:codigo>/", views_reserva.reserva_confirmacao, name="reserva_confirmacao"),
    path("reserva/<int:pk>/cancelar/", views_reserva.reserva_cancelar, name="reserva_cancelar"),
]
