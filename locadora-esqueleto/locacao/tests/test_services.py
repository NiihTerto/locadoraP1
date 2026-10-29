"""DONO: P4 - Grupo 2 (Domínio)
TODO: um teste por fórmula + o exemplo numérico completo (R$ 690,00).
Use django.test.SimpleTestCase (sem banco). Cubra: frações de 24 h, tolerância
exata de 60 min, arredondamento HALF_UP, combustível sem crédito.
Rodar: python manage.py test locacao.tests.test_services
"""
from datetime import datetime
from decimal import Decimal

from django.test import SimpleTestCase

from locacao import services


class DiariasContratadasTests(SimpleTestCase):
    def test_tres_dias_exatos(self):
        retirada = datetime(2026, 10, 10, 9, 0)
        prevista = datetime(2026, 10, 13, 9, 0)
        self.assertEqual(services.diarias_contratadas(retirada, prevista), 3)

    def test_uma_hora_a_mais_conta_outra_diaria(self):
        retirada = datetime(2026, 10, 10, 9, 0)
        prevista = datetime(2026, 10, 13, 10, 0)
        self.assertEqual(services.diarias_contratadas(retirada, prevista), 4)

    def test_minimo_de_uma_diaria(self):
        retirada = datetime(2026, 10, 10, 9, 0)
        prevista = datetime(2026, 10, 10, 11, 0)
        self.assertEqual(services.diarias_contratadas(retirada, prevista), 1)


class ValorPrevistoTests(SimpleTestCase):
    def test_tres_diarias_de_120(self):
        resultado = services.valor_previsto(3, Decimal("120.00"))
        self.assertEqual(resultado, Decimal("360.00"))

    def test_uma_diaria(self):
        resultado = services.valor_previsto(1, Decimal("99.90"))
        self.assertEqual(resultado, Decimal("99.90"))


class DiariasDeAtrasoTests(SimpleTestCase):
    def setUp(self):
        self.prevista = datetime(2026, 10, 13, 9, 0)

    def test_dentro_da_tolerancia(self):
        real = datetime(2026, 10, 13, 9, 30)
        self.assertEqual(services.diarias_de_atraso(self.prevista, real), 0)

    def test_exatamente_60_minutos_nao_tem_atraso(self):
        real = datetime(2026, 10, 13, 10, 0)
        self.assertEqual(services.diarias_de_atraso(self.prevista, real), 0)

    def test_um_minuto_alem_da_tolerancia(self):
        real = datetime(2026, 10, 13, 10, 1)
        self.assertEqual(services.diarias_de_atraso(self.prevista, real), 1)

    def test_exemplo_do_projeto_5_horas(self):
        real = datetime(2026, 10, 13, 14, 0)
        self.assertEqual(services.diarias_de_atraso(self.prevista, real), 1)

    def test_devolveu_antes_do_prazo(self):
        real = datetime(2026, 10, 12, 9, 0)
        self.assertEqual(services.diarias_de_atraso(self.prevista, real), 0)

    def test_24h_mais_tolerancia_ainda_e_uma_diaria(self):
        real = datetime(2026, 10, 14, 10, 0)
        self.assertEqual(services.diarias_de_atraso(self.prevista, real), 1)

    def test_um_minuto_depois_vira_duas_diarias(self):
        real = datetime(2026, 10, 14, 10, 1)
        self.assertEqual(services.diarias_de_atraso(self.prevista, real), 2)

class ValorMultaTests(SimpleTestCase):
    def test_exemplo_do_projeto(self):
        resultado = services.valor_multa(1, Decimal("120.00"))
        self.assertEqual(resultado, Decimal("180.00"))

    def test_duas_diarias_de_atraso(self):
        resultado = services.valor_multa(2, Decimal("120.00"))
        self.assertEqual(resultado, Decimal("360.00"))

    def test_sem_atraso_nao_tem_multa(self):
        resultado = services.valor_multa(0, Decimal("120.00"))
        self.assertEqual(resultado, Decimal("0.00"))

    def test_arredonda_para_cima_na_metade(self):
        # 99,99 x 1,5 = 149,985 -> arredonda para 149,99
        resultado = services.valor_multa(1, Decimal("99.99"))
        self.assertEqual(resultado, Decimal("149.99"))

class TaxaCombustivelTests(SimpleTestCase):
    def test_exemplo_do_projeto(self):
        resultado = services.taxa_combustivel(4, 2, Decimal("300.00"))
        self.assertEqual(resultado, Decimal("150.00"))

    def test_voltou_igual_nao_cobra(self):
        resultado = services.taxa_combustivel(4, 4, Decimal("300.00"))
        self.assertEqual(resultado, Decimal("0.00"))

    def test_voltou_com_mais_nao_tem_credito(self):
        resultado = services.taxa_combustivel(2, 4, Decimal("300.00"))
        self.assertEqual(resultado, Decimal("0.00"))

    def test_um_quarto_a_menos(self):
        resultado = services.taxa_combustivel(4, 3, Decimal("300.00"))
        self.assertEqual(resultado, Decimal("75.00"))

    def test_arredonda_para_cima_na_metade(self):
        # 100,10 / 4 = 25,025 -> arredonda para 25,03
        resultado = services.taxa_combustivel(4, 3, Decimal("100.10"))
        self.assertEqual(resultado, Decimal("25.03"))

class ValorTotalTests(SimpleTestCase):
    def test_soma_das_tres_partes(self):
        resultado = services.valor_total(
            Decimal("360.00"), Decimal("180.00"), Decimal("150.00")
        )
        self.assertEqual(resultado, Decimal("690.00"))

    def test_sem_multa_e_sem_combustivel(self):
        resultado = services.valor_total(
            Decimal("360.00"), Decimal("0.00"), Decimal("0.00")
        )
        self.assertEqual(resultado, Decimal("360.00"))


class MultaCancelamentoTests(SimpleTestCase):
    def setUp(self):
        self.retirada = datetime(2026, 10, 13, 9, 0)
        self.valor = Decimal("360.00")

    def test_menos_de_24h_cobra_20_por_cento(self):
        agora = datetime(2026, 10, 12, 10, 0)  # faltam 23 h
        resultado = services.multa_cancelamento(self.valor, self.retirada, agora)
        self.assertEqual(resultado, Decimal("72.00"))

    def test_exatamente_24h_nao_cobra(self):
        agora = datetime(2026, 10, 12, 9, 0)  # faltam 24 h
        resultado = services.multa_cancelamento(self.valor, self.retirada, agora)
        self.assertEqual(resultado, Decimal("0.00"))

    def test_mais_de_24h_nao_cobra(self):
        agora = datetime(2026, 10, 10, 9, 0)  # faltam 72 h
        resultado = services.multa_cancelamento(self.valor, self.retirada, agora)
        self.assertEqual(resultado, Decimal("0.00"))

    def test_um_minuto_antes_de_completar_24h_cobra(self):
        agora = datetime(2026, 10, 12, 9, 1)  # faltam 23 h 59 min
        resultado = services.multa_cancelamento(self.valor, self.retirada, agora)
        self.assertEqual(resultado, Decimal("72.00"))


class ExemploNumericoTests(SimpleTestCase):
    def test_exemplo_numerico_690(self):
        diaria = Decimal("120.00")
        tanque_cheio = Decimal("300.00")
        retirada = datetime(2026, 10, 10, 9, 0)
        prevista = datetime(2026, 10, 13, 9, 0)
        real = datetime(2026, 10, 13, 14, 0)

        diarias = services.diarias_contratadas(retirada, prevista)
        previsto = services.valor_previsto(diarias, diaria)
        atraso = services.diarias_de_atraso(prevista, real)
        multa = services.valor_multa(atraso, diaria)
        combustivel = services.taxa_combustivel(4, 2, tanque_cheio)
        total = services.valor_total(previsto, multa, combustivel)

        self.assertEqual(diarias, 3)
        self.assertEqual(previsto, Decimal("360.00"))
        self.assertEqual(atraso, 1)
        self.assertEqual(multa, Decimal("180.00"))
        self.assertEqual(combustivel, Decimal("150.00"))
        self.assertEqual(total, Decimal("690.00"))