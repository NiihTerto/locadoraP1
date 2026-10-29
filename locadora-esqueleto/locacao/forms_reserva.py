"""DONO: P8 - Grupo 3 (Telas)
TODO: BuscaDisponibilidadeForm (retirada, devolução, categoria opcional) e o formulário
de nova reserva. RN10 já na busca: devolução depois da retirada.
"""
from django import forms  # noqa: F401
from .models import Categoria, Cliente

class BuscaDisponibilidadeForm(forms.Form):
    retirada = forms.DateTimeField(label="Retirada", widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})), format = "%Y-%m-%dT%H:%M", input_formats=["%Y-%m-%dT%H:%M"]
    devolucao = forms.DateTimeField(label="Devolução", widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})), format = "%Y-%m-%dT%H:%M", input_formats=["%Y-%m-%dT%H:%M"]
    categoria = forms.ModelChoiceField(label="Categoria (opcional)", queryset=Categoria.objects.all(), required=False, empty_label="Todas as categorias", widget=forms.Select(attrs={"class": "form-select"}))
    cliente = forms.ModelChoiceField(label="Cliente", queryset=Cliente.objects.all(), required=True, widget=forms.Select(attrs={"class": "form-select"}))

def clean(self):
    dados = super().clean()
    retirada = dados.get("retirada")
    devolucao = dados.get("devolucao")

    # RN10: devolução depois da retirada
    if retirada and devolucao and devolucao <= retirada:
        raise forms.ValidationError("A data de devolução deve ser posterior à data de retirada.")
    return dados

class ClienteChoiceField(forms.ModelChoiceField):
# Define o texto de cada opção na lista, sem depender do __str__ do P3
    def label_from_instance(self, cliente):
        return f"{cliente.nome} ({cliente.cpf})"

class NovaReservaForm(forms.Form):
    cliente = ClienteChoiceField(
        label="Cliente",
        # RN03: cliente deve ser selecionado a partir de uma lista de clientes cadastrados, a criar_reserva confere novamente se o cliente existe
        queryset=Cliente.objects.filter(ativo=True).order_by("nome"),
        empty_label="Selecione um cliente",
        widget=forms.Select(attrs={"class": "form-select"})
    )