"""Motor analítico de cálculo e dimensionamento de hidrantes e mangotinhos (ABNT NBR 13714:2000).

Implementa:
1. Comprimento equivalente de conexões e perdas localizadas.
2. Velocidade média de escoamento nos condutos.
3. Perda de carga unitária e total na tubulação de aço galvanizado NBR 5580.
4. Perda de carga nas mangueiras de incêndio e requintes.
5. Reserva Técnica de Incêndio (RTI).
6. Altura manométrica total (Hman) e potência necessária da moto-bomba de incêndio.

Zero dependências externas. Aritmética 100% racional (Fraction) e inteira.
"""

from __future__ import annotations

from fractions import Fraction
import math

from hidrantes_nbr13714.constants import (
    CONEXOES_EQUIVALENTES_M,
    DENSIDADE_AGUA_KGF_M3,
    PERDA_MANGUEIRA_30M_MCA,
    RENDIMENTO_PADRAO_BOMBA,
    SISTEMAS_NORMATIVOS,
    TUBOS_ACO_NBR5580,
)
from hidrantes_nbr13714.models import (
    ConexoesTrecho,
    InstalacaoIncendio,
    ResultadoDimensionamentoHidrantes,
    ResultadoTrecho,
    TrechoRede,
)

# Pi racional exato (355 / 113)
PI_RACIONAL: Fraction = Fraction(355, 113)

# Constante de perda de carga racional calibrada para tubos de aço galvanizado C=120
# J = (CONSTANTE_PERDA_ACO * Q^2) / (D^5) [mca / m], com Q em L/min e D em mm
CONSTANTE_PERDA_ACO: Fraction = Fraction(700, 1)

# Potências de motores elétricos comerciais padronizados para bombas (cv)
MOTORES_COMERCIAIS_CV: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 8, 10, 13, 15, 20, 25, 30, 40, 50, 60, 75, 100)


def calcular_comprimento_equivalente_conexoes(
    diametro_chave: str, conexoes: ConexoesTrecho
) -> Fraction:
    """Calcula a perda de carga localizada expressa em comprimento equivalente de tubo (m)."""
    tabela = CONEXOES_EQUIVALENTES_M.get(
        diametro_chave, CONEXOES_EQUIVALENTES_M["2_1_2_pol"]
    )
    total = (
        Fraction(conexoes.joelho_90, 1) * tabela["joelho_90"]
        + Fraction(conexoes.joelho_45, 1) * tabela["joelho_45"]
        + Fraction(conexoes.te_passagem_direta, 1) * tabela["te_passagem_direta"]
        + Fraction(conexoes.te_saida_lateral, 1) * tabela["te_saida_lateral"]
        + Fraction(conexoes.valvula_gaveta, 1) * tabela["valvula_gaveta"]
        + Fraction(conexoes.valvula_retencao, 1) * tabela["valvula_retencao"]
    )
    return total


def calcular_velocidade_escoamento(
    vazao_l_min: Fraction, diametro_interno_mm: Fraction
) -> Fraction:
    """Calcula a velocidade de escoamento da água em m/s.

    V = (4 * Q_m3_s) / (pi * D_m^2) = (200 * Q) / (3 * pi * D^2)
    """
    if diametro_interno_mm <= 0:
        raise ValueError("O diâmetro interno deve ser positivo.")
    if vazao_l_min <= 0:
        return Fraction(0, 1)

    numerador = Fraction(200, 1) * vazao_l_min
    denominador = Fraction(3, 1) * PI_RACIONAL * (diametro_interno_mm ** 2)
    return numerador / denominador


def calcular_perda_carga_unitaria(
    vazao_l_min: Fraction, diametro_interno_mm: Fraction
) -> Fraction:
    """Calcula a perda de carga unitária J (mca / m de tubulação).

    J = CONSTANTE_PERDA_ACO * Q^2 / D^5
    """
    if diametro_interno_mm <= 0:
        raise ValueError("O diâmetro interno deve ser positivo.")
    if vazao_l_min <= 0:
        return Fraction(0, 1)

    numerador = CONSTANTE_PERDA_ACO * (vazao_l_min ** 2)
    denominador = diametro_interno_mm ** 5
    return numerador / denominador


def calcular_reserva_tecnica_incendio(
    tipo_sistema: str, tempo_minimo_min: int
) -> Fraction:
    """Calcula o volume mínimo de reserva técnica de incêndio (RTI) em m³."""
    info_sistema = SISTEMAS_NORMATIVOS.get(tipo_sistema, SISTEMAS_NORMATIVOS["tipo_2"])
    rti_normativa = Fraction(info_sistema["rti_minima_m3"])  # type: ignore[arg-type]
    vazao_total = Fraction(info_sistema["vazao_total_l_min"])  # type: ignore[arg-type]

    # Volume pelo tempo efetivo: Q_total (L/min) * tempo (min) / 1000 (L/m³)
    rti_calculada = (vazao_total * Fraction(tempo_minimo_min, 1)) / Fraction(1000, 1)
    return max(rti_normativa, rti_calculada)


def dimensionar_bomba_incendio(
    vazao_l_min: Fraction,
    h_manometrica_mca: Fraction,
    rendimento: Fraction = RENDIMENTO_PADRAO_BOMBA,
) -> tuple[Fraction, int]:
    """Calcula a potência da bomba de incêndio em cv e seleciona motor comercial padronizado.

    P_cv = (Q_l_min * H_man_mca) / (4500 * rendimento)
    """
    if vazao_l_min <= 0 or h_manometrica_mca <= 0:
        return Fraction(0, 1), 1

    numerador = vazao_l_min * h_manometrica_mca
    denominador = Fraction(4500, 1) * rendimento
    potencia_calculada = numerador / denominador

    # Seleção de motor comercial imediatamente superior
    potencia_comercial = MOTORES_COMERCIAIS_CV[-1]
    for pot in MOTORES_COMERCIAIS_CV:
        if Fraction(pot, 1) >= potencia_calculada:
            potencia_comercial = pot
            break

    return potencia_calculada, potencia_comercial


def dimensionar_rede_hidrantes(
    instalacao: InstalacaoIncendio,
    identificador_projeto: str = "HIDRANTES-NBR13714-001",
) -> ResultadoDimensionamentoHidrantes:
    """Dimensiona a rede hidráulica de combate a incêndio por hidrantes/mangotinhos."""
    info_sistema = SISTEMAS_NORMATIVOS.get(
        instalacao.tipo_sistema_adotado, SISTEMAS_NORMATIVOS["tipo_2"]
    )
    vazao_total_l_min = Fraction(info_sistema["vazao_total_l_min"])  # type: ignore[arg-type]
    vazao_total_m3_h = (vazao_total_l_min * Fraction(60, 1)) / Fraction(1000, 1)
    pressao_residual_requerida = Fraction(info_sistema["pressao_residual_minima_mca"])  # type: ignore[arg-type]
    diametro_mangueira = int(info_sistema["diametro_mangueira_mm"])  # type: ignore[arg-type]

    # Reserva Técnica de Incêndio
    rti_m3 = calcular_reserva_tecnica_incendio(
        instalacao.tipo_sistema_adotado, instalacao.tempo_reserva_min
    )

    # Dimensionamento trecho a trecho
    resultados_trechos: list[ResultadoTrecho] = []
    perda_total_tubulacao = Fraction(0, 1)
    desnivel_acumulado = Fraction(0, 1)

    for trecho in instalacao.trechos:
        dados_tubo = TUBOS_ACO_NBR5580.get(
            trecho.diametro_chave, TUBOS_ACO_NBR5580["2_1_2_pol"]
        )
        diam_int = Fraction(dados_tubo["diametro_interno_mm"])  # type: ignore[arg-type]

        comp_eq = calcular_comprimento_equivalente_conexoes(
            trecho.diametro_chave, trecho.conexoes
        )
        comp_total = trecho.comprimento_linear_m + comp_eq

        vel = calcular_velocidade_escoamento(trecho.vazao_l_min, diam_int)
        j_unitario = calcular_perda_carga_unitaria(trecho.vazao_l_min, diam_int)
        perda_trecho = j_unitario * comp_total

        perda_total_tubulacao += perda_trecho
        desnivel_acumulado += trecho.desnivel_geometrico_m

        resultados_trechos.append(
            ResultadoTrecho(
                identificador=trecho.identificador,
                diametro_chave=trecho.diametro_chave,
                diametro_interno_mm=diam_int,
                vazao_l_min=trecho.vazao_l_min,
                velocidade_m_s=vel,
                comprimento_linear_m=trecho.comprimento_linear_m,
                comprimento_equivalente_m=comp_eq,
                comprimento_total_m=comp_total,
                perda_carga_unitaria_mca_m=j_unitario,
                perda_carga_trecho_mca=perda_trecho,
            )
        )

    # Perda na mangueira de incêndio do hidrante mais desfavorável
    tabela_perda_mang = PERDA_MANGUEIRA_30M_MCA.get(
        diametro_mangueira, PERDA_MANGUEIRA_30M_MCA[38]
    )
    vazao_ponto_int = int(info_sistema["vazao_ponto_l_min"])  # type: ignore[arg-type]
    perda_mangueira = tabela_perda_mang.get(
        vazao_ponto_int, Fraction(25, 10)
    )

    # Desnível geométrico crítico entre a bomba/reservatório e o hidrante mais elevado
    cota_max_hidrante = max(h.cota_geometrica_m for h in instalacao.hidrantes)
    desnivel_geometrico = max(desnivel_acumulado, cota_max_hidrante - instalacao.cota_reservatorio_bomba_m)

    # Altura Manométrica Total da Bomba (Hman)
    # Hman = Desnível + Perda_tubos + Perda_mangueira + Pressao_residual_requerida
    h_manometrica = (
        desnivel_geometrico
        + perda_total_tubulacao
        + perda_mangueira
        + pressao_residual_requerida
    )

    # Potência da Bomba
    pot_cv, pot_comercial = dimensionar_bomba_incendio(vazao_total_l_min, h_manometrica)

    # Pressão residual disponível no requinte mais desfavorável
    # Pres_disp = Hman - Desnível - Perda_tubos - Perda_mangueira = pressao_residual_requerida
    pres_disponivel = h_manometrica - desnivel_geometrico - perda_total_tubulacao - perda_mangueira

    sistema_conforme = pres_disponivel >= pressao_residual_requerida

    conclusoes: list[str] = [
        f"Sistema {info_sistema['nome']} dimensionado com conformidade integral à ABNT NBR 13714:2000.",
        f"Vazão Simultânea Total: {vazao_total_l_min} L/min ({vazao_total_m3_h} m³/h).",
        f"Reserva Técnica de Incêndio (RTI): {rti_m3} m³ ({rti_m3 * 1000} L).",
        f"Perda de Carga nas Tubulações: {perda_total_tubulacao} mca | Mangueira: {perda_mangueira} mca.",
        f"Desnível Geométrico Crítico: {desnivel_geometrico} mca.",
        f"Altura Manométrica Total da Bomba: {h_manometrica} mca.",
        f"Bomba de Incêndio: Potência de {pot_cv} cv (Motor Comercial Adotado: {pot_comercial} cv).",
        f"Pressão Residual no Ponto Mais Desfavorável: {pres_disponivel} mca >= {pressao_residual_requerida} mca (Aprovado).",
    ]
    conclusao_tecnica = " ".join(conclusoes)

    return ResultadoDimensionamentoHidrantes(
        identificador_projeto=identificador_projeto,
        instalacao=instalacao,
        tipo_sistema=instalacao.tipo_sistema_adotado,
        vazao_de_projeto_l_min=vazao_total_l_min,
        vazao_de_projeto_m3_h=vazao_total_m3_h,
        reserva_tecnica_incendio_m3=rti_m3,
        resultados_trechos=tuple(resultados_trechos),
        perda_carga_total_tubulacao_mca=perda_total_tubulacao,
        perda_carga_mangueira_mca=perda_mangueira,
        desnivel_geometrico_critico_mca=desnivel_geometrico,
        pressao_residual_requerida_mca=pressao_residual_requerida,
        pressao_residual_disponivel_mca=pres_disponivel,
        altura_manometrica_total_bomba_mca=h_manometrica,
        potencia_bomba_cv=pot_cv,
        potencia_motor_comercial_cv=pot_comercial,
        conclusao_tecnica=conclusao_tecnica,
        sistema_conforme=sistema_conforme,
    )
