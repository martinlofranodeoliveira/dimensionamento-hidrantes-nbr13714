from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hidrantes_nbr13714.calculator import dimensionar_rede_hidrantes
from hidrantes_nbr13714.models import Hidrante, InstalacaoIncendio, TrechoRede
from hidrantes_nbr13714.svg_generator import gerar_painel_svg


class TestSvgGenerator(unittest.TestCase):
    def test_gerar_painel_svg_estrutura_xml(self) -> None:
        t1 = TrechoRede("T1", "2_1_2_pol", Fraction(10, 1), Fraction(260, 1), Fraction(5, 1))
        h1 = Hidrante("H1", "tipo_2", "Térreo", Fraction(5, 1))
        inst = InstalacaoIncendio("Edifício Residencial Sol", "Residencial", "tipo_2", Fraction(0, 1), (t1,), (h1,))
        res = dimensionar_rede_hidrantes(inst, "PROJ-HIDRANTES-SOL")
        svg = gerar_painel_svg(res)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        self.assertIn("1440", svg)
        self.assertIn("900", svg)
        self.assertIn("ABNT NBR 13714:2000", svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("Edifício Residencial Sol", svg)
        self.assertIn("SISTEMA CONFORME", svg)


if __name__ == "__main__":
    unittest.main()
