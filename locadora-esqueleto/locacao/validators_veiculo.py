"""DONO: P2 - Grupo 1 (Fundação)
TODO: validadores usados pelo modelo Veiculo.
  validar_placa(valor)    formato antigo (ABC-1234) ou Mercosul (ABC1D23)
  validar_chassi(valor)   17 caracteres, sem as letras I, O e Q
Ao falhar, levantam django.core.exceptions.ValidationError.
"""
import re

from django.core.exceptions import ValidationError

# Formato antigo (ABC1234) e Mercosul (ABC1D23)
PADRAO_PLACA = re.compile(r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$")
# Chassi (VIN): 17 caracteres, sem as letras I, O e Q
PADRAO_CHASSI = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


def validar_placa(valor):
    placa = valor.upper().replace("-", "")
    if not PADRAO_PLACA.match(placa):
        raise ValidationError("Placa inválida. Use ABC-1234 ou ABC1D23.")


def validar_chassi(valor):
    chassi = valor.upper()
    if not PADRAO_CHASSI.match(chassi):
        raise ValidationError(
            "Chassi inválido. Use 17 caracteres, sem as letras I, O e Q."
        )

