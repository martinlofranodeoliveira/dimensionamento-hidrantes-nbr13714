"""Exportadores de laudos, planilhas e pacotes determinísticos para hidrantes NBR 13714.

Garante:
1. Geração de relatório técnico textual com tabelas de trechos e moto-bomba.
2. Sanitização estrita de CSV contra injeção de fórmulas (=, +, -, @, \\t, \\r).
3. Criação de arquivo ZIP determinístico com carimbo fixo (2026-01-01 00:00:00)
   e garantia de não sobrescrita atômica via os.O_EXCL.
"""

from __future__ import annotations

import csv
from io import StringIO
import os
from pathlib import Path
import zipfile

from hidrantes_nbr13714.codecs import exportar_resultado_json
from hidrantes_nbr13714.models import ResultadoDimensionamentoHidrantes

TIMESTAMP_DETERMINISTICO = (2026, 1, 1, 0, 0, 0)
CARACTERES_INJECAO_FORMULA = ("=", "+", "-", "@", "\t", "\r")


def sanitizar_campo_csv(valor: object) -> str:
    """Sanitiza campos de texto para evitar execução indevida de fórmulas em planilhas."""
    texto = str(valor)
    if texto.startswith(CARACTERES_INJECAO_FORMULA):
        return f"'{texto}"
    return texto


def gerar_relatorio_texto(resultado: ResultadoDimensionamentoHidrantes) -> str:
    """Gera relatório técnico analítico em texto plano com formatação tabular."""
    linhas = [
        "=" * 82,
        "MEMORIAL DE CÁLCULO DE SISTEMA DE HIDRANTES E MANGOTINHOS - ABNT NBR 13714:2000",
        "PADRÃO DE ENGENHARIA: LOFRANO TECNOLOGIA (ARITMÉTICA RACIONAL EXATA)",
        "=" * 82,
        f"Projeto: {resultado.identificador_projeto}",
        f"Obra: {resultado.instalacao.nome_projeto} | Ocupação: {resultado.instalacao.tipo_ocupacao}",
        f"Sistema Adotado: {resultado.tipo_sistema.upper()}",
        f"Vazão de Projeto Total: {resultado.vazao_de_projeto_l_min} L/min ({resultado.vazao_de_projeto_m3_h} m³/h)",
        f"Reserva Técnica de Incêndio (RTI): {resultado.reserva_tecnica_incendio_m3} m³ ({resultado.reserva_tecnica_incendio_m3 * 1000} L)",
        "-" * 82,
        "1. DIMENSIONAMENTO HIDRÁULICO DOS TRECHOS DA REDE",
        "-" * 82,
        f"{'Trecho':<20} | {'DN':<9} | {'Q (L/min)':<9} | {'V (m/s)':<8} | {'L_real':<7} | {'L_eq':<7} | {'Perda (mca)':<10}",
        "-" * 82,
    ]

    for t in resultado.resultados_trechos:
        linhas.append(
            f"{t.identificador:<20} | {t.diametro_chave:<9} | {str(t.vazao_l_min):<9} | {str(t.velocidade_m_s):<8} | "
            f"{str(t.comprimento_linear_m):<7} | {str(t.comprimento_equivalente_m):<7} | {str(t.perda_carga_trecho_mca):<10}"
        )

    linhas.extend([
        "-" * 82,
        "2. EQUAÇÃO DE CARGA E DIMENSIONAMENTO DA BOMBA DE INCÊNDIO",
        "-" * 82,
        f"Perda de Carga Total nas Tubulações:       {resultado.perda_carga_total_tubulacao_mca} mca",
        f"Perda de Carga na Mangueira (30m):          {resultado.perda_carga_mangueira_mca} mca",
        f"Desnível Geométrico Crítico (Hgeom):        {resultado.desnivel_geometrico_critico_mca} mca",
        f"Pressão Residual Mínima Requerida:         {resultado.pressao_residual_requerida_mca} mca",
        f"ALTURA MANOMÉTRICA TOTAL DA BOMBA (Hman):   {resultado.altura_manometrica_total_bomba_mca} mca",
        f"Potência Calculada da Bomba:               {resultado.potencia_bomba_cv} cv",
        f"Potência do Motor Comercial Adotado:       {resultado.potencia_motor_comercial_cv} cv",
        f"Pressão Residual Disponível no Requinte:   {resultado.pressao_residual_disponivel_mca} mca",
        "=" * 82,
        f"PARECER TÉCNICO CONCLUSIVO: {resultado.conclusao_tecnica}",
        "=" * 82,
    ])

    return "\n".join(linhas) + "\n"


def gerar_csv_sanitizado(resultado: ResultadoDimensionamentoHidrantes) -> str:
    """Gera dados de saída em CSV sanitizado contra injeção de fórmulas."""
    buffer = StringIO()
    escritor = csv.writer(buffer, lineterminator="\n")

    escritor.writerow([
        sanitizar_campo_csv("Tipo_Registro"),
        sanitizar_campo_csv("Identificador"),
        sanitizar_campo_csv("Diametro"),
        sanitizar_campo_csv("Vazao_L_min"),
        sanitizar_campo_csv("Velocidade_m_s"),
        sanitizar_campo_csv("Comprimento_Linear_m"),
        sanitizar_campo_csv("Comprimento_Equivalente_m"),
        sanitizar_campo_csv("Comprimento_Total_m"),
        sanitizar_campo_csv("Perda_Carga_mca"),
        sanitizar_campo_csv("Norma_Referencia"),
    ])

    # Linhas de trechos
    for t in resultado.resultados_trechos:
        escritor.writerow([
            sanitizar_campo_csv("Trecho_Tubulacao"),
            sanitizar_campo_csv(t.identificador),
            sanitizar_campo_csv(t.diametro_chave),
            sanitizar_campo_csv(t.vazao_l_min),
            sanitizar_campo_csv(t.velocidade_m_s),
            sanitizar_campo_csv(t.comprimento_linear_m),
            sanitizar_campo_csv(t.comprimento_equivalente_m),
            sanitizar_campo_csv(t.comprimento_total_m),
            sanitizar_campo_csv(t.perda_carga_trecho_mca),
            sanitizar_campo_csv("ABNT NBR 13714:2000"),
        ])

    # Linhas de resumo da bomba e RTI
    totais = [
        ("Resumo_RTI", "RTI_Minima", "-", str(resultado.vazao_de_projeto_l_min), "-", "-", "-", "-", str(resultado.reserva_tecnica_incendio_m3), "NBR 13714"),
        ("Resumo_Bomba", "Bomba_Incendio", "-", str(resultado.vazao_de_projeto_l_min), "-", "-", "-", "-", str(resultado.altura_manometrica_total_bomba_mca), "NBR 13714"),
        ("Resumo_Motor", f"{resultado.potencia_motor_comercial_cv} cv", "-", "-", "-", "-", "-", "-", str(resultado.potencia_bomba_cv), "NBR 13714"),
    ]
    for tr, iden, diam, q, vel, l_lin, l_eq, l_tot, perda, nrm in totais:
        escritor.writerow([
            sanitizar_campo_csv(tr),
            sanitizar_campo_csv(iden),
            sanitizar_campo_csv(diam),
            sanitizar_campo_csv(q),
            sanitizar_campo_csv(vel),
            sanitizar_campo_csv(l_lin),
            sanitizar_campo_csv(l_eq),
            sanitizar_campo_csv(l_tot),
            sanitizar_campo_csv(perda),
            sanitizar_campo_csv(nrm),
        ])

    return buffer.getvalue()


def gerar_pacote_zip_deterministico(
    resultado: ResultadoDimensionamentoHidrantes, caminho_destino: Path | str
) -> None:
    """Cria arquivo ZIP determinístico com carimbo fixo e proteção contra sobrescrita atômica."""
    caminho = Path(caminho_destino)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY

    fd = os.open(caminho, flags, 0o644)
    with open(fd, "wb", closefd=True) as f_out:
        with zipfile.ZipFile(f_out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            conteudos = {
                "relatorio_hidrantes.txt": gerar_relatorio_texto(resultado).encode("utf-8"),
                "dados_dimensionamento.csv": gerar_csv_sanitizado(resultado).encode("utf-8"),
                "resultado_hidrantes.json": exportar_resultado_json(resultado).encode("utf-8"),
            }
            for nome_arquivo, dados_bytes in conteudos.items():
                info = zipfile.ZipInfo(filename=nome_arquivo, date_time=TIMESTAMP_DETERMINISTICO)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                zf.writestr(info, dados_bytes)
