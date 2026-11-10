from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hidrantes_nbr13714.calculator import (
    calcular_comprimento_equivalente_conexoes,
    calcular_perda_carga_unitaria,
    calcular_reserva_tecnica_incendio,
    calcular_velocidade_escoamento,
    dimensionar_bomba_incendio,
    dimensionar_rede_hidrantes,
)
from hidrantes_nbr13714.models import (
    ConexoesTrecho,
    Hidrante,
    InstalacaoIncendio,
    TrechoRede,
)


class TestCalculadora(unittest.TestCase):
    def test_calcular_comprimento_equivalente_conexoes(self) -> None:
        conexoes = ConexoesTrecho(joelho_90=2, valvula_gaveta=1, valvula_retencao=1)
        # 2_1_2_pol: joelho_90=2.5m, valvula_gaveta=0.5m, valvula_retencao=6.5m
        # Total = 2*2.5 + 0.5 + 6.5 = 5.0 + 7.0 = 12.0m
        leq = calcular_comprimento_equivalente_conexoes("2_1_2_pol", conexoes)
        self.assertEqual(leq, Fraction(12, 1))

    def test_calcular_velocidade_escoamento(self) -> None:
        # Q = 260 L/min, D = 68.7 mm (687/10 mm)
        vel = calcular_velocidade_escoamento(Fraction(260, 1), Fraction(687, 10))
        self.assertGreater(vel, 0)
        # V ~ 1.16 m/s
        self.assertTrue(Fraction(1, 1) < vel < Fraction(2, 1))

    def test_calcular_velocidade_vazao_zero(self) -> None:
        vel = calcular_velocidade_escoamento(Fraction(0, 1), Fraction(50, 1))
        self.assertEqual(vel, Fraction(0, 1))

    def test_calcular_perda_carga_unitaria(self) -> None:
        j = calcular_perda_carga_unitaria(Fraction(260, 1), Fraction(687, 10))
        self.assertGreater(j, 0)
        # j ~ 0.03 mca/m
        self.assertTrue(Fraction(2, 100) < j < Fraction(5, 100))

    def test_calcular_reserva_tecnica_incendio_tipo2(self) -> None:
        rti = calcular_reserva_tecnica_incendio("tipo_2", 30)
        # Tipo 2: 260 L/min * 30 min / 1000 = 7.8 m3 -> RTI min = 8 m3 -> max(8, 7.8) = 8 m3
        self.assertEqual(rti, Fraction(8, 1))

    def test_calcular_reserva_tecnica_incendio_tipo4(self) -> None:
        rti = calcular_reserva_tecnica_incendio("tipo_4", 60)
        # Tipo 4: 600 L/min * 60 min / 1000 = 36 m3 -> RTI min = 25 m3 -> max(25, 36) = 36 m3
        self.assertEqual(rti, Fraction(36, 1))

    def test_dimensionar_bomba_incendio(self) -> None:
        # Q = 260 L/min, Hman = 45 mca -> Pot = 11700 / 2925 = 4 cv exato
        pot, motor = dimensionar_bomba_incendio(Fraction(260, 1), Fraction(45, 1))
        self.assertEqual(pot, Fraction(4, 1))
        self.assertEqual(motor, 4)  # 4 cv comercial

    def test_dimensionar_bomba_vazao_zero(self) -> None:
        pot, motor = dimensionar_bomba_incendio(Fraction(0, 1), Fraction(30, 1))
        self.assertEqual(pot, Fraction(0, 1))
        self.assertEqual(motor, 1)

    def test_calcular_perda_carga_diametro_zero_erro(self) -> None:
        with self.assertRaises(ValueError):
            calcular_perda_carga_unitaria(Fraction(200, 1), Fraction(0, 1))

    def test_calcular_velocidade_diametro_zero_erro(self) -> None:
        with self.assertRaises(ValueError):
            calcular_velocidade_escoamento(Fraction(200, 1), Fraction(0, 1))

    def test_dimensionar_rede_tipo1_mangotinho(self) -> None:
        t1 = TrechoRede("T1", "1_1_2_pol", Fraction(15, 1), Fraction(200, 1), Fraction(8, 1))
        h1 = Hidrante("M1", "tipo_1", "1º Pavimento", Fraction(8, 1), 30)
        inst = InstalacaoIncendio("Mangotinho", "Residencial", "tipo_1", Fraction(0, 1), (t1,), (h1,))
        res = dimensionar_rede_hidrantes(inst)
        self.assertEqual(res.tipo_sistema, "tipo_1")
        self.assertEqual(res.reserva_tecnica_incendio_m3, Fraction(6, 1))
        self.assertEqual(res.vazao_de_projeto_l_min, Fraction(200, 1))

    def test_dimensionar_rede_tipo3_comercial(self) -> None:
        t1 = TrechoRede("T1", "2_1_2_pol", Fraction(25, 1), Fraction(400, 1), Fraction(20, 1))
        h1 = Hidrante("H1", "tipo_3", "Cobertura", Fraction(20, 1), 30)
        inst = InstalacaoIncendio("Comercial", "Comercial", "tipo_3", Fraction(0, 1), (t1,), (h1,))
        res = dimensionar_rede_hidrantes(inst)
        self.assertEqual(res.tipo_sistema, "tipo_3")
        self.assertEqual(res.vazao_de_projeto_l_min, Fraction(400, 1))
        self.assertEqual(res.reserva_tecnica_incendio_m3, Fraction(15, 1))

    def test_dimensionar_rede_tipo5_alto_risco(self) -> None:
        t1 = TrechoRede("T1", "4_pol", Fraction(40, 1), Fraction(1500, 1), Fraction(10, 1))
        h1 = Hidrante("H1", "tipo_5", "Pátio", Fraction(10, 1), 30)
        inst = InstalacaoIncendio("Alto Risco", "Depósito", "tipo_5", Fraction(0, 1), (t1,), (h1,))
        res = dimensionar_rede_hidrantes(inst)
        self.assertEqual(res.tipo_sistema, "tipo_5")
        self.assertEqual(res.vazao_de_projeto_l_min, Fraction(1500, 1))
        self.assertEqual(res.reserva_tecnica_incendio_m3, Fraction(45, 1))

    def test_dimensionar_rede_hidrantes_completa(self) -> None:
        t1 = TrechoRede(
            "T1",
            "2_1_2_pol",
            Fraction(20, 1),
            Fraction(260, 1),
            Fraction(15, 1),
            ConexoesTrecho(joelho_90=2, valvula_gaveta=1),
        )
        h1 = Hidrante("H1", "tipo_2", "Cobertura", Fraction(15, 1), 30)
        inst = InstalacaoIncendio(
            nome_projeto="Edifício Teste",
            tipo_ocupacao="Residencial",
            tipo_sistema_adotado="tipo_2",
            cota_reservatorio_bomba_m=Fraction(0, 1),
            trechos=(t1,),
            hidrantes=(h1,),
            tempo_reserva_min=30,
        )
        res = dimensionar_rede_hidrantes(inst, "PROJ-TESTE")
        self.assertTrue(res.sistema_conforme)
        self.assertEqual(res.identificador_projeto, "PROJ-TESTE")
        self.assertGreater(res.altura_manometrica_total_bomba_mca, Fraction(15, 1))
        self.assertEqual(res.reserva_tecnica_incendio_m3, Fraction(8, 1))


if __name__ == "__main__":
    unittest.main()
