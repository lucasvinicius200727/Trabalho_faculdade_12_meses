import unittest
from decimal import Decimal as D
from rentsmart import Apartamento, Casa, Estudio, TaxaContratual, Orcamento, ProjecaoFinanceira


class TestImoveis(unittest.TestCase):
    def test_apartamento_1_quarto(self):
        self.assertEqual(Apartamento(1, 0, True).aluguel_mensal(), D("700.00"))

    def test_apartamento_2_quartos_garagem_sem_criancas(self):
        # (700 + 200 + 300) * 0,95 = 1140
        self.assertEqual(Apartamento(2, 1, False).aluguel_mensal(), D("1140.00"))

    def test_apartamento_com_criancas_sem_desconto(self):
        self.assertEqual(Apartamento(2, 1, True).aluguel_mensal(), D("1200.00"))

    def test_casa_1_quarto(self):
        self.assertEqual(Casa(1, 0).aluguel_mensal(), D("900.00"))

    def test_casa_2_quartos_garagem(self):
        self.assertEqual(Casa(2, 1).aluguel_mensal(), D("1450.00"))

    def test_estudio_sem_vaga(self):
        self.assertEqual(Estudio(0).aluguel_mensal(), D("1200.00"))

    def test_estudio_pacote_2_vagas(self):
        self.assertEqual(Estudio(2).aluguel_mensal(), D("1450.00"))

    def test_estudio_4_vagas(self):
        self.assertEqual(Estudio(4).aluguel_mensal(), D("1570.00"))


class TestTaxaEProjecao(unittest.TestCase):
    def test_parcelas_somam_taxa(self):
        for n in range(1, 6):
            self.assertEqual(sum(TaxaContratual(n).valor_parcelas()), D("2000.00"))

    def test_tres_parcelas(self):
        self.assertEqual(TaxaContratual(3).valor_parcelas(),
                         [D("666.66"), D("666.66"), D("666.68")])

    def test_parcelas_invalidas(self):
        for n in (0, 6):
            with self.assertRaises(ValueError):
                TaxaContratual(n)

    def test_projecao_12_meses(self):
        orc = Orcamento("Teste", Casa(1, 0), TaxaContratual(5))
        linhas = ProjecaoFinanceira(orc).linhas()
        self.assertEqual(len(linhas), 12)
        self.assertEqual(linhas[0][3], D("1300.00"))   # 900 + 400
        self.assertEqual(linhas[5][3], D("900.00"))    # sem taxa
        self.assertEqual(linhas[-1][4], D("900.00") * 12 + D("2000.00"))


if __name__ == "__main__":
    unittest.main()
