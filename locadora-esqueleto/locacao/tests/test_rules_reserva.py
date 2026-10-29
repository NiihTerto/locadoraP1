"""DONO: P5 - Grupo 2 (Domínio)
TODO: para cada regra, um teste que passa e um que falha. Casos de borda: exatamente
21 anos, exatamente 24 h antes, exatamente 4 h depois.
"""
from django.test import SimpleTestCase

from locacao.excecoes import RegraNegocioError

from datetime import datetime, timedelta, timezone, date

from locacao import rules  # noqa: F401


class RegrasReservaTests(SimpleTestCase):

## RN01 - Idade mínima
    def test_rn01_19_anos_levanta_erro(self):
         nascimento = date(2007, 10, 7)
         retirada = date(2026, 10, 7)
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_idade(nascimento, retirada)
         self.assertEqual(ctx.exception.codigo, "RN01")

    def test_rn01_1_dia_antes_21_anos_levanta_erro(self):
         nascimento = date(2005, 10, 7)
         retirada = date(2026, 10, 6)
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_idade(nascimento, retirada)
         self.assertEqual(ctx.exception.codigo, "RN01")

    def test_rn01_exatamente_21_anos_nao_levanta_erro(self):
         nascimento = date(2005, 10, 7)
         retirada = date(2026, 10, 7)
         rules.validar_idade(nascimento, retirada)

    def test_rn01_1_dia_depois_21_anos_nao_levanta_erro(self):
         nascimento = date(2005, 10, 7)
         retirada = date(2026, 10, 8)
         rules.validar_idade(nascimento, retirada)

    def test_rn01_26_anos_nao_levanta_erro(self):
         nascimento = date(2000, 10, 7)
         retirada = date(2026, 10, 7)
         rules.validar_idade(nascimento, retirada)




## RN02 - Validar cnh

    def test_rn02_categoria_recusada(self):  
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_cnh(categoria="A",devolucao_prevista = date(2026, 10, 20),validade = date(2026, 10, 21))
         self.assertEqual(ctx.exception.codigo, "RN02")

    def test_rn02_categoria_minima_aceita(self):
         rules.validar_cnh(categoria="B", devolucao_prevista= date(2026, 10, 20),validade = date(2026, 10, 21))

    def test_rn02_categoria_superior_aceita(self):
         rules.validar_cnh(categoria="E", devolucao_prevista= date(2026, 10, 20),validade = date(2026, 10, 21))

    def test_rn02_validade_no_dia_exato_aceita(self):
         rules.validar_cnh(categoria="E", devolucao_prevista=date(2026, 10, 20),validade=date(2026,10,20))

    def test_rn02_validade_um_dia_antes_recusada(self):
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_cnh(categoria="E",devolucao_prevista=date(2026, 10, 20),validade=date(2026, 10, 19))
         self.assertEqual(ctx.exception.codigo, "RN02")

         


## RN03 - Validar cliente ativo ou inativo

    def test_rn03_cliente_inativo_levanta_erro(self):
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_cliente_ativo(ativo=False)
         self.assertEqual(ctx.exception.codigo, "RN03")

    def test_rn03_cliente_ativo_passa(self):
         rules.validar_cliente_ativo(ativo=True)




## RN04 - Validar cliente com atraso e sem atraso

    def test_rn04_cliente_com_atraso_levanta_erro(self):
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_sem_atraso(tem_locacao_atrasada=True)
         self.assertEqual(ctx.exception.codigo, "RN04")

    def test_rn04_cliente_sem_atraso_passa(self):
         rules.validar_sem_atraso(tem_locacao_atrasada=False)




## RN08, RN09 e RN10 - Validar periodo

   # Teste da ordem - RN10, RN09 e RN08
    def test_ordem_rn10_rn09_rn08(self):
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada + timedelta(minutes=30)
         agora = retirada + timedelta(hours=1)
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)
         self.assertEqual(ctx.exception.codigo, "RN09")
         


   # RN08 
    def test_rn8_1min_depois_da_retirada_da_erro(self):
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada + timedelta(minutes=1)
         agora = datetime(2026, 10, 20, 7, tzinfo=timezone.utc)  
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)
         self.assertEqual(ctx.exception.codigo, "RN08")

    def test_rn8_devolucao_1min_abaixo_do_minimo_da_erro(self):
         agora = datetime(2026, 10, 20, 7, tzinfo=timezone.utc)
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada+timedelta(hours=23, minutes=59)
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)
         self.assertEqual(ctx.exception.codigo, "RN08")

    def test_rn8_devolucao_apos_15_dias_passa(self):
         agora = datetime(2026, 10, 20, 7, tzinfo=timezone.utc)
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada+timedelta(days=15)
         rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)

    def test_rn8_devolucao_exatamente_30_dias_passa(self):
         agora = datetime(2026, 10, 20, 7, tzinfo=timezone.utc)
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada+timedelta(days=30)
         rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)

    def test_rn8_devolucao_1min_apos_30_dias_da_erro(self):
         agora = datetime(2026, 10, 20, 7, tzinfo=timezone.utc)
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada+timedelta(days=30, minutes=1)
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)
         self.assertEqual(ctx.exception.codigo, "RN08")
         
         
         


   # RN09 
    def test_rn9_retirada_1min_antes_de_agora_da_erro(self):
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada + timedelta(days=2)
         agora = retirada + timedelta(minutes=1)
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)
         self.assertEqual(ctx.exception.codigo, "RN09")

    def test_rn9_retirada_1min_depois_de_agora_passa(self):
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada + timedelta(days=2)
         agora = retirada - timedelta(minutes=1)
         rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)

    def test_rn9_retirada_igual_ao_agora_passa(self):
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada + timedelta(days=2)
         agora = retirada
         rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)


   # RN10 
    def test_rn10_exatamente_24h_depois_passa(self):
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = datetime(2026, 10, 20, 8, tzinfo=timezone.utc) + timedelta(days=1)
         agora = datetime(2026, 10, 20, 7, tzinfo=timezone.utc)
         rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)

    def test_rn10_1min_antes_da_retirada_da_erro(self):
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada - timedelta(minutes=1)
         agora = datetime(2026, 10, 20, 7, tzinfo=timezone.utc)  
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)
         self.assertEqual(ctx.exception.codigo, "RN10")

    def test_rn10_momento_exato_da_retirada_da_erro(self):
         retirada = datetime(2026, 10, 20, 8, tzinfo=timezone.utc)
         devolucao = retirada 
         agora = datetime(2026, 10, 20, 7, tzinfo=timezone.utc)  
         with self.assertRaises(RegraNegocioError) as ctx:
              rules.validar_periodo(retirada=retirada, devolucao=devolucao, agora=agora)
         self.assertEqual(ctx.exception.codigo, "RN10")





         
         




## RN11 - Cancelamento_com_multa
    def test_rn11_21h_antes_tem_multa(self):
        retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
        agora = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
        self.assertTrue(rules.cancelamento_com_multa(retirada, agora))

    def test_rn11_1h_depois_tem_multa(self):
         retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
         agora = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
         self.assertTrue(rules.cancelamento_com_multa(retirada, agora))

    def test_rn11_1h_antes_tem_multa(self):
         retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
         agora = datetime(2026, 10, 20, 8, 0, tzinfo=timezone.utc)
         self.assertTrue(rules.cancelamento_com_multa(retirada, agora))


#RN11 - Cancelamento_com_ou_sem_multa - casos de borda
    def test_rn11_23h59_antes_tem_multa(self):
        retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
        agora = datetime(2026, 10, 19, 9, 1, tzinfo=timezone.utc)
        self.assertTrue(rules.cancelamento_com_multa(retirada, agora))

    def test_rn11_24h_antes_nao_tem_multa(self):
            retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
            agora = datetime(2026, 10, 19, 9, 0, tzinfo=timezone.utc)
            self.assertFalse(rules.cancelamento_com_multa(retirada, agora))

    def test_rn11_24h01_antes_nao_tem_multa(self):
            retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
            agora = datetime(2026, 10, 19, 8, 59, tzinfo=timezone.utc)
            self.assertFalse(rules.cancelamento_com_multa(retirada, agora))


#RN11 - Cancelamento_sem_multa
    def test_rn11_3_dias_antes_nao_tem_multa(self):
        retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
        agora = datetime(2026, 10, 17, 9, 0, tzinfo=timezone.utc)
        self.assertFalse(rules.cancelamento_com_multa(retirada, agora))




#RN12 - Reservas expiradas
    def test_rn12_1h_antes_nao_expirou(self):
        retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
        agora = retirada - timedelta(hours=1)
        self.assertFalse(rules.reserva_expirada(retirada, agora))

    def test_rn12_1h_depois_nao_expirou(self):
        retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
        agora = retirada + timedelta(hours=1)
        self.assertFalse(rules.reserva_expirada(retirada, agora))

    def test_rn12_exatamente_na_hora_nao_expirou(self):
        retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
        agora = retirada
        self.assertFalse(rules.reserva_expirada(retirada, agora))

    def test_rn12_exatamente_4h_depois_nao_expirou(self):
        retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
        agora = retirada + timedelta(hours=4)
        self.assertFalse(rules.reserva_expirada(retirada, agora))

    def test_rn12_4h01_depois_expirou(self):
        retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
        agora = retirada + timedelta(hours=4, minutes=1)
        self.assertTrue(rules.reserva_expirada(retirada, agora))

    def test_rn12_1_dia_depois_expirou(self):
        retirada = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
        agora = retirada + timedelta(days=1)
        self.assertTrue(rules.reserva_expirada(retirada, agora))