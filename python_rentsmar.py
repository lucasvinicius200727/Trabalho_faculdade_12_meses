"""
RentSmart - Sistema de Orçamento de Locação da R.M Imóveis.

Disciplina: Algorithmic Thinking & Introduction to Object-Oriented Programming.

Organização das classes:
    Imovel (abstrata)  -> Apartamento, Casa, Estudio   (regras de cada tipo)
    TaxaContratual                                      (valor e parcelamento)
    Orcamento                                           (junta imóvel + taxa e gera o resumo)
    ProjecaoFinanceira                                  (projeção de 12 meses e CSV)
    InterfaceConsole                                    (entrada e validação de dados)
"""

import csv
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

CENTAVO = Decimal("0.01")


# --------------------------------------------------------------------------
# Funções utilitárias
# --------------------------------------------------------------------------
def dinheiro(valor):
    """Arredonda para 2 casas (arredondamento comercial)."""
    return Decimal(valor).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def formatar_brl(valor):
    """Formata um Decimal como moeda brasileira: R$ 1.234,56."""
    texto = f"{dinheiro(valor):,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_csv(valor):
    """Número com vírgula decimal, sem símbolo (padrão do Excel em português)."""
    return f"{dinheiro(valor):.2f}".replace(".", ",")


# --------------------------------------------------------------------------
# Imóveis
# --------------------------------------------------------------------------
class Imovel(ABC):
    """Classe base: define o contrato que todo tipo de imóvel deve cumprir.

    Cada subclasse monta a lista de itens (descrição, valor) do aluguel
    mensal e o desconto aplicável. O cálculo comum fica aqui, evitando
    repetição de código nas subclasses.
    """

    nome_tipo = "Imóvel"
    ALUGUEL_BASE = Decimal("0")

    def __init__(self, quartos=1, vagas=0):
        self.quartos = quartos
        self.vagas = vagas

    @abstractmethod
    def itens_aluguel(self):
        """Lista de tuplas (descrição, valor) que compõem o aluguel bruto."""

    def desconto(self, subtotal):
        """Desconto sobre o aluguel. Por padrão não há desconto."""
        return Decimal("0.00")

    def descricao_desconto(self):
        return ""

    def aluguel_bruto(self):
        return dinheiro(sum(valor for _, valor in self.itens_aluguel()))

    def aluguel_mensal(self):
        bruto = self.aluguel_bruto()
        return dinheiro(bruto - self.desconto(bruto))

    def descricao(self):
        return self.nome_tipo


class _ImovelResidencial(Imovel):
    """Comportamento comum de casas e apartamentos (garagem a R$ 300,00)."""

    ADICIONAL_2_QUARTOS = Decimal("0")
    VAGA_GARAGEM = Decimal("300.00")

    def itens_aluguel(self):
        itens = [("Aluguel-base (1 quarto)", self.ALUGUEL_BASE)]
        if self.quartos == 2:
            itens.append(("Adicional de 2 quartos", self.ADICIONAL_2_QUARTOS))
        if self.vagas:
            itens.append(("Vaga de garagem", self.VAGA_GARAGEM))
        return itens

    def descricao(self):
        return f"{self.nome_tipo} de {self.quartos} quarto(s)"


class Apartamento(_ImovelResidencial):
    nome_tipo = "Apartamento"
    ALUGUEL_BASE = Decimal("700.00")
    ADICIONAL_2_QUARTOS = Decimal("200.00")
    DESCONTO_SEM_CRIANCAS = Decimal("0.05")

    def __init__(self, quartos=1, vagas=0, tem_criancas=True):
        super().__init__(quartos, vagas)
        self.tem_criancas = tem_criancas

    def desconto(self, subtotal):
        # 5% sobre o aluguel já com os adicionais (inclui garagem)
        if not self.tem_criancas:
            return dinheiro(subtotal * self.DESCONTO_SEM_CRIANCAS)
        return Decimal("0.00")

    def descricao_desconto(self):
        return "Desconto de 5% (sem crianças)"


class Casa(_ImovelResidencial):
    nome_tipo = "Casa"
    ALUGUEL_BASE = Decimal("900.00")
    ADICIONAL_2_QUARTOS = Decimal("250.00")


class Estudio(Imovel):
    nome_tipo = "Estúdio"
    ALUGUEL_BASE = Decimal("1200.00")
    PACOTE_INICIAL_VAGAS = 2
    VALOR_PACOTE = Decimal("250.00")
    VALOR_VAGA_EXTRA = Decimal("60.00")

    def __init__(self, vagas=0):
        super().__init__(quartos=1, vagas=vagas)

    def itens_aluguel(self):
        itens = [("Aluguel-base", self.ALUGUEL_BASE)]
        if self.vagas >= self.PACOTE_INICIAL_VAGAS:
            itens.append((f"Pacote de {self.PACOTE_INICIAL_VAGAS} vagas", self.VALOR_PACOTE))
            extras = self.vagas - self.PACOTE_INICIAL_VAGAS
            if extras:
                itens.append(
                    (f"{extras} vaga(s) adicional(is) x {formatar_brl(self.VALOR_VAGA_EXTRA)}",
                     self.VALOR_VAGA_EXTRA * extras)
                )
        return itens

    def descricao(self):
        return self.nome_tipo


# --------------------------------------------------------------------------
# Taxa contratual
# --------------------------------------------------------------------------
class TaxaContratual:
    """Taxa única do contrato (R$ 2.000,00) em até 5 parcelas."""

    VALOR = Decimal("2000.00")
    MAX_PARCELAS = 5

    def __init__(self, parcelas=1):
        if not 1 <= parcelas <= self.MAX_PARCELAS:
            raise ValueError(f"A taxa pode ser dividida em 1 a {self.MAX_PARCELAS} parcelas.")
        self.parcelas = parcelas

    def valor_parcelas(self):
        """Lista com o valor de cada parcela.

        A diferença de centavos da divisão vai para a última parcela,
        garantindo que a soma seja exatamente R$ 2.000,00.
        """
        base = (self.VALOR / self.parcelas).quantize(CENTAVO, rounding="ROUND_DOWN")
        valores = [base] * self.parcelas
        valores[-1] = self.VALOR - base * (self.parcelas - 1)
        return valores


# --------------------------------------------------------------------------
# Orçamento
# --------------------------------------------------------------------------
class Orcamento:
    """Reúne imóvel e taxa e produz o resumo para o cliente."""

    def __init__(self, cliente, imovel, taxa):
        self.cliente = cliente
        self.imovel = imovel
        self.taxa = taxa

    def aluguel_mensal(self):
        return self.imovel.aluguel_mensal()

    def resumo(self):
        linhas = []
        larg = 52
        linhas.append("=" * larg)
        linhas.append("RENTSMART - ORÇAMENTO DE LOCAÇÃO | R.M Imóveis".center(larg))
        linhas.append("=" * larg)
        linhas.append(f"Cliente: {self.cliente}")
        linhas.append(f"Imóvel : {self.imovel.descricao()}")
        linhas.append("-" * larg)
        linhas.append("ALUGUEL MENSAL")
        for descricao, valor in self.imovel.itens_aluguel():
            linhas.append(f"  {descricao:<34}{formatar_brl(valor):>16}")
        bruto = self.imovel.aluguel_bruto()
        desconto = self.imovel.desconto(bruto)
        linhas.append(f"  {'Subtotal':<34}{formatar_brl(bruto):>16}")
        if desconto > 0:
            linhas.append(f"  {self.imovel.descricao_desconto():<34}{'- ' + formatar_brl(desconto):>16}")
        linhas.append(f"  {'ALUGUEL MENSAL FINAL':<34}{formatar_brl(self.aluguel_mensal()):>16}")
        linhas.append("-" * larg)
        linhas.append("TAXA CONTRATUAL (cobrada à parte do aluguel)")
        linhas.append(f"  {'Valor total':<34}{formatar_brl(TaxaContratual.VALOR):>16}")
        parcelas = self.taxa.valor_parcelas()
        if self.taxa.parcelas == 1:
            linhas.append("  Condição: pagamento à vista (1 parcela)")
        else:
            linhas.append(f"  Condição: {self.taxa.parcelas}x de {formatar_brl(parcelas[0])}")
            if parcelas[-1] != parcelas[0]:
                linhas.append(f"  (última parcela: {formatar_brl(parcelas[-1])})")
        linhas.append("-" * larg)
        total_12 = self.aluguel_mensal() * 12 + TaxaContratual.VALOR
        linhas.append(f"  {'Total previsto em 12 meses':<34}{formatar_brl(total_12):>16}")
        linhas.append("=" * larg)
        return "\n".join(linhas)


# --------------------------------------------------------------------------
# Projeção de 12 meses e CSV
# --------------------------------------------------------------------------
class ProjecaoFinanceira:
    """Gera a projeção mês a mês do primeiro ano de contrato."""

    MESES = 12

    def __init__(self, orcamento):
        self.orcamento = orcamento

    def linhas(self):
        aluguel = self.orcamento.aluguel_mensal()
        parcelas = self.orcamento.taxa.valor_parcelas()
        resultado = []
        acumulado = Decimal("0.00")
        for mes in range(1, self.MESES + 1):
            taxa_mes = parcelas[mes - 1] if mes <= len(parcelas) else Decimal("0.00")
            total = aluguel + taxa_mes
            acumulado += total
            resultado.append((mes, aluguel, taxa_mes, total, acumulado))
        return resultado

    def exportar_csv(self, caminho="projecao_12_meses.csv"):
        """Salva o CSV (separador ';', vírgula decimal, UTF-8 com BOM p/ Excel)."""
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["Mês", "Aluguel (R$)", "Parcela da taxa (R$)",
                               "Total do mês (R$)", "Acumulado (R$)"])
            for mes, aluguel, taxa, total, acumulado in self.linhas():
                escritor.writerow([mes, formatar_csv(aluguel), formatar_csv(taxa),
                                   formatar_csv(total), formatar_csv(acumulado)])
        return caminho


# --------------------------------------------------------------------------
# Interface de console
# --------------------------------------------------------------------------
class InterfaceConsole:
    """Cuida apenas da conversa com o usuário e da validação das entradas."""

    @staticmethod
    def _ler_inteiro(pergunta, minimo, maximo):
        while True:
            texto = input(pergunta).strip()
            if texto.isdigit() and minimo <= int(texto) <= maximo:
                return int(texto)
            print(f"  Entrada inválida. Digite um número de {minimo} a {maximo}.")

    @staticmethod
    def _ler_sim_nao(pergunta):
        while True:
            texto = input(pergunta + " (s/n): ").strip().lower()
            if texto in ("s", "sim"):
                return True
            if texto in ("n", "nao", "não"):
                return False
            print("  Entrada inválida. Responda com 's' ou 'n'.")

    @staticmethod
    def _ler_nome():
        while True:
            nome = input("Nome do cliente: ").strip()
            if len(nome) >= 2 and any(c.isalpha() for c in nome):
                return nome
            print("  Informe um nome válido.")

    def coletar_imovel(self):
        print("\nTipos de imóvel: 1) Apartamento  2) Casa  3) Estúdio")
        tipo = self._ler_inteiro("Escolha o tipo (1-3): ", 1, 3)

        if tipo == 3:
            vagas = 0
            if self._ler_sim_nao("Deseja estacionamento? (pacote inicial de 2 vagas)"):
                vagas = self._ler_inteiro("Total de vagas desejadas (mínimo 2, máximo 10): ", 2, 10)
            return Estudio(vagas=vagas)

        quartos = self._ler_inteiro("Número de quartos (1 ou 2): ", 1, 2)
        vagas = 1 if self._ler_sim_nao("Deseja uma vaga de garagem?") else 0
        if tipo == 1:
            tem_criancas = self._ler_sim_nao("Possui crianças?")
            return Apartamento(quartos, vagas, tem_criancas)
        return Casa(quartos, vagas)

    def coletar_parcelas(self):
        return self._ler_inteiro("Parcelas da taxa contratual (1 a 5): ", 1, 5)

    def executar(self):
        print("=== RentSmart | R.M Imóveis ===")
        cliente = self._ler_nome()
        imovel = self.coletar_imovel()
        taxa = TaxaContratual(self.coletar_parcelas())
        orcamento = Orcamento(cliente, imovel, taxa)
        print()
        print(orcamento.resumo())
        caminho = ProjecaoFinanceira(orcamento).exportar_csv()
        print(f"\nProjeção de 12 meses salva em: {caminho}")


if __name__ == "__main__":
    InterfaceConsole().executar()
