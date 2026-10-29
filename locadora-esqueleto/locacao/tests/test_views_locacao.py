"""DONO: P9 - Grupo 3 (Telas)

Testes de retirada (UC04) e devolução (UC05).
"""
from datetime import datetime
from decimal import Decimal

from django.test import SimpleTestCase
from django.utils import timezone

from locacao import operacoes_locacao


class ExtratoTests(SimpleTestCase):
    def test_exemplo_numerico_690(self):
        """Exemplo da documentação: diária R$ 120, 3 dias, 5 h de atraso e meio tanque a menos."""
        fuso = timezone.get_current_timezone()
        retirada = datetime(2026, 10, 10, 9, 0, tzinfo=fuso)
        prevista = datetime(2026, 10, 13, 9, 0, tzinfo=fuso)
        real = datetime(2026, 10, 13, 14, 0, tzinfo=fuso)

        extrato = operacoes_locacao.calcular_extrato(
            valor_diaria=Decimal("120.00"),
            valor_tanque_cheio=Decimal("300.00"),
            data_retirada=retirada,
            devolucao_prevista=prevista,
            devolucao_real=real,
            combustivel_saida="CHEIO",
            combustivel_retorno="METADE",
        )

        self.assertEqual(extrato["diarias"], 3)
        self.assertEqual(extrato["valor_previsto"], Decimal("360.00"))
        self.assertEqual(extrato["dias_de_atraso"], 1)
        self.assertEqual(extrato["valor_multa"], Decimal("180.00"))
        self.assertEqual(extrato["taxa_combustivel"], Decimal("150.00"))
        self.assertEqual(extrato["valor_total"], Decimal("690.00"))