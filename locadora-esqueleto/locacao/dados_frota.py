"""DONO: P2 - Grupo 1 (Fundação)
TODO: dados de exemplo da frota, usados pelo comando seed (do P3).
  criar_categorias()  -> Econômico (diária 120, caução 500, tanque 300), Intermediário, SUV, Executivo
  criar_veiculos()    -> 10 veículos distribuídos nas categorias
"""


from .models_frota import Categoria, Veiculo

# (nome, valor_diaria, valor_caucao, valor_tanque_cheio)
CATEGORIAS = [
    ("Econômico", "120.00", "500.00", "300.00"),
    ("Intermediário", "160.00", "600.00", "350.00"),
    ("SUV", "250.00", "800.00", "400.00"),
    ("Executivo", "400.00", "1200.00", "450.00"),
]

# (placa, chassi, marca, modelo, ano, cor, km, categoria)
VEICULOS = [
    ("FGH1A23", "9BWZZZ377VT004251", "Fiat", "Mobi", 2023, "Branco", 12000, "Econômico"),
    ("FGH2B34", "9BWZZZ377VT004252", "Chevrolet", "Onix", 2023, "Prata", 18000, "Econômico"),
    ("JKL3C45", "9BWZZZ377VT004253", "Renault", "Kwid", 2022, "Vermelho", 25000, "Econômico"),
    ("JKL4D56", "9BWZZZ377VT004254", "Volkswagen", "Polo", 2023, "Preto", 9000, "Intermediário"),
    ("MNP5E67", "9BWZZZ377VT004255", "Hyundai", "HB20", 2024, "Cinza", 5000, "Intermediário"),
    ("MNP6F78", "9BWZZZ377VT004256", "Jeep", "Renegade", 2023, "Branco", 15000, "SUV"),
    ("RST7G89", "9BWZZZ377VT004257", "Volkswagen", "T-Cross", 2024, "Azul", 7000, "SUV"),
    ("RST8H90", "9BWZZZ377VT004258", "Hyundai", "Creta", 2022, "Prata", 30000, "SUV"),
    ("UVW9I12", "9BWZZZ377VT004259", "Toyota", "Corolla", 2024, "Preto", 4000, "Executivo"),
    ("UVW0J23", "9BWZZZ377VT004260", "Honda", "Civic", 2023, "Cinza", 11000, "Executivo"),
]


def criar_categorias():
    for nome, diaria, caucao, tanque in CATEGORIAS:
        Categoria.objects.get_or_create(
            nome=nome,
            defaults={
                "valor_diaria": diaria,
                "valor_caucao": caucao,
                "valor_tanque_cheio": tanque,
            },
        )


def criar_veiculos():
    criar_categorias()
    for placa, chassi, marca, modelo, ano, cor, km, nome_categoria in VEICULOS:
        Veiculo.objects.get_or_create(
            placa=placa,
            defaults={
                "chassi": chassi,
                "marca": marca,
                "modelo": modelo,
                "ano_fabricacao": ano,
                "cor": cor,
                "km_atual": km,
                "categoria": Categoria.objects.get(nome=nome_categoria),
            },
        )
