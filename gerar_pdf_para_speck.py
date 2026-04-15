"""Documento focado para apresentar ao Prof. Bruno W. Speck.

Versão do material empírico do projeto orientada especificamente para
a agenda de pesquisa sobre financiamento eleitoral, reforma de 2015 e
reorganização material da política brasileira. Serve como base para
conversa de orientação e apresentação dos achados mais relevantes à
sua linha de trabalho.
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

SAIDA = Path("outputs/documento_para_speck.pdf")

styles = getSampleStyleSheet()
st_titulo = ParagraphStyle("titulo", parent=styles["Title"], fontSize=17,
                           alignment=TA_CENTER, spaceAfter=12)
st_subt = ParagraphStyle("subt", parent=styles["Normal"], fontSize=11,
                         alignment=TA_CENTER, spaceAfter=5,
                         textColor=colors.HexColor("#444"))
st_h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=14,
                       spaceBefore=14, spaceAfter=8)
st_h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12,
                       spaceBefore=10, spaceAfter=5)
st_body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10.5,
                         leading=15, alignment=TA_JUSTIFY, spaceAfter=7)
st_leg = ParagraphStyle("leg", parent=styles["Italic"], fontSize=8,
                        alignment=TA_CENTER,
                        textColor=colors.HexColor("#555"), spaceAfter=12)
st_destaque = ParagraphStyle("destaque", parent=styles["Normal"],
                             fontSize=11, leading=16, alignment=TA_JUSTIFY,
                             spaceAfter=10, textColor=colors.HexColor("#1a4dd0"),
                             leftIndent=15, rightIndent=15,
                             borderWidth=0.5, borderColor=colors.HexColor("#1a4dd0"),
                             borderPadding=10, borderRadius=3)
st_cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8,
                         leading=11, alignment=TA_LEFT)
st_cell_c = ParagraphStyle("cell_c", parent=styles["Normal"], fontSize=8,
                           leading=11, alignment=TA_CENTER)
st_cell_b = ParagraphStyle("cell_b", parent=styles["Normal"], fontSize=8,
                           leading=11, fontName="Helvetica-Bold",
                           alignment=TA_CENTER)
st_bib = ParagraphStyle("bib", parent=styles["Normal"], fontSize=9,
                        leading=12, alignment=TA_JUSTIFY, spaceAfter=4)


def p(t): return Paragraph(t, st_body)
def h1(t): return Paragraph(t, st_h1)
def h2(t): return Paragraph(t, st_h2)
def destaque(t): return Paragraph(t, st_destaque)
def _c(t): return Paragraph(t, st_cell)
def _cc(t): return Paragraph(t, st_cell_c)
def _cb(t): return Paragraph(t, st_cell_b)


def tab(dados, col_widths):
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


conteudo = []

# ---------- CAPA ----------
conteudo.append(Paragraph(
    "Financiamento eleitoral, reforma de 2015<br/>"
    "e recomposição da direita paulistana (2012–2024)",
    st_titulo,
))
conteudo.append(Paragraph(
    "Apresentação dos achados empíricos do projeto<br/>"
    "\"Disputa partidária e comportamento político nos bairros ricos de São Paulo\"",
    st_subt,
))
conteudo.append(Spacer(1, 0.6 * cm))
conteudo.append(Paragraph(
    "<b>Candidato:</b> Thiago Suzuki Conti Miaguchi<br/>"
    "<b>Programa:</b> Pós-Graduação em Ciência Política — DCP/FFLCH/USP<br/>"
    "<b>Documento dirigido a:</b> Prof. Bruno Wilhelm Speck",
    st_subt,
))
conteudo.append(Spacer(1, 0.8 * cm))

conteudo.append(destaque(
    "Este documento apresenta três achados empíricos sobre "
    "financiamento eleitoral e recomposição partidária em São Paulo "
    "que dialogam diretamente com a agenda de pesquisa do Prof. "
    "Speck. O material é um recorte focado do relatório consolidado "
    "do projeto, organizado para servir como base para conversa de "
    "orientação. Código e dados primários em "
    "<font color='#1a4dd0'><u>github.com/miaguchi/democracia-em-dados</u></font>."
))

conteudo.append(h1("Os três achados centrais"))
conteudo.append(p(
    "<b>Achado 1 — Três eras regulatórias com assinaturas materiais "
    "distintas.</b> A análise dos quatro ciclos municipais "
    "(2012–2024) mostra que a reforma do financiamento eleitoral de "
    "2015 dividiu a trajetória do financiamento de vereadores "
    "paulistanos em três regimes empiricamente distinguíveis — "
    "2012 (era PJ), 2016 (era transicional sem FEFC), 2020–2024 "
    "(era FEFC consolidado). A janela 2016 teve participação "
    "temporária de pessoa física (41% do total), que desapareceu "
    "nos ciclos seguintes após a consolidação do Fundo Especial."
))
conteudo.append(p(
    "<b>Achado 2 — O PSDB paulistano era empresarial, não "
    "\"progressista de classe média\".</b> Dados de prestação de "
    "contas de 2012 mostram que os candidatos a vereador mais "
    "votados em Pinheiros e Indianópolis captavam 37% e 46% "
    "(respectivamente) via pessoa jurídica, principalmente de "
    "construtoras (Construtora OAS, WTorre, UTC Engenharia, "
    "S.A. Paulista, Passarelli), bancos (Itaú Unibanco) e empresas "
    "de engenharia. A imagem canônica do tucanato como \"doador "
    "individual de classe média educada\" é empiricamente falsa "
    "para o legislativo municipal paulistano pré-2015. A estrutura "
    "material do PSDB era idêntica à dos demais partidos da "
    "direita — empresarial."
))
conteudo.append(p(
    "<b>Achado 3 — A recomposição pós-PSDB ocorreu em três "
    "direções simultâneas, não uma.</b> O colapso do PSDB "
    "paulistano (de 48% do voto de vereador em Pinheiros em 2012 "
    "para praticamente zero em 2024) não produziu uma herdeira "
    "única. Produziu três herdeiras com modelos materiais "
    "distintos: (a) <b>NOVO</b>, que manteve captação de pessoa "
    "física via mobilização digital (candidatos como Janaína "
    "Carla com 99% PF e Cristina Monteiro com 16% PF); (b) "
    "<b>MDB de Ricardo Nunes</b>, continuidade institucional "
    "direta do ciclo Covas (Nunes foi vice-prefeito, assumiu com "
    "a morte de Bruno Covas em 2021), com captação via FEFC "
    "partidário; (c) <b>PL/PP</b>, conservadorismo duro com "
    "dependência <i>quase integral</i> do FEFC (Janaína Paschoal "
    "100% partido, Lucas Pavanato 93%, Murillo Lima 96%). <b>A "
    "H3 do projeto, formulada como \"absorção da centro-direita "
    "pela direita\", precisa ser reformulada como dispersão em "
    "três subcampos com bases materiais próprias</b>."
))

# ---------- PARTE 1: TRÊS ERAS ----------
conteudo.append(PageBreak())
conteudo.append(h1("1. Três eras regulatórias do financiamento de vereadores em SP"))
conteudo.append(p(
    "A série temporal completa do financiamento eleitoral de "
    "vereadores paulistanos atravessa um dos períodos regulatórios "
    "mais turbulentos da história brasileira pós-redemocratização. "
    "Três eras empiricamente distinguíveis:"
))
dados_eras = [
    [_cb("Ano"), _cb("Total R$ mi"), _cb("% Partido"),
     _cb("% PF"), _cb("% PJ"), _cb("% Próprio"), _cb("Era")],
    [_c("2012"), _cc("93,1"), _cc("41,7"), _cc("0,0"),
     _cc("<b>23,8</b>"), _cc("8,0"), _c("PJ permitida")],
    [_c("2016"), _cc("43,1"), _cc("28,0"), _cc("<b>41,0</b>"),
     _cc("0,0"), _cc("21,7"), _c("Pós-reforma, pré-FEFC")],
    [_c("2020"), _cc("84,0"), _cc("65,0"), _cc("23,7"),
     _cc("0,0"), _cc("8,1"), _c("FEFC inicial")],
    [_c("2024"), _cc("<b>209,4</b>"), _cc("<b>86,7</b>"), _cc("9,1"),
     _cc("0,0"), _cc("2,2"), _c("FEFC consolidado")],
]
conteudo.append(tab(dados_eras, [1.5*cm, 2*cm, 1.8*cm, 1.5*cm, 1.5*cm, 1.8*cm, 4*cm]))
conteudo.append(Spacer(1, 0.3 * cm))

conteudo.extend(fig(
    "outputs/grafico_trajetoria_financiamento.png",
    w_cm=15,
    legenda="Figura 1 — Trajetória das fontes de financiamento dos "
    "vereadores SP em quatro ciclos municipais (2012–2024). "
    "Eras: PJ (2012) → PF transicional (2016) → FEFC dominante "
    "(2020-2024). A janela 2016 foi o único momento em que "
    "pessoa física foi a fonte principal, e durou apenas uma "
    "eleição."
))

conteudo.append(h2("Interpretação substantiva"))
conteudo.append(p(
    "A leitura mais direta desses números é: <b>a reforma de 2015 "
    "não produziu a democratização do financiamento que seus "
    "defensores esperavam</b>. A pessoa física subiu dramaticamente "
    "em 2016 (0% → 41%) como consequência direta da proibição de "
    "PJ — os candidatos passaram a mobilizar diretamente os "
    "doadores individuais porque não tinham alternativa. Mas o "
    "Fundo Especial de Financiamento de Campanha, criado em 2017, "
    "inflado a cada ciclo, <b>reocupou o espaço aberto pela "
    "reforma pelo caminho institucional-partidário</b>. Em 2024, "
    "PF é 9,1% e FEFC+Fundo Partidário somam 86,7%."
))
conteudo.append(destaque(
    "A leitura historicamente precisa é: a reforma proibiu o "
    "doador empresarial, e o Estado — via FEFC — assumiu o "
    "lugar dos doadores empresariais, sem produzir transição "
    "sustentada para financiamento popular. O aumento de PF em "
    "2016 foi um efeito transitório, não uma consolidação."
))
conteudo.append(p(
    "Essa leitura é mais forte do que \"a reforma falhou\" ou "
    "\"a reforma democratizou\". Ela identifica <b>um mecanismo "
    "específico</b>: o Estado substitui o capital empresarial "
    "como fonte primária do financiamento, via partidos. O "
    "resultado líquido é um <b>sistema de financiamento "
    "estatal-partidário</b>, que não tem as patologias do "
    "financiamento empresarial (capturas setoriais específicas) "
    "mas também não tem a legitimidade democrática que o "
    "financiamento popular poderia dar."
))
conteudo.append(p(
    "<b>Questão aberta para conversa:</b> essa dinâmica "
    "reproduz-se em outras capitais brasileiras? Rio de "
    "Janeiro, Belo Horizonte e Porto Alegre tiveram trajetórias "
    "comparáveis? Se sim, temos um padrão regulatório "
    "generalizado e não uma especificidade paulistana. Seria "
    "útil saber se há trabalhos do grupo do Prof. Speck (ou "
    "coautores) que investigaram essa dimensão para outras "
    "cidades."
))

# ---------- PARTE 2: DOADORES 2012 ----------
conteudo.append(PageBreak())
conteudo.append(h1("2. Quem eram os doadores empresariais de 2012?"))
conteudo.append(p(
    "A categoria \"recursos de pessoa jurídica\" em 2012 somou "
    "R$ 22,2 milhões para vereadores de SP — 23,8% do total "
    "arrecadado. A composição setorial é politicamente reveladora:"
))
dados_setores = [
    [_cb("Setor econômico"), _cb("R$ total"), _cb("N. doações")],
    [_c("Construção de edifícios"), _cc("R$ 3.791.200"), _cc("75")],
    [_c("Incorporação imobiliária"), _cc("R$ 1.964.500"), _cc("50")],
    [_c("Outras obras de engenharia civil"), _cc("R$ 1.960.000"), _cc("25")],
    [_c("Bancos múltiplos com carteira comercial"), _cc("R$ 938.500"), _cc("19")],
    [_c("Construção de rodovias e ferrovias"), _cc("R$ 733.920"), _cc("25")],
    [_c("Obras de montagem industrial"), _cc("R$ 715.000"), _cc("5")],
    [_c("Edição impressão cadastros"), _cc("R$ 409.370"), _cc("119")],
    [_c("Comércio varejista de combustíveis"), _cc("R$ 360.086"), _cc("20")],
    [_c("Serviços de engenharia"), _cc("R$ 298.180"), _cc("20")],
    [_c("Vigilância e segurança privada"), _cc("R$ 256.360"), _cc("6")],
]
conteudo.append(tab(dados_setores, [8*cm, 3.5*cm, 2.5*cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(p(
    "<b>Construção civil e imobiliário somados</b> — edifícios, "
    "incorporação, engenharia civil, rodovias, montagem industrial "
    "— respondem por R$ 9,9 milhões = 45% de todo o financiamento "
    "empresarial de vereadores de SP em 2012. Bancos são 4%. Os "
    "demais setores pulverizam. <b>Construtoras financiavam a "
    "política municipal paulistana</b>, um padrão coerente com a "
    "intersecção entre licenciamento urbanístico, contratos de "
    "obras públicas e decisões de plano diretor no âmbito da "
    "Câmara Municipal."
))
conteudo.append(h2("Empresas individuais no topo"))
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
conteudo.append(tab(dados_empresas, [10*cm, 4*cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(p(
    "Duas das dez maiores doadoras de vereadores de SP em 2012 — "
    "<b>Construtora OAS</b> e <b>UTC Engenharia</b> — viriam a "
    "ser citadas centralmente nos desdobramentos da Operação Lava "
    "Jato a partir de 2014, que terminou por justificar "
    "politicamente a reforma de 2015. O dado é consistente com o "
    "diagnóstico de Mancuso &amp; Speck (2015): o financiamento "
    "empresarial não era uma patologia abstrata — era uma rede "
    "concreta de interdependências entre setores específicos "
    "(construção civil, grandes bancos) e a representação "
    "política local."
))
conteudo.append(p(
    "<b>Nota metodológica:</b> consegui reconstruir essa tabela "
    "a partir do arquivo <i>receitas_candidatos_2012_SP.txt</i> "
    "do TSE (repositório de dados abertos). O layout de 2012 é "
    "diferente do pós-2018 — usa campos em português, menos "
    "colunas, formato TXT — mas é completo e permite a análise "
    "setorial. O pipeline de padronização está no repositório "
    "público em <i>trajetoria_financiamento.py</i>, caso seja "
    "de interesse reusar para outros estudos."
))

# ---------- PARTE 3: TRAJETÓRIA DINÁSTICA ----------
conteudo.append(PageBreak())
conteudo.append(h1("3. A trajetória dinástica: Matarazzo → Covas → Monteiro"))
conteudo.append(p(
    "A recomposição do voto para vereador nas zonas ricas de SP "
    "é mais interessante quando observada no nível do candidato "
    "individual do que no nível do partido. A tabela abaixo "
    "lista os 3 candidatos mais votados em Pinheiros (Z251) e "
    "Indianópolis (Z258) em cada um dos quatro ciclos "
    "municipais:"
))
dados_traj = [
    [_cb("Ano"), _cb("Pinheiros (Z251) — top 3"),
     _cb("Indianópolis (Z258) — top 3")],
    [_c("<b>2012</b>"),
     _c("<b>Ângelo Matarazzo (PSDB)</b> 9.606 · "
       "Nabil Bonduki (PT) 4.742 · "
       "Floriano Pesaro (PSDB) 3.392"),
     _c("<b>Ângelo Matarazzo (PSDB)</b> 11.968 · "
       "Mario Covas Neto (PSDB) 5.046 · "
       "Alvarenga Tripol (PV) 4.907")],
    [_c("<b>2016</b>"),
     _c("<b>Eduardo Suplicy (PT)</b> 5.392 · "
       "Daniel Annenberg (PSDB) 2.849 · "
       "Mario Covas Neto (PSDB) 2.785"),
     _c("<b>Eduardo Suplicy (PT)</b> 5.881 · "
       "Mario Covas Neto (PSDB) 5.752 · "
       "Fernando Bispo (DEM) 3.116")],
    [_c("<b>2020</b>"),
     _c("Eduardo Suplicy (PT) 2.324 · "
       "<b>Janaína Carla (NOVO)</b> 2.070 · "
       "Erika Silva (PSOL) 1.807"),
     _c("<b>Janaína Carla (NOVO)</b> 3.322 · "
       "Felipe Becari (PSD) 2.675 · "
       "Suplicy (PT) 2.587")],
    [_c("<b>2024</b>"),
     _c("<b>Cristina Monteiro (NOVO)</b> 5.552 · "
       "<b>Marina Bragante (Rede)</b> 5.286 · "
       "Nabil Bonduki (PT) 3.534"),
     _c("<b>Cristina Monteiro (NOVO)</b> 6.553 · "
       "Janaína Paschoal (PP) 3.773 · "
       "Lucas Pavanato (PL) 3.535")],
]
conteudo.append(tab(dados_traj, [1.5*cm, 7*cm, 7*cm]))
conteudo.append(Spacer(1, 0.3 * cm))

conteudo.append(p(
    "<b>Observações:</b>"
))
conteudo.append(p(
    "<b>(a) Em 2012, duas famílias tradicionais paulistanas "
    "dominavam a representação dos bairros ricos via PSDB:</b> "
    "Ângelo Matarazzo (sobrinho do ex-deputado Andrea Matarazzo, "
    "família de industriais) é o candidato mais votado em "
    "<b>ambas as zonas</b>, somando quase 22 mil votos. Mario "
    "Covas Neto — sobrinho-neto do ex-prefeito/ex-governador "
    "Mario Covas e primo de Bruno Covas — é o segundo mais "
    "votado em Indianópolis. Aqui há uma <b>continuidade "
    "familiar-partidária quase literal</b>, que ainda não foi "
    "perturbada."
))
conteudo.append(p(
    "<b>(b) Em 2016, emerge Eduardo Matarazzo Suplicy (PT)</b> "
    "como reocupação simbólica. Ele é ele próprio descendente da "
    "família Matarazzo por lado materno, e foi enviado pelo PT "
    "para \"roubar\" os bairros ricos que pelas hipóteses "
    "convencionais de voto de classe deveriam ser PSDB. Vence "
    "em Pinheiros (5.392) e em Indianópolis (5.881). O Mario "
    "Covas Neto do PSDB ainda aparece no top 3 das duas "
    "zonas — mas em posições secundárias. O PSDB mantém "
    "presença via Daniel Annenberg em Pinheiros."
))
conteudo.append(p(
    "<b>(c) Em 2020, aparece pela primeira vez Janaína Carla "
    "de Lima (NOVO)</b>, candidata com captação <b>99% pessoa "
    "física</b>. Ela é o primeiro sinal claro de que um modelo "
    "alternativo de financiamento sobreviveria no ambiente "
    "pós-reforma: não é o PSDB, é o NOVO, e não é via empresas "
    "nem via FEFC — é via doação individual digital. O PSDB "
    "some do top 3 nas duas zonas simultaneamente nesse ano."
))
conteudo.append(p(
    "<b>(d) Em 2024, a transição está consolidada.</b> Cristina "
    "Monteiro (NOVO) — ex-PSDB que migrou para o Novo em 2018 — "
    "é a mais votada em <b>ambas</b> as zonas (12.105 votos "
    "somados), herdando o espaço Matarazzo/Covas. Marina "
    "Bragante (Rede, psicóloga) aparece como complemento "
    "progressista em Pinheiros. Nabil Bonduki (PT, professor da "
    "FAU-USP) sobrevive como o único candidato presente tanto "
    "em 2012 quanto em 2024 — é o elo de continuidade do PT em "
    "Pinheiros ao longo dos 12 anos. <b>Em Indianópolis, o "
    "top 3 é totalmente de direita não-tucana</b> (NOVO, PP, PL)."
))

conteudo.append(h2("Caso análogo no executivo: Ricardo Nunes"))
conteudo.append(p(
    "A trajetória análoga no Executivo vale mencionar porque "
    "adiciona uma dimensão de continuidade institucional ao "
    "argumento. <b>Ricardo Nunes (MDB)</b> foi o vice-prefeito "
    "de Bruno Covas (PSDB) na chapa de 2020. Com a morte de "
    "Bruno Covas em maio de 2021, assumiu a prefeitura. Em "
    "2024, elegeu-se pelo MDB após coligação com o PP e com o "
    "PL. É, portanto, <b>continuidade institucional quase "
    "literal do ciclo Covas-Serra-Alckmin</b>, agora via um "
    "partido diferente (MDB em vez de PSDB). A transição "
    "\"PSDB → MDB\" no executivo é, na prática, a mesma "
    "continuidade pessoal-institucional, com mudança "
    "apenas de legenda."
))

# ---------- PARTE 4: PERFIL DE CAPTAÇÃO ----------
conteudo.append(PageBreak())
conteudo.append(h1("4. Perfil de captação dos top-6 candidatos por zona"))
conteudo.append(p(
    "A síntese mais direta da reorganização material é a "
    "comparação entre o perfil médio de captação dos 6 "
    "candidatos mais votados em cada zona, ponderada pelos votos "
    "recebidos, ao longo dos quatro ciclos. Para Pinheiros "
    "(Z251):"
))
dados_pin = [
    [_cb("Ano"), _cb("% PF"), _cb("% Partido"), _cb("% PJ"),
     _cb("Partidos do top-6")],
    [_c("2012"), _cc("0%"), _cc("51%"), _cc("<b>37%</b>"),
     _c("PSDB, PT, PPS, PV")],
    [_c("2016"), _cc("<b>68%</b>"), _cc("2%"), _cc("0%"),
     _c("PT, PSDB, NOVO, Rede")],
    [_c("2020"), _cc("59%"), _cc("29%"), _cc("0%"),
     _c("PT, NOVO, PSOL, PSDB")],
    [_c("2024"), _cc("18%"), _cc("<b>77%</b>"), _cc("0%"),
     _c("NOVO, Rede, PT, PSOL")],
]
conteudo.append(tab(dados_pin, [1.5*cm, 1.2*cm, 1.8*cm, 1.5*cm, 7*cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(p("E para Indianópolis (Z258):"))
dados_ind = [
    [_cb("Ano"), _cb("% PF"), _cb("% Partido"), _cb("% PJ"),
     _cb("Partidos do top-6")],
    [_c("2012"), _cc("0%"), _cc("43%"), _cc("<b>46%</b>"),
     _c("PSDB, PV, PPS, PSD")],
    [_c("2016"), _cc("<b>59%</b>"), _cc("0%"), _cc("0%"),
     _c("PT, PSDB, DEM, NOVO, PV")],
    [_c("2020"), _cc("57%"), _cc("25%"), _cc("0%"),
     _c("NOVO, PSD, PT, Patriota")],
    [_c("2024"), _cc("10%"), _cc("<b>88%</b>"), _cc("0%"),
     _c("NOVO, PP, PL, Rede, PSOL")],
]
conteudo.append(tab(dados_ind, [1.5*cm, 1.2*cm, 1.8*cm, 1.5*cm, 7*cm]))
conteudo.append(Spacer(1, 0.3 * cm))

conteudo.append(h2("Dois achados desmontam narrativas canônicas"))
conteudo.append(p(
    "<b>(i) O PSDB dos bairros ricos NÃO era sustentado por "
    "doador individual.</b> A imagem convencional de que o "
    "tucanato paulistano seria financiado por \"classe média "
    "educada via doações individuais\" é empiricamente falsa "
    "para vereador em 2012: <b>zero</b> pessoa física nas duas "
    "zonas, 37% e 46% de pessoa jurídica. O PSDB era "
    "empresarial como qualquer outro partido brasileiro pré-"
    "reforma. Essa descoberta contraria a hipótese implícita em "
    "parte da literatura sobre representação de classe média "
    "via PSDB, e merece ser discutida com atenção."
))
conteudo.append(p(
    "<b>(ii) A democratização do financiamento existiu, foi "
    "breve, e desapareceu.</b> Entre 2016 e 2020, os candidatos "
    "mais votados nos bairros ricos paulistanos captavam 57–68% "
    "de suas receitas via pessoa física. Essa é a janela em "
    "que a reforma de 2015 funcionou conforme o desenho original "
    "— proibir o empresarial, forçar candidatos a mobilizar "
    "doadores individuais. Mas o FEFC, criado em 2017 e "
    "inflado nos ciclos 2020 e 2024, reocupou esse espaço. Em "
    "2024, PF é residual (10–18%) e partido é dominante (77–88%). "
    "<b>O eleitor-doador de Pinheiros existiu eleitoralmente "
    "por uma janela de 4–8 anos e foi estatizado.</b>"
))

conteudo.append(destaque(
    "Essas duas descobertas são, em si, resultados substantivos "
    "que podem alimentar um capítulo de dissertação ou um paper "
    "curto para revista especializada. Elas dialogam diretamente "
    "com Mancuso (2012), Mancuso &amp; Speck (2015) e Sacchet "
    "&amp; Speck (2012), e adicionam granularidade intra-municipal "
    "a um debate que historicamente opera no nível do município "
    "ou do estado."
))

# ---------- PARTE 5: NOVO vs PL/PP ----------
conteudo.append(h1("5. Diferenciação intra-partidária no modelo pós-FEFC"))
conteudo.append(p(
    "Um achado lateral importante: mesmo dentro do campo pós-"
    "PSDB, os partidos respondem à reforma com modelos "
    "materiais distintos. Dois perfis claros emergem entre os "
    "candidatos com voto concentrado nas zonas ricas em 2024:"
))
dados_modelos = [
    [_cb("Candidato"), _cb("Partido"), _cb("% PF"), _cb("% Partido"),
     _cb("Votos")],
    [_c("Janaína Carla (2020)"), _c("<b>NOVO</b>"), _cc("<b>99%</b>"),
     _cc("1%"), _cc("2.070")],
    [_c("Cristina Monteiro (2020)"), _c("<b>NOVO</b>"), _cc("<b>79%</b>"),
     _cc("2%"), _cc("1.789")],
    [_c("Fernando Holiday (2020)"), _c("Patriota"), _cc("<b>75%</b>"),
     _cc("0%"), _cc("2.373")],
    [_c("Cristina Monteiro (2024)"), _c("<b>NOVO</b>"), _cc("16%"),
     _cc("82%"), _cc("56.904")],
    [_c("Marina Bragante (2024)"), _c("Rede"), _cc("28%"),
     _cc("67%"), _cc("39.147")],
    [_c("Nabil Bonduki (2024)"), _c("PT"), _cc("25%"),
     _cc("71%"), _cc("3.534")],
    [_c("Janaína Paschoal (2024)"), _c("<b>PP</b>"), _cc("0%"),
     _cc("<b>100%</b>"), _cc("1.758")],
    [_c("Lucas Pavanato (2024)"), _c("<b>PL</b>"), _cc("7%"),
     _cc("<b>93%</b>"), _cc("1.741")],
    [_c("Murillo Lima (2024)"), _c("<b>PP</b>"), _cc("2%"),
     _cc("<b>96%</b>"), _cc("1.346")],
]
conteudo.append(tab(dados_modelos, [5*cm, 2.5*cm, 1.5*cm, 2*cm, 2*cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(p(
    "<b>Padrão:</b> PL e PP, que substituíram institucionalmente "
    "o PSDB em 2024 nas zonas ricas, operam com <b>dependência "
    "quase exclusiva do FEFC via partido</b>. O NOVO mantém "
    "(embora em menor proporção do que em 2020) <b>captação "
    "individual ativa</b>. Isso indica que a reforma de 2015 + "
    "FEFC criaram um <b>sistema bipartido internamente</b>: "
    "partidos que mantiveram infraestrutura de captação "
    "digital-individual (NOVO é o caso puro, Rede e PT "
    "ainda captam PF em níveis não-desprezíveis) vs partidos "
    "que operam 100% via repasse partidário (PL, PP, União, "
    "Republicanos)."
))
conteudo.append(p(
    "<b>Questão para discussão:</b> essa diferenciação é "
    "transitória ou estrutural? Os partidos que hoje dependem "
    "100% do FEFC nas zonas ricas (PL, PP) reconstruirão "
    "infraestrutura de captação de PF em ciclos futuros, ou "
    "essa é uma consequência estável da reforma — criando "
    "uma clivagem entre \"partidos digitais\" e \"partidos "
    "estatais-partidários\" no interior do espaço político "
    "brasileiro?"
))

# ---------- PARTE 6: H3 REFORMULADA ----------
conteudo.append(h1("6. Reformulação da H3 do projeto original"))
conteudo.append(p(
    "A Hipótese 3 do projeto original (Miaguchi, 2023) afirma: "
    "<i>\"o recrutamento e as disputas intrapartidárias da "
    "centro-direita ao longo do tempo influenciaram o novo "
    "comportamento eleitoral marcado pela contestação. "
    "Destarte, a centro-direita foi atraída pelo campo da "
    "direita e extrema-direita\"</i>. Os achados desta análise "
    "sugerem que a hipótese precisa ser <b>reformulada com maior "
    "precisão empírica</b>:"
))
conteudo.append(destaque(
    "A centro-direita paulistana não foi absorvida pela direita — "
    "foi dispersada em três subcampos com bases materiais "
    "próprias. <b>(a) NOVO</b>, renovação liberal com captação "
    "digital de PF e identidade cosmopolita; <b>(b) MDB de "
    "Nunes</b>, continuidade institucional direta do ciclo "
    "Covas via sucessão pessoal; <b>(c) PL/PP/União</b>, "
    "conservadorismo duro com dependência quase integral do "
    "FEFC e ausência de infraestrutura de captação de doador "
    "individual."
))
conteudo.append(p(
    "O colapso do PSDB é empiricamente real (de 48% do voto "
    "de vereador em Pinheiros em 2012 para virtualmente zero "
    "em 2024), mas a reorganização da oferta partidária que "
    "substitui esse espaço não é unilateral. Há <b>três "
    "circuitos distintos</b> competindo simultaneamente pelo "
    "eleitor de centro-direita paulistano, e os três operam "
    "com modelos materiais diferentes, alicerces organizacionais "
    "diferentes e perfis simbólicos diferentes."
))
conteudo.append(p(
    "<b>Implicação teórica:</b> não há uma única narrativa de "
    "\"radicalização à direita\" aplicável aos bairros ricos "
    "paulistanos. Há três trajetórias paralelas, cada uma "
    "com sua própria lógica, que convivem e competem entre si "
    "no mesmo espaço territorial. A análise deve tratar "
    "\"direita\" como campo heterogêneo, não como categoria "
    "monolítica."
))

# ---------- QUESTÕES PARA O PROF. SPECK ----------
conteudo.append(PageBreak())
conteudo.append(h1("Questões abertas para conversa de orientação"))
conteudo.append(p(
    "As análises apresentadas nas seções anteriores levantam "
    "cinco questões substantivas que gostaria de discutir na "
    "orientação:"
))
conteudo.append(p(
    "<b>1. Generalidade do padrão regulatório.</b> A trajetória "
    "PJ → PF transicional → FEFC dominante se repete em outras "
    "capitais brasileiras, ou é específica de SP? Há análises "
    "comparativas já feitas pelo grupo do Prof. Speck ou por "
    "outros pesquisadores que investigaram essa questão?"
))
conteudo.append(p(
    "<b>2. O caso NOVO como exceção substantiva.</b> O NOVO "
    "aparece como o partido que mantém infraestrutura de "
    "captação individual no período pós-FEFC. Isso é "
    "sociologicamente interessante porque vai contra o padrão "
    "do restante da direita (PL, PP, União). Há estudos "
    "sistemáticos do modelo de financiamento do Novo? Seria "
    "produtivo desenvolver um capítulo específico sobre esse "
    "caso como exemplo de variação intra-campo da direita "
    "brasileira pós-2018?"
))
conteudo.append(p(
    "<b>3. Relação entre reforma de 2015 e ascensão do FEFC.</b> "
    "A reforma de 2015 é usualmente narrada como \"democratização\" "
    "do financiamento. Os dados sugerem que essa interpretação "
    "é incompleta — a democratização durou uma eleição e foi "
    "substituída pela estatização via FEFC. Como o Prof. Speck "
    "leria essa evidência empírica? Há continuidade com "
    "trabalhos anteriores do grupo (Mancuso &amp; Speck, 2015; "
    "Speck &amp; Balbachevsky, 2016) ou há novidade aqui?"
))
conteudo.append(p(
    "<b>4. Identificação causal via a reforma de 2015.</b> A "
    "reforma como choque exógeno permite, em princípio, usar "
    "desenhos de diferenças-em-diferenças para estimar seus "
    "efeitos sobre diferentes variáveis (composição de "
    "candidatos, perfil de doadores, representação de gênero, "
    "etc.). O Prof. Speck considera essa uma estratégia "
    "metodológica viável? Há armadilhas específicas de "
    "identificação causal na reforma de financiamento "
    "brasileira que eu deveria conhecer?"
))
conteudo.append(p(
    "<b>5. A variável gênero.</b> A proposta original do projeto "
    "cita Sacchet &amp; Speck (2012) sobre o gap de "
    "financiamento entre homens e mulheres. Ainda não "
    "desenvolvi essa dimensão empiricamente — os dados do "
    "TSE têm a variável gênero e permitem fazer essa análise "
    "cruzada com o financiamento e com o tipo de zona. Seria "
    "útil desenvolver esse capítulo, especialmente no "
    "contexto das políticas de cota do FEFC para mulheres "
    "(30% a partir de 2018). Há trabalhos recentes do grupo "
    "sobre esse tema que eu deveria incorporar?"
))

# ---------- BIBLIOGRAFIA ----------
conteudo.append(h1("Referências"))
refs = [
    "Bartolini, S.; Mair, P. (1990). <i>Identity, Competition and "
    "Electoral Availability: The Stabilization of European "
    "Electorates 1885–1985</i>. Cambridge University Press.",
    "Curi, H. (2022). \"Ninho dos Tucanos: o PSDB em São Paulo "
    "(1994–2018)\". <i>Opinião Pública</i>, 27.",
    "Limongi, F.; Mesquita, L. (2008). \"Estratégia partidária e "
    "preferência dos eleitores: as eleições municipais em São "
    "Paulo entre 1985 e 2004\". <i>Novos Estudos CEBRAP</i>, 81.",
    "Mancuso, W. P. (2012). \"Investimento eleitoral no Brasil: "
    "balanço da literatura e agenda de pesquisa\". <i>Revista de "
    "Sociologia e Política</i>, 20(43).",
    "Mancuso, W. P.; Speck, B. W. (2015). \"Financiamento "
    "empresarial na eleição para deputado federal (2002–2010): "
    "determinantes e consequências\". <i>Teoria &amp; Sociedade</i>, "
    "23(2).",
    "Miaguchi, T. S. C. (2023). \"Disputa partidária e comportamento "
    "político nos bairros ricos de São Paulo (2012–2022)\". "
    "Proposta de dissertação, DCP/FFLCH-USP.",
    "Pedersen, M. N. (1979). \"The Dynamics of European Party "
    "Systems: Changing Patterns of Electoral Volatility\". "
    "<i>European Journal of Political Research</i>, 7(1).",
    "Sacchet, T.; Speck, B. W. (2012). \"Financiamento eleitoral, "
    "representação política e gênero: uma análise das eleições "
    "de 2006\". <i>Opinião Pública</i>, 18(1).",
    "Speck, B. W. (2013). \"Nem ideológica, nem oportunista: a "
    "filiação partidária no contexto pré-eleitoral no Brasil\". "
    "<i>Cadernos Adenauer</i>, XIV(2).",
    "Speck, B. W.; Balbachevsky, E. (2016). \"Identificação "
    "partidária e voto: as diferenças entre petistas e "
    "peessedebistas\". <i>Opinião Pública</i>, 22(3).",
    "Speck, B. W.; Mancuso, W. P. (2014). \"A study on the impact "
    "of campaign finance, political capital and gender on "
    "electoral performance\". <i>Brazilian Political Science "
    "Review</i>, 8(1).",
]
for r in refs:
    conteudo.append(Paragraph(r, st_bib))

# ---------- GERAR ----------
SAIDA.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(
    str(SAIDA),
    pagesize=A4,
    leftMargin=2.5 * cm, rightMargin=2.5 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Financiamento eleitoral SP 2012-2024 - para Speck",
    author="Thiago Suzuki Conti Miaguchi",
)
doc.build(conteudo)
print(f"PDF gerado: {SAIDA}")
print(f"Tamanho: {SAIDA.stat().st_size / 1024:.1f} KB")
