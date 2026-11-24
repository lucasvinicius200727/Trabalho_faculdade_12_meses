# RentSmart — Sistema de Orçamento de Locação (R.M Imóveis)

Aplicação em Python (somente biblioteca padrão) que calcula o orçamento mensal de locação de
apartamentos, casas e estúdios, apresenta a taxa contratual separadamente e gera um CSV com a
projeção dos 12 primeiros meses. Projeto da disciplina *Algorithmic Thinking & Introduction to
Object-Oriented Programming*.

## Requisitos
- Python 3.9 ou superior (não há dependências externas)

## Como executar
```bash
python rentsmart.py
```
O programa pergunta nome, tipo de imóvel, quartos, garagem/vagas, crianças (só apartamento) e
número de parcelas da taxa (1 a 5). Ao final, exibe o orçamento e cria `projecao_12_meses.csv`
na pasta atual.

## Como rodar os testes
```bash
python test_rentsmart.py
```

## Regras implementadas
| Tipo | Base | 2 quartos | Estacionamento |
|---|---|---|---|
| Apartamento | R$ 700,00 | + R$ 200,00 | Garagem + R$ 300,00 |
| Casa | R$ 900,00 | + R$ 250,00 | Garagem + R$ 300,00 |
| Estúdio | R$ 1.200,00 | — | Pacote de 2 vagas R$ 250,00 + R$ 60,00 por vaga adicional |

- Apartamento **sem crianças**: 5% de desconto sobre o aluguel após os adicionais (inclui garagem).
- Taxa contratual: R$ 2.000,00, em 1 a 5 parcelas, **separada do aluguel**. A diferença de centavos
  da divisão fica na última parcela (ex.: 3x → 666,66 + 666,66 + 666,68).

## Decisões de interpretação
1. O desconto de 5% incide sobre o aluguel com todos os adicionais, inclusive garagem.
2. No estúdio, estacionamento é opcional; se contratado, o mínimo é o pacote de 2 vagas.
3. Casas e apartamentos aceitam no máximo 1 vaga de garagem (o enunciado fala em "uma vaga").
4. Valores monetários usam `Decimal` para evitar erros de ponto flutuante.

## Estrutura do código
| Classe | Responsabilidade |
|---|---|
| `Imovel` (abstrata) | Contrato comum: itens do aluguel, desconto, total mensal |
| `Apartamento`, `Casa`, `Estudio` | Regras específicas de cada tipo (herança/polimorfismo) |
| `TaxaContratual` | Valor da taxa e divisão em parcelas |
| `Orcamento` | Reúne imóvel + taxa e monta o resumo ao cliente |
| `ProjecaoFinanceira` | Projeção de 12 meses e exportação do CSV |
| `InterfaceConsole` | Entrada de dados e validações |

## Formato do CSV
Separador `;`, vírgula decimal e UTF-8 com BOM (abre corretamente no Excel em português).
Colunas: `Mês; Aluguel (R$); Parcela da taxa (R$); Total do mês (R$); Acumulado (R$)`.

## Exemplo
Apartamento, 2 quartos, com garagem, sem crianças, taxa em 3x:
aluguel final R$ 1.140,00; taxa 666,66 + 666,66 + 666,68; total em 12 meses R$ 15.680,00.
(Veja `exemplo_projecao_12_meses.csv`.)
