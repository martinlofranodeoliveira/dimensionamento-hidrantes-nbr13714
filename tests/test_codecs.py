from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hidrantes_nbr13714.calculator import dimensionar_rede_hidrantes
from hidrantes_nbr13714.codecs import (
    JSONCodecError,
    carregar_entrada_json,
    exportar_resultado_json,
    fracao_para_dict,
    parsear_fracao_segura,
)
from hidrantes_nbr13714.models import ConexoesTrecho, Hidrante, InstalacaoIncendio, TrechoRede


class TestCodecs(unittest.TestCase):
    def test_parsear_fracao_segura(self) -> None:
        self.assertEqual(parsear_fracao_segura(10), Fraction(10, 1))
        self.assertEqual(parsear_fracao_segura("130/3"), Fraction(130, 3))
        self.assertEqual(parsear_fracao_segura({"num": 5, "den": 2}), Fraction(5, 2))
        self.assertEqual(parsear_fracao_segura(Fraction(3, 1)), Fraction(3, 1))

    def test_parsear_fracao_segura_erro_tipo(self) -> None:
        with self.assertRaises(JSONCodecError):
            parsear_fracao_segura([1, 2])

    def test_parsear_fracao_segura_erro_str(self) -> None:
        with self.assertRaises(JSONCodecError):
            parsear_fracao_segura("invalido")

    def test_fracao_para_dict(self) -> None:
        d = fracao_para_dict(Fraction(7, 4))
        self.assertEqual(d["num"], 7)
        self.assertEqual(d["den"], 4)
        self.assertEqual(d["str"], "7/4")

    def test_rejeicao_bom_bytes_e_str(self) -> None:
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json(b"\xef\xbb\xbf{}")
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json("\ufeff{}")

    def test_rejeicao_ponto_flutuante(self) -> None:
        json_com_float = '{"nome_projeto": "Teste", "tipo_sistema_adotado": "tipo_2", "trechos": [], "hidrantes": [], "tempo_reserva_min": 30.5}'
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json(json_com_float)

    def test_rejeicao_chaves_duplicadas(self) -> None:
        json_duplicado = '{"nome_projeto": "A", "nome_projeto": "B", "tipo_sistema_adotado": "tipo_2", "trechos": [], "hidrantes": []}'
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json(json_duplicado)

    def test_rejeicao_profundidade_excessiva(self) -> None:
        d: dict[str, object] = {"fim": 1}
        for _ in range(40):
            d = {"sub": d}
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json(json.dumps(d))

    def test_carregar_entrada_json_sem_campos_obrigatorios(self) -> None:
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json('{"nome_projeto": "Incompleto"}')

    def test_carregar_entrada_json_raiz_nao_dict(self) -> None:
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json('["lista"]')

    def test_carregar_e_exportar_json_valido(self) -> None:
        t1 = TrechoRede("T1", "2_1_2_pol", Fraction(10, 1), Fraction(260, 1), Fraction(5, 1))
        h1 = Hidrante("H1", "tipo_2", "Térreo", Fraction(5, 1))
        inst = InstalacaoIncendio("Teste", "Residencial", "tipo_2", Fraction(0, 1), (t1,), (h1,))
        res = dimensionar_rede_hidrantes(inst)
        json_str = exportar_resultado_json(res)
        self.assertIn("ABNT NBR 13714:2000", json_str)
        self.assertIn("LOFRANO TECNOLOGIA", json_str)


if __name__ == "__main__":
    unittest.main()
