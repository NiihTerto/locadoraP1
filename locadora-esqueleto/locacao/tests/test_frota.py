from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from locacao.models_frota import Categoria, Veiculo
from locacao.validators_veiculo import validar_chassi, validar_placa


class ValidarPlacaTest(SimpleTestCase):
    def test_placa_antiga_valida(self):
        validar_placa("ABC1234")

    def test_placa_mercosul_valida(self):
        validar_placa("ABC1D23")

    def test_placa_com_hifen_valida(self):
        validar_placa("ABC-1234")

    def test_placa_minuscula_valida(self):
        validar_placa("abc1d23")

    def test_placa_invalida_levanta_erro(self):
        with self.assertRaises(ValidationError):
            validar_placa("123ABCD")

    def test_placa_curta_levanta_erro(self):
        with self.assertRaises(ValidationError):
            validar_placa("AB12")


class ValidarChassiTest(SimpleTestCase):
    def test_chassi_valido(self):
        validar_chassi("9BWZZZ377VT004251")

    def test_chassi_com_16_caracteres_levanta_erro(self):
        with self.assertRaises(ValidationError):
            validar_chassi("9BWZZZ377VT00425")

    def test_chassi_com_letra_proibida_levanta_erro(self):
        with self.assertRaises(ValidationError):
            validar_chassi("9BWZZZ377VT00425O")  # letra O, não zero


class UnicidadeTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Teste",
            valor_diaria="100.00",
            valor_caucao="500.00",
            valor_tanque_cheio="300.00",
        )
        Veiculo.objects.create(
            placa="ABC1D23",
            chassi="9BWZZZ377VT004251",
            marca="Fiat",
            modelo="Mobi",
            ano_fabricacao=2023,
            cor="Branco",
            categoria=self.categoria,
        )

    def test_placa_repetida_e_recusada(self):
        outro = Veiculo(
            placa="ABC1D23",
            chassi="9BWZZZ377VT004999",
            marca="Fiat",
            modelo="Argo",
            ano_fabricacao=2023,
            cor="Preto",
            categoria=self.categoria,
        )
        with self.assertRaises(ValidationError):
            outro.full_clean()

    def test_chassi_repetido_e_recusado(self):
        outro = Veiculo(
            placa="DEF4G56",
            chassi="9BWZZZ377VT004251",
            marca="Fiat",
            modelo="Argo",
            ano_fabricacao=2023,
            cor="Preto",
            categoria=self.categoria,
        )
        with self.assertRaises(ValidationError):
            outro.full_clean()
            
