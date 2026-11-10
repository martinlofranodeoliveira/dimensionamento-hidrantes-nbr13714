"""Constantes e parâmetros normativos da ABNT NBR 13714:2000.

Define tipos de sistemas de combate a incêndio (mangotinhos e hidrantes),
vazões mínimas, pressões residuais, reservas técnicas de incêndio (RTI),
tubulações normatizadas de aço NBR 5580 e comprimentos equivalentes de conexões.
Todos os cálculos utilizam estritamente aritmética racional exata (Fraction).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Final

# Densidade da água e aceleração da gravidade
DENSIDADE_AGUA_KGF_M3: Final[int] = 1000  # kgf / m³
RENDIMENTO_PADRAO_BOMBA: Final[Fraction] = Fraction(65, 100)  # 65%

# Tabela 2 e 3 da ABNT NBR 13714:2000 - Tipos de Sistemas
SISTEMAS_NORMATIVOS: Final[dict[str, dict[str, Fraction | int | str]]] = {
    "tipo_1": {
        "codigo": "tipo_1",
        "nome": "Tipo 1 - Sistema de Mangotinho (DN 25 - 1 pol)",
        "vazao_ponto_l_min": Fraction(100, 1),        # 100 L/min por ponto
        "pontos_simultaneos": 2,                      # 2 pontos mais desfavoráveis
        "vazao_total_l_min": Fraction(200, 1),        # 200 L/min total
        "pressao_residual_minima_mca": Fraction(8, 1),# 8 mca
        "tempo_minimo_rti_min": 30,                   # 30 minutos
        "rti_minima_m3": Fraction(6, 1),              # 6 m³
        "diametro_mangueira_mm": 25,
        "comprimento_mangueira_m": 30,
        "requinte_esguicho_mm": 25,
    },
    "tipo_2": {
        "codigo": "tipo_2",
        "nome": "Tipo 2 - Sistema de Hidrante (DN 40 - 1 1/2 pol)",
        "vazao_ponto_l_min": Fraction(130, 1),        # 130 L/min
        "pontos_simultaneos": 2,
        "vazao_total_l_min": Fraction(260, 1),        # 260 L/min
        "pressao_residual_minima_mca": Fraction(10, 1), # 10 mca
        "tempo_minimo_rti_min": 30,
        "rti_minima_m3": Fraction(8, 1),              # 8 m³
        "diametro_mangueira_mm": 38,
        "comprimento_mangueira_m": 30,
        "requinte_esguicho_mm": 13,
    },
    "tipo_3": {
        "codigo": "tipo_3",
        "nome": "Tipo 3 - Sistema de Hidrante Comercial / Industrial Leve",
        "vazao_ponto_l_min": Fraction(200, 1),        # 200 L/min
        "pontos_simultaneos": 2,
        "vazao_total_l_min": Fraction(400, 1),        # 400 L/min
        "pressao_residual_minima_mca": Fraction(15, 1), # 15 mca
        "tempo_minimo_rti_min": 60,
        "rti_minima_m3": Fraction(15, 1),             # 15 m³
        "diametro_mangueira_mm": 38,
        "comprimento_mangueira_m": 30,
        "requinte_esguicho_mm": 16,
    },
    "tipo_4": {
        "codigo": "tipo_4",
        "nome": "Tipo 4 - Sistema de Hidrante Industrial (DN 65 - 2 1/2 pol)",
        "vazao_ponto_l_min": Fraction(300, 1),        # 300 L/min
        "pontos_simultaneos": 2,
        "vazao_total_l_min": Fraction(600, 1),        # 600 L/min
        "pressao_residual_minima_mca": Fraction(20, 1), # 20 mca
        "tempo_minimo_rti_min": 60,
        "rti_minima_m3": Fraction(25, 1),             # 25 m³
        "diametro_mangueira_mm": 65,
        "comprimento_mangueira_m": 30,
        "requinte_esguicho_mm": 19,
    },
    "tipo_5": {
        "codigo": "tipo_5",
        "nome": "Tipo 5 - Sistema de Alto Risco / Depósito",
        "vazao_ponto_l_min": Fraction(750, 1),        # 750 L/min
        "pontos_simultaneos": 2,
        "vazao_total_l_min": Fraction(1500, 1),       # 1500 L/min
        "pressao_residual_minima_mca": Fraction(30, 1), # 30 mca
        "tempo_minimo_rti_min": 60,
        "rti_minima_m3": Fraction(45, 1),             # 45 m³
        "diametro_mangueira_mm": 65,
        "comprimento_mangueira_m": 30,
        "requinte_esguicho_mm": 25,
    },
}

# Tubos de Aço Carbono Galvanizado ABNT NBR 5580 (Classe Média)
# Diâmetros nominais em polegadas e diâmetros internos reais em milímetros
TUBOS_ACO_NBR5580: Final[dict[str, dict[str, str | int | Fraction]]] = {
    "1_pol": {
        "dn_pol": "1 pol",
        "dn_mm": 25,
        "diametro_interno_mm": Fraction(273, 10),      # 27,3 mm
        "espessura_parede_mm": Fraction(325, 100),     # 3,25 mm
        "rugosidade_c": 120,
    },
    "1_1_4_pol": {
        "dn_pol": "1 1/4 pol",
        "dn_mm": 32,
        "diametro_interno_mm": Fraction(360, 10),      # 36,0 mm
        "espessura_parede_mm": Fraction(325, 100),
        "rugosidade_c": 120,
    },
    "1_1_2_pol": {
        "dn_pol": "1 1/2 pol",
        "dn_mm": 40,
        "diametro_interno_mm": Fraction(419, 10),      # 41,9 mm
        "espessura_parede_mm": Fraction(325, 100),
        "rugosidade_c": 120,
    },
    "2_pol": {
        "dn_pol": "2 pol",
        "dn_mm": 50,
        "diametro_interno_mm": Fraction(530, 10),      # 53,0 mm
        "espessura_parede_mm": Fraction(365, 100),     # 3,65 mm
        "rugosidade_c": 120,
    },
    "2_1_2_pol": {
        "dn_pol": "2 1/2 pol",
        "dn_mm": 65,
        "diametro_interno_mm": Fraction(687, 10),      # 68,7 mm
        "espessura_parede_mm": Fraction(365, 100),
        "rugosidade_c": 120,
    },
    "3_pol": {
        "dn_pol": "3 pol",
        "dn_mm": 80,
        "diametro_interno_mm": Fraction(809, 10),      # 80,9 mm
        "espessura_parede_mm": Fraction(400, 100),     # 4,00 mm
        "rugosidade_c": 120,
    },
    "4_pol": {
        "dn_pol": "4 pol",
        "dn_mm": 100,
        "diametro_interno_mm": Fraction(1053, 10),     # 105,3 mm
        "espessura_parede_mm": Fraction(450, 100),     # 4,50 mm
        "rugosidade_c": 120,
    },
}

# Comprimentos equivalentes de conexões em metros (Tabela B.1 da NBR 13714)
# Mapeado por diâmetro nominal: joelho 90, joelho 45, tê passagem direta, tê saída lateral, válvula gaveta aberta, válvula retenção
CONEXOES_EQUIVALENTES_M: Final[dict[str, dict[str, Fraction]]] = {
    "1_1_2_pol": {
        "joelho_90": Fraction(15, 10),        # 1,5 m
        "joelho_45": Fraction(7, 10),         # 0,7 m
        "te_passagem_direta": Fraction(8, 10),# 0,8 m
        "te_saida_lateral": Fraction(32, 10), # 3,2 m
        "valvula_gaveta": Fraction(3, 10),    # 0,3 m
        "valvula_retencao": Fraction(40, 10), # 4,0 m
    },
    "2_pol": {
        "joelho_90": Fraction(20, 10),        # 2,0 m
        "joelho_45": Fraction(10, 10),        # 1,0 m
        "te_passagem_direta": Fraction(10, 10),# 1,0 m
        "te_saida_lateral": Fraction(41, 10), # 4,1 m
        "valvula_gaveta": Fraction(4, 10),    # 0,4 m
        "valvula_retencao": Fraction(52, 10), # 5,2 m
    },
    "2_1_2_pol": {
        "joelho_90": Fraction(25, 10),        # 2,5 m
        "joelho_45": Fraction(13, 10),        # 1,3 m
        "te_passagem_direta": Fraction(14, 10),# 1,4 m
        "te_saida_lateral": Fraction(52, 10), # 5,2 m
        "valvula_gaveta": Fraction(5, 10),    # 0,5 m
        "valvula_retencao": Fraction(65, 10), # 6,5 m
    },
    "3_pol": {
        "joelho_90": Fraction(31, 10),        # 3,1 m
        "joelho_45": Fraction(17, 10),        # 1,7 m
        "te_passagem_direta": Fraction(17, 10),# 1,7 m
        "te_saida_lateral": Fraction(66, 10), # 6,6 m
        "valvula_gaveta": Fraction(7, 10),    # 0,7 m
        "valvula_retencao": Fraction(79, 10), # 7,9 m
    },
    "4_pol": {
        "joelho_90": Fraction(40, 10),        # 4,0 m
        "joelho_45": Fraction(21, 10),        # 2,1 m
        "te_passagem_direta": Fraction(23, 10),# 2,3 m
        "te_saida_lateral": Fraction(87, 10), # 8,7 m
        "valvula_gaveta": Fraction(9, 10),    # 0,9 m
        "valvula_retencao": Fraction(104, 10),# 10,4 m
    },
}

# Perda de carga em mangueiras de incêndio padrão (30m de comprimento)
# Valores médios normativos de perda mca em função da vazão e diâmetro da mangueira
PERDA_MANGUEIRA_30M_MCA: Final[dict[int, dict[int, Fraction]]] = {
    # Diâmetro 38 mm
    38: {
        130: Fraction(22, 10),  # 2,2 mca para 130 L/min
        200: Fraction(52, 10),  # 5,2 mca para 200 L/min
        260: Fraction(86, 10),  # 8,6 mca para 260 L/min
    },
    # Diâmetro 65 mm
    65: {
        300: Fraction(15, 10),  # 1,5 mca para 300 L/min
        600: Fraction(55, 10),  # 5,5 mca para 600 L/min
        750: Fraction(85, 10),  # 8,5 mca para 750 L/min
    },
    # Mangotinho 25 mm
    25: {
        100: Fraction(45, 10),  # 4,5 mca para 100 L/min
    },
}
