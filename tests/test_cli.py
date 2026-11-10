from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hidrantes_nbr13714 import __version__
from hidrantes_nbr13714.cli import main


class TestCli(unittest.TestCase):
    def test_cli_sem_comando(self) -> None:
        with patch("sys.stdout", new_callable=StringIO) as out:
            ret = main([])
            self.assertEqual(ret, 0)
            self.assertIn("hidrantes-nbr13714", out.getvalue())

    def test_cli_versao(self) -> None:
        with patch("sys.stdout", new_callable=StringIO) as out:
            with self.assertRaises(SystemExit) as cm:
                main(["--versao"])
            self.assertEqual(cm.exception.code, 0)

    def test_cli_catalogo_todos(self) -> None:
        with patch("sys.stdout", new_callable=StringIO) as out:
            ret = main(["catalogo"])
            self.assertEqual(ret, 0)
            saida = out.getvalue()
            self.assertIn("TIPOS DE SISTEMAS DE HIDRANTES", saida)
            self.assertIn("TUBULAÇÕES DE AÇO CARBONO", saida)
            self.assertIn("COMPRIMENTOS EQUIVALENTES", saida)

    def test_cli_catalogo_secoes(self) -> None:
        with patch("sys.stdout", new_callable=StringIO) as out:
            self.assertEqual(main(["catalogo", "--secao", "sistemas"]), 0)
            self.assertIn("TIPOS DE SISTEMAS", out.getvalue())

        with patch("sys.stdout", new_callable=StringIO) as out:
            self.assertEqual(main(["catalogo", "--secao", "tubos"]), 0)
            self.assertIn("TUBULAÇÕES DE AÇO", out.getvalue())

        with patch("sys.stdout", new_callable=StringIO) as out:
            self.assertEqual(main(["catalogo", "--secao", "conexoes"]), 0)
            self.assertIn("COMPRIMENTOS EQUIVALENTES", out.getvalue())

    def test_cli_gerar_exemplo(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_exemplo = Path(tmpdir) / "exemplo.json"
            ret = main(["gerar-exemplo", "--tipo", "residencial-tipo2", "--saida", str(caminho_exemplo)])
            self.assertEqual(ret, 0)
            self.assertTrue(caminho_exemplo.exists())
            conteudo = caminho_exemplo.read_text(encoding="utf-8")
            self.assertIn("Edifício Residencial Belo Horizonte", conteudo)

    def test_cli_calcular_texto(self) -> None:
        exemplo = Path(__file__).resolve().parent.parent / "examples" / "edificio_residencial_belo_horizonte.json"
        with patch("sys.stdout", new_callable=StringIO) as out:
            ret = main(["calcular", str(exemplo), "--formato", "texto"])
            self.assertEqual(ret, 0)
            self.assertIn("MEMORIAL DE CÁLCULO DE SISTEMA DE HIDRANTES", out.getvalue())

    def test_cli_calcular_json(self) -> None:
        exemplo = Path(__file__).resolve().parent.parent / "examples" / "edificio_residencial_belo_horizonte.json"
        with patch("sys.stdout", new_callable=StringIO) as out:
            ret = main(["calcular", str(exemplo), "--formato", "json"])
            self.assertEqual(ret, 0)
            self.assertIn("ABNT NBR 13714:2000", out.getvalue())

    def test_cli_calcular_csv(self) -> None:
        exemplo = Path(__file__).resolve().parent.parent / "examples" / "edificio_residencial_belo_horizonte.json"
        with patch("sys.stdout", new_callable=StringIO) as out:
            ret = main(["calcular", str(exemplo), "--formato", "csv"])
            self.assertEqual(ret, 0)
            self.assertIn("Tipo_Registro,Identificador", out.getvalue())

    def test_cli_calcular_svg_e_zip(self) -> None:
        exemplo = Path(__file__).resolve().parent.parent / "examples" / "edificio_residencial_belo_horizonte.json"
        with tempfile.TemporaryDirectory() as tmpdir:
            svg_saida = Path(tmpdir) / "painel.svg"
            zip_saida = Path(tmpdir) / "pacote.zip"

            ret_svg = main(["calcular", str(exemplo), "--formato", "svg", "--saida", str(svg_saida)])
            self.assertEqual(ret_svg, 0)
            self.assertTrue(svg_saida.exists())

            ret_zip = main(["calcular", str(exemplo), "--formato", "zip", "--saida", str(zip_saida)])
            self.assertEqual(ret_zip, 0)
            self.assertTrue(zip_saida.exists())

    def test_cli_erro_arquivo_inexistente(self) -> None:
        with patch("sys.stderr", new_callable=StringIO) as err:
            ret = main(["calcular", "/tmp/fantasma_inexistente.json"])
            self.assertEqual(ret, 1)
            self.assertIn("inexistente", err.getvalue())


if __name__ == "__main__":
    unittest.main()
