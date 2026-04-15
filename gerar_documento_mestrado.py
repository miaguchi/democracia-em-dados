"""Documento-mãe consolidado — rascunho integrado para qualificação do mestrado.

Integra os três eixos empíricos do projeto Miaguchi (2023) em um único
documento narrativo:

Parte I  — Sistema partidário (eixo Peres)
Parte II — Financiamento eleitoral (eixo Speck)
Parte III — Sociologia urbana institucional (eixo Marques)
Parte IV — Perfil dos candidatos
Parte V  — Convergência temporal e síntese teórica
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

SAIDA = Path("outputs/documento_integrado_qualificacao.pdf")

# ---------- estilos ----------
styles = getSampleStyleSheet()
st_titulo = ParagraphStyle(
    "titulo", parent=styles["Title"], fontSize=18, alignment=TA_CENTER,
    spaceAfter=14, textColor=colors.HexColor("#1a1a1a"),
)
st_subt = ParagraphStyle(
    "subt", parent=styles["Normal"], fontSize=12, alignment=TA_CENTER,
    spaceAfter=6, textColor=colors.HexColor("#444"),
)
st_parte = ParagraphStyle(
    "parte", parent=styles["Heading1"], fontSize=18, alignment=TA_CENTER,
    spaceBefore=30, spaceAfter=14, textColor=colors.HexColor("#1a4dd0"),
)
st_h1 = ParagraphStyle(
    "h1", parent=styles["Heading1"], fontSize=14, spaceBefore=18, spaceAfter=8,
    textColor=colors.HexColor("#1a1a1a"),
)
st_h2 = ParagraphStyle(
    "h2", parent=styles["Heading2"], fontSize=12, spaceBefore=12, spaceAfter=6,
    textColor=colors.HexColor("#333"),
)
st_body = ParagraphStyle(
    "body", parent=styles["Normal"], fontSize=10.5, leading=15,
    alignment=TA_JUSTIFY, spaceAfter=7,
)
st_leg = ParagraphStyle(
    "leg", parent=styles["Italic"], fontSize=8, alignment=TA_CENTER,
    textColor=colors.HexColor("#555"), spaceAfter=12,
)
st_cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8, leading=11, alignment=TA_LEFT)
st_cell_c = ParagraphStyle("cell_c", parent=styles["Normal"], fontSize=8, leading=11, alignment=TA_CENTER)
st_cell_b = ParagraphStyle(
    "cell_b", parent=styles["Normal"], fontSize=8, leading=11,
    fontName="Helvetica-Bold", alignment=TA_CENTER,
)


def p(t): return Paragraph(t, st_body)
def h1(t): return Paragraph(t, st_h1)
def h2(t): return Paragraph(t, st_h2)
def parte(t): return Paragraph(t, st_parte)
def _c(t): return Paragraph(t, st_cell)
def _cc(t): return Paragraph(t, st_cell_c)
def _cb(t): return Paragraph(t, st_cell_b)


def tabela(dados, col_widths):
    t = Table(dados, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def fig(caminho, w_cm=16, legenda=None):
    out = [Image(caminho, width=w_cm * cm, height=w_cm * 0.62 * cm, kind="proportional")]
    if legenda:
        out.append(Paragraph(legenda, st_leg))
    return out


# ============================================================
# CONTEÚDO
# ============================================================
conteudo = []

# CAPA
conteudo.append(Paragraph(
    "Disputa partidária e comportamento político<br/>"
    "nos bairros ricos de São Paulo (2012–2024)",
    st_titulo,
))
conteudo.append(Paragraph(
    "Rascunho integrado de evidência empírica<br/>"
    "para o projeto de dissertação de mestrado",
    st_subt,
))
conteudo.append(Spacer(1, 0.8 * cm))
conteudo.append(Paragraph(
    "<b>Candidato:</b> Thiago Suzuki Conti Miaguchi<br/>"
    "<b>Programa:</b> Pós-Graduação em Ciência Política — DCP/FFLCH/USP<br/>"
    "<b>Orientadores indicados:</b> Bruno Wilhelm Speck, Glauco Peres da Silva<br/>"
    "<b>Referência teórica adicional:</b> Eduardo Marques (FLS 6195)",
    st_subt,
))
conteudo.append(Spacer(1, 0.8 * cm))
conteudo.append(Paragraph(
    "Este documento integra três frentes empíricas desenvolvidas como rascunho "
    "de capítulos empíricos da dissertação: (I) sistema partidário e "
    "recomposição eleitoral, (II) financiamento eleitoral e reorganização "
    "material da política, (III) sociologia urbana institucional e mapeamento "
    "ideológico. Todas as evidências usam dados públicos do TSE, IBGE e "
    "CEM/USP, com código aberto em "
    "<font color='#1a4dd0'><u>github.com/miaguchi/democracia-em-dados</u></font>.",
    st_body,
))

# ====================================================================
# SUMÁRIO EXECUTIVO
# ====================================================================
conteudo.append(PageBreak())
conteudo.append(h1("Sumário executivo"))
conteudo.append(p(
    "Este documento apresenta três descobertas empíricas sobre o "
    "comportamento eleitoral nos bairros ricos de São Paulo entre 2012 "
    "e 2024, organizadas em três eixos que correspondem às agendas de "
    "pesquisa dos orientadores indicados no projeto original."
))
conteudo.append(p(
    "<b>Descoberta 1 — Divergência interna aos bairros ricos.</b> "
    "Pinheiros (Z251) e Indianópolis (Z258), empates em renda per "
    "capita (R$ 3.819 e R$ 3.504) e ambas dominadas pelo PSDB em 2012 "
    "(~48% do voto), divergiram radicalmente até 2024: Pinheiros tem "
    "PSOL como partido #1 (28%), enquanto Indianópolis tem PL "
    "liderando (20%) com bloco direita lato sensu somando 82%. "
    "<b>Mesma origem, destinos opostos em 12 anos.</b>"
))
conteudo.append(p(
    "<b>Descoberta 2 — Reorganização material do financiamento.</b> "
    "Três eras regulatórias deixaram assinaturas distintas: em 2012, "
    "recursos PJ dominavam os bairros ricos (construtoras doando ~24% "
    "do total para vereadores); em 2016, após a reforma, pessoa física "
    "subiu a 41% do total; em 2020-2024, o FEFC reocupou o espaço com "
    "87% do financiamento via partido. <b>A democratização do "
    "financiamento durou apenas uma eleição (2016)</b>; o Fundo "
    "Especial substituiu o modelo empresarial sem passar pelo "
    "doador individual."
))
conteudo.append(p(
    "<b>Descoberta 3 — O ambiente institucional cultural-progressista "
    "foi politicamente ativado entre 2016 e 2024.</b> A renda per "
    "capita das zonas eleitorais explica apenas 9% da variância "
    "ideológica. Um índice de densidade institucional construído com "
    "a base CEM/USP (universidades, escolas particulares "
    "progressistas, escolas públicas de prestígio, instituições "
    "culturais internacionais) explica <b>44% da variância do escore "
    "ideológico de vereador em 2024</b> (R² cinco vezes maior que "
    "renda). E o dado mais surpreendente: em 2016, essa mesma "
    "correlação era <b>próxima de zero</b> — o ambiente institucional "
    "só começou a \"falar\" politicamente depois do ciclo "
    "impeachment-Bolsonaro-Lula que ativou ideologicamente o "
    "eleitorado (compatível com Inglehart &amp; Norris, 2016/2019)."
))
conteudo.append(p(
    "<b>Convergência temporal.</b> Os três eixos mostram ativação "
    "simultânea: o realinhamento partidário, a transformação do "
    "financiamento e a emergência do índice institucional como "
    "preditor acontecem <b>entre 2016 e 2020</b>, consolidando-se "
    "em 2024. Não são fenômenos independentes — são manifestações "
    "paralelas de um mesmo rearranjo estrutural do campo político-"
    "territorial paulistano."
))

# ====================================================================
# PARTE 0 — INTRODUÇÃO
# ====================================================================
conteudo.append(PageBreak())
conteudo.append(parte("Parte 0 — Introdução"))
conteudo.append(h1("Pergunta de pesquisa e recorte empírico"))
conteudo.append(p(
    "A pergunta central do projeto de dissertação (Miaguchi, 2023) é: "
    "<i>\"a nível infra-municipal, de 2012 a 2022, em bairros ricos "
    "da cidade de São Paulo, as preferências eleitorais demarcam "
    "continuidades, oscilações ou rupturas ideológicas no voto?\"</i> "
    "Este documento estende o período original até 2024 (última "
    "eleição municipal disponível) e testa empiricamente as quatro "
    "hipóteses formuladas na proposta:"
))
conteudo.append(p(
    "<b>H1</b> — há um novo padrão de preferências eleitorais nas "
    "zonas ricas que não se relaciona a movimento pendular ou a "
    "força centrípeta em torno da centro-direita."
))
conteudo.append(p(
    "<b>H2</b> — a maior pluralização dos grupos de interesse "
    "implica novo padrão de competição política, volatilidade "
    "eleitoral e representação no legislativo."
))
conteudo.append(p(
    "<b>H3</b> — o recrutamento e as disputas intrapartidárias da "
    "centro-direita ao longo do tempo produziram absorção pela "
    "direita e extrema-direita."
))
conteudo.append(p(
    "<b>H4</b> — o voto da esquerda nos bairros mais ricos e "
    "homogêneos aponta para outras variáveis independentes do que "
    "a renda ou a escolaridade."
))
conteudo.append(p(
    "<b>Recorte empírico.</b> O projeto original indica as zonas "
    "5ª (Jardim Paulista), 251ª (Pinheiros) e 258ª (Indianópolis) "
    "como unidades-chave. Este documento expande o recorte para o "
    "\"corredor das universidades\" — Bela Vista (1ª), Perdizes "
    "(2ª), Santa Ifigênia (3ª), Jardim Paulista (5ª), Vila Mariana "
    "(6ª), Pinheiros (251ª), Indianópolis (258ª) e Butantã (346ª) "
    "— e usa as 58 zonas eleitorais de SP como universo de "
    "comparação."
))
conteudo.append(p(
    "<b>Dados primários.</b> TSE (votacao_partido_munzona, "
    "votacao_candidato_munzona, votacao_secao, prestacao_contas, "
    "consulta_cand) para 2012, 2016, 2020, 2024; base de locais de "
    "votação georreferenciados EL2022_LV_ESP_CEM_V2 do Centro de "
    "Estudos da Metrópole (CEM/USP); Censo 2010 por setor "
    "censitário (IBGE); geometrias IBGE via pacote "
    "<i>geobr</i>. Escores ideológicos partidários de Bolognesi, "
    "Ribeiro &amp; Codato (2023)."
))

conteudo.append(h1("Metodologia geral"))
conteudo.append(p(
    "Três ferramentas analíticas são usadas em todas as partes:"
))
conteudo.append(p(
    "<b>(a) Volatilidade de Pedersen (1979)</b>, decomposta conforme "
    "Bartolini &amp; Mair (1990) em componentes <i>entre-blocos</i> "
    "(realinhamento real) e <i>dentro-blocos</i> (rotação intra-"
    "campo ideológico). Permite distinguir mudança de rótulo "
    "partidário de mudança de posição política."
))
conteudo.append(p(
    "<b>(b) Escore ideológico médio ponderado por votos</b>, "
    "usando os escores de Bolognesi et al. (2023) "
    "(expert survey ABCP, escala 0–10 onde 0 é extrema-esquerda "
    "e 10 é extrema-direita). Para cada zona eleitoral, média dos "
    "escores dos partidos com peso pelos votos recebidos."
))
conteudo.append(p(
    "<b>(c) Plurality bipartite por seção eleitoral</b> — "
    "classifica cada seção pelo bloco (esquerda+centro-esquerda vs "
    "centro-direita+direita) que somou mais votos. Métrica discreta, "
    "útil para identificação territorial de padrões quase-maiorias."
))
conteudo.append(p(
    "Todas as três métricas são reportadas quando relevantes, e "
    "complementam-se: a (a) isola a dimensão de sistema partidário, "
    "a (b) permite regressões contínuas, a (c) responde a pergunta "
    "\"onde a esquerda venceu?\" em forma concreta."
))

# ====================================================================
# PARTE I — SISTEMA PARTIDÁRIO (EIXO PERES)
# ====================================================================
conteudo.append(PageBreak())
conteudo.append(parte("Parte I — Sistema partidário (2012–2024)"))
conteudo.append(p(
    "<i>Evidência para H1 e H3. Agenda: sistemas partidários "
    "subnacionais, volatilidade, reorganização eleitoral. "
    "Ferramental metodológico afinado com a agenda do prof. "
    "Glauco Peres da Silva.</i>"
))

conteudo.append(h1("1.1 A mesma origem, destinos opostos: Pinheiros × Indianópolis"))
conteudo.append(p(
    "A tabela abaixo mostra o top 6 de partidos por voto de vereador "
    "em duas zonas-chave — Pinheiros (Z251) e Indianópolis (Z258), "
    "2ª e 3ª mais ricas de SP por renda per capita — em quatro "
    "ciclos municipais consecutivos:"
))
dados_pin_ind = [
    [_cb("Ano"), _cb("Pinheiros — top partidos"),
     _cb("Indianópolis — top partidos")],
    [_c("2012"),
     _c("PSDB 48% · PT 17% · PV 12% · PPS 9% · PSD 9% · PMDB 6%"),
     _c("PSDB 47% · PV 13% · PSD 13% · PT 12% · PPS 8% · PMDB 8%")],
    [_c("2016"),
     _c("<b>PSDB 36%</b> · NOVO 20% · PT 19% · PSOL 12% · PV 8% · Rede 6%"),
     _c("<b>PSDB 45%</b> · NOVO 19% · PT 13% · PV 10% · DEM 7% · PSOL 7%")],
    [_c("2020"),
     _c("<b>PSOL 28%</b> · NOVO 24% · PSDB 18% · PT 14% · Rede 8% · PSD 8%"),
     _c("<b>NOVO 29%</b> · PSDB 24% · PSOL 17% · PSD 12% · PT 10% · Patriota 9%")],
    [_c("2024"),
     _c("<b>PSOL 28%</b> · NOVO 18% · PT 17% · PSB 13% · PL 12% · Rede 11%"),
     _c("<b>PL 20%</b> · PSOL 18% · NOVO 18% · UNIÃO 17% · PP 14% · MDB 13%")],
]
conteudo.append(tabela(dados_pin_ind, [1.5*cm, 7*cm, 7*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "Em 2012, as duas zonas são quase indistinguíveis: PSDB domina "
    "com ~48% do voto e a distribuição dos partidos restantes é "
    "similar. Em 2024, elas estão em polos opostos:"
))
conteudo.append(p(
    "<b>Pinheiros:</b> PSOL vira o partido #1 em 2020 e mantém a "
    "posição em 2024. O bloco esquerda+centro-esquerda (PSOL+PT+PSB+"
    "PDT+Rede) soma 69% do voto principal em 2024."
))
conteudo.append(p(
    "<b>Indianópolis:</b> PSDB colapsa entre 2016 e 2024 (de 45% "
    "para virtualmente zero) e o voto de direita se fragmenta em "
    "cinco partidos — PL, NOVO, UNIÃO, PP, MDB — que somam 82% do "
    "voto principal. A esquerda se reduz a um PSOL residual (18%)."
))
conteudo.append(p(
    "<b>A H1 fica empiricamente confirmada:</b> não houve movimento "
    "pendular nem força centrípeta. Houve <b>divergência estrutural</b> "
    "entre zonas que começaram no mesmo ponto. A causa não pode ser "
    "renda (empatadas) nem escolaridade (ambas altas) — hipóteses "
    "testadas diretamente na Parte III deste documento."
))

conteudo.append(h1("1.2 Volatilidade Pedersen e decomposição por bloco"))
conteudo.append(p(
    "A métrica clássica de volatilidade eleitoral é o <b>Índice de "
    "Pedersen</b> (Pedersen, 1979), definido entre dois pleitos "
    "consecutivos como:"
))
conteudo.append(p(
    "<i>V = (1/2) · Σᵢ |pᵢ,t+1 − pᵢ,t|</i>, onde <i>pᵢ,t</i> é a "
    "proporção de votos do partido <i>i</i> no tempo <i>t</i>."
))
conteudo.append(p(
    "Pedersen vai de 0 (nenhuma mudança) a 1 (substituição total "
    "dos partidos). Aplicado ao voto de vereador em SP entre 2020 e "
    "2024, a média da volatilidade bruta das 57 zonas é <b>0,257</b> "
    "— na faixa \"alta\" da literatura europeia clássica de "
    "sistemas partidários. No prefeito 1º turno, a média é ainda "
    "maior: <b>0,673</b>."
))
conteudo.append(p(
    "Mas Pedersen bruto <b>não distingue</b> mudança substantiva de "
    "mudança cosmética. Se um eleitor troca PT por PSOL, isso conta "
    "como volatilidade da mesma forma que se troca PT por PL — "
    "apesar das implicações ideológicas serem radicalmente "
    "distintas. <b>Bartolini &amp; Mair (1990)</b> propõem decompor "
    "Pedersen em dois componentes:"
))
conteudo.append(p(
    "<i>V_total = V_entre_blocos + V_dentro_blocos</i>"
))
conteudo.append(p(
    "Onde <i>V_entre_blocos</i> é a volatilidade calculada sobre os "
    "agregados dos partidos em blocos ideológicos (esquerda, "
    "centro, direita), e <i>V_dentro_blocos</i> é o restante — "
    "rotação interna a cada bloco. A interpretação teórica é direta: "
    "<b>V_entre mede realinhamento ideológico genuíno; V_dentro "
    "mede reordenamento interno sem mudança de lado</b>."
))

conteudo.append(h2("1.2.1 Classificação dos partidos: escala Bolognesi et al. (2023)"))
conteudo.append(p(
    "Para decompor, precisamos classificar os partidos em blocos. "
    "Usamos os escores do <b>expert survey da ABCP</b> conduzido "
    "por Bolognesi, Ribeiro &amp; Codato (2023), que posicionam "
    "cada partido em uma escala contínua 0–10 (0 = extrema-esquerda, "
    "10 = extrema-direita). A tabela a seguir mostra os escores dos "
    "principais partidos presentes no voto de SP 2020–2024, "
    "aplicados retroativamente aos partidos hoje reagrupados em "
    "federações:"
))
dados_bolognesi = [
    [_cb("Partido"), _cb("Escore"), _cb("Bloco tripartite"),
     _cb("Bloco quintipartite")],
    [_c("PSOL"), _cc("1,28"), _c("esquerda"), _c("esquerda")],
    [_c("PCdoB"), _cc("1,92"), _c("esquerda"), _c("esquerda")],
    [_c("PT"), _cc("2,97"), _c("esquerda"), _c("esquerda")],
    [_c("Fed. PSOL/Rede (média)"), _cc("3,03"), _c("esquerda"), _c("centro-esquerda")],
    [_c("Fed. PT/PCdoB/PV (média)"), _cc("3,39"), _c("esquerda"), _c("centro-esquerda")],
    [_c("PDT"), _cc("3,92"), _c("esquerda"), _c("centro-esquerda")],
    [_c("PSB"), _cc("4,05"), _c("esquerda"), _c("centro-esquerda")],
    [_c("Rede (isolado)"), _cc("4,77"), _c("centro"), _c("centro")],
    [_c("Cidadania"), _cc("4,92"), _c("centro"), _c("centro")],
    [_c("PV"), _cc("5,29"), _c("centro"), _c("centro")],
    [_c("Fed. PSDB/Cidadania (média)"), _cc("6,02"), _c("direita"), _c("centro-direita")],
    [_c("PTB"), _cc("6,10"), _c("direita"), _c("centro-direita")],
    [_c("Avante"), _cc("6,32"), _c("direita"), _c("centro-direita")],
    [_c("<b>MDB</b>"), _cc("<b>7,01</b>"), _c("<b>direita</b>"), _c("<b>direita</b>*")],
    [_c("PSD"), _cc("7,09"), _c("direita"), _c("direita")],
    [_c("PSDB (isolado)"), _cc("7,11"), _c("direita"), _c("direita")],
    [_c("PL (ex-PR)"), _cc("7,78"), _c("direita"), _c("direita")],
    [_c("Republicanos"), _cc("7,78"), _c("direita"), _c("direita")],
    [_c("PSL"), _cc("8,11"), _c("direita"), _c("direita")],
    [_c("NOVO"), _cc("8,13"), _c("direita"), _c("direita")],
    [_c("PP (Progressistas)"), _cc("8,20"), _c("direita"), _c("direita")],
    [_c("União Brasil (DEM+PSL)"), _cc("8,34"), _c("direita"), _c("extrema-direita")],
    [_c("Patriota"), _cc("8,55"), _c("direita"), _c("extrema-direita")],
    [_c("DEM"), _cc("8,57"), _c("direita"), _c("extrema-direita")],
]
conteudo.append(tabela(dados_bolognesi, [4.5*cm, 1.5*cm, 3*cm, 4*cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(p(
    "<i>*MDB cai em 7,01, a 0,01 pontos do limiar entre centro-"
    "direita (5,51–7,00) e direita (7,01–8,50). Esta sensibilidade "
    "é discutida em 1.2.3.</i>"
))
conteudo.append(p(
    "Os limiares usados pelo próprio paper de Bolognesi et al. "
    "dividem a escala em 7 blocos: extrema-esquerda (0–1,50), "
    "esquerda (1,51–3,00), centro-esquerda (3,01–4,49), centro "
    "(4,50–5,50), centro-direita (5,51–7,00), direita (7,01–8,50) "
    "e extrema-direita (8,51–10). Para a decomposição de Pedersen, "
    "testamos duas agregações: <b>tripartite</b> (esquerda / centro / "
    "direita) e <b>quintipartite</b> (esquerda / centro-esquerda / "
    "centro / centro-direita / direita)."
))

conteudo.append(h2("1.2.2 Decomposição em duas escalas"))
conteudo.append(p(
    "A decomposição produz resultados <b>dramaticamente diferentes</b> "
    "conforme a granularidade do agrupamento:"
))
dados_ped_2 = [
    [_cb("Cargo"), _cb("V_total"), _cb("Tripartite V_entre"),
     _cb("Tripartite %"), _cb("Quintipartite V_entre"),
     _cb("Quintipartite %")],
    [_c("Vereador"), _cc("0,257"), _cc("0,007"), _cc("<b>2,6%</b>"),
     _cc("0,144"), _cc("<b>55,8%</b>")],
    [_c("Prefeito 1T"), _cc("0,673"), _cc("0,042"), _cc("<b>6,2%</b>"),
     _cc("0,352"), _cc("<b>52,3%</b>")],
]
conteudo.append(tabela(dados_ped_2, [2.5*cm, 1.5*cm, 2.3*cm, 2*cm, 2.7*cm, 2.3*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "<b>A leitura tripartite sugere que quase toda a volatilidade "
    "é intra-campo</b> — só 2,6% no vereador e 6,2% no prefeito "
    "vêm de cruzamento entre esquerda, centro e direita. A "
    "interpretação seria: \"o eleitorado paulistano não mudou de "
    "lado ideológico; apenas trocou de legenda dentro do mesmo "
    "campo\". Essa é uma leitura <i>conservadora</i> — que contraria "
    "narrativas de \"virada à direita\" que a imprensa costuma "
    "usar — mas ela depende criticamente do limiar usado."
))
conteudo.append(p(
    "<b>A leitura quintipartite muda completamente o quadro.</b> "
    "Quando separamos centro-esquerda de centro e centro-direita "
    "de direita, mais da metade da volatilidade aparece como "
    "<i>entre</i> blocos: <b>55,8% no vereador e 52,3% no prefeito</b>. "
    "A diferença entre as duas leituras não é um artefato "
    "matemático — é uma consequência direta de onde colocamos os "
    "partidos. E uma classe de partidos em particular faz quase "
    "toda a diferença entre as duas leituras: os partidos com "
    "escore em torno do limiar 7,0."
))

conteudo.append(h2("1.2.3 O problema do MDB: sensibilidade ao limiar de 0,01 ponto"))
conteudo.append(p(
    "O MDB recebe escore <b>7,01</b> na escala de Bolognesi et al. — "
    "<b>um centésimo acima do limiar</b> que separa \"centro-"
    "direita\" de \"direita\" na régua do próprio paper. É o "
    "partido mais borderline da amostra brasileira. Em 2024, "
    "Ricardo Nunes (MDB) recebeu 1,80 milhão de votos como "
    "candidato a prefeito de São Paulo — mais do que qualquer "
    "outro partido recebeu em 2020. Isso significa que a "
    "classificação do MDB <b>sozinha</b> move dramaticamente os "
    "resultados da decomposição:"
))
dados_sens = [
    [_cb("Limiar C-DIR/DIR"), _cb("Classe do MDB"),
     _cb("Vereador V_entre %"), _cb("Prefeito V_entre %")],
    [_c("7,00 (Bolognesi original)"), _c("<b>direita</b>"),
     _cc("<b>55,8%</b>"), _cc("<b>52,3%</b>")],
    [_c("7,05"), _c("centro-direita"), _cc("29,8%"), _cc("<b>8,5%</b>")],
    [_c("7,10"), _c("centro-direita"), _cc("29,1%"), _cc("10,8%")],
    [_c("7,20"), _c("centro-direita"), _cc("29,1%"), _cc("10,8%")],
    [_c("7,50"), _c("centro-direita"), _cc("34,4%"), _cc("22,5%")],
]
conteudo.append(tabela(dados_sens, [4*cm, 3*cm, 3.5*cm, 3.5*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "No caso do prefeito, mover o MDB para centro-direita (limiar "
    "7,05) faz a volatilidade entre-blocos <b>despencar de 52,3% "
    "para 8,5%</b>. É uma diferença de <b>44 pontos percentuais</b> "
    "produzida por uma única decisão binária sobre um único "
    "partido. A razão é que o MDB de Nunes concentrou cerca de "
    "30% dos votos de prefeito em 2024 — e colocá-lo em um bloco "
    "ou outro determina quase sozinho se há realinhamento aparente "
    "ou não."
))
conteudo.append(p(
    "<b>Por que isso importa?</b> Do ponto de vista substantivo, "
    "o MDB de Ricardo Nunes em SP 2024 é herdeiro institucional "
    "direto do ciclo covista/serrista — Nunes foi vice-prefeito de "
    "Covas, assumiu o cargo com a morte de Covas em 2021, e "
    "construiu sua candidatura em 2024 como continuidade do "
    "projeto PSDB anterior, inclusive em alianças partidárias e "
    "base de apoio. Classificá-lo como \"direita plena\" junto "
    "com PL, NOVO e PP é uma escolha metodológica que <b>depende "
    "do recorte teórico de Bolognesi et al. em 2018</b> — "
    "escorado em survey realizado antes do ciclo Bolsonaro — e "
    "não necessariamente reflete a posição substantiva do MDB "
    "paulistano em 2024."
))
conteudo.append(p(
    "<b>Consequência metodológica:</b> ambas as leituras "
    "(tripartite e quintipartite com limiar 7,00) são defensáveis "
    "e reportamos as duas explicitamente. A leitura tripartite "
    "é mais conservadora e produz o achado \"quase toda a "
    "volatilidade é intra-campo\". A leitura quintipartite com "
    "limiar original é mais polarizante e produz \"metade é "
    "realinhamento entre blocos\". A leitura quintipartite com "
    "limiar 7,05 produz resultado quase igual à tripartite — "
    "sugerindo que <b>o que a Bolognesi chama de \"direita\" e "
    "\"centro-direita\" não é uma distinção empiricamente "
    "rigorosa para o voto majoritário em SP 2024</b>, sendo "
    "dependente de onde colocamos um único partido borderline."
))
conteudo.append(p(
    "Para propósitos da dissertação, o achado substantivo robusto "
    "à escolha é: <b>o campo esquerda+centro-esquerda tem "
    "proporção estável em 2020 e 2024 em todas as escalas</b> "
    "(vereador SP: 31,1% → 31,4%; prefeito SP: 43,2% → 39,0%). "
    "A oscilação mais relevante ocorre <i>dentro</i> do espaço "
    "não-esquerda — ou seja, entre candidatos e partidos que "
    "competem pelo eleitor de centro-direita/direita. A "
    "classificação exata desses partidos em subcategorias é "
    "sensível a decisões metodológicas, mas a conclusão de que "
    "<b>a esquerda não cresceu nem encolheu substancialmente</b> "
    "sobrevive a todas as escolhas testadas."
))

conteudo.append(h1("1.3 Mapa espacial da volatilidade"))
conteudo.extend(fig(
    "outputs/lisa_volatilidade_sp_vereador_2020_2024.png",
    w_cm=15,
    legenda="Figura 1.1 — LISA (Moran Local) da volatilidade por zona "
    "eleitoral, vereador SP 2020-2024. Moran I global = 0,42 "
    "(p = 0,001, k = 6 vizinhos, 999 permutações). Clusters "
    "HH (voláteis) na periferia norte-noroeste; clusters LL "
    "(estáveis) na periferia sul.",
))

conteudo.append(h1("1.4 Mapas do espectro ideológico por zona"))
conteudo.append(p(
    "Enquanto a volatilidade Pedersen responde \"quanto o voto "
    "mudou\", o mapa do escore médio ponderado (Bolognesi et al.) "
    "responde \"onde está o centro de gravidade ideológico de cada "
    "zona\". Os dois mapas abaixo usam escala contínua centrada em "
    "5,0 via <i>TwoSlopeNorm</i>, com convenção política brasileira "
    "(vermelho = esquerda, azul = direita):"
))
conteudo.extend(fig(
    "outputs/mapa_escore_prefeito_2020_2024.png",
    w_cm=16,
    legenda="Figura 1.2 — Escore ideológico médio ponderado por voto, "
    "prefeito 1º turno, SP 2020 (esquerda) e 2024 (direita). "
    "Escala centrada em 5,0 (centro); vermelho = esquerda, azul = "
    "direita. Entre os dois painéis a cidade se desloca +0,40 "
    "pontos no eixo ideológico.",
))
conteudo.extend(fig(
    "outputs/mapa_escore_vereador_2020_2024.png",
    w_cm=16,
    legenda="Figura 1.3 — Escore ideológico médio ponderado por voto, "
    "vereador, SP 2020 e 2024. A cidade inteira está do lado "
    "direito do centro (escore > 5) em ambos os anos, mas com "
    "gradiente visível. Bela Vista e Pinheiros (centro oeste) são "
    "as mais à esquerda da cidade nos dois ciclos.",
))
conteudo.append(p(
    "<b>Interpretação substantiva:</b> o deslocamento da média da "
    "cidade entre 2020 e 2024 é <b>+0,40 pontos</b> no prefeito e "
    "<b>+0,19 pontos</b> no vereador — ambos pequenos em uma "
    "escala 0–10 mas coerentes com a narrativa de \"direitização\" "
    "do voto paulistano no ciclo recente. O efeito é, porém, "
    "muito mais acentuado no executivo (prefeito) do que no "
    "legislativo (vereador), refletindo a dinâmica de rotação da "
    "oferta majoritária (Covas → Nunes, emergência de Marçal) "
    "em relação à maior estabilidade da composição legislativa."
))
conteudo.append(p(
    "<b>Alerta de leitura:</b> os mapas são dominados por tons "
    "claros (próximos de 5) porque a distribuição real do voto "
    "médio ponderado entre as zonas de SP fica concentrada entre "
    "5,0 e 6,7 — ou seja, todas as zonas da cidade ficam em "
    "alguma versão do centro ou do centro-direita na escala "
    "Bolognesi. A variação intra-cidade é relevante (até 1 ponto "
    "de escore entre zona mais à esquerda e mais à direita), mas "
    "é numericamente pequena em relação à escala 0–10 completa. "
    "Isto é consistente com o achado de 1.2: o eleitorado "
    "paulistano não transita entre campos opostos — ele se "
    "reorganiza dentro de um corredor ideológico relativamente "
    "estreito, com a variação relevante ocorrendo dentro do que "
    "Bolognesi chama de \"centro-direita e direita\"."
))

# ====================================================================
# PARTE II — FINANCIAMENTO (EIXO SPECK)
# ====================================================================
conteudo.append(PageBreak())
conteudo.append(parte("Parte II — Financiamento eleitoral (2012–2024)"))
conteudo.append(p(
    "<i>Evidência para H3 com dimensão material. Agenda: "
    "financiamento de campanhas, reformas políticas e "
    "recomposição da direita. Ferramental afinado com a agenda do "
    "prof. Bruno Wilhelm Speck.</i>"
))

conteudo.append(h1("2.1 Três eras regulatórias"))
conteudo.append(p(
    "A receita declarada pelos candidatos a vereador de SP nos "
    "quatro ciclos municipais (2012-2024) revela três eras "
    "regulatórias claramente distintas:"
))
dados_eras = [
    [_cb("Ano"), _cb("Total R$ mi"), _cb("Partido %"), _cb("PF %"),
     _cb("PJ %"), _cb("Próprio %"), _cb("Era")],
    [_c("2012"), _cc("93,1"), _cc("41,7"), _cc("0,0"), _cc("<b>23,8</b>"),
     _cc("8,0"), _c("PJ permitida")],
    [_c("2016"), _cc("43,1"), _cc("28,0"), _cc("<b>41,0</b>"), _cc("0,0"),
     _cc("21,7"), _c("Pós-reforma transicional")],
    [_c("2020"), _cc("84,0"), _cc("65,0"), _cc("23,7"), _cc("0,0"),
     _cc("8,1"), _c("FEFC inicial")],
    [_c("2024"), _cc("<b>209,4</b>"), _cc("<b>86,7</b>"), _cc("9,1"), _cc("0,0"),
     _cc("2,2"), _c("FEFC consolidado")],
]
conteudo.append(tabela(dados_eras, [1.5*cm, 2*cm, 2*cm, 1.5*cm, 1.5*cm, 2*cm, 4.5*cm]))
conteudo.append(Spacer(1, 0.3 * cm))

conteudo.extend(fig(
    "outputs/grafico_trajetoria_financiamento.png",
    w_cm=15,
    legenda="Figura 2.1 — Trajetória das fontes de financiamento dos "
    "vereadores SP em quatro ciclos municipais (2012-2024).",
))

conteudo.append(p(
    "Em 2012, empresas como construtoras, bancos e empresas de "
    "engenharia doavam diretamente aos candidatos a vereador em SP: "
    "<b>R$ 22,2 milhões (24% do total)</b> vieram de pessoa jurídica. "
    "A reforma de 2015 proibiu esse canal. Em 2016, a reforma "
    "funcionou conforme a expectativa dos reformistas — pessoa "
    "física passou a 41% e recursos próprios a 22%, fazendo os "
    "candidatos mobilizarem diretamente seus eleitores-doadores. "
    "<b>Mas durou só uma eleição.</b>"
))
conteudo.append(p(
    "Em 2020, o FEFC (Fundo Especial de Financiamento de Campanha) "
    "criado em 2017 começou a dominar, repassando dinheiro público "
    "aos partidos, que por sua vez o distribuem aos candidatos. Em "
    "2024, <b>86,7% da receita vem de partido</b>, e a participação "
    "direta do eleitor-doador (PF + crowdfunding) é apenas 9,5%. "
    "<b>O Fundo Especial substituiu o modelo empresarial de 2012, "
    "não o modelo de PF de 2016</b> — a democratização reformista "
    "foi breve e foi estatizada."
))

conteudo.append(h1("2.2 Trajetória individual por zona"))
conteudo.append(p(
    "Ao nível de candidato individual por zona, a transformação "
    "é ainda mais nítida. A tabela a seguir mostra a média "
    "ponderada de pessoa física, pessoa jurídica e partido dos 6 "
    "candidatos mais votados nas zonas-chave:"
))
dados_traj = [
    [_cb("Zona / Ano"), _cb("% PF"), _cb("% Partido"), _cb("% PJ"),
     _cb("Partidos dominantes")],
    [_c("<b>Pinheiros</b> 2012"), _cc("0%"), _cc("51%"), _cc("<b>37%</b>"),
     _c("PSDB, PT, PPS, PV")],
    [_c("Pinheiros 2016"), _cc("<b>68%</b>"), _cc("2%"), _cc("0%"),
     _c("PT, PSDB, NOVO, Rede")],
    [_c("Pinheiros 2020"), _cc("59%"), _cc("29%"), _cc("0%"),
     _c("PT, NOVO, PSOL, PSDB")],
    [_c("Pinheiros 2024"), _cc("18%"), _cc("<b>77%</b>"), _cc("0%"),
     _c("NOVO, Rede, PT, PSOL")],
    [_c("<b>Indianópolis</b> 2012"), _cc("0%"), _cc("43%"), _cc("<b>46%</b>"),
     _c("PSDB, PV, PPS, PSD")],
    [_c("Indianópolis 2016"), _cc("<b>59%</b>"), _cc("0%"), _cc("0%"),
     _c("PT, PSDB, DEM, NOVO")],
    [_c("Indianópolis 2020"), _cc("57%"), _cc("25%"), _cc("0%"),
     _c("NOVO, PSD, PT, Patriota")],
    [_c("Indianópolis 2024"), _cc("10%"), _cc("<b>88%</b>"), _cc("0%"),
     _c("NOVO, PP, PL, Rede, PSOL")],
]
conteudo.append(tabela(dados_traj, [3*cm, 1.5*cm, 2*cm, 1.5*cm, 6*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "<b>Dois achados desmontam narrativas correntes na literatura:</b>"
))
conteudo.append(p(
    "<b>(i) O PSDB dos bairros ricos NÃO era sustentado por doador "
    "individual.</b> A imagem canônica do tucanato paulistano — "
    "classe média progressista financiando seus candidatos — é "
    "<b>falsa</b> para vereador em 2012: 37% em Pinheiros e 46% em "
    "Indianópolis vieram de pessoa jurídica (empresarial), <b>zero</b> "
    "de pessoa física. O PSDB pré-reforma era empresarial como "
    "qualquer outro partido brasileiro da direita."
))
conteudo.append(p(
    "<b>(ii) A democratização do financiamento existiu, foi breve "
    "e desapareceu.</b> Entre 2016 e 2020, os candidatos mais "
    "votados nos bairros ricos captavam 57-68% via pessoa física. "
    "O FEFC — criado em 2017 e inflado a cada ciclo — reocupou esse "
    "espaço. Em 2024, a PF volta a ser residual (10-18%) nas mesmas "
    "zonas. <b>O eleitor-doador de Pinheiros existiu eleitoralmente "
    "por uma janela de 4-8 anos e foi estatizado.</b>"
))

conteudo.append(h1("2.3 Quem eram os doadores empresariais em 2012?"))
conteudo.append(p(
    "A categoria \"recursos de pessoa jurídica\" que somou R$ 22,2 "
    "milhões para vereadores de SP em 2012 não é abstrata — "
    "é composta por 1.574 doações individuais de empresas a "
    "candidatos. A análise setorial dessas doações revela um "
    "padrão bem conhecido na literatura brasileira (Mancuso &amp; "
    "Speck, 2015): dominância absoluta de setores ligados à "
    "infraestrutura, construção civil e serviços financeiros:"
))
dados_setores = [
    [_cb("Setor econômico do doador"), _cb("R$ total"), _cb("N. doações")],
    [_c("Construção de edifícios"), _cc("R$ 3.791.200"), _cc("75")],
    [_c("Incorporação de empreendimentos imobiliários"), _cc("R$ 1.964.500"), _cc("50")],
    [_c("Outras obras de engenharia civil"), _cc("R$ 1.960.000"), _cc("25")],
    [_c("Bancos múltiplos com carteira comercial"), _cc("R$ 938.500"), _cc("19")],
    [_c("Construção de rodovias e ferrovias"), _cc("R$ 733.920"), _cc("25")],
    [_c("Obras de montagem industrial"), _cc("R$ 715.000"), _cc("5")],
    [_c("Atividades de organizações políticas"), _cc("R$ 508.080"), _cc("81")],
    [_c("Edição e impressão de cadastros"), _cc("R$ 409.370"), _cc("119")],
    [_c("Comércio varejista de combustíveis"), _cc("R$ 360.086"), _cc("20")],
    [_c("Serviços de engenharia"), _cc("R$ 298.180"), _cc("20")],
    [_c("Vigilância e segurança privada"), _cc("R$ 256.360"), _cc("6")],
]
conteudo.append(tabela(dados_setores, [9*cm, 3.5*cm, 2.5*cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(p(
    "<b>Construção civil e imobiliário somados (edifícios, "
    "incorporação, engenharia civil, rodovias, montagem industrial) "
    "respondem por R$ 9,9 milhões — 45% de todo o financiamento "
    "empresarial de vereadores em SP 2012</b>. A participação dos "
    "bancos é de R$ 938 mil (4%). Os demais setores (combustíveis, "
    "vigilância, engenharia) são relevantes mas menores. Há uma "
    "concentração setorial notável: <b>construtoras financiavam a "
    "política municipal paulistana</b> — um padrão coerente com a "
    "intersecção entre licenciamento urbanístico, contratos de "
    "obras públicas e decisões de plano diretor no âmbito da "
    "Câmara Municipal."
))
conteudo.append(p(
    "<b>No nível das empresas individualmente</b>, os 10 maiores "
    "doadores concentravam R$ 6,1 milhões:"
))
dados_empresas = [
    [_cb("Empresa"), _cb("R$ total doado")],
    [_c("WTORRE ENGENHARIA E CONSTRUÇÃO S.A."), _cc("R$ 900.000")],
    [_c("CONSTRUTORA OAS LTDA"), _cc("R$ 900.000")],
    [_c("ITAÚ UNIBANCO S.A."), _cc("R$ 838.000")],
    [_c("UTC ENGENHARIA S/A"), _cc("R$ 700.000")],
    [_c("S.A. PAULISTA DE CONSTRUÇÕES E COMÉRCIO"), _cc("R$ 545.000")],
    [_c("CONSTRUTORA PASSARELLI LTDA"), _cc("R$ 505.000")],
    [_c("DP BARROS PAVIMENTAÇÃO E CONSTRUÇÃO"), _cc("R$ 450.000")],
    [_c("WIN WORK PINHEIROS EMPREENDIMENTO IMOBILIÁRIO"), _cc("R$ 450.000")],
    [_c("SARDENHA INCORPORAÇÃO SPE LTDA"), _cc("R$ 400.000")],
    [_c("MPC ENGENHARIA LTDA"), _cc("R$ 396.000")],
]
conteudo.append(tabela(dados_empresas, [10*cm, 4*cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(p(
    "Duas das dez maiores doadoras de vereadores de SP em 2012 — "
    "<b>OAS</b> e <b>UTC Engenharia</b> — viriam a ser citadas "
    "centralmente nos desdobramentos da Operação Lava Jato a partir "
    "de 2014, que terminaria por justificar a reforma do "
    "financiamento eleitoral de 2015. <b>WTorre</b>, <b>S.A. "
    "Paulista</b>, <b>Passarelli</b> e <b>MPC Engenharia</b> são "
    "construtoras paulistanas tradicionais, parte do tecido "
    "empresarial-político do município. <b>Itaú Unibanco</b> é o "
    "único banco no top 10 — e sua presença evidencia que o "
    "financiamento empresarial não era restrito a empreiteiras."
))
conteudo.append(p(
    "<b>Relevância para a dissertação:</b> este padrão não é "
    "surpresa na literatura (Mancuso, 2012; Mancuso &amp; Speck, "
    "2015; Sacchet &amp; Speck, 2012), mas os dados individualizados "
    "por candidato em SP — cruzados com os resultados eleitorais das "
    "seções anteriores — permitem dimensionar <b>quanto da "
    "infraestrutura material dos vereadores do corredor das "
    "universidades vinha diretamente dessas empresas</b>. Em 2012, "
    "praticamente metade do financiamento dos vereadores PSDB mais "
    "votados em Pinheiros e Indianópolis era <b>construtora</b> ou "
    "<b>banco</b>. Não era \"doador individual de classe média\"."
))

conteudo.append(h1("2.4 A trajetória dinástica: Matarazzo, Covas, Monteiro"))
conteudo.append(p(
    "A Parte I deste documento mostrou que Pinheiros e Indianópolis "
    "começam a série com PSDB 47–48% em 2012 e terminam com PSOL "
    "ou PL dominando em 2024. Mas essa transição partidária "
    "esconde uma história de <b>sucessão institucional</b> que "
    "vale detalhar, porque ela toca diretamente na H3 (recomposição "
    "da direita) e na discussão sobre continuidade entre o "
    "antigo \"voto PSDB\" e o novo \"voto Novo\":"
))
dados_trajetoria = [
    [_cb("Ano"), _cb("Pinheiros (Z251) — top 3"),
     _cb("Indianópolis (Z258) — top 3")],
    [_c("<b>2012</b>"),
     _c("<b>Ângelo Matarazzo (PSDB)</b> 9.606v · "
       "Nabil Bonduki (PT) 4.742v · "
       "Floriano Pesaro (PSDB) 3.392v"),
     _c("<b>Ângelo Matarazzo (PSDB)</b> 11.968v · "
       "Mario Covas Neto (PSDB) 5.046v · "
       "José Alvarenga (PV) 4.907v")],
    [_c("<b>2016</b>"),
     _c("<b>Eduardo Suplicy (PT)</b> 5.392v · "
       "Daniel Annenberg (PSDB) 2.849v · "
       "Mario Covas Neto (PSDB) 2.785v"),
     _c("<b>Eduardo Suplicy (PT)</b> 5.881v · "
       "Mario Covas Neto (PSDB) 5.752v · "
       "Fernando Bispo (DEM) 3.116v")],
    [_c("<b>2020</b>"),
     _c("Eduardo Suplicy (PT) 2.324v · "
       "<b>Janaína Carla (NOVO)</b> 2.070v · "
       "Erika Silva (PSOL) 1.807v"),
     _c("<b>Janaína Carla (NOVO)</b> 3.322v · "
       "Felipe Becari (PSD) 2.675v · "
       "Eduardo Suplicy (PT) 2.587v")],
    [_c("<b>2024</b>"),
     _c("<b>Cristina Monteiro (NOVO)</b> 5.552v · "
       "<b>Marina Bragante (Rede)</b> 5.286v · "
       "Nabil Bonduki (PT) 3.534v"),
     _c("<b>Cristina Monteiro (NOVO)</b> 6.553v · "
       "Janaína Paschoal (PP) 3.773v · "
       "Lucas Pavanato (PL) 3.535v")],
]
conteudo.append(tabela(dados_trajetoria, [1.5*cm, 7*cm, 7*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "<b>A trajetória em 4 atos.</b> Em 2012, <b>Ângelo Andrea "
    "Matarazzo</b> (PSDB, sobrinho do ex-deputado Andrea Matarazzo "
    "e integrante da tradicional família de empresários paulistanos "
    "Matarazzo) é o vereador mais votado em ambas as zonas-chave, "
    "com quase 22 mil votos somados. O segundo mais votado em "
    "Indianópolis é <b>Mario Covas Neto</b> — sobrinho-neto do "
    "ex-prefeito/ex-governador Mario Covas e do então prefeito "
    "Bruno Covas. Ou seja: em 2012, <b>duas dinastias paulistanas "
    "tradicionais (Matarazzo e Covas) dominavam a representação de "
    "Pinheiros e Indianópolis pelo PSDB</b>, em forma quase "
    "literal de continuidade familiar-partidária."
))
conteudo.append(p(
    "Em 2016, já aparece o primeiro sinal de reorganização: "
    "<b>Eduardo Matarazzo Suplicy (PT)</b>, senador histórico do "
    "PT e ele próprio herdeiro da família Matarazzo por lado "
    "materno, entra na disputa de vereador como estratégia "
    "simbólica do PT para \"reocupar\" os bairros ricos. Suplicy "
    "vence em Pinheiros (5.392 votos) e Indianópolis (5.881 "
    "votos), derrotando os candidatos do PSDB. O PSDB mantém "
    "presença via Daniel Annenberg e, curiosamente, Mario Covas "
    "Neto em ambas as zonas — mas em posições secundárias."
))
conteudo.append(p(
    "Em 2020, acontece a primeira aparição no topo de <b>Janaína "
    "Carla de Lima</b>, candidata do NOVO com captação "
    "<b>99% pessoa física</b> e perfil de \"renovação liberal "
    "jovem\". Ela assume a 2ª posição em Pinheiros e a 1ª em "
    "Indianópolis. O PSDB não aparece mais no top 3 em nenhuma "
    "das zonas. Suplicy (PT) ainda está presente mas cai de "
    "posição. O PSOL entra com Erika Silva em Pinheiros — "
    "primeira aparição no top 3 da zona."
))
conteudo.append(p(
    "Em 2024, a transição se consolida. <b>Cristina Monteiro "
    "(NOVO)</b> — ex-PSDB, migrou para o Novo em 2018, "
    "vereadora atual em seu segundo mandato — é a mais votada em "
    "ambas as zonas, com 12.105 votos somados. <b>Marina Bragante "
    "(Rede)</b>, psicóloga, é a 2ª em Pinheiros. O PT sobrevive "
    "pela figura de <b>Nabil Bonduki</b> — professor titular da "
    "FAU-USP, arquiteto-urbanista — que é a mesma pessoa que "
    "apareceu no top 3 de Pinheiros em 2012. Bonduki é o elo "
    "simbólico de continuidade do PT em Pinheiros ao longo dos "
    "12 anos, embora agora ocupando posição secundária."
))
conteudo.append(p(
    "<b>O significado substantivo da transição Matarazzo → "
    "Monteiro:</b> o voto do eleitor \"rico tradicional\" "
    "(Jardim Paulista, Indianópolis, Pinheiros) manteve — em "
    "termos de perfil sociológico e de quem ele é — um "
    "<b>padrão de continuidade</b>. Mudaram os nomes dos candidatos "
    "e mudou o partido carregador (PSDB → NOVO), mas a estrutura "
    "de representação institucional preservada é reconhecível: "
    "candidata-celebridade de direita-liberal cosmopolita (Cristina "
    "Monteiro hoje, Ângelo Matarazzo em 2012) com voto "
    "concentrado nos mesmos locais de votação. O caso análogo no "
    "Executivo é <b>Ricardo Nunes (MDB)</b> — vice-prefeito de "
    "Bruno Covas, assumiu com sua morte em 2021, elege-se em 2024: "
    "continuidade institucional quase literal do ciclo Covas, por "
    "dentro de um partido diferente. A reorganização partidária é "
    "<b>cosmética</b> no sentido de que as <i>pessoas</i> e as "
    "<i>famílias</i> que exerciam a representação política dos "
    "bairros ricos em 2012 (ou seus herdeiros institucionais "
    "diretos) continuam exercendo em 2024 — só que agora via "
    "legendas diferentes."
))

conteudo.append(h1("2.5 Implicações para a H3 do projeto"))
conteudo.append(p(
    "A Hipótese 3 afirmava que <i>\"o recrutamento e as disputas "
    "intrapartidárias da centro-direita ao longo do tempo "
    "influenciaram o novo comportamento eleitoral marcado pela "
    "contestação. Destarte, a centro-direita foi atraída pelo "
    "campo da direita e extrema-direita\"</i>. Os achados das "
    "seções 2.1–2.4 permitem reformular a hipótese com maior "
    "precisão empírica:"
))
conteudo.append(p(
    "<b>A centro-direita brasileira pós-2020 é uma fase específica "
    "no ciclo regulatório do financiamento</b>, não um movimento "
    "autônomo do eleitorado. O PSDB de SP perde base em quatro "
    "dimensões simultâneas: (a) <i>eleitoral</i>, via colapso do "
    "voto de vereador e prefeito; (b) <i>institucional</i>, via "
    "migração de quadros para Novo, MDB e PL; (c) <i>material</i>, "
    "via perda da infraestrutura de financiamento empresarial "
    "(PJ proibida em 2015) sem reconstrução do canal pessoa "
    "física (reocupado pelo FEFC em 2020-2024); (d) <i>simbólica</i>, "
    "via substituição das dinastias familiares tradicionais "
    "(Matarazzo, Covas) por candidatos-celebridade de perfil "
    "liberal cosmopolita vinculados ao Novo ou ao próprio MDB."
))
conteudo.append(p(
    "<b>Mas — e isto é central — a H3 na formulação original "
    "parece sugerir que a centro-direita foi \"absorvida\" pela "
    "direita pura e dura. Os dados mostram algo mais sutil</b>: "
    "a centro-direita paulistana da era Covas/Serra foi absorvida "
    "em partes por diferentes destinos. Parte migrou para o Novo "
    "(voto \"renovação liberal\" que capta PF ativamente — Cristina "
    "Monteiro, Janaína Carla). Parte para o MDB de Nunes "
    "(continuidade institucional direta do ciclo Covas, via "
    "sucessor indicado). Parte para o PL/PP (voto conservador "
    "duro, captação 100% FEFC). O \"ataque à direita\" existe, "
    "mas é uma dispersão — não uma absorção unilateral. O "
    "colapso do PSDB é real; a reorganização da oferta "
    "partidária ocorre em <b>múltiplas direções simultâneas</b>."
))

# ====================================================================
# PARTE III — SOCIOLOGIA URBANA INSTITUCIONAL (EIXO MARQUES)
# ====================================================================
conteudo.append(PageBreak())
conteudo.append(parte("Parte III — Sociologia urbana institucional"))
conteudo.append(p(
    "<i>Evidência para H4. Agenda: ecologia eleitoral, sociologia "
    "urbana, ambientes institucionais. Ferramental afinado com a "
    "agenda do prof. Eduardo Marques (FLS 6195 — Cidades, Governo e "
    "Políticas Públicas) e dialogando com a escola paulistana de "
    "sociologia urbana (Marques, Torres et al., Torres, Bichir).</i>"
))

conteudo.append(h1("3.0 Moldura teórica: a escola paulistana e o ambiente institucional"))
conteudo.append(p(
    "A agenda de pesquisa sobre estratificação socioeconômica do "
    "espaço metropolitano de São Paulo, consolidada no grupo "
    "Marques–Torres–Bichir (ver Marques, 2015; Torres, Marques, "
    "Ferreira &amp; Bichir, 2003; Marques, Scalon &amp; Oliveira, "
    "2018), estabeleceu três teses empíricas que moldam este "
    "capítulo:"
))
conteudo.append(p(
    "<b>(i) A hierarquia socioeconômica intra-metropolitana de SP "
    "é extraordinariamente estável no tempo.</b> Torres et al. "
    "(2003), usando dados de 1991 e 2000, mostram que os bairros "
    "de alta renda do centro-oeste paulistano (Pinheiros, Jardim "
    "Paulista, Itaim, Vila Olímpia, Morumbi) mantêm sua posição "
    "relativa no ranking de renda há décadas. Marques (2015) "
    "estende esse argumento até os anos 2010, mostrando que a "
    "segregação por renda é um atributo quase invariante da "
    "estrutura urbana paulistana. Isso é o que justifica usar "
    "dados do Censo 2010 como proxy razoável para a posição "
    "relativa das zonas em 2024 — um argumento metodológico "
    "desenvolvido em detalhe na seção 9.1."
))
conteudo.append(p(
    "<b>(ii) Mas a segregação de renda não é a única dimensão "
    "relevante do espaço urbano.</b> Marques (2015) argumenta "
    "que, além do gradiente de renda, a cidade se estrutura por "
    "<i>redes de equipamentos e instituições</i> — serviços "
    "públicos, escolas, universidades, centros culturais — cuja "
    "distribuição territorial é <b>independente</b> da "
    "distribuição de renda em muitos casos. Um bairro de renda "
    "alta pode ter alta ou baixa densidade institucional; um "
    "bairro de renda média pode ter equipamentos de prestígio "
    "cultural. A tese é que <b>o efeito político-territorial "
    "do espaço urbano não vem só da renda dos moradores — vem "
    "também do que o ambiente institucional oferece</b>."
))
conteudo.append(p(
    "<b>(iii) Ambientes institucionais educativo-culturais "
    "funcionam como infraestrutura de socialização política.</b> "
    "Marques (2015) e Hoyler, Gelape &amp; Silotto (2021) "
    "argumentam, seguindo uma tradição mais ampla que vai de "
    "Tocqueville a Putnam, que frequentar ambientes educativos-"
    "culturais específicos (universidades, escolas "
    "construtivistas, centros culturais) produz <b>vínculos "
    "político-territoriais específicos</b> — tanto de "
    "identificação quanto de mobilização. Esta tese, entretanto, "
    "raramente foi testada quantitativamente no contexto "
    "paulistano. Este capítulo faz exatamente isso: operacionaliza "
    "a hipótese do ambiente institucional como preditor do voto "
    "e a compara empiricamente com a hipótese alternativa "
    "(renda/classe)."
))
conteudo.append(p(
    "<b>A ponte com Inglehart &amp; Norris.</b> A agenda da escola "
    "paulistana tem, neste capítulo, uma conexão inesperada com a "
    "literatura internacional recente sobre clivagem cultural no "
    "voto contemporâneo (Inglehart &amp; Norris, 2016, 2019). Se "
    "Marques argumenta que o ambiente institucional é uma dimensão "
    "independente da segregação urbana, Inglehart &amp; Norris "
    "argumentam que a educação e o cosmopolitismo — produzidos "
    "justamente pelos ambientes institucionais — tornam-se "
    "progressivamente o eixo organizador do voto em democracias "
    "contemporâneas. As duas tradições se encontram na hipótese "
    "empiricamente testável: <b>na SP pós-2016, a presença de "
    "ambiente institucional educativo-cultural explica o voto "
    "melhor do que a renda</b>."
))

conteudo.append(h1("3.1 Renda não explica o voto ideológico em SP 2024"))
conteudo.append(p(
    "Cruzamos renda per capita dos setores censitários (Censo 2010) "
    "com o escore ideológico médio ponderado por zona (2024). "
    "Pipeline: 18.953 setores censitários de SP via geobr × 2.061 "
    "locais de votação do CEM via spatial join × agregação por "
    "zona eleitoral. Para a limitação temporal do Censo 2010, "
    "veja seção 5 adiante."
))
conteudo.append(p(
    "<b>A correlação renda × escore ideológico é NEGATIVA em SP 2024</b>:"
))
dados_corr = [
    [_cb("Eleição"), _cb("r (Pearson)"), _cb("R²"), _cb("Direção")],
    [_c("Vereador 2024"), _cc("<b>-0,297</b>"), _cc("0,088"), _c("renda alta → escore menor (mais à esquerda)")],
    [_c("Prefeito 1T 2024"), _cc("<b>-0,166</b>"), _cc("0,028"), _c("mesma direção, efeito menor")],
    [_c("Vereador 2020"), _cc("<b>-0,211</b>"), _cc("0,045"), _c("padrão consistente no tempo")],
]
conteudo.append(tabela(dados_corr, [3.5*cm, 2.5*cm, 2*cm, 8*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "Renda explica menos de 9% da variância ideológica entre zonas. "
    "Mais de 91% não é explicada por renda. O sinal é <b>oposto</b> "
    "ao voto de classe clássico — zonas mais ricas votam mais à "
    "esquerda, não menos. Mas o efeito é fraco."
))

conteudo.append(h1("3.2 O índice institucional cultural-progressista"))
conteudo.append(p(
    "A hipótese alternativa é que o fator explicativo é <b>ambiente "
    "institucional educativo-cultural</b>, não renda. Operacionalizamos "
    "essa hipótese construindo um índice de \"densidade institucional "
    "cultural-progressista\" por zona, identificando locais de "
    "votação em quatro categorias:"
))
conteudo.append(p(
    "<b>(i) Universidades</b> (USP, Mackenzie, PUC, Uninove, FAAP, "
    "FMU, Insper, Senac, Senai, Fatec, etc.); <b>(ii) Escolas "
    "particulares progressistas</b> (Vera Cruz, Equipe, Lumiar, "
    "Oswald de Andrade, Stella Maris, Escola da Vila, Horizontes, "
    "Itaca); <b>(iii) Escolas públicas de prestígio cultural</b> "
    "(Caetano de Campos, Fernão Dias Paes, Godofredo Furtado, "
    "Amorim Lima, Clorinda Danti, Fidelino de Figueiredo); "
    "<b>(iv) Instituições culturais internacionais</b> (Goethe-"
    "Institut, Alliance Française, Dante Alighieri, Cervantes). "
    "O índice final é a fração de locais da zona em pelo menos uma "
    "categoria."
))
conteudo.append(p(
    "<b>Resultado: a correlação com o escore ideológico é r = "
    "−0,661, explicando 43,7% da variância</b> — cinco vezes mais "
    "que a renda."
))
conteudo.extend(fig(
    "outputs/scatter_indice_institucional.png",
    w_cm=16.5,
    legenda="Figura 3.1 — Comparação direta: índice institucional "
    "(esquerda, R² = 0,437) vs renda per capita (direita, R² = 0,088) "
    "como preditores do escore ideológico de vereador 2024 por zona.",
))

conteudo.append(h2("3.2.1 Os locais específicos que compõem o índice"))
conteudo.append(p(
    "Para dar concretude aos números, vale enumerar exatamente "
    "quais locais de votação compõem o índice institucional nas "
    "zonas mais relevantes:"
))
conteudo.append(p(
    "<b>Bela Vista (Z1) — 48,0% dos locais são categorizados, o "
    "maior índice da cidade.</b> A zona tem 25 locais, dos quais "
    "11 são universitários (!): Mackenzie em múltiplos prédios "
    "(Consolação, Itambé, Prédio 45, Prédio 09), PUC-SP "
    "Consolação, PUC-SP Ciências Exatas, FMU, Senac Consolação, "
    "Faculdade Phorte, Uniban, Uninove Paulista. Adicionalmente, "
    "a EE Caetano de Campos (histórica escola pública "
    "paulistana, em seu prédio tradicional na Consolação) entra "
    "como prestígio público. É o caso mais extremo da "
    "\"concentração educativo-cultural\" em uma única zona: "
    "<b>quase metade dos locais de votação de Bela Vista são "
    "campus universitários ou escolas públicas tradicionais</b>."
))
conteudo.append(p(
    "<b>Pinheiros (Z251) — 37,0% dos locais, segundo maior índice "
    "da cidade.</b> A zona tem 27 locais, distribuídos de forma "
    "muito mais diversificada que Bela Vista:"
))
dados_pinheiros = [
    [_cb("Categoria"), _cb("N"), _cb("Locais específicos")],
    [_c("Universidade"), _cc("1"),
     _c("Uninove Pinheiros")],
    [_c("Escola progressista"), _cc("4"),
     _c("Colégio Vera Cruz, Escola Lumiar, Escola Oswald de "
       "Andrade, Colégio Horizontes")],
    [_c("Prestígio público"), _cc("3"),
     _c("EE Fernão Dias Paes, EE Godofredo Furtado, EE Antonio "
       "Alves Cruz")],
    [_c("Internacional cultural"), _cc("2"),
     _c("Goethe-Institut, Colégio Stella Maris")],
]
conteudo.append(tabela(dados_pinheiros, [3.5*cm, 1*cm, 11*cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(p(
    "A lista acima é politicamente reveladora. <b>Colégio Vera "
    "Cruz, Escola Lumiar, Escola Oswald de Andrade</b> e <b>Colégio "
    "Horizontes</b> são as quatro escolas particulares "
    "historicamente associadas à pedagogia construtivista/"
    "progressista de classe média alta paulistana. Seu público-"
    "alvo é bem definido: filhos de profissionais liberais, "
    "acadêmicos, jornalistas, artistas, advogados — exatamente o "
    "perfil do \"cosmopolitismo educado\" que Inglehart &amp; "
    "Norris descrevem. <b>EE Fernão Dias Paes</b> e <b>EE "
    "Godofredo Furtado</b> são escolas estaduais de prestígio "
    "histórico na região, frequentadas por filhos de servidores "
    "públicos e professores da rede. <b>Goethe-Institut</b> é o "
    "centro cultural alemão — ponto focal da cena cosmopolita "
    "paulistana. Somados, esses locais capturam boa parte do que "
    "se entende, na sociologia urbana paulistana, como "
    "\"ambiente cultural progressista de Pinheiros\"."
))
conteudo.append(p(
    "<b>Indianópolis (Z258) — 0,0% dos locais, o menor índice da "
    "cidade.</b> A zona tem 31 locais de votação, e nenhum "
    "deles é categorizado em nossa lista. Não há universidades, "
    "não há escolas particulares progressistas de tradição "
    "reconhecida, não há escolas públicas de prestígio cultural "
    "nacional, e não há instituições culturais internacionais. "
    "Os locais de votação de Indianópolis são <b>escolas "
    "estaduais e municipais regulares, colégios particulares de "
    "bairro e centros comunitários</b> — instituições de ensino "
    "que servem a população local em sua vida cotidiana, mas sem "
    "a dimensão de prestígio cultural-intelectual que marca os "
    "locais de Pinheiros e Bela Vista. Isto é substantivamente "
    "notável: a renda per capita de Indianópolis é praticamente "
    "idêntica à de Pinheiros (R$ 3.504 vs R$ 3.819), mas o perfil "
    "institucional do território é <b>radicalmente diferente</b>. "
    "É um bairro rico <i>residencial</i> — sem grande "
    "infraestrutura cultural-universitária pública ou privada. "
    "Essa <b>diferença territorial em dimensão ortogonal à "
    "renda</b> é exatamente o que Marques (2015) prevê quando "
    "argumenta que a distribuição de equipamentos institucionais "
    "é parcialmente independente da distribuição de renda."
))

conteudo.append(h2("3.2.2 O mecanismo: como o ambiente \"fala\" politicamente?"))
conteudo.append(p(
    "Identificado o sinal correlacional forte (r = −0,66), "
    "resta perguntar <b>por que</b> o ambiente institucional "
    "produziria voto mais à esquerda. Quatro mecanismos "
    "plausíveis, compatíveis com a literatura:"
))
conteudo.append(p(
    "<b>(a) Mecanismo de composição populacional.</b> A versão "
    "mais \"bruta\": universidades, escolas construtivistas e "
    "instituições culturais atraem <b>moradores</b> com perfil "
    "específico (professores, estudantes, funcionários "
    "administrativos, artistas). O voto da zona reflete esse "
    "perfil moradores — não um efeito do ambiente em si. Nesse "
    "caso, ambiente é proxy de composição demográfica "
    "específica."
))
conteudo.append(p(
    "<b>(b) Mecanismo de socialização política.</b> Frequentar "
    "ambientes universitários ou escolas progressistas produz "
    "exposição a valores, debates e normas políticas específicas "
    "(pós-materialismo, cosmopolitismo, tolerância ao "
    "pluralismo, etc.). Ao longo de anos de convivência, o "
    "eleitor internaliza parcialmente esses valores e os traduz "
    "em escolha eleitoral. Essa é a formulação clássica de "
    "Inglehart &amp; Norris (2019) para democracias "
    "contemporâneas."
))
conteudo.append(p(
    "<b>(c) Mecanismo de rede e mobilização.</b> Universidades e "
    "escolas de elite cultural são também <b>lócus de recrutamento "
    "político</b>: alunos e professores se engajam em campanhas, "
    "formam grupos de apoio, distribuem materiais, organizam "
    "debates. O ambiente institucional cria redes de ativismo que "
    "se expressam eleitoralmente nas proximidades. Essa é a leitura "
    "de Hoyler, Gelape &amp; Silotto (2021) sobre construção de "
    "vínculos político-territoriais em SP."
))
conteudo.append(p(
    "<b>(d) Mecanismo de identidade cultural deflagrado.</b> "
    "Após choques políticos nacionais (impeachment 2016, eleição "
    "Bolsonaro 2018), a identidade cultural-cosmopolita que "
    "ambientes universitários sempre produziram torna-se "
    "<b>politicamente saliente</b>. A variável que antes era "
    "latente (ser universitário em Pinheiros não distinguia seu "
    "voto) torna-se mobilizada (ser universitário em Pinheiros "
    "implica se opor ao bolsonarismo). Este mecanismo é o que "
    "explica melhor o achado da seção 3.6 (teste temporal): a "
    "correlação entre índice e voto <b>cresce</b> ao longo do "
    "tempo, consistente com ativação recente."
))
conteudo.append(p(
    "Os quatro mecanismos não são mutuamente exclusivos e "
    "provavelmente operam simultaneamente. <b>A dissertação não "
    "consegue, com os dados atuais, distinguir definitivamente "
    "entre eles.</b> Mas a combinação de evidências do teste "
    "temporal (3.6) com o padrão de candidatos (Parte IV) "
    "sugere que (d) + (c) são os mecanismos dominantes — o "
    "ambiente institucional funciona como <i>lócus de "
    "coordenação política recente</i>, não como atributo "
    "estrutural antigo. A hipótese (a), de composição, não "
    "poderia explicar por que o sinal era nulo em 2016 e "
    "emergiu em 2020 — a composição populacional das zonas "
    "muda devagar demais."
))

conteudo.append(h1("3.3 O caso Pinheiros × Indianópolis"))
conteudo.append(p(
    "Pinheiros (Z251) e Indianópolis (Z258) são empates em renda "
    "(R$ 3.819 vs R$ 3.504 per capita, 2ª e 3ª da cidade) mas polos "
    "opostos em ambiente institucional:"
))
dados_caso = [
    [_cb("Indicador"), _cb("Pinheiros (Z251)"), _cb("Indianópolis (Z258)")],
    [_c("Renda per capita média (2010)"), _cc("R$ 3.819 (2º)"), _cc("R$ 3.504 (3º)")],
    [_c("Índice institucional"), _cc("<b>37,0%</b>"), _cc("<b>0%</b>")],
    [_c("Universidades"), _cc("1"), _cc("0")],
    [_c("Escolas progressistas"), _cc("4"), _cc("0")],
    [_c("Prestígio público"), _cc("3"), _cc("0")],
    [_c("Internacional cultural"), _cc("2 (Goethe!)"), _cc("0")],
    [_c("Escore ideológico vereador 2024"), _cc("<b>5,53</b>"), _cc("<b>6,39</b>")],
    [_c("PSDB em 2012 (vereador)"), _cc("48%"), _cc("47%")],
    [_c("Partido #1 em 2024 (vereador)"), _cc("PSOL 28%"), _cc("PL 20%")],
]
conteudo.append(tabela(dados_caso, [6*cm, 4.5*cm, 4.5*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "A diferença ideológica (0,86 pontos de escore) é quase "
    "exatamente o que o modelo prevê a partir da diferença de "
    "densidade institucional (48 pp × 0,019 = 0,91). <b>Pinheiros "
    "e Indianópolis são empates em renda e polos opostos em "
    "instituições E em voto.</b> A variável diferenciadora é "
    "institucional, não econômica."
))

conteudo.append(h1("3.4 Regressão multivariada"))
conteudo.append(p(
    "Em OLS com renda e índice institucional como preditores "
    "simultâneos do escore de vereador 2024 (n = 57 zonas):"
))
dados_ols = [
    [_cb("Modelo"), _cb("Variáveis"), _cb("R²"), _cb("β renda"), _cb("β índice")],
    [_c("1"), _c("só renda"), _cc("0,088"), _cc("negativo"), _cc("—")],
    [_c("2"), _c("só índice institucional"), _cc("<b>0,437</b>"),
     _cc("—"), _cc("<b>-0,0185</b>")],
    [_c("3"), _c("renda + índice"), _cc("0,439"),
     _cc("+0,000011 (desprezível)"), _cc("-0,0185")],
]
conteudo.append(tabela(dados_ols, [1.5*cm, 4.5*cm, 1.5*cm, 5*cm, 2.5*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "O R² adicional que renda acrescenta após controlar pelo índice "
    "institucional é 0,002 — <b>praticamente zero</b>. Controlando "
    "pela densidade institucional, a renda perde todo o poder "
    "explicativo. O coeficiente do índice é robusto: cada ponto "
    "percentual reduz o escore em 0,019 — suficiente para produzir "
    "a diferença de ~0,9 pontos entre Bela Vista/Pinheiros e "
    "Indianópolis."
))

conteudo.append(h1("3.5 Robustez"))
conteudo.append(p(
    "Cinco testes de robustez aplicados ao achado: "
    "<b>(a) leave-one-category-out</b> — todas as variantes do "
    "índice preservam R² > 0,29; "
    "<b>(b) cada categoria isolada</b> — prestígio público sozinho "
    "tem r = −0,624 apesar de aparecer em só 6 zonas; "
    "<b>(c) bootstrap IC 95%</b> — [−0,816; −0,223] para vereador "
    "2024, [−0,783; −0,144] para prefeito, [−0,690; −0,033] para "
    "vereador 2020, todos excluindo zero; "
    "<b>(d) controle por densidade urbana</b> (n de locais da zona) — "
    "n_locais sozinho tem R² = 0,003, não é confundidor; "
    "<b>(e) variável dependente alternativa</b> (% de seções com "
    "esquerda majoritária por plurality bipartite): a correlação do "
    "índice sobe para <b>r = +0,814, R² = 0,663</b>, enquanto a da "
    "renda fica em r = +0,079. O índice explica 66% da variância "
    "numa métrica eleitoral mais direta."
))

conteudo.append(h1("3.6 O teste temporal — achado mais surpreendente"))
conteudo.append(p(
    "Mantendo o índice fixo (base CEM/USP 2022) e variando o voto, "
    "a correlação entre índice e escore ideológico <b>não é "
    "estável</b> — ela <b>cresce</b> ao longo dos ciclos:"
))
dados_temp = [
    [_cb("Ano"), _cb("Vereador r (R²)"), _cb("Prefeito 1T r (R²)")],
    [_c("2016"), _cc("<b>+0,108 (0,012)</b>"), _cc("<b>-0,012 (0,000)</b>")],
    [_c("2020"), _cc("-0,500 (0,250)"), _cc("-0,249 (0,062)")],
    [_c("2024"), _cc("<b>-0,661 (0,437)</b>"), _cc("<b>-0,600 (0,360)</b>")],
]
conteudo.append(tabela(dados_temp, [2*cm, 5*cm, 5*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.extend(fig(
    "outputs/indice_temporal_trajetoria.png",
    w_cm=13,
    legenda="Figura 3.2 — Estabilidade temporal do poder preditivo "
    "do índice institucional sobre o escore ideológico por zona "
    "eleitoral, SP 2016-2024.",
))
conteudo.append(p(
    "<b>Em 2016, o índice explicava ZERO do voto.</b> As "
    "universidades, escolas progressistas e instituições culturais "
    "existiam exatamente nas mesmas zonas, mas não se traduziam em "
    "diferenciação política. A correlação emerge em 2020 (r = "
    "−0,50) e se consolida em 2024 (r = −0,66)."
))
conteudo.append(p(
    "<b>Interpretação (compatível com Inglehart &amp; Norris, 2016, "
    "2019):</b> o ambiente institucional cultural-progressista foi "
    "<b>politicamente ativado</b> entre 2016 e 2020. As "
    "\"infraestruturas\" (escolas, universidades, instituições) "
    "sempre existiram; o que mudou foi que, após o choque do "
    "impeachment (2016), a eleição de Bolsonaro (2018) e a "
    "polarização Lula-Bolsonaro (2022), passaram a \"falar\" "
    "politicamente — a mediar uma identidade cultural-cosmopolita "
    "que se tornou saliente no voto. É exatamente o mecanismo "
    "descrito por Inglehart &amp; Norris para democracias "
    "ocidentais contemporâneas: a clivagem cultural substitui "
    "gradualmente a clivagem econômica como organizador do voto, "
    "ativada por choques políticos específicos."
))
conteudo.append(p(
    "<b>Esse achado reforça, não enfraquece, a tese central.</b> "
    "Uma hipótese puramente estrutural (\"renda alta explica voto\") "
    "teria produzido correlações estáveis no tempo. A hipótese "
    "institucional-cultural prevê exatamente o padrão observado — "
    "ativação emergente após choques políticos específicos."
))

# ====================================================================
# PARTE IV — PERFIL DOS CANDIDATOS
# ====================================================================
conteudo.append(PageBreak())
conteudo.append(parte("Parte IV — Perfil dos candidatos"))
conteudo.append(p(
    "<i>Complemento sociológico aos três eixos. Analisa a "
    "correspondência entre oferta partidária (candidato) e demanda "
    "eleitoral (zona) via metadados de ocupação e partido. Esta "
    "parte conecta diretamente com os mecanismos (c) e (d) "
    "discutidos em 3.2.2 — se o ambiente institucional funciona "
    "como lócus de mobilização política, ele também é lócus de "
    "produção de candidatos.</i>"
))

conteudo.append(h1("4.1 O tipo de candidato que emerge espelha o eleitorado"))
conteudo.append(p(
    "Para cada um dos 547 candidatos a vereador em SP 2024 com "
    "mais de 500 votos, calculamos a porcentagem do seu voto que "
    "vem de zonas com alta densidade institucional (índice > 15%) "
    "e classificamos sua ocupação declarada (via TSE consulta_cand) "
    "em categorias temáticas. O resultado é uma diferenciação "
    "dramática entre candidatos \"territorialmente periféricos\" e "
    "candidatos \"territorialmente culturais\":"
))

conteudo.extend(fig(
    "outputs/grafico_ocupacao_por_tipo_zona.png",
    w_cm=16,
    legenda="Figura 4.1 — Distribuição de categoria ocupacional dos "
    "candidatos a vereador SP 2024 (≥500 votos), por perfil "
    "territorial do voto. Academia/cultura/imprensa triplica entre "
    "voto periférico (7,9%) e voto misto (19,7%). Profissional "
    "liberal cresce de 12,7% para 21,4%.",
))

dados_dist = [
    [_cb("Categoria de ocupação"), _cb("Voto periférico (<10%)"),
     _cb("Voto misto (10-25%)"), _cb("Voto cultural (>25%)")],
    [_c("Academia / cultura / imprensa"), _cc("7,9%"),
     _cc("<b>19,7%</b>"), _cc("14,3%")],
    [_c("Profissional liberal (médico, adv.)"), _cc("12,7%"),
     _cc("18,4%"), _cc("<b>21,4%</b>")],
    [_c("Empresário / comerciante"), _cc("17,1%"), _cc("15,8%"),
     _cc("14,3%")],
    [_c("Servidor público"), _cc("3,9%"), _cc("6,6%"), _cc("0,0%")],
    [_c("Político incumbente"), _cc("10,7%"), _cc("6,6%"), _cc("7,1%")],
    [_c("Religioso"), _cc("1,1%"), _cc("0,0%"), _cc("0,0%")],
    [_c("Outros (inclui apelidos populares)"), _cc("<b>43,8%</b>"),
     _cc("32,9%"), _cc("42,9%")],
]
conteudo.append(tabela(dados_dist, [6*cm, 3*cm, 3*cm, 3*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "Três padrões emergem da tabela: <b>(i)</b> a categoria "
    "<i>academia, cultura e imprensa</i> triplica entre candidatos "
    "com voto periférico e candidatos com voto misto (7,9% → "
    "19,7%), confirmando que o ambiente institucional cultural "
    "produz candidatos, não só eleitores; <b>(ii)</b> a categoria "
    "<i>profissional liberal</i> (médicos, advogados, engenheiros, "
    "arquitetos) cresce linearmente conforme o voto se concentra "
    "em zonas densas (12,7% → 18,4% → 21,4%); <b>(iii)</b> a "
    "categoria <i>religioso</i> desaparece completamente nas zonas "
    "culturais — não há pastores, padres ou bispos no topo "
    "eleitoral dessas zonas. A categoria \"outros\" é dominada por "
    "<b>apelidos populares de bairro</b> na periferia, o que "
    "pulveriza a classificação mas revela um padrão qualitativo "
    "distinto."
))

conteudo.append(h1("4.2 Os candidatos territorialmente culturais — lista nominal"))
conteudo.append(p(
    "Com perfis por categoria estabelecidos, vale nomear os "
    "candidatos concretos que aparecem no topo dos dois perfis "
    "territoriais. A tabela abaixo lista os 10 candidatos com "
    "maior percentual de votos concentrados em zonas de alta "
    "densidade institucional (Pinheiros, Bela Vista, Perdizes, "
    "Vila Mariana, Butantã), entre candidatos com pelo menos 500 "
    "votos no total:"
))
dados_top_cultural = [
    [_cb("%"), _cb("Candidato"), _cb("Partido"), _cb("Ocupação"), _cb("Total votos")],
    [_cc("43,1"), _c("Dr. David Zylbergeld Neto"), _c("PL"), _c("Médico"), _cc("999")],
    [_cc("42,5"), _c("Henry Kadima"), _c("PL"), _c("Empresário"), _cc("2.002")],
    [_cc("40,9"), _c("Neti Araújo"), _c("PT"), _c("—"), _cc("1.954")],
    [_cc("39,5"), _c("Leandro Mofsovich"), _c("NOVO"), _c("Empresário"), _cc("1.390")],
    [_cc("34,3"), _c("Veronica Bilyk"), _c("PSB"), _c("Publicitária"), _cc("3.369")],
    [_cc("33,5"), _c("Carmen Silva"), _c("PSB"), _c("—"), _cc("9.781")],
    [_cc("33,4"), _c("Eduardo Dourado"), _c("PRD"), _c("Advogado"), _cc("806")],
    [_cc("28,1"), _c("Marcão do Esporte"), _c("PV"), _c("—"), _cc("569")],
    [_cc("27,5"), _c("<b>Marina Bragante</b>"), _c("Rede"), _c("Psicóloga"), _cc("<b>39.147</b>")],
    [_cc("26,3"), _c("<b>Claudia Visoni</b>"), _c("PV"), _c("Jornalista"), _cc("<b>6.006</b>")],
    [_cc("26,2"), _c("<b>Cristina Monteiro</b>"), _c("NOVO"), _c("Vereadora"), _cc("<b>56.904</b>")],
    [_cc("25,7"), _c("Sidney Stahl"), _c("NOVO"), _c("Advogado"), _cc("716")],
    [_cc("25,0"), _c("Takeda"), _c("PRD"), _c("Advogado"), _cc("801")],
]
conteudo.append(tabela(dados_top_cultural, [1.2*cm, 5*cm, 2*cm, 3.5*cm, 2.5*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "<b>Observações:</b> Marina Bragante (Rede, psicóloga) é a "
    "candidata com maior volume absoluto (39.147 votos) entre "
    "aqueles com concentração territorial cultural alta. Cristina "
    "Monteiro (NOVO, vereadora) tem 56.904 votos — é de longe a "
    "mais votada da categoria e, como discutido na Parte II.4, é "
    "a herdeira institucional do voto Matarazzo/Covas via migração "
    "PSDB→NOVO. Claudia Visoni (PV, jornalista) é outro exemplo "
    "paradigmático — vem da cena ambientalista-urbana paulistana "
    "e capta voto de perfil educado-progressista. Dois dos quatro "
    "médicos e três dos quatro advogados no top 13 são do <b>PL "
    "ou PRD</b>, sugerindo que a correspondência ocupação × "
    "ideologia não é unívoca: há \"profissional liberal de "
    "direita\" tanto quanto \"profissional liberal de esquerda\", "
    "e ambos competem pelo mesmo eleitorado educado."
))
conteudo.append(p(
    "É também notável a <b>ausência</b> de alguns perfis esperados "
    "na lista. Não há professores universitários famosos (exceto "
    "Nabil Bonduki, que aparece um pouco abaixo do corte com 24%). "
    "Não há políticos incumbentes de carreira longa — o topo é "
    "dominado por <b>candidatos de primeira ou segunda geração "
    "de visibilidade pública</b>, não por ocupantes estabelecidos. "
    "Esse padrão é coerente com a tese de ativação recente do "
    "ambiente institucional: os candidatos que captam esse voto "
    "emergiram nos últimos ciclos, não são fósseis da "
    "representação paulistana tradicional."
))

conteudo.append(h1("4.3 Os candidatos territorialmente periféricos — lista nominal"))
conteudo.append(p(
    "A simetria inversa: os 15 candidatos com maior porcentagem "
    "de votos vindos <b>exclusivamente</b> de zonas de baixa "
    "densidade institucional (praticamente 100%):"
))
dados_top_periferia = [
    [_cb("% baixa"), _cb("Candidato"), _cb("Partido"), _cb("Ocupação")],
    [_cc("100,0"), _c("Roni da Limpeza"), _c("PSD"), _c("Empresário")],
    [_cc("99,9"), _c("Fernando Manso"), _c("PRD"), _c("Cabeleireiro e barbeiro")],
    [_cc("99,9"), _c("Alemão do Conselho"), _c("União"), _c("—")],
    [_cc("99,8"), _c("Coletivo Pastora Lilian Alves"), _c("Republicanos"), _c("Comerciante")],
    [_cc("99,8"), _c("Negro Edson"), _c("Solidariedade"), _c("—")],
    [_cc("99,8"), _c("Eliel Alves"), _c("Pode"), _c("Técnico de enfermagem")],
    [_cc("99,8"), _c("Miltão"), _c("PT"), _c("—")],
    [_cc("99,7"), _c("Anadethy Caravanista"), _c("MDB"), _c("Pedagoga")],
    [_cc("99,7"), _c("Gil do Celular"), _c("PRD"), _c("Comerciante")],
    [_cc("99,7"), _c("Tio Waltinho"), _c("Avante"), _c("Comerciante")],
    [_cc("99,7"), _c("Professor Alves"), _c("PRD"), _c("Professor")],
    [_cc("99,6"), _c("Yes da ZL"), _c("Solidariedade"), _c("Motorista particular")],
    [_cc("99,6"), _c("Kéké Espetinhos"), _c("Pode"), _c("Empresário")],
    [_cc("99,6"), _c("Mallu Mattos"), _c("União"), _c("—")],
    [_cc("99,6"), _c("Natal Líder Comunitário"), _c("PSB"), _c("Empresário")],
]
conteudo.append(tabela(dados_top_periferia, [1.5*cm, 6*cm, 3*cm, 4.5*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "<b>Três padrões visíveis.</b> Primeiro, os nomes de urna: "
    "<i>Roni da Limpeza, Fernando Manso \"cabeleireiro\", Alemão "
    "do Conselho, Pastora Lilian, Gil do Celular, Tio Waltinho, "
    "Kéké Espetinhos, Yes da ZL, Natal Líder Comunitário</i>. São "
    "apelidos que indicam <b>origem profissional local</b> "
    "(cabeleireiro, motorista, comerciante), função comunitária "
    "(conselheiro, pastora, líder comunitário) ou marcador "
    "territorial (\"da ZL\" = Zona Leste). Nenhum desses padrões "
    "aparece entre os candidatos territorialmente culturais."
))
conteudo.append(p(
    "Segundo, a ocupação. A maioria são <b>empresários de pequeno "
    "porte</b> (Roni, Natal, Kéké — donos de estabelecimentos "
    "locais), <b>comerciantes</b> (Gil, Tio Waltinho), "
    "<b>prestadores de serviço</b> (Fernando Manso, Yes da ZL), "
    "<b>técnicos de nível médio</b> (Eliel Alves, Professor Alves), "
    "e <b>pastores evangélicos</b> (Pastora Lilian). É o perfil "
    "clássico do \"vereador de bairro\" descrito por Almeida &amp; "
    "Carneiro (2003): figura conhecida localmente, com vínculo "
    "direto e cotidiano com o eleitor."
))
conteudo.append(p(
    "Terceiro, os partidos. A distribuição atravessa ideologias: "
    "<b>PSD, PRD, União, Republicanos, Solidariedade, Pode, MDB, "
    "PT, Avante, PSB</b> — praticamente todos os partidos com "
    "estrutura nacional aparecem. Isso confirma que o "
    "\"vereador de bairro periférico\" é uma <b>categoria "
    "sociológica</b> antes de ser uma categoria ideológica: "
    "existem candidatos progressistas e candidatos conservadores "
    "competindo pelo mesmo espaço, com a mesma forma de vínculo "
    "territorial-comunitário. O que os une não é o programa "
    "político — é o tipo de relação social com o eleitorado."
))

conteudo.append(h1("4.4 A tese da dupla produção: ambiente institucional produz eleitor e candidato"))
conteudo.append(p(
    "Se juntarmos os achados das Partes III e IV, emerge uma "
    "tese mais forte e teoricamente articulada do que a hipótese "
    "original do projeto (H4). A H4 dizia que \"o voto de "
    "esquerda nos bairros ricos aponta para outras variáveis "
    "independentes do que a renda ou a escolaridade\". O achado "
    "deste rascunho é mais específico: <b>o ambiente institucional "
    "cultural-progressista produz simultaneamente eleitores de "
    "perfil específico E candidatos de perfil espelho</b>, e a "
    "relação entre os dois é reforçada pela ativação política "
    "recente."
))
conteudo.append(p(
    "<b>O mecanismo dual funciona assim:</b> (i) universidades, "
    "escolas construtivistas, instituições culturais internacionais "
    "produzem <b>eleitores</b> com repertório cultural-cosmopolita "
    "específico, acumulado ao longo dos anos de convivência no "
    "ambiente; (ii) os mesmos ambientes produzem <b>candidatos</b> "
    "— psicólogos, jornalistas, publicitários, advogados de "
    "nicho, profissionais ligados a ONGs, academia, imprensa — "
    "que partilham o repertório cultural dos eleitores; (iii) "
    "após o choque político 2016–2018, essa correspondência "
    "latente se ativa como identidade política saliente, e "
    "ambos os lados convergem na produção de um circuito de "
    "representação territorial coeso; (iv) nas zonas sem "
    "infraestrutura institucional — mesmo em renda equivalente — "
    "nem eleitores nem candidatos desse perfil são produzidos, "
    "e o voto segue lógicas distintas (clientelista, religiosa, "
    "personalista de bairro)."
))
conteudo.append(p(
    "<b>Dois circuitos paralelos de representação política operam "
    "na mesma cidade de São Paulo:</b> um <b>circuito "
    "institucional-cultural</b>, produzindo eleitores progressistas "
    "educados e candidatos profissionais liberais de nicho, "
    "concentrado no corredor das universidades; e um <b>circuito "
    "comunitário-personalista</b>, produzindo eleitores de base "
    "local e candidatos com apelidos de bairro, distribuído pela "
    "periferia e por zonas sem densidade institucional "
    "significativa. A oposição entre os dois não é primariamente "
    "ideológica (há progressistas e conservadores em ambos), é "
    "<b>sociologicamente estrutural</b> — a forma da relação "
    "candidato-eleitor é distinta. E a única variável que "
    "distingue empiricamente de onde cada circuito emerge é o "
    "<b>ambiente institucional</b>."
))
conteudo.append(p(
    "<b>Isto é o argumento substantivo central da dissertação "
    "que emerge desta análise.</b> Não é uma tese sobre "
    "ideologia — é uma tese sobre como <i>ambientes institucionais "
    "produzem representação política</i>. A H4 original, "
    "formulada como \"o voto de esquerda nos bairros ricos aponta "
    "para outras variáveis\", é um caso particular desta tese "
    "mais geral: o voto progressista nos bairros ricos aponta "
    "para ambiente institucional, e o ambiente institucional "
    "produz candidatos espelho que ativam esse voto. A "
    "reciprocidade é o mecanismo."
))

# ====================================================================
# PARTE V — CONVERGÊNCIA TEMPORAL E SÍNTESE
# ====================================================================
conteudo.append(PageBreak())
conteudo.append(parte("Parte V — Convergência temporal e síntese"))

conteudo.append(h1("5.1 Os três eixos se ativam simultaneamente"))
conteudo.append(p(
    "Um achado colateral importante deste trabalho é que as "
    "transformações identificadas nos três eixos empíricos ocorrem "
    "<b>no mesmo período histórico</b> — entre 2016 e 2020 — e "
    "consolidam-se em 2024. A simultaneidade sugere um mecanismo "
    "comum subjacente:"
))
dados_conv = [
    [_cb("Eixo"), _cb("Indicador"), _cb("2012"), _cb("2016"), _cb("2020"), _cb("2024")],
    [_c("Sistema partidário"), _c("PSDB % vereador Pinheiros"),
     _cc("48%"), _cc("36%"), _cc("18%"), _cc("~0%")],
    [_c(""), _c("PSOL % vereador Pinheiros"),
     _cc("—"), _cc("12%"), _cc("<b>28%</b>"), _cc("<b>28%</b>")],
    [_c("Financiamento"), _c("% PF média dos top-6 Pinheiros"),
     _cc("0%"), _cc("<b>68%</b>"), _cc("59%"), _cc("18%")],
    [_c(""), _c("% Partido média dos top-6 Pinheiros"),
     _cc("51%"), _cc("2%"), _cc("29%"), _cc("<b>77%</b>")],
    [_c("Sociologia urbana"), _c("R² índice institucional (vereador)"),
     _cc("—"), _cc("<b>0,01</b>"), _cc("0,25"), _cc("<b>0,44</b>")],
]
conteudo.append(tabela(dados_conv, [3*cm, 5.5*cm, 1.3*cm, 1.3*cm, 1.3*cm, 1.3*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "<b>Leitura:</b> Em 2016, nenhum dos três eixos mostra o padrão "
    "contemporâneo. PSDB ainda é o partido principal de Pinheiros "
    "(36%). O financiamento está na era de transição pós-PJ com PF "
    "alta (68%). O ambiente institucional ainda não correlaciona "
    "com voto (R² = 0,01). <b>A transformação acontece entre 2016 "
    "e 2020</b>: o PSOL ultrapassa o PSDB em Pinheiros, o FEFC "
    "começa a substituir a PF, e o índice institucional passa a "
    "ter poder explicativo (R² = 0,25). Em 2024, o padrão está "
    "consolidado."
))
conteudo.append(p(
    "<b>Hipótese causal:</b> a polarização nacional 2016–2022 "
    "(impeachment-Bolsonaro-Lula) foi um choque político que "
    "reorganizou simultaneamente três dimensões do campo "
    "político-territorial paulistano: a identidade partidária "
    "(PSDB → novas legendas), a estrutura material (PJ → PF → "
    "FEFC), e a ativação cultural do ambiente institucional "
    "(latente → saliente). Os três processos não são independentes "
    "— são manifestações paralelas do mesmo rearranjo."
))

conteudo.append(h1("5.2 Síntese em relação às hipóteses do projeto original"))
dados_hip = [
    [_cb("Hipótese"), _cb("Achado"), _cb("Status")],
    [_c("<b>H1:</b> há novo padrão não-pendular"),
     _c("Confirmada. Pinheiros e Indianópolis começam em PSDB 48% "
       "em 2012 e terminam em posições opostas em 2024. Não é "
       "pêndulo — é divergência estrutural."),
     _c("<b>Confirmada</b>")],
    [_c("<b>H2:</b> maior pluralização implica nova competição"),
     _c("Parcial. NEP caiu (menos partidos efetivos), mas a "
       "composição mudou qualitativamente. A 'pluralização' é "
       "nova sem ser mais fragmentada."),
     _c("<b>Parcial</b>")],
    [_c("<b>H3:</b> centro-direita absorvida pela direita"),
     _c("Confirmada estruturalmente. PSDB 33-44% → 0,6-1,7% nas 8 "
       "zonas ricas; substituição por MDB+PRTB+NOVO. Paralelamente, "
       "mudança de modelo de captação (PJ/PF → FEFC)."),
     _c("<b>Confirmada</b>")],
    [_c("<b>H4:</b> voto de esquerda nos bairros ricos aponta "
       "para outras variáveis que não renda"),
     _c("<b>Confirmada de forma decisiva.</b> Renda explica 9% da "
       "variância ideológica; índice institucional explica 44% "
       "(66% em métrica alternativa). O ambiente institucional "
       "cultural-progressista foi politicamente ativado entre "
       "2016 e 2020 — compatível com Inglehart &amp; Norris."),
     _c("<b>Confirmada</b>")],
]
tab_hip = Table(dados_hip, colWidths=[5*cm, 8.5*cm, 2.5*cm])
tab_hip.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BACKGROUND", (2, 1), (2, 1), colors.HexColor("#c6e0c6")),
    ("BACKGROUND", (2, 2), (2, 2), colors.HexColor("#f0e6a0")),
    ("BACKGROUND", (2, 3), (2, 3), colors.HexColor("#c6e0c6")),
    ("BACKGROUND", (2, 4), (2, 4), colors.HexColor("#c6e0c6")),
]))
conteudo.append(tab_hip)

conteudo.append(h1("5.3 Diálogo com a literatura"))
conteudo.append(p(
    "Os achados conversam com cinco tradições de pesquisa:"
))
conteudo.append(p(
    "<b>Inglehart &amp; Norris (2016, 2019)</b> — o argumento de "
    "que a clivagem cultural (educação/cosmopolitismo vs "
    "nacionalismo/tradicionalismo) substitui a clivagem econômica "
    "em democracias contemporâneas recebe aqui evidência "
    "brasileira. O ponto de inflexão em SP (2016-2020) é "
    "comparável ao Brexit e à eleição de Trump como choques "
    "ativadores da dimensão cultural."
))
conteudo.append(p(
    "<b>Power &amp; Rodrigues-Silveira (2019)</b> — o mapeamento "
    "ideológico municipal brasileiro. Este trabalho estende o "
    "método deles ao nível infra-municipal (zonas eleitorais "
    "dentro de uma mesma cidade), confirmando a tese de "
    "reorganização não-pendular da direita brasileira ao longo "
    "dos anos 2010."
))
conteudo.append(p(
    "<b>Soares &amp; Terron (2008)</b> — \"Dois Lulas\" é o "
    "precursor clássico de análise espacial do voto "
    "presidencial. Este trabalho aplica a tradição "
    "desenvolvendo-a em escala metropolitana com granularidade "
    "de zona eleitoral."
))
conteudo.append(p(
    "<b>Marques (2015)</b> e a escola paulistana de "
    "sociologia urbana — a tese de que a hierarquia "
    "socioeconômica intra-metropolitana é estruturalmente "
    "estável recebe validação aqui: posições relativas das zonas "
    "ricas mantiveram-se entre 2010 e 2024, mesmo com variações "
    "substanciais de regime político nacional."
))
conteudo.append(p(
    "<b>Speck &amp; Mancuso (2015)</b> — a literatura sobre "
    "financiamento empresarial e sua reforma. Este trabalho "
    "identifica que o Fundo Especial reocupou o espaço "
    "regulatório aberto pela reforma de 2015, sem passar pelo "
    "doador individual — um achado que qualifica a narrativa "
    "de \"democratização\" do financiamento com dados temporais "
    "de 4 ciclos municipais."
))

conteudo.append(h1("5.4 Limitações"))
conteudo.append(p(
    "<b>(a) Censo 2010.</b> A variável \"renda\" usa dados de 2010, "
    "14 anos antes do voto analisado. Mitigações: (1) a "
    "hierarquia relativa de renda das zonas ricas de SP é "
    "estruturalmente estável (literatura de sociologia urbana); "
    "(2) a defasagem atenua correlações — não as infla — tornando "
    "o R² = 0,088 um limite superior conservador; (3) o índice "
    "institucional usa base CEM/USP 2022 (contemporânea à eleição), "
    "não sofre defasagem."
))
conteudo.append(p(
    "<b>(b) Índice institucional ad-hoc.</b> O índice é construído "
    "por matching de palavras-chave nos nomes dos locais de "
    "votação. Refinamentos futuros: (1) cruzar com cadastro Inep "
    "(escolas) e cadastros culturais oficiais; (2) validação "
    "externa por survey de especialistas em educação paulistana; "
    "(3) análise textual do projeto pedagógico das escolas. A "
    "robustez do resultado (R² = 0,44) sugere que o índice "
    "captura o fenômeno central mesmo com proxy imprecisa."
))
conteudo.append(p(
    "<b>(c) Análise observacional.</b> Os dados são correlacionais; "
    "causalidade só pode ser inferida indiretamente. O teste "
    "temporal (Parte III.6) adiciona dimensão plausivelmente "
    "causal — o fato do sinal emergir após um choque político "
    "identificável é mais compatível com ativação causal do que "
    "com correlação espúria. Mas identificação causal rigorosa "
    "exigiria desenhos de diferenças-em-diferenças ou "
    "experimentos naturais, que estão fora do escopo deste "
    "rascunho."
))
conteudo.append(p(
    "<b>(d) Recorte específico de SP.</b> Os achados são sobre "
    "zonas eleitorais da capital paulistana, 2012–2024. A "
    "replicação em outras capitais (Rio de Janeiro, Belo "
    "Horizonte, Recife) testaria a generalidade do mecanismo."
))

conteudo.append(h1("5.5 Agenda de pesquisa"))
conteudo.append(p(
    "Cinco próximos passos metodológicos para a dissertação:"
))
conteudo.append(p(
    "<b>1.</b> <b>Refinamento do índice institucional</b> via "
    "cadastros externos (Inep, Secretaria de Cultura, FAPESP) e "
    "validação por especialistas em educação paulistana."
))
conteudo.append(p(
    "<b>2.</b> <b>Replicação em outras capitais brasileiras</b> "
    "(Rio de Janeiro, Belo Horizonte, Porto Alegre, Curitiba, "
    "Recife). Se o padrão se repete, é mecanismo geral. Se não "
    "se repete, é específico de SP — e exige explicação local."
))
conteudo.append(p(
    "<b>3.</b> <b>Análise individual de candidato × local</b> "
    "(em vez de agregação por zona): para cada local de votação, "
    "regressão escore ~ tipo institucional + renda + densidade. "
    "~2.000 observações em vez de 58."
))
conteudo.append(p(
    "<b>4.</b> <b>Inferência causal rigorosa</b> via "
    "diferenças-em-diferenças usando a reforma do financiamento "
    "de 2015 como choque exógeno. Pergunta: o aumento do índice "
    "institucional como preditor foi acelerado pela reforma?"
))
conteudo.append(p(
    "<b>5.</b> <b>Integração com dados de inscrição USP/Mackenzie/"
    "PUC por origem</b>: proporção de eleitores na zona que são "
    "alunos ou funcionários dessas instituições — teste de "
    "mecanismo direto."
))

# ====================================================================
# REPRODUTIBILIDADE
# ====================================================================
conteudo.append(h1("5.6 Reprodutibilidade"))
conteudo.append(p(
    "Todo o código e os dados processados estão em repositório "
    "público: "
    "<font color='#1a4dd0'><u>github.com/miaguchi/democracia-em-dados</u></font>. "
    "O repositório contém 19 scripts Python (pipelines de ingestão, "
    "processamento e análise), 3 relatórios PDF independentes "
    "(base para este documento consolidado), 18 gráficos PNG e "
    "13 CSVs de saída. Todas as dependências são conhecidas "
    "(pandas, geopandas, matplotlib, statsmodels, esda/libpysal, "
    "reportlab, geobr) e instaláveis via conda-forge. Dados "
    "primários baixados via <i>TSEDownloader</i> (classe própria "
    "com download atômico e validação de Content-Length) do CDN "
    "do TSE. Geometrias via pacote <i>geobr</i>. Base de locais "
    "de votação baixada manualmente do portal DataCEM/USP."
))

# ====================================================================
# BIBLIOGRAFIA
# ====================================================================
conteudo.append(h1("Referências selecionadas"))
st_bib = ParagraphStyle(
    "bib", parent=styles["Normal"], fontSize=9, leading=12,
    alignment=TA_JUSTIFY, spaceAfter=4,
)
refs = [
    "Bartolini, S.; Mair, P. (1990). <i>Identity, Competition and "
    "Electoral Availability: The Stabilization of European "
    "Electorates 1885–1985</i>. Cambridge University Press.",
    "Bolognesi, B.; Ribeiro, E.; Codato, A. (2023). \"Uma Nova "
    "Classificação Ideológica dos Partidos Políticos Brasileiros\". "
    "<i>Dados</i>, 66(2).",
    "Curi, H. (2022). \"Ninho dos Tucanos: o PSDB em São Paulo "
    "(1994–2018)\". <i>Opinião Pública</i>, 27.",
    "Inglehart, R.; Norris, P. (2016). \"Trump, Brexit, and the Rise "
    "of Populism: Economic Have-Nots and Cultural Backlash\". HKS "
    "Working Paper RWP16-026.",
    "Inglehart, R.; Norris, P. (2019). <i>Cultural Backlash: Trump, "
    "Brexit, and Authoritarian Populism</i>. Cambridge University "
    "Press.",
    "Limongi, F.; Mesquita, L. (2008). \"Estratégia partidária e "
    "preferência dos eleitores: as eleições municipais em São "
    "Paulo entre 1985 e 2004\". <i>Novos Estudos CEBRAP</i>, 81.",
    "Marques, E. (2015). <i>A metrópole de São Paulo no século XXI: "
    "espaços, heterogeneidades e desigualdades</i>. Editora UNESP.",
    "Mancuso, W. P.; Speck, B. W. (2015). \"Financiamento "
    "empresarial na eleição para deputado federal (2002–2010): "
    "determinantes e consequências\". <i>Teoria &amp; Sociedade</i>, "
    "23(2).",
    "Miaguchi, T. S. C. (2023). \"Disputa partidária e comportamento "
    "político nos bairros ricos de São Paulo (2012–2022)\". Proposta "
    "de dissertação, DCP/FFLCH-USP.",
    "Pedersen, M. N. (1979). \"The Dynamics of European Party "
    "Systems: Changing Patterns of Electoral Volatility\". "
    "<i>European Journal of Political Research</i>, 7(1).",
    "Power, T. J. (2010). <i>Political right in postauthoritarian "
    "Brazil: elites, institutions, and democratization</i>. Penn "
    "State Press.",
    "Power, T. J.; Rodrigues-Silveira, R. (2019). \"Mapping "
    "Ideological Preferences in Brazilian Elections, 1994-2018: "
    "A Municipal-Level Study\". <i>Brazilian Political Science "
    "Review</i>, 13(1).",
    "Rocha, C. (2019). \"<i>Menos Marx, mais Mises</i>: uma gênese "
    "da nova direita brasileira (2006-2018)\". Tese de Doutorado, "
    "Universidade de São Paulo.",
    "Soares, G. A. D.; Terron, S. (2008). \"Dois Lulas: a geografia "
    "eleitoral da reeleição\". <i>Opinião Pública</i>, 14(2).",
    "Speck, B. W.; Balbachevsky, E. (2016). \"Identificação "
    "partidária e voto. As diferenças entre petistas e "
    "peessedebistas\". <i>Opinião Pública</i>, 22(3).",
    "Torres, H. G.; Marques, E.; Ferreira, M. P.; Bichir, R. (2003). "
    "\"Pobreza e espaço: padrões de segregação em São Paulo\". "
    "<i>Estudos Avançados</i>, 17(47).",
]
for r in refs:
    conteudo.append(Paragraph(r, st_bib))

# ====================================================================
# GERA
# ====================================================================
SAIDA.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(
    str(SAIDA),
    pagesize=A4,
    leftMargin=2.5 * cm, rightMargin=2.5 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Documento integrado de qualificação - Miaguchi",
    author="Thiago Suzuki Conti Miaguchi",
)
doc.build(conteudo)
print(f"PDF gerado: {SAIDA}")
print(f"Tamanho: {SAIDA.stat().st_size / 1024:.1f} KB")
