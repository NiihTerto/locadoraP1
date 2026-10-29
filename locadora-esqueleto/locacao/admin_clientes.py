from django.contrib import admin
from .models_clientes import Cliente, Funcionario, Locacao

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'cnh_numero', 'cnh_categoria', 'ativo')
    search_fields = ('nome', 'cpf', 'cnh_numero')
    list_filter = ('ativo', 'cnh_categoria')

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'cargo')
    search_fields = ('user__username', 'user__email')

@admin.register(Locacao)
class LocacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'veiculo', 'status', 'data_retirada', 'data_devolucao_prevista')
    list_filter = ('status', 'data_retirada')
    search_fields = ('cliente__nome',)