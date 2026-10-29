from django.core.exceptions import ValidationError


def so_numeros(texto):
    """'529.982.247-25' vira '52998224725'."""
    return "".join(c for c in (texto or "") if c.isdigit())


def calcular_digito(numeros):
    """Calcula um dígito do CPF.

    Multiplica cada número por um peso que começa em (quantidade + 1) e vai
    diminuindo de 1 em 1. Soma tudo e usa o resto da divisão por 11.
    """
    peso = len(numeros) + 1
    soma = 0
    for n in numeros:
        soma += int(n) * peso
        peso -= 1

    resto = soma % 11
    if resto < 2:
        return "0"
    return str(11 - resto)


def cpf_valido(cpf):
    cpf = so_numeros(cpf)

    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:  # ex.: 11111111111
        return False

    digito1 = calcular_digito(cpf[:9])
    digito2 = calcular_digito(cpf[:9] + digito1)
    return cpf[9:] == digito1 + digito2


def validar_cpf(cpf):
    """Usado no campo do modelo: dá erro se o CPF for inválido."""
    if not cpf_valido(cpf):
        raise ValidationError("CPF inválido.")