"""DONO: P9 - Grupo 3 (Telas)"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms_locacao import DevolucaoForm, RetiradaForm


@login_required
def retirada(request, pk):
    if request.method == "POST":
        form = RetiradaForm(request.POST)
        if form.is_valid():
            messages.success(request, "Formulário válido (ainda não grava nada).")
    else:
        form = RetiradaForm()
    return render(request, "locacao/retirada_form.html", {"form": form})


@login_required
def devolucao(request, pk):
    if request.method == "POST":
        form = DevolucaoForm(request.POST)
        if form.is_valid():
            messages.success(request, "Formulário válido (ainda não grava nada).")
    else:
        form = DevolucaoForm()
    return render(request, "locacao/devolucao_form.html", {"form": form})