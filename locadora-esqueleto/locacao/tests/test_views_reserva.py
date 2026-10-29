"""DONO: P8 - Grupo 3 (Telas)
Testes das telas de reserva (UC03): busca, nova reserva e cancelamento.
O self.client do Django faz o papel do navegador.
"""
from datetime import date, timedelta
from decimal import Decimal
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import number_format

from locacao.enums import CategoriaCNH, StatusReserva, StatusVeiculo
from locacao.models import Categoria, Cliente, Reserva, Veiculo


# ---------- fábricas de dados ----------
# Se o P2 ou o P3 mudarem algum campo dos modelos, só estas funções precisam mudar.


def criar_categoria():
    return Categoria.objects.create(
        nome="Econômico",
        valor_diaria=Decimal("120.00"),
        valor_caucao=Decimal("500.00"),
        valor_tanque_cheio=Decimal("300.00"),
        descricao="Categoria usada nos testes",
    )


def criar_veiculo(categoria, placa, status=StatusVeiculo.DISPONIVEL):
    return Veiculo.objects.create(
        placa=placa,
        chassi=f"CHASSI{placa}",
        marca="Fiat",
        modelo="Argo",
        ano_fabricacao=2024,
        cor="Branco",
        km_atual=1000,
        status=status,
        categoria=categoria,
    )


def criar_cliente():
    return Cliente.objects.create(
        nome="Maria Souza",
        cpf="52998224725",
        email="maria@example.com",
        telefone="11999990000",
        data_nascimento=date(1990, 5, 20),
        endereco="Rua das Flores, 100",
        ativo=True,
        cnh_numero="12345678900",
        cnh_categoria=CategoriaCNH.B,
        cnh_validade=date.today() + timedelta(days=365 * 5),
    )


def criar_reserva_no_banco(
    cliente, veiculo, retirada, devolucao, codigo="RES-TESTE001", status=StatusReserva.ATIVA
):
    return Reserva.objects.create(
        codigo=codigo,
        cliente=cliente,
        veiculo=veiculo,
        retirada_prevista=retirada,
        devolucao_prevista=devolucao,
        valor_estimado=Decimal("360.00"),
        status=status,
    )


# ---------- ajudantes ----------


def formatar(momento):
    """Escreve a data como o campo datetime-local do navegador envia."""
    return timezone.localtime(momento).strftime("%Y-%m-%dT%H:%M")


def mensagens(resposta):
    """Junta, num texto só, as mensagens que a tela mostrou ao usuário."""
    return " ".join(str(m) for m in get_messages(resposta.wsgi_request))


class TelasDeReservaTest(TestCase):
    def setUp(self):
        # As telas exigem login: entramos como atendente
        usuario = User.objects.create_user(username="atendente", password="senha-de-teste")
        self.client.force_login(usuario)

        self.categoria = criar_categoria()
        self.veiculo = criar_veiculo(self.categoria, "ABC1D23")
        self.cliente = criar_cliente()

        # Momentos usados nos testes, sem segundos (o formulário só envia até os minutos)
        self.agora = timezone.now().replace(second=0, microsecond=0)
        self.retirada = self.agora + timedelta(days=3)
        self.devolucao = self.retirada + timedelta(days=3)  # 3 diárias

    def url_nova_reserva(self, veiculo):
        periodo = urlencode(
            {
                "retirada": formatar(self.retirada),
                "devolucao": formatar(self.devolucao),
            }
        )
        return f"{reverse('reserva_nova', args=[veiculo.pk])}?{periodo}"

    def reservar(self, veiculo=None):
        """Faz o que a pessoa faz na tela: escolhe o cliente e confirma."""
        veiculo = veiculo or self.veiculo
        return self.client.post(
            self.url_nova_reserva(veiculo), {"cliente": self.cliente.pk}
        )

    def cancelar(self, reserva):
        return self.client.post(reverse("reserva_cancelar", args=[reserva.pk]))

    # ---------- busca ----------

    def test_busca_exige_login(self):
        self.client.logout()
        url = reverse("disponibilidade")

        resposta = self.client.get(url)

        self.assertRedirects(
            resposta,
            f"{resolve_url(settings.LOGIN_URL)}?next={url}",
            fetch_redirect_response=False,
        )

    def test_busca_mostra_so_veiculos_livres(self):
        livre = criar_veiculo(self.categoria, "ABC1D24")
        criar_veiculo(self.categoria, "ABC1D25", status=StatusVeiculo.MANUTENCAO)
        # self.veiculo tem uma reserva ATIVA que bate com o período buscado
        criar_reserva_no_banco(self.cliente, self.veiculo, self.retirada, self.devolucao)

        resposta = self.client.get(
            reverse("disponibilidade"),
            {
                "retirada": formatar(self.retirada),
                "devolucao": formatar(self.devolucao),
            },
        )

        placas = [v.placa for v in resposta.context["veiculos"]]
        self.assertEqual(placas, [livre.placa])  # RN05, RN06 e RN07

    def test_busca_com_devolucao_antes_da_retirada_mostra_rn10(self):
        resposta = self.client.get(
            reverse("disponibilidade"),
            {
                "retirada": formatar(self.devolucao),  # datas invertidas de propósito
                "devolucao": formatar(self.retirada),
            },
        )

        self.assertContains(resposta, "RN10")
        self.assertIsNone(resposta.context["veiculos"])

    # ---------- nova reserva ----------

    def test_reservar_pela_tela_grava_reserva_ativa(self):
        resposta = self.reservar()

        reserva = Reserva.objects.get()  # tem que existir exatamente uma
        self.assertEqual(reserva.status, StatusReserva.ATIVA)
        self.assertEqual(reserva.cliente, self.cliente)
        self.assertEqual(reserva.veiculo, self.veiculo)
        self.assertEqual(reserva.valor_estimado, Decimal("360.00"))  # 3 diárias x R$ 120,00
        self.assertRedirects(
            resposta, reverse("reserva_confirmacao", args=[reserva.codigo])
        )

    def test_reserva_sobreposta_e_recusada_com_rn06(self):
        self.reservar()  # a primeira reserva funciona

        resposta = self.reservar()  # a segunda, no mesmo período, não pode

        self.assertEqual(resposta.status_code, 200)  # a pessoa continua no formulário
        self.assertEqual(Reserva.objects.count(), 1)
        self.assertIn("RN06", mensagens(resposta))

    def test_veiculo_em_manutencao_nao_pode_ser_reservado(self):
        # Mesmo digitando o endereço na mão, a RN05 vale
        manutencao = criar_veiculo(
            self.categoria, "ABC1D25", status=StatusVeiculo.MANUTENCAO
        )

        resposta = self.reservar(manutencao)

        self.assertEqual(Reserva.objects.count(), 0)
        self.assertIn("RN05", mensagens(resposta))

    # ---------- cancelamento ----------

    def test_cancelar_com_menos_de_24h_cobra_multa_de_20_por_cento(self):
        retirada = self.agora + timedelta(hours=2)  # falta menos de 24 h
        reserva = criar_reserva_no_banco(
            self.cliente, self.veiculo, retirada, retirada + timedelta(days=3)
        )

        resposta = self.cancelar(reserva)

        reserva.refresh_from_db()
        self.assertEqual(reserva.status, StatusReserva.CANCELADA)
        multa = number_format(Decimal("72.00"), decimal_pos=2)  # 20% de R$ 360,00
        self.assertIn(f"Multa: R$ {multa}", mensagens(resposta))

    def test_cancelar_com_mais_de_24h_nao_cobra_multa(self):
        reserva = criar_reserva_no_banco(
            self.cliente, self.veiculo, self.retirada, self.devolucao  # daqui a 3 dias
        )

        resposta = self.cancelar(reserva)

        reserva.refresh_from_db()
        self.assertEqual(reserva.status, StatusReserva.CANCELADA)
        self.assertIn("cancelada", mensagens(resposta))
        self.assertNotIn("Multa", mensagens(resposta))

    def test_cancelar_reserva_ja_cancelada_e_recusado(self):
        reserva = criar_reserva_no_banco(
            self.cliente,
            self.veiculo,
            self.retirada,
            self.devolucao,
            status=StatusReserva.CANCELADA,
        )

        resposta = self.cancelar(reserva)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("RN11", mensagens(resposta))  # código usado em cancelar_reserva

    # ---------- status que mudam com o tempo ----------

    def test_reserva_ativa_vencida_vira_expirada_ao_abrir_a_busca(self):
        fim = self.agora + timedelta(days=2)
        vencida = criar_reserva_no_banco(
            self.cliente,
            self.veiculo,
            self.agora - timedelta(hours=5),
            fim,
            codigo="RES-TESTE001",
        )
        no_prazo = criar_reserva_no_banco(
            self.cliente,
            self.veiculo,
            self.agora - timedelta(hours=1),
            fim,
            codigo="RES-TESTE002",
        )

        self.client.get(reverse("disponibilidade"))

        vencida.refresh_from_db()
        no_prazo.refresh_from_db()
        self.assertEqual(vencida.status, StatusReserva.EXPIRADA)  # passou de 4 h (RN12)
        self.assertEqual(no_prazo.status, StatusReserva.ATIVA)  # ainda dentro das 4 h