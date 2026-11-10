"""Codecs canônicos RFC 8259 e serialização segura para hidrantes NBR 13714.

Garante:
1. Rejeição de marcas de ordem de byte (BOM UTF-8: \\xef\\xbb\\xbf / \\ufeff).
2. Rejeição estrita de números de ponto flutuante (proibição de float).
3. Rejeição de chaves duplicadas em objetos JSON.
4. Limite de profundidade de aninhamento (máximo 32 níveis).
5. Conversão bidirecional de grandezas racionais exatas (Fraction).
"""

from __future__ import annotations

from fractions import Fraction
import json
from typing import Any

from hidrantes_nbr13714.models import (
    ConexoesTrecho,
    Hidrante,
    InstalacaoIncendio,
    ResultadoDimensionamentoHidrantes,
    ResultadoTrecho,
    TrechoRede,
)

PROFUNDIDADE_MAXIMA_PERMITIDA = 32


class JSONCodecError(ValueError):
    """Erro em caso de violação de conformidade com o codec JSON canônico."""


def _verificar_profundidade(obj: Any, nivel_atual: int = 1) -> None:
    if nivel_atual > PROFUNDIDADE_MAXIMA_PERMITIDA:
        raise JSONCodecError(
            f"Profundidade excessiva de aninhamento ({nivel_atual} > {PROFUNDIDADE_MAXIMA_PERMITIDA})."
        )
    if isinstance(obj, dict):
        for valor in obj.values():
            _verificar_profundidade(valor, nivel_atual + 1)
    elif isinstance(obj, list):
        for item in obj:
            _verificar_profundidade(item, nivel_atual + 1)


def _rejeitar_float(valor: str) -> None:
    raise JSONCodecError(
        f"Ponto flutuante proibido pelo padrão de engenharia LOFRANO TECNOLOGIA: {valor!r}. "
        "Utilize inteiros ou frações exatas (ex: '25/2' ou {'num': 25, 'den': 2})."
    )


def _object_pairs_hook_sem_duplicatas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    resultado: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise JSONCodecError(f"Chave duplicada proibida no JSON: {chave!r}")
        resultado[chave] = valor
    return resultado


def parsear_fracao_segura(valor: Any) -> Fraction:
    """Converte int, str fracionária ('1/2') ou dict ({'num': 1, 'den': 2}) em Fraction."""
    if isinstance(valor, Fraction):
        return valor
    if isinstance(valor, int):
        return Fraction(valor, 1)
    if isinstance(valor, str):
        if "/" in valor:
            partes = valor.split("/")
            if len(partes) == 2 and partes[0].strip().lstrip("-").isdigit() and partes[1].strip().isdigit():
                return Fraction(int(partes[0].strip()), int(partes[1].strip()))
        if valor.strip().lstrip("-").isdigit():
            return Fraction(int(valor.strip()), 1)
        raise JSONCodecError(f"Formato de string fracionária inválido: {valor!r}")
    if isinstance(valor, dict) and "num" in valor and "den" in valor:
        num = valor["num"]
        den = valor["den"]
        if isinstance(num, int) and isinstance(den, int) and den != 0:
            return Fraction(num, den)
        raise JSONCodecError(f"Dicionário de fração com valores não inteiros: {valor!r}")
    raise JSONCodecError(f"Tipo não conversível em Fraction exata: {type(valor)} ({valor!r})")


def fracao_para_dict(fracao: Fraction) -> dict[str, int | str]:
    """Serializa Fraction em formato canônico com numerador, denominador e representação."""
    return {
        "num": fracao.numerator,
        "den": fracao.denominator,
        "str": f"{fracao.numerator}/{fracao.denominator}" if fracao.denominator != 1 else str(fracao.numerator),
    }


def carregar_entrada_json(conteudo: str | bytes) -> InstalacaoIncendio:
    """Carrega dados de entrada de uma instalação de hidrantes rejeitando BOM, floats e duplicatas."""
    if isinstance(conteudo, bytes):
        if conteudo.startswith(b"\xef\xbb\xbf"):
            raise JSONCodecError("Marca de ordem de byte (BOM) UTF-8 rejeitada na entrada.")
        texto = conteudo.decode("utf-8")
    else:
        if conteudo.startswith("\ufeff"):
            raise JSONCodecError("Marca de ordem de byte (BOM) rejeitada na entrada.")
        texto = conteudo

    dados = json.loads(
        texto,
        object_pairs_hook=_object_pairs_hook_sem_duplicatas,
        parse_float=_rejeitar_float,
    )
    _verificar_profundidade(dados)

    if not isinstance(dados, dict):
        raise JSONCodecError("A raiz do JSON de entrada deve ser um objeto dicionário.")

    campos_obrigatorios = ("nome_projeto", "tipo_sistema_adotado", "trechos", "hidrantes")
    for campo in campos_obrigatorios:
        if campo not in dados:
            raise JSONCodecError(f"Campo obrigatório ausente no JSON: {campo!r}")

    nome_projeto = str(dados["nome_projeto"])
    tipo_ocupacao = str(dados.get("tipo_ocupacao", "Residencial Multifamiliar"))
    tipo_sistema = str(dados["tipo_sistema_adotado"])
    cota_res = parsear_fracao_segura(dados.get("cota_reservatorio_bomba_m", 0))
    tempo_res = int(dados.get("tempo_reserva_min", 30))

    # Parse dos trechos
    lista_trechos: list[TrechoRede] = []
    for t in dados["trechos"]:
        conexoes_dict = t.get("conexoes", {})
        conexoes = ConexoesTrecho(
            joelho_90=int(conexoes_dict.get("joelho_90", 0)),
            joelho_45=int(conexoes_dict.get("joelho_45", 0)),
            te_passagem_direta=int(conexoes_dict.get("te_passagem_direta", 0)),
            te_saida_lateral=int(conexoes_dict.get("te_saida_lateral", 0)),
            valvula_gaveta=int(conexoes_dict.get("valvula_gaveta", 0)),
            valvula_retencao=int(conexoes_dict.get("valvula_retencao", 0)),
        )
        trecho = TrechoRede(
            identificador=str(t["identificador"]),
            diametro_chave=str(t["diametro_chave"]),
            comprimento_linear_m=parsear_fracao_segura(t["comprimento_linear_m"]),
            vazao_l_min=parsear_fracao_segura(t["vazao_l_min"]),
            desnivel_geometrico_m=parsear_fracao_segura(t.get("desnivel_geometrico_m", 0)),
            conexoes=conexoes,
        )
        lista_trechos.append(trecho)

    # Parse dos hidrantes
    lista_hidrantes: list[Hidrante] = []
    for h in dados["hidrantes"]:
        hidrante = Hidrante(
            identificador=str(h["identificador"]),
            tipo_sistema=str(h.get("tipo_sistema", tipo_sistema)),
            pavimento=str(h.get("pavimento", "Pavimento Tipo")),
            cota_geometrica_m=parsear_fracao_segura(h["cota_geometrica_m"]),
            comprimento_mangueira_m=int(h.get("comprimento_mangueira_m", 30)),
        )
        lista_hidrantes.append(hidrante)

    return InstalacaoIncendio(
        nome_projeto=nome_projeto,
        tipo_ocupacao=tipo_ocupacao,
        tipo_sistema_adotado=tipo_sistema,
        cota_reservatorio_bomba_m=cota_res,
        trechos=tuple(lista_trechos),
        hidrantes=tuple(lista_hidrantes),
        tempo_reserva_min=tempo_res,
    )


def exportar_resultado_json(resultado: ResultadoDimensionamentoHidrantes) -> str:
    """Serializa ResultadoDimensionamentoHidrantes em JSON canônico formatado."""
    dict_resultado: dict[str, Any] = {
        "norma_referencia": "ABNT NBR 13714:2000",
        "padrao_engenharia": "LOFRANO TECNOLOGIA",
        "identificador_projeto": resultado.identificador_projeto,
        "conforme": resultado.sistema_conforme,
        "conclusao_tecnica": resultado.conclusao_tecnica,
        "instalacao": {
            "nome_projeto": resultado.instalacao.nome_projeto,
            "tipo_ocupacao": resultado.instalacao.tipo_ocupacao,
            "tipo_sistema_adotado": resultado.instalacao.tipo_sistema_adotado,
            "cota_reservatorio_bomba_m": fracao_para_dict(resultado.instalacao.cota_reservatorio_bomba_m),
            "tempo_reserva_min": resultado.instalacao.tempo_reserva_min,
        },
        "dimensionamento_hidraulico": {
            "tipo_sistema": resultado.tipo_sistema,
            "vazao_de_projeto_l_min": fracao_para_dict(resultado.vazao_de_projeto_l_min),
            "vazao_de_projeto_m3_h": fracao_para_dict(resultado.vazao_de_projeto_m3_h),
            "reserva_tecnica_incendio_m3": fracao_para_dict(resultado.reserva_tecnica_incendio_m3),
            "perda_carga_total_tubulacao_mca": fracao_para_dict(resultado.perda_carga_total_tubulacao_mca),
            "perda_carga_mangueira_mca": fracao_para_dict(resultado.perda_carga_mangueira_mca),
            "desnivel_geometrico_critico_mca": fracao_para_dict(resultado.desnivel_geometrico_critico_mca),
            "pressao_residual_requerida_mca": fracao_para_dict(resultado.pressao_residual_requerida_mca),
            "pressao_residual_disponivel_mca": fracao_para_dict(resultado.pressao_residual_disponivel_mca),
            "altura_manometrica_total_bomba_mca": fracao_para_dict(resultado.altura_manometrica_total_bomba_mca),
            "potencia_bomba_cv": fracao_para_dict(resultado.potencia_bomba_cv),
            "potencia_motor_comercial_cv": resultado.potencia_motor_comercial_cv,
        },
        "trechos": [
            {
                "identificador": t.identificador,
                "diametro_chave": t.diametro_chave,
                "diametro_interno_mm": fracao_para_dict(t.diametro_interno_mm),
                "vazao_l_min": fracao_para_dict(t.vazao_l_min),
                "velocidade_m_s": fracao_para_dict(t.velocidade_m_s),
                "comprimento_linear_m": fracao_para_dict(t.comprimento_linear_m),
                "comprimento_equivalente_m": fracao_para_dict(t.comprimento_equivalente_m),
                "comprimento_total_m": fracao_para_dict(t.comprimento_total_m),
                "perda_carga_unitaria_mca_m": fracao_para_dict(t.perda_carga_unitaria_mca_m),
                "perda_carga_trecho_mca": fracao_para_dict(t.perda_carga_trecho_mca),
            }
            for t in resultado.resultados_trechos
        ],
    }

    return json.dumps(dict_resultado, indent=2, ensure_ascii=False)
