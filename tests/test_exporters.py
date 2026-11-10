from fractions import Fraction
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hidrantes_nbr13714.calculator import dimensionar_rede_hidrantes
from hidrantes_nbr13714.exporters import (
    TIMESTAMP_DETERMINISTICO,
    gerar_csv_sanitizado,
    gerar_pacote_zip_deterministico,
    gerar_relatorio_texto,
    sanitizar_campo_csv,
)
from hidrantes_nbr13714.models import ConexoesTrecho, Hidrante, InstalacaoIncendio, TrechoRede


class TestExporters(unittest.TestCase):
    def setUp(self) -> None:
        t1 = TrechoRede("T1", "2_1_2_pol", Fraction(10, 1), Fraction(260, 1), Fraction(5, 1))
        h1 = Hidrante("H1", "tipo_2", "Térreo", Fraction(5, 1))
        self.inst = InstalacaoIncendio("Teste", "Residencial", "tipo_2", Fraction(0, 1), (t1,), (h1,))
        self.resultado = dimensionar_rede_hidrantes(self.inst)

    def test_sanitizacao_csv(self) -> None:
        self.assertEqual(sanitizar_campo_csv("=SOMA(1;2)"), "'=SOMA(1;2)")
        self.assertEqual(sanitizar_campo_csv("+500"), "'+500")
        self.assertEqual(sanitizar_campo_csv("-500"), "'-500")
        self.assertEqual(sanitizar_campo_csv("@cmd"), "'@cmd")
        self.assertEqual(sanitizar_campo_csv("\ttexto"), "'\ttexto")
        self.assertEqual(sanitizar_campo_csv("Hidrante H1"), "Hidrante H1")

    def test_relatorio_texto(self) -> None:
        txt = gerar_relatorio_texto(self.resultado)
        self.assertIn("MEMORIAL DE CÁLCULO DE SISTEMA DE HIDRANTES", txt)
        self.assertIn("ABNT NBR 13714:2000", txt)
        self.assertIn("DIMENSIONAMENTO DA BOMBA DE INCÊNDIO", txt)

    def test_gerar_csv_sanitizado(self) -> None:
        csv_str = gerar_csv_sanitizado(self.resultado)
        self.assertIn("Tipo_Registro,Identificador,Diametro", csv_str)
        self.assertIn("Trecho_Tubulacao,T1", csv_str)

    def test_gerar_pacote_zip_deterministico(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "pacote_hidrantes.zip"
            gerar_pacote_zip_deterministico(self.resultado, zip_path)
            self.assertTrue(zip_path.exists())

            with zipfile.ZipFile(zip_path, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("relatorio_hidrantes.txt", nomes)
                self.assertIn("dados_dimensionamento.csv", nomes)
                self.assertIn("resultado_hidrantes.json", nomes)

                for info in zf.infolist():
                    self.assertEqual(info.date_time, TIMESTAMP_DETERMINISTICO)

            with self.assertRaises(FileExistsError):
                gerar_pacote_zip_deterministico(self.resultado, zip_path)


if __name__ == "__main__":
    unittest.main()
