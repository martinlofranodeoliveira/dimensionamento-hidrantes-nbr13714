"""Interface de Linha de Comando (CLI) para dimensionamento de hidrantes (ABNT NBR 13714:2000).

Comandos disponíveis:
  calcular       Dimensiona a rede de hidrantes a partir de arquivo de entrada JSON.
  catalogo       Exibe parâmetros normativos, vazões, tubos e conexões equivalentes.
  gerar-exemplo  Gera modelo JSON canônico para projetos prediais e industriais.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from hidrantes_nbr13714 import __version__
from hidrantes_nbr13714.calculator import dimensionar_rede_hidrantes
from hidrantes_nbr13714.codecs import (
    JSONCodecError,
    carregar_entrada_json,
    exportar_resultado_json,
)
from hidrantes_nbr13714.constants import (
    CONEXOES_EQUIVALENTES_M,
    SISTEMAS_NORMATIVOS,
    TUBOS_ACO_NBR5580,
)
from hidrantes_nbr13714.exporters import (
    gerar_csv_sanitizado,
    gerar_pacote_zip_deterministico,
    gerar_relatorio_texto,
)
from hidrantes_nbr13714.svg_generator import gerar_painel_svg


def criar_parser() -> argparse.ArgumentParser:
    """Cria o analisador de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        prog="hidrantes-nbr13714",
        description="Dimensionamento analítico de hidrantes e mangotinhos (ABNT NBR 13714:2000).",
    )
    parser.add_argument(
        "--versao",
        "-v",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Exibe a versão instalada do programa.",
    )

    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Comando: calcular
    parser_calc = subparsers.add_parser("calcular", help="Dimensiona a rede de hidrantes a partir de JSON.")
    parser_calc.add_argument("arquivo", type=str, help="Caminho do arquivo JSON de entrada.")
    parser_calc.add_argument(
        "--formato",
        "-f",
        choices=["texto", "json", "csv", "svg", "zip"],
        default="texto",
        help="Formato do resultado de saída (padrão: texto).",
    )
    parser_calc.add_argument(
        "--saida",
        "-o",
        type=str,
        default=None,
        help="Arquivo de destino (se omitido, imprime no terminal).",
    )
    parser_calc.add_argument(
        "--projeto",
        "-p",
        type=str,
        default="HIDRANTES-NBR13714-001",
        help="Identificador do projeto.",
    )

    # Comando: catalogo
    parser_cat = subparsers.add_parser("catalogo", help="Exibe parâmetros normativos da NBR 13714.")
    parser_cat.add_argument(
        "--secao",
        "-s",
        choices=["todos", "sistemas", "tubos", "conexoes"],
        default="todos",
        help="Seção do catálogo a exibir (padrão: todos).",
    )

    # Comando: gerar-exemplo
    parser_ex = subparsers.add_parser("gerar-exemplo", help="Gera arquivo de entrada JSON de exemplo.")
    parser_ex.add_argument(
        "--tipo",
        "-t",
        choices=["residencial-tipo2", "comercial-tipo3", "industrial-tipo4"],
        default="residencial-tipo2",
        help="Tipo de instalação de combate a incêndio.",
    )
    parser_ex.add_argument(
        "--saida",
        "-o",
        type=str,
        default=None,
        help="Arquivo de destino (se omitido, imprime no terminal).",
    )

    return parser


def comando_catalogo(secao: str) -> int:
    """Exibe tabelas e especificações normativas no terminal."""
    if secao in ("todos", "sistemas"):
        print("=" * 72)
        print("ABNT NBR 13714:2000 · TIPOS DE SISTEMAS DE HIDRANTES E MANGOTINHOS")
        print("=" * 72)
        for codigo, dados in SISTEMAS_NORMATIVOS.items():
            print(f"Código: {codigo} | {dados['nome']}")
            print(f"  • Vazão por ponto: {dados['vazao_ponto_l_min']} L/min")
            print(f"  • Pontos simultâneos: {dados['pontos_simultaneos']}")
            print(f"  • Vazão total: {dados['vazao_total_l_min']} L/min")
            print(f"  • Pressão residual mínima no esguicho: {dados['pressao_residual_minima_mca']} mca")
            print(f"  • Reserva Técnica de Incêndio mínima (RTI): {dados['rti_minima_m3']} m³")
            print(f"  • Mangueira: DN {dados['diametro_mangueira_mm']} mm x {dados['comprimento_mangueira_m']} m")
            print()

    if secao in ("todos", "tubos"):
        print("=" * 72)
        print("TUBULAÇÕES DE AÇO CARBONO GALVANIZADO (NBR 5580)")
        print("=" * 72)
        for chave, t in TUBOS_ACO_NBR5580.items():
            print(f"Diâmetro Nominal: {t['dn_pol']} (DN {t['dn_mm']} mm)")
            print(f"  • Diâmetro interno real: {t['diametro_interno_mm']} mm")
            print(f"  • Espessura da parede: {t['espessura_parede_mm']} mm")
            print(f"  • Rugosidade de Hazen-Williams: C={t['rugosidade_c']}")
            print()

    if secao in ("todos", "conexoes"):
        print("=" * 72)
        print("COMPRIMENTOS EQUIVALENTES DE CONEXÕES EM METROS (TABELA B.1)")
        print("=" * 72)
        for chave, c in CONEXOES_EQUIVALENTES_M.items():
            print(f"Diâmetro Nominal: {chave}")
            for peca, comp in c.items():
                print(f"  • {peca:22}: {comp} m")
            print()

    return 0


def comando_gerar_exemplo(tipo: str, saida: str | None) -> int:
    """Gera dados de exemplo estruturados em JSON."""
    mapa_exemplos = {
        "residencial-tipo2": {
            "nome_projeto": "Edifício Residencial Belo Horizonte",
            "tipo_ocupacao": "Residencial Multifamiliar",
            "tipo_sistema_adotado": "tipo_2",
            "cota_reservatorio_bomba_m": "0",
            "tempo_reserva_min": 30,
            "trechos": [
                {
                    "identificador": "Sucção da Bomba",
                    "diametro_chave": "2_1_2_pol",
                    "comprimento_linear_m": "4",
                    "vazao_l_min": "260",
                    "desnivel_geometrico_m": "0",
                    "conexoes": {
                        "valvula_gaveta": 1,
                        "joelho_90": 1
                    }
                },
                {
                    "identificador": "Coluna de Recalque",
                    "diametro_chave": "2_1_2_pol",
                    "comprimento_linear_m": "28",
                    "vazao_l_min": "260",
                    "desnivel_geometrico_m": "24",
                    "conexoes": {
                        "valvula_retencao": 1,
                        "valvula_gaveta": 1,
                        "joelho_90": 2,
                        "te_passagem_direta": 2
                    }
                },
                {
                    "identificador": "Ramal Hidrante Crítico",
                    "diametro_chave": "2_1_2_pol",
                    "comprimento_linear_m": "6",
                    "vazao_l_min": "130",
                    "desnivel_geometrico_m": "0",
                    "conexoes": {
                        "te_saida_lateral": 1,
                        "joelho_90": 1,
                        "valvula_gaveta": 1
                    }
                }
            ],
            "hidrantes": [
                {
                    "identificador": "H1",
                    "tipo_sistema": "tipo_2",
                    "pavimento": "Térreo",
                    "cota_geometrica_m": "1",
                    "comprimento_mangueira_m": 30
                },
                {
                    "identificador": "H2",
                    "tipo_sistema": "tipo_2",
                    "pavimento": "3º Pavimento",
                    "cota_geometrica_m": "12",
                    "comprimento_mangueira_m": 30
                },
                {
                    "identificador": "H3",
                    "tipo_sistema": "tipo_2",
                    "pavimento": "Ático / Cobertura",
                    "cota_geometrica_m": "24",
                    "comprimento_mangueira_m": 30
                }
            ]
        },
        "comercial-tipo3": {
            "nome_projeto": "Centro Empresarial Paulista",
            "tipo_ocupacao": "Comercial Escritórios e Lojas",
            "tipo_sistema_adotado": "tipo_3",
            "cota_reservatorio_bomba_m": "0",
            "tempo_reserva_min": 60,
            "trechos": [
                {
                    "identificador": "Sucção da Bomba",
                    "diametro_chave": "3_pol",
                    "comprimento_linear_m": "5",
                    "vazao_l_min": "400",
                    "desnivel_geometrico_m": "0",
                    "conexoes": {
                        "valvula_gaveta": 1,
                        "joelho_90": 1
                    }
                },
                {
                    "identificador": "Barrilete e Prumada",
                    "diametro_chave": "2_1_2_pol",
                    "comprimento_linear_m": "35",
                    "vazao_l_min": "400",
                    "desnivel_geometrico_m": "30",
                    "conexoes": {
                        "valvula_retencao": 1,
                        "valvula_gaveta": 1,
                        "joelho_90": 3
                    }
                }
            ],
            "hidrantes": [
                {
                    "identificador": "H_Critico",
                    "tipo_sistema": "tipo_3",
                    "pavimento": "Cobertura",
                    "cota_geometrica_m": "30",
                    "comprimento_mangueira_m": 30
                }
            ]
        },
        "industrial-tipo4": {
            "nome_projeto": "Galpão Industrial Mauá",
            "tipo_ocupacao": "Industrial / Logística",
            "tipo_sistema_adotado": "tipo_4",
            "cota_reservatorio_bomba_m": "0",
            "tempo_reserva_min": 60,
            "trechos": [
                {
                    "identificador": "Sucção da Bomba",
                    "diametro_chave": "4_pol",
                    "comprimento_linear_m": "6",
                    "vazao_l_min": "600",
                    "desnivel_geometrico_m": "0",
                    "conexoes": {
                        "valvula_gaveta": 1,
                        "joelho_90": 1
                    }
                },
                {
                    "identificador": "Rede Externa Enterrada",
                    "diametro_chave": "3_pol",
                    "comprimento_linear_m": "80",
                    "vazao_l_min": "600",
                    "desnivel_geometrico_m": "2",
                    "conexoes": {
                        "valvula_retencao": 1,
                        "valvula_gaveta": 2,
                        "joelho_90": 4
                    }
                }
            ],
            "hidrantes": [
                {
                    "identificador": "H_Externo_Mais_Distante",
                    "tipo_sistema": "tipo_4",
                    "pavimento": "Pátio Logístico",
                    "cota_geometrica_m": "2",
                    "comprimento_mangueira_m": 30
                }
            ]
        }
    }

    import json
    dados = mapa_exemplos.get(tipo, mapa_exemplos["residencial-tipo2"])
    conteudo = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"

    if saida:
        Path(saida).write_text(conteudo, encoding="utf-8")
        print(f"Exemplo JSON salvo com sucesso em: {saida}")
    else:
        print(conteudo, end="")

    return 0


def comando_calcular(arquivo: str, formato: str, saida: str | None, projeto: str) -> int:
    """Executa a rotina analítica de dimensionamento."""
    caminho = Path(arquivo)
    if not caminho.exists():
        sys.stderr.write(f"Erro: Arquivo de entrada inexistente: {arquivo}\n")
        return 1

    try:
        conteudo_bytes = caminho.read_bytes()
        instalacao = carregar_entrada_json(conteudo_bytes)
        resultado = dimensionar_rede_hidrantes(instalacao, identificador_projeto=projeto)

        if formato == "texto":
            texto = gerar_relatorio_texto(resultado)
            if saida:
                Path(saida).write_text(texto, encoding="utf-8")
                print(f"Relatório técnico salvo em: {saida}")
            else:
                print(texto, end="")
        elif formato == "json":
            texto = exportar_resultado_json(resultado)
            if saida:
                Path(saida).write_text(texto, encoding="utf-8")
                print(f"Resultado JSON salvo em: {saida}")
            else:
                print(texto)
        elif formato == "csv":
            texto = gerar_csv_sanitizado(resultado)
            if saida:
                Path(saida).write_text(texto, encoding="utf-8")
                print(f"Dados CSV salvos em: {saida}")
            else:
                print(texto, end="")
        elif formato == "svg":
            texto = gerar_painel_svg(resultado)
            if saida:
                Path(saida).write_text(texto, encoding="utf-8")
                print(f"Painel vetorial SVG salvo em: {saida}")
            else:
                print(texto, end="")
        elif formato == "zip":
            if not saida:
                sys.stderr.write("Erro: Parâmetro --saida é obrigatório para exportação em formato ZIP.\n")
                return 1
            gerar_pacote_zip_deterministico(resultado, saida)
            print(f"Pacote determinístico ZIP salvo em: {saida}")

        return 0

    except JSONCodecError as exc:
        sys.stderr.write(f"Erro de conformidade JSON: {exc}\n")
        return 2
    except Exception as exc:
        sys.stderr.write(f"Erro no processamento do dimensionamento: {exc}\n")
        return 3


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada principal da CLI."""
    parser = criar_parser()
    args = parser.parse_args(argv)

    if not args.comando:
        parser.print_help()
        return 0

    if args.comando == "catalogo":
        return comando_catalogo(args.secao)
    elif args.comando == "gerar-exemplo":
        return comando_gerar_exemplo(args.tipo, args.saida)
    elif args.comando == "calcular":
        return comando_calcular(args.arquivo, args.formato, args.saida, args.projeto)

    return 0


if __name__ == "__main__":
    sys.exit(main())
