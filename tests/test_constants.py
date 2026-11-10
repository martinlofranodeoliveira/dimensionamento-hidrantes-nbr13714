from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hidrantes_nbr13714.constants import (
    CONEXOES_EQUIVALENTES_M,
    DENSIDADE_AGUA_KGF_M3,
    PERDA_MANGUEIRA_30M_MCA,
    RENDIMENTO_PADRAO_BOMBA,
    SISTEMAS_NORMATIVOS,
    TUBOS_ACO_NBR5580,
)


class TestConstantes(unittest.TestCase):
    def test_sistemas_normativos_completos(self) -> None:
        for tipo in ("tipo_1", "tipo_2", "tipo_3", "tipo_4", "tipo_5"):
            self.assertIn(tipo, SISTEMAS_NORMATIVOS)
            dados = SISTEMAS_NORMATIVOS[tipo]
            self.assertGreater(dados["vazao_ponto_l_min"], 0)
            self.assertEqual(dados["pontos_simultaneos"], 2)
            self.assertGreater(dados["pressao_residual_minima_mca"], 0)
            self.assertGreater(dados["rti_minima_m3"], 0)

    def test_tubos_aco_nbr5580(self) -> None:
        for chave in ("1_pol", "1_1_4_pol", "1_1_2_pol", "2_pol", "2_1_2_pol", "3_pol", "4_pol"):
            self.assertIn(chave, TUBOS_ACO_NBR5580)
            t = TUBOS_ACO_NBR5580[chave]
            self.assertGreater(t["dn_mm"], 0)
            self.assertGreater(t["diametro_interno_mm"], 0)
            self.assertEqual(t["rugosidade_c"], 120)

    def test_conexoes_equivalentes(self) -> None:
        for chave in ("1_1_2_pol", "2_pol", "2_1_2_pol", "3_pol", "4_pol"):
            self.assertIn(chave, CONEXOES_EQUIVALENTES_M)
            c = CONEXOES_EQUIVALENTES_M[chave]
            self.assertIn("joelho_90", c)
            self.assertIn("valvula_retencao", c)
            self.assertIn("valvula_gaveta", c)

    def test_perda_mangueiras(self) -> None:
        self.assertIn(38, PERDA_MANGUEIRA_30M_MCA)
        self.assertIn(65, PERDA_MANGUEIRA_30M_MCA)
        self.assertIn(25, PERDA_MANGUEIRA_30M_MCA)

    def test_constantes_fisicas(self) -> None:
        self.assertEqual(DENSIDADE_AGUA_KGF_M3, 1000)
        self.assertEqual(RENDIMENTO_PADRAO_BOMBA, Fraction(65, 100))


if __name__ == "__main__":
    unittest.main()
