"""DONO: P9 - Grupo 3 (Telas)

Formulários de retirada (UC04) e devolução (UC05).
"""
from django import forms

# Provisório: quando o P4 entregar o enum NivelCombustivel, troque esta lista por ele.
NIVEIS_COMBUSTIVEL = [
    ("VAZIO", "Vazio"),
    ("UM_QUARTO", "1/4"),
    ("METADE", "1/2"),
    ("TRES_QUARTOS", "3/4"),
    ("CHEIO", "Cheio"),
]


class RetiradaForm(forms.Form):
    km_saida = forms.IntegerField(
        label="Quilometragem de saída",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    combustivel_saida = forms.ChoiceField(
        label="Nível de combustível",
        choices=NIVEIS_COMBUSTIVEL,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

class DevolucaoForm(forms.Form):
    devolucao_real = forms.DateTimeField(
        label="Data e hora da devolução",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
    )
    km_retorno = forms.IntegerField(
        label="Quilometragem de retorno",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    combustivel_retorno = forms.ChoiceField(
        label="Nível de combustível na devolução",
        choices=NIVEIS_COMBUSTIVEL,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    avaria = forms.CharField(
        label="Avaria (deixe em branco se não houve)",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )


