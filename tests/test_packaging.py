from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import hidrantes_nbr13714


class TestPackaging(unittest.TestCase):
    def test_versao_pacote(self) -> None:
        self.assertEqual(hidrantes_nbr13714.__version__, "1.0.0")

    def test_simbolos_exportados(self) -> None:
        simbolos = hidrantes_nbr13714.__all__
        self.assertIn("InstalacaoIncendio", simbolos)
        self.assertIn("TrechoRede", simbolos)
        self.assertIn("Hidrante", simbolos)
        self.assertIn("ConexoesTrecho", simbolos)
        self.assertIn("dimensionar_rede_hidrantes", simbolos)
        self.assertIn("calcular_reserva_tecnica_incendio", simbolos)
        self.assertIn("calcular_velocidade_escoamento", simbolos)
        self.assertIn("calcular_perda_carga_unitaria", simbolos)
        self.assertIn("calcular_comprimento_equivalente_conexoes", simbolos)
        self.assertIn("dimensionar_bomba_incendio", simbolos)
        self.assertIn("gerar_painel_svg", simbolos)
        self.assertIn("gerar_relatorio_texto", simbolos)
        self.assertIn("gerar_csv_sanitizado", simbolos)
        self.assertIn("gerar_pacote_zip_deterministico", simbolos)
        self.assertIn("carregar_entrada_json", simbolos)
        self.assertIn("exportar_resultado_json", simbolos)

        for s in simbolos:
            self.assertTrue(hasattr(hidrantes_nbr13714, s), f"Símbolo {s} não encontrado no módulo.")


if __name__ == "__main__":
    unittest.main()
