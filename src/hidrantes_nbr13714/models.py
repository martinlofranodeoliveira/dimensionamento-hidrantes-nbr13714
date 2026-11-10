"""Modelos de dados imutáveis para dimensionamento de hidrantes (ABNT NBR 13714:2000).

Utiliza dataclasses imutáveis (frozen=True) e tipos puramente racionais (Fraction)
ou inteiros, eliminando imprecisões de ponto flutuante conforme o padrão de
engenharia LOFRANO TECNOLOGIA.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction


@dataclass(frozen=True)
class ConexoesTrecho:
    """Contagem de conexões e acessórios hidráulicos em um trecho de tubulação."""

    joelho_90: int = 0
    joelho_45: int = 0
    te_passagem_direta: int = 0
    te_saida_lateral: int = 0
    valvula_gaveta: int = 0
    valvula_retencao: int = 0

    def total_pecas(self) -> int:
        return (
            self.joelho_90
            + self.joelho_45
            + self.te_passagem_direta
            + self.te_saida_lateral
            + self.valvula_gaveta
            + self.valvula_retencao
        )


@dataclass(frozen=True)
class TrechoRede:
    """Trecho de tubulação da rede de hidrantes."""

    identificador: str
    diametro_chave: str           # chave em TUBOS_ACO_NBR5580 (ex: "2_1_2_pol")
    comprimento_linear_m: Fraction
    vazao_l_min: Fraction
    desnivel_geometrico_m: Fraction
    conexoes: ConexoesTrecho = field(default_factory=ConexoesTrecho)

    def __post_init__(self) -> None:
        if self.comprimento_linear_m <= 0:
            raise ValueError("O comprimento linear do trecho deve ser positivo.")
        if self.vazao_l_min <= 0:
            raise ValueError("A vazão do trecho deve ser positiva.")


@dataclass(frozen=True)
class Hidrante:
    """Ponto de hidrante ou mangotinho na edificação."""

    identificador: str
    tipo_sistema: str             # chave em SISTEMAS_NORMATIVOS
    pavimento: str
    cota_geometrica_m: Fraction
    comprimento_mangueira_m: int = 30


@dataclass(frozen=True)
class InstalacaoIncendio:
    """Dados de entrada gerais da instalação de hidrantes predial ou industrial."""

    nome_projeto: str
    tipo_ocupacao: str
    tipo_sistema_adotado: str
    cota_reservatorio_bomba_m: Fraction
    trechos: tuple[TrechoRede, ...]
    hidrantes: tuple[Hidrante, ...]
    tempo_reserva_min: int = 30

    def __post_init__(self) -> None:
        if not self.trechos:
            raise ValueError("A instalação deve conter pelo menos um trecho de rede.")
        if not self.hidrantes:
            raise ValueError("A instalação deve conter pelo menos um hidrante.")
        if self.tempo_reserva_min <= 0:
            raise ValueError("O tempo de reserva deve ser positivo.")


@dataclass(frozen=True)
class ResultadoTrecho:
    """Resultados hidráulicos de dimensionamento de um trecho da rede."""

    identificador: str
    diametro_chave: str
    diametro_interno_mm: Fraction
    vazao_l_min: Fraction
    velocidade_m_s: Fraction
    comprimento_linear_m: Fraction
    comprimento_equivalente_m: Fraction
    comprimento_total_m: Fraction
    perda_carga_unitaria_mca_m: Fraction
    perda_carga_trecho_mca: Fraction


@dataclass(frozen=True)
class ResultadoDimensionamentoHidrantes:
    """Resultado analítico global da rede de combate a incêndio por hidrantes."""

    identificador_projeto: str
    instalacao: InstalacaoIncendio
    tipo_sistema: str
    vazao_de_projeto_l_min: Fraction
    vazao_de_projeto_m3_h: Fraction
    reserva_tecnica_incendio_m3: Fraction
    resultados_trechos: tuple[ResultadoTrecho, ...]
    perda_carga_total_tubulacao_mca: Fraction
    perda_carga_mangueira_mca: Fraction
    desnivel_geometrico_critico_mca: Fraction
    pressao_residual_requerida_mca: Fraction
    pressao_residual_disponivel_mca: Fraction
    altura_manometrica_total_bomba_mca: Fraction
    potencia_bomba_cv: Fraction
    potencia_motor_comercial_cv: int
    conclusao_tecnica: str
    sistema_conforme: bool
