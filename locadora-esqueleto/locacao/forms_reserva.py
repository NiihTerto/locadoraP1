"""DONO: P8 - Grupo 3 (Telas)
TODO: BuscaDisponibilidadeForm (retirada, devolução, categoria opcional) e o formulário
de nova reserva. RN10 já na busca: devolução depois da retirada.
"""
from django import forms

from .models import Categoria, Cliente


class BuscaDisponibilidadeForm(forms.Form):
    retirada = forms.DateTimeField(
        label="Retirada",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    devolucao = forms.DateTimeField(
        label="Devolução",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    categoria = forms.ModelChoiceField(
        label="Categoria (opcional)",
        queryset=Categoria.objects.all(),
        required=False,
        empty_label="Todas as categorias",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean(self):
        dados = super().clean()
        retirada = dados.get("retirada")
        devolucao = dados.get("devolucao")

        # RN10: a devolução precisa ser depois da retirada
        if retirada and devolucao and devolucao <= retirada:
            raise forms.ValidationError(
                "RN10: a devolução deve ser depois da retirada."
            )
        return dados


class ClienteChoiceField(forms.ModelChoiceField):
    # Define o texto de cada opção da lista, sem depender do __str__ do P3
    def label_from_instance(self, cliente):
        return f"{cliente.nome} (CPF {cliente.cpf})"


class NovaReservaForm(forms.Form):
    cliente = ClienteChoiceField(
        label="Cliente",
        # RN03: só clientes ativos aparecem; a criar_reserva confere de novo
        queryset=Cliente.objects.filter(ativo=True).order_by("nome"),
        empty_label="Selecione o cliente",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
