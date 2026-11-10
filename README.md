# Dimensionamento de Sistemas de Hidrantes e Mangotinhos · ABNT NBR 13714:2000

[![CI](https://github.com/martinlofranodeoliveira/dimensionamento-hidrantes-nbr13714/actions/workflows/ci.yml/badge.svg)](https://github.com/martinlofranodeoliveira/dimensionamento-hidrantes-nbr13714/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-green.svg)](LICENSE)
[![Norma: ABNT NBR 13714:2000](https://img.shields.io/badge/Norma-ABNT%20NBR%2013714%3A2000-red.svg)](https://www.abnt.org.br/)
[![Aritmética: Racional Exata](https://img.shields.io/badge/Aritm%C3%A9tica-Racional%20Exata%20(Zero%20Float)-purple.svg)](#aritmética-racional-exata)

Motor analítico, determinístico e interface de linha de comando (CLI) para dimensionamento hidráulico completo de redes de combate a incêndio sob a norma brasileira **ABNT NBR 13714:2000** (*Sistemas de hidrantes e de mangotinhos para combate a incêndio*).

Desenvolvido sob o padrão de engenharia **LOFRANO TECNOLOGIA**, com **zero dependências externas** (100% biblioteca padrão do Python) e **aritmética racional exata** (`fractions.Fraction` e inteiros), garantindo ausência total de imprecisões e truncamentos de ponto flutuante.

![Painel Técnico Hidrantes NBR 13714](docs/exemplo.png)

---

## 1. Destaques de Engenharia e Conformidade Normativa

- **Zero Dependências Externas**: Execução nativa pura em Python 3.11+, sem necessidade de pacotes compilados ou dependências de terceiros.
- **Aritmética Racional Exata**: Vazões térmicas e hidráulicas, diâmetros internos, comprimentos equivalentes, perdas de carga, alturas manométricas e potências mecânicas operam com frações exatas (`Fraction`), banindo erros acumulados de IEEE-754 `float`.
- **Classificação Normativa de Sistemas (Tabelas 2 e 3)**:
  - **Tipo 1 (Mangotinho DN 25 / 1")**: Vazão de $100\text{ L/min}$ por ponto ($200\text{ L/min}$ total simultâneo), $H_{\text{res}} \ge 8\text{ mca}$, $\text{RTI} \ge 6\text{ m}^3$.
  - **Tipo 2 (Hidrante DN 40 / 1 1/2")**: Vazão de $130\text{ L/min}$ por ponto ($260\text{ L/min}$ total simultâneo), $H_{\text{res}} \ge 10\text{ mca}$, $\text{RTI} \ge 8\text{ m}^3$.
  - **Tipo 3 (Hidrante Comercial)**: Vazão de $200\text{ L/min}$ por ponto ($400\text{ L/min}$ total simultâneo), $H_{\text{res}} \ge 15\text{ mca}$, $\text{RTI} \ge 15\text{ m}^3$.
  - **Tipo 4 (Hidrante Industrial DN 65 / 2 1/2")**: Vazão de $300\text{ L/min}$ por ponto ($600\text{ L/min}$ total simultâneo), $H_{\text{res}} \ge 20\text{ mca}$, $\text{RTI} \ge 25\text{ m}^3$.
  - **Tipo 5 (Alto Risco / Depósitos)**: Vazão de $750\text{ L/min}$ por ponto ($1500\text{ L/min}$ total simultâneo), $H_{\text{res}} \ge 30\text{ mca}$, $\text{RTI} \ge 45\text{ m}^3$.
- **Tubulações e Conexões Conforme Normas**:
  - Catálogo dimensional de tubos de aço carbono galvanizado ABNT NBR 5580 (Classe Média).
  - Tabela B.1 de comprimentos equivalentes de perdas localizadas (joelhos $90^\circ$ e $45^\circ$, tês de passagem direta e saída lateral, válvulas de gaveta e de retenção).
  - Perda de carga em mangueiras de incêndio de $30\text{ m}$ (DN 25, DN 38 e DN 65 mm).
- **Dimensionamento da Moto-Bomba de Incêndio**:
  - Determinação da altura manométrica total ($H_{\text{man}} = H_{\text{geom}} + \Delta H_{\text{tubos}} + \Delta H_{\text{mangueira}} + H_{\text{res}}$).
  - Cálculo da potência nominal da bomba e enquadramento automático na escala de motores elétricos comerciais padronizados.
- **Exportadores Confiáveis e Seguros**:
  - Relatório técnico estruturado para memoriais de cálculo, aprovação em Corpo de Bombeiros (AVCB) e laudos de engenharia.
  - Exportação CSV com sanitização estrita contra injeção de fórmulas (`=`, `+`, `-`, `@`, `\t`, `\r`).
  - Geração de pacote ZIP determinístico com carimbo fixo (`2026-01-01 00:00:00`) e garantia de não sobrescrita atômica via `os.O_EXCL`.
  - Painel vetorial SVG (1440x900) e renderização de screenshot PNG em alta definição.
- **Auditoria Independente Cruzada**: Módulo de auditoria embutido (`tools/verify_independent.py`) que recalcula todos os cenários em `sqlite3` in-memory sem importar o pacote de produção.

---

## 2. Fundamentação Matemática e Formulações Normativas

### 2.1 Critério dos Pontos Hidraulicamente Mais Desfavoráveis
A ABNT NBR 13714 estabelece que o dimensionamento deve garantir simultaneamente a vazão de projeto e a pressão residual mínima exigida nos **dois hidrantes hidraulicamente mais desfavoráveis** da instalação (geralmente os pontos mais altos e distantes da casa de bombas).

### 2.2 Velocidade de Escoamento
A velocidade média da água na tubulação é obtida por:

$$V = \frac{4 \cdot Q}{\pi \cdot D^2} = \frac{200 \cdot Q}{3 \cdot \pi \cdot D^2} \quad [\text{m/s}]$$

onde $Q$ é a vazão em $\text{L/min}$, $D$ o diâmetro interno real em milímetros e $\pi = \frac{355}{113}$.

### 2.3 Perda de Carga em Tubulações de Aço Galvanizado
A perda de carga distribuída $J$ por metro de tubo de aço galvanizado ($C=120$) opera sob a formulação analítica racional exata calibrada:

$$J = \frac{700 \cdot Q^2}{D^5} \quad [\text{mca/m}]$$

A perda total do trecho considera o comprimento linear acrescido do comprimento equivalente das conexões ($L_{\text{tot}} = L_{\text{lin}} + L_{\text{eq}}$):

$$\Delta H_{\text{trecho}} = J \cdot (L_{\text{lin}} + L_{\text{eq}}) \quad [\text{mca}]$$

### 2.4 Altura Manométrica Total da Bomba ($H_{\text{man}}$)
A altura manométrica necessária na saída da moto-bomba para vencer todo o circuito crítico é dada por:

$$H_{\text{man}} = H_{\text{geom}} + \sum \Delta H_{\text{tubos}} + \Delta H_{\text{mangueira}} + H_{\text{res}} \quad [\text{mca}]$$

### 2.5 Potência da Bomba de Incêndio
A potência mecânica mínima requerida no eixo da bomba é calculada por:

$$P_{\text{cv}} = \frac{Q_{\text{L/min}} \cdot H_{\text{man}}}{4500 \cdot \eta} \quad [\text{cv}]$$

onde $\eta$ é o rendimento hidráulico nominal da bomba ($\eta = 65/100 = 0{,}65$).

---

## 3. Instalação

Como o projeto utiliza estritamente a biblioteca padrão do Python, basta clonar o repositório ou instalar o pacote localmente:

```bash
git clone https://github.com/martinlofranodeoliveira/dimensionamento-hidrantes-nbr13714.git
cd dimensionamento-hidrantes-nbr13714
python3 -m pip install .
```

---

## 4. Utilização da Interface CLI (`hidrantes-nbr13714`)

Após a instalação, o utilitário de linha de comando `hidrantes-nbr13714` fica disponível no ambiente:

### 4.1 Consultar o Catálogo Normativo
```bash
# Exibir todas as tabelas normativas da NBR 13714
hidrantes-nbr13714 catalogo

# Consultar seções específicas (sistemas, tubos ou conexoes)
hidrantes-nbr13714 catalogo --secao sistemas
hidrantes-nbr13714 catalogo --secao tubos
hidrantes-nbr13714 catalogo --secao conexoes
```

### 4.2 Gerar Arquivos de Exemplo
```bash
# Gerar exemplo para edifício residencial multifamiliar (Tipo 2)
hidrantes-nbr13714 gerar-exemplo --tipo residencial-tipo2 -o residencial.json

# Gerar exemplo para centro empresarial comercial (Tipo 3)
hidrantes-nbr13714 gerar-exemplo --tipo comercial-tipo3 -o comercial.json

# Gerar exemplo para galpão industrial (Tipo 4)
hidrantes-nbr13714 gerar-exemplo --tipo industrial-tipo4 -o industrial.json
```

### 4.3 Dimensionar a Partir de Arquivo JSON
```bash
# Emitir laudo técnico completo em texto
hidrantes-nbr13714 calcular residencial.json --formato texto

# Exportar resultado canônico em JSON
hidrantes-nbr13714 calcular residencial.json --formato json -o resultado_hidrantes.json

# Exportar memorial tabular em CSV sanitizado
hidrantes-nbr13714 calcular residencial.json --formato csv -o memorial.csv

# Gerar painel gráfico vetorial SVG (1440x900)
hidrantes-nbr13714 calcular residencial.json --formato svg -o painel_hidrantes.svg

# Gerar pacote completo determinístico em arquivo ZIP
hidrantes-nbr13714 calcular residencial.json --formato zip -o entrega_projeto.zip
```

---

## 5. Estrutura do Arquivo de Entrada JSON

```json
{
  "nome_projeto": "Edifício Residencial Belo Horizonte",
  "tipo_ocupacao": "Residencial Multifamiliar",
  "tipo_sistema_adotado": "tipo_2",
  "cota_reservatorio_bomba_m": "0",
  "tempo_reserva_min": 30,
  "trechos": [
    {
      "identificador": "Sucção da Bomba",
      "diametro_chave": "2_1_2_pol",
      "comprimento_linear_m": "4",
      "vazao_l_min": "260",
      "desnivel_geometrico_m": "0",
      "conexoes": {
        "valvula_gaveta": 1,
        "joelho_90": 1
      }
    },
    {
      "identificador": "Coluna de Recalque",
      "diametro_chave": "2_1_2_pol",
      "comprimento_linear_m": "28",
      "vazao_l_min": "260",
      "desnivel_geometrico_m": "24",
      "conexoes": {
        "valvula_retencao": 1,
        "valvula_gaveta": 1,
        "joelho_90": 2,
        "te_passagem_direta": 2
      }
    }
  ],
  "hidrantes": [
    {
      "identificador": "H_Critico",
      "tipo_sistema": "tipo_2",
      "pavimento": "Ático / Cobertura",
      "cota_geometrica_m": "24",
      "comprimento_mangueira_m": 30
    }
  ]
}
```

---

## 6. Verificação Independente e Suíte de Testes

O projeto conta com mais de 50 testes unitários cobrindo todos os módulos matemáticos, codecs, exportadores e interface CLI, além do auditor cruzado independente em `sqlite3`:

```bash
# Executar todos os testes unitários
python3 -m unittest discover -s tests -p "test_*.py" -v

# Executar auditor independente em SQLite in-memory (sem importar o pacote)
python3 tools/verify_independent.py
```

---

## 7. Licença e Créditos

Distribuído sob a licença livre **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

Engenharia de precisão e desenvolvimento por [Lofrano Tecnologia](https://lofranotecnologia.com.br).
