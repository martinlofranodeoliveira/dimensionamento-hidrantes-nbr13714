"""Motor analítico e CLI para dimensionamento de hidrantes segundo a ABNT NBR 13714:2000.

Padrão de Engenharia LOFRANO TECNOLOGIA:
- Zero dependências de terceiros (100% biblioteca padrão do Python 3.11+).
- Aritmética racional exata com Fraction e grandezas inteiras (zero ponto flutuante).
- Cálculo rigoroso de perda de carga, RTI, altura manométrica e moto-bomba de incêndio.
"""

from __future__ import annotations

from hidrantes_nbr13714.calculator import (
    calcular_comprimento_equivalente_conexoes,
    calcular_perda_carga_unitaria,
    calcular_reserva_tecnica_incendio,
    calcular_velocidade_escoamento,
    dimensionar_bomba_incendio,
    dimensionar_rede_hidrantes,
)
from hidrantes_nbr13714.codecs import (
    carregar_entrada_json,
    exportar_resultado_json,
    fracao_para_dict,
    parsear_fracao_segura,
)
from hidrantes_nbr13714.constants import (
    CONEXOES_EQUIVALENTES_M,
    DENSIDADE_AGUA_KGF_M3,
    PERDA_MANGUEIRA_30M_MCA,
    RENDIMENTO_PADRAO_BOMBA,
    SISTEMAS_NORMATIVOS,
    TUBOS_ACO_NBR5580,
)
from hidrantes_nbr13714.exporters import (
    gerar_csv_sanitizado,
    gerar_pacote_zip_deterministico,
    gerar_relatorio_texto,
    sanitizar_campo_csv,
)
from hidrantes_nbr13714.models import (
    ConexoesTrecho,
    Hidrante,
    InstalacaoIncendio,
    ResultadoDimensionamentoHidrantes,
    ResultadoTrecho,
    TrechoRede,
)
from hidrantes_nbr13714.svg_generator import gerar_painel_svg

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "CONEXOES_EQUIVALENTES_M",
    "ConexoesTrecho",
    "DENSIDADE_AGUA_KGF_M3",
    "Hidrante",
    "InstalacaoIncendio",
    "PERDA_MANGUEIRA_30M_MCA",
    "RENDIMENTO_PADRAO_BOMBA",
    "ResultadoDimensionamentoHidrantes",
    "ResultadoTrecho",
    "SISTEMAS_NORMATIVOS",
    "TUBOS_ACO_NBR5580",
    "TrechoRede",
    "calcular_comprimento_equivalente_conexoes",
    "calcular_perda_carga_unitaria",
    "calcular_reserva_tecnica_incendio",
    "calcular_velocidade_escoamento",
    "carregar_entrada_json",
    "dimensionar_bomba_incendio",
    "dimensionar_rede_hidrantes",
    "exportar_resultado_json",
    "fracao_para_dict",
    "gerar_csv_sanitizado",
    "gerar_pacote_zip_deterministico",
    "gerar_painel_svg",
    "gerar_relatorio_texto",
    "parsear_fracao_segura",
    "sanitizar_campo_csv",
]
