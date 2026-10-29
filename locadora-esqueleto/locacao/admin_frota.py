"""DONO: P2 - Grupo 1 (Fundação)
TODO: registrar Categoria, Veiculo e Reserva no admin (@admin.register).
Veiculo: list_display, search_fields (placa, modelo) e list_filter por status.
Reserva: somente leitura.
"""
from django.contrib import admin  # noqa: F401


from .models_frota import Categoria, Reserva, Veiculo


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "valor_diaria", "valor_caucao", "valor_tanque_cheio")
    search_fields = ("nome",)


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "modelo", "marca", "categoria", "status")
    search_fields = ("placa", "chassi", "modelo")
    list_filter = ("status", "categoria")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "cliente", "veiculo", "retirada_prevista", "status")
    search_fields = ("codigo",)
    list_filter = ("status",)

    # Reservas são somente leitura no admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False