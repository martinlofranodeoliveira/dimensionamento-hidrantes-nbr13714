from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hidrantes_nbr13714.models import (
    ConexoesTrecho,
    Hidrante,
    InstalacaoIncendio,
    TrechoRede,
)


class TestModelos(unittest.TestCase):
    def test_conexoes_trecho_total(self) -> None:
        c = ConexoesTrecho(joelho_90=2, valvula_gaveta=1, valvula_retencao=1)
        self.assertEqual(c.total_pecas(), 4)

    def test_trecho_valido(self) -> None:
        t = TrechoRede(
            identificador="T1",
            diametro_chave="2_1_2_pol",
            comprimento_linear_m=Fraction(10, 1),
            vazao_l_min=Fraction(260, 1),
            desnivel_geometrico_m=Fraction(5, 1),
        )
        self.assertEqual(t.identificador, "T1")
        self.assertEqual(t.comprimento_linear_m, Fraction(10, 1))

    def test_trecho_invalido_comprimento_negativo(self) -> None:
        with self.assertRaises(ValueError):
            TrechoRede(
                identificador="T_Invalido",
                diametro_chave="2_1_2_pol",
                comprimento_linear_m=Fraction(-5, 1),
                vazao_l_min=Fraction(260, 1),
                desnivel_geometrico_m=Fraction(0, 1),
            )

    def test_trecho_invalido_vazao_negativa(self) -> None:
        with self.assertRaises(ValueError):
            TrechoRede(
                identificador="T_Invalido",
                diametro_chave="2_1_2_pol",
                comprimento_linear_m=Fraction(5, 1),
                vazao_l_min=Fraction(-260, 1),
                desnivel_geometrico_m=Fraction(0, 1),
            )

    def test_instalacao_invalida_sem_trechos(self) -> None:
        h = Hidrante("H1", "tipo_2", "Térreo", Fraction(1, 1))
        with self.assertRaises(ValueError):
            InstalacaoIncendio(
                nome_projeto="Sem Trechos",
                tipo_ocupacao="Residencial",
                tipo_sistema_adotado="tipo_2",
                cota_reservatorio_bomba_m=Fraction(0, 1),
                trechos=(),
                hidrantes=(h,),
            )

    def test_instalacao_tempo_reserva_invalido(self) -> None:
        t = TrechoRede("T1", "2_1_2_pol", Fraction(10, 1), Fraction(260, 1), Fraction(0, 1))
        h = Hidrante("H1", "tipo_2", "Térreo", Fraction(1, 1))
        with self.assertRaises(ValueError):
            InstalacaoIncendio("Invalido", "Residencial", "tipo_2", Fraction(0, 1), (t,), (h,), tempo_reserva_min=0)

    def test_instalacao_invalida_sem_hidrantes(self) -> None:
        t = TrechoRede("T1", "2_1_2_pol", Fraction(10, 1), Fraction(260, 1), Fraction(0, 1))
        with self.assertRaises(ValueError):
            InstalacaoIncendio(
                nome_projeto="Sem Hidrantes",
                tipo_ocupacao="Residencial",
                tipo_sistema_adotado="tipo_2",
                cota_reservatorio_bomba_m=Fraction(0, 1),
                trechos=(t,),
                hidrantes=(),
            )


if __name__ == "__main__":
    unittest.main()
