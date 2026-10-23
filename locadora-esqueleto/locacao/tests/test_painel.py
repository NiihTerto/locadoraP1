"""DONO: P1 - Grupo 1 (Fundação)
TODO: login obrigatório e carregamento de painel e listas.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class PainelTests(TestCase):
    ROTAS = ["painel", "reserva_lista", "locacao_lista"]

    def test_login_obrigatorio(self):
        for nome in self.ROTAS:
            url = reverse(nome)
            resp = self.client.get(url)
            self.assertRedirects(resp, f"/login/?next={url}")

    def test_paginas_carregam_logado(self):
        get_user_model().objects.create_user("teste", password="senha12345")
        self.client.login(username="teste", password="senha12345")
        for nome in self.ROTAS:
            resp = self.client.get(reverse(nome))
            self.assertEqual(resp.status_code, 200)