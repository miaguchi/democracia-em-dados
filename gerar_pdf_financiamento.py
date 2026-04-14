"""Relatório PDF — Financiamento eleitoral dos vereadores das zonas ricas de SP, 2024."""

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

SAIDA = Path("outputs/relatorio_financiamento_zonas_ricas.pdf")

styles = getSampleStyleSheet()
st_titulo = ParagraphStyle(
    "titulo", parent=styles["Title"], fontSize=16, alignment=TA_CENTER, spaceAfter=10
)
st_subt = ParagraphStyle(
    "subt",
    parent=styles["Normal"],
    fontSize=11,
    alignment=TA_CENTER,
    spaceAfter=4,
    textColor=colors.HexColor("#444"),
)
st_h1 = ParagraphStyle(
    "h1", parent=styles["Heading1"], fontSize=13, spaceBefore=12, spaceAfter=6
)
st_h2 = ParagraphStyle(
    "h2", parent=styles["Heading2"], fontSize=11, spaceBefore=8, spaceAfter=4
)
st_body = ParagraphStyle(
    "body",
    parent=styles["Normal"],
    fontSize=10,
    leading=14,
    alignment=TA_JUSTIFY,
    spaceAfter=6,
)
st_cell = ParagraphStyle(
    "cell", parent=styles["Normal"], fontSize=8, leading=11, alignment=TA_LEFT
)
st_cell_c = ParagraphStyle(
    "cell_c", parent=styles["Normal"], fontSize=8, leading=11, alignment=TA_CENTER
)
st_cell_b = ParagraphStyle(
    "cell_b",
    parent=styles["Normal"],
    fontSize=8,
    leading=11,
    fontName="Helvetica-Bold",
    alignment=TA_CENTER,
)


def p(t):
    return Paragraph(t, st_body)


def h1(t):
    return Paragraph(t, st_h1)


def h2(t):
    return Paragraph(t, st_h2)


def _c(t):
    return Paragraph(t, st_cell)


def _cc(t):
    return Paragraph(t, st_cell_c)


def _cb(t):
    return Paragraph(t, st_cell_b)


def tabela_estilizada(dados, col_widths, dest_cols_center=None):
    t = Table(dados, colWidths=col_widths)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]
    t.setStyle(TableStyle(style))
    return t


conteudo = []

conteudo.append(
    Paragraph(
        "Financiamento eleitoral dos vereadores nas zonas ricas de São Paulo<br/>"
        "Eleições municipais de 2024",
        st_titulo,
    )
)
conteudo.append(
    Paragraph(
        "Relatório complementar à análise de comportamento político<br/>"
        "— Projeto de dissertação, DCP/FFLCH-USP",
        st_subt,
    )
)
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(
    Paragraph(
        "<b>Candidato:</b> Thiago Suzuki Conti Miaguchi<br/>"
        "<b>Orientação indicada:</b> Bruno W. Speck, Glauco Peres da Silva<br/>"
        "<b>Dado primário:</b> TSE — Prestação de Contas Eleitorais 2024 "
        "(receitas_candidatos_2024_SP)",
        st_subt,
    )
)
conteudo.append(Spacer(1, 0.6 * cm))

conteudo.append(h1("1. Pergunta e motivação"))
conteudo.append(
    p(
        "Este relatório responde a uma pergunta específica derivada das "
        "Hipóteses 3 e 4 do projeto de dissertação (Miaguchi, 2023): <b>o "
        "perfil de financiamento dos vereadores cujo voto concentra nos "
        "bairros ricos progressistas (Pinheiros, Bela Vista, Perdizes) "
        "difere do perfil dos vereadores cujo voto concentra em bairros "
        "ricos conservadores (Jardim Paulista, Indianópolis) e em "
        "periferias populares?</b> O financiamento eleitoral é um indicador "
        "direto da infraestrutura material-organizacional do voto — "
        "complementa a análise puramente eleitoral e permite verificar se "
        "a distinção ideológica corresponde também a bases materiais "
        "distintas (Speck &amp; Mancuso, 2015; Sacchet &amp; Speck, 2012)."
    )
)

conteudo.append(h1("2. Trajetória temporal do financiamento (2012–2024)"))
conteudo.append(
    p(
        "Antes da análise de 2024, é importante contextualizar com a "
        "trajetória dos 4 ciclos municipais. O período cobre <b>três "
        "eras regulatórias</b> distintas do financiamento eleitoral:"
    )
)
conteudo.append(
    p(
        "<b>(i) 2012 — era da PJ.</b> Doação de pessoa jurídica ainda era "
        "permitida. Construtoras, bancos e empresas de serviços dominavam "
        "a lista de doadores em SP. Setores mais ativos (em valor doado a "
        "vereadores): construção de edifícios (R$ 3,79 mi), incorporação "
        "imobiliária (R$ 1,96 mi), obras de engenharia civil (R$ 1,96 mi), "
        "bancos múltiplos (R$ 938 mil), construção de rodovias (R$ 734 mil). "
        "É a fotografia clássica do financiamento empresarial denunciado "
        "na literatura (Mancuso &amp; Speck, 2015)."
    )
)
conteudo.append(
    p(
        "<b>(ii) 2016 — era transicional.</b> Reforma de 2015 proibiu "
        "doação PJ. O FEFC (Fundo Especial de Financiamento de Campanha) "
        "ainda não havia sido criado (surge só em 2018). O resultado foi "
        "uma eleição anômala onde <b>pessoa física passou a dominar (41% "
        "da receita)</b> e recursos próprios saltaram para 22%. Muitos "
        "candidatos simplesmente <b>não tiveram dinheiro</b>: a receita "
        "total de vereador em SP em 2016 foi de R$ 43,1 milhões — menos "
        "da metade de 2012 e um quinto de 2024. Esse foi o único "
        "momento em que a mobilização direta do eleitor-doador se "
        "tornou estratégia central de financiamento."
    )
)
conteudo.append(
    p(
        "<b>(iii) 2020/2024 — era do FEFC consolidado.</b> O Fundo "
        "Especial foi criado em 2017 e cresceu a cada ciclo. Em 2020, "
        "representava 65% do financiamento dos vereadores em SP. Em "
        "2024, chegou a <b>86,7%</b>. A receita total quadruplicou em "
        "relação a 2016 (R$ 209,4 milhões), mas a participação direta "
        "do eleitor-doador (PF + crowdfunding) caiu para apenas "
        "<b>9,5%</b> — menor do que em 2020 (25,8%) e muito menor do "
        "que em 2016 (41%)."
    )
)
conteudo.extend(
    [
        Image(
            "outputs/grafico_trajetoria_financiamento.png",
            width=16 * cm,
            height=10 * cm,
            kind="proportional",
        ),
        Paragraph(
            "Figura 1. Trajetória das fontes de financiamento dos "
            "vereadores de SP em quatro ciclos municipais (2012–2024). "
            "Destaque: queda progressiva da participação de pessoa física "
            "após 2016, compensada pelo aumento do FEFC via partido.",
            ParagraphStyle(
                "leg", parent=styles["Italic"], fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#555"), spaceAfter=10,
            ),
        ),
    ]
)

dados_trajetoria = [
    [_cb("Ano"), _cb("Total R$ mi"), _cb("Partido %"), _cb("PF %"),
     _cb("PJ %"), _cb("Próprio %"), _cb("FinColet %"), _cb("Era")],
    [_c("2012"), _cc("93,1"), _cc("41,7"), _cc("0,0"), _cc("<b>23,8</b>"),
     _cc("8,0"), _cc("0,0"), _c("Era PJ")],
    [_c("2016"), _cc("43,1"), _cc("28,0"), _cc("<b>41,0</b>"), _cc("0,0"),
     _cc("21,7"), _cc("0,0"), _c("Transição")],
    [_c("2020"), _cc("84,0"), _cc("65,0"), _cc("23,7"), _cc("0,0"),
     _cc("8,1"), _cc("2,1"), _c("FEFC inicial")],
    [_c("2024"), _cc("<b>209,4</b>"), _cc("<b>86,7</b>"), _cc("9,1"), _cc("0,0"),
     _cc("2,2"), _cc("0,4"), _c("FEFC consolidado")],
]
conteudo.append(
    tabela_estilizada(
        dados_trajetoria,
        [1.5*cm, 2*cm, 2*cm, 1.5*cm, 1.5*cm, 1.8*cm, 2*cm, 2.7*cm],
    )
)
conteudo.append(Spacer(1, 0.3 * cm))

conteudo.append(h2("2.1 A trajetória partidária em Pinheiros e Indianópolis"))
conteudo.append(
    p(
        "A análise de votos por partido nas zonas-chave do projeto ao "
        "longo dos 4 ciclos revela um padrão notável: <b>Pinheiros "
        "(Z251) e Indianópolis (Z258) começam no mesmo ponto em 2012 "
        "(PSDB com ~48% do voto) e terminam em posições opostas em "
        "2024</b>. A divergência interna ao próprio \"bairro rico\" "
        "é possivelmente o achado mais relevante para a Hipótese 1 "
        "do projeto."
    )
)

dados_pin_ind = [
    [_cb("Ano"), _cb("Pinheiros (Z251) — top partidos"), _cb("Indianópolis (Z258) — top partidos")],
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
conteudo.append(tabela_estilizada(dados_pin_ind, [1.5*cm, 7*cm, 7*cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(
    p(
        "Em <b>Pinheiros</b>, o voto tucano migrou paulatinamente para "
        "PSOL (que vira o partido #1 já em 2020) e o campo de esquerda "
        "somado (PSOL + PT + PSB + Rede) chega a 69% do voto principal "
        "em 2024. O Novo aparece como herdeiro parcial do PSDB, mas em "
        "minoria. Em <b>Indianópolis</b>, o mesmo voto tucano fragmentou-"
        "se à direita: PL, União, PP e MDB (partidos que em 2012 tinham "
        "participação marginal ou inexistiam) somam 82% do voto "
        "principal em 2024, enquanto a esquerda se reduz ao PSOL (18%) "
        "sem PT nem PSB expressivos."
    )
)
conteudo.append(
    p(
        "A <b>mesma origem eleitoral</b> (voto PSDB de classe alta "
        "paulistana em 2012) gerou dois destinos opostos em 12 anos. "
        "A variável diferenciadora não parece ser renda ou escolaridade "
        "(ambos Pinheiros e Indianópolis estão entre os bairros mais "
        "ricos e escolarizados da cidade) — o que sugere, como a análise "
        "de redutos institucionais discutiu na seção anterior do "
        "relatório principal, que o fator explicativo é <b>ambiente "
        "institucional educativo-cultural</b>: Pinheiros tem USP, PUC, "
        "Goethe-Institut, colégios progressistas (Vera Cruz, Equipe, "
        "Lumiar, Oswald de Andrade); Indianópolis tem perfil mais "
        "residencial-condominial, sem densidade equivalente de "
        "instituições culturais progressistas."
    )
)

conteudo.append(PageBreak())
conteudo.append(h1("3. Panorama detalhado do financiamento em 2024"))
conteudo.append(
    p(
        "A receita total declarada pelos 1.003 candidatos a vereador em "
        "São Paulo em 2024 soma <b>R$ 209,4 milhões</b>. A distribuição "
        "por origem é extremamente concentrada em recursos públicos "
        "distribuídos via partidos:"
    )
)
dados_panorama = [
    [_cb("Origem dos recursos"), _cb("R$ milhões"), _cb("% total"), _cb("Candidatos")],
    [_c("Recursos de partido político (FEFC + Fundo Partidário)"), _cc("181,4"), _cc("86,6%"), _cc("5.076 lançamentos")],
    [_c("Recursos de pessoas físicas"), _cc("19,0"), _cc("9,1%"), _cc("3.517")],
    [_c("Recursos próprios (autofinanciamento)"), _cc("4,6"), _cc("2,2%"), _cc("495")],
    [_c("Recursos de outros candidatos"), _cc("3,6"), _cc("1,7%"), _cc("279")],
    [_c("Financiamento coletivo (crowdfunding)"), _cc("0,8"), _cc("0,4%"), _cc("253")],
    [_c("Outras origens"), _cc("0,04"), _cc("0,02%"), _cc("—")],
]
conteudo.append(
    tabela_estilizada(dados_panorama, [7.5 * cm, 2.5 * cm, 2 * cm, 3.5 * cm])
)
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(
    p(
        "A característica mais marcante do sistema é a <b>dependência "
        "quase total do FEFC</b> — 86,6% dos recursos recebidos pelos "
        "candidatos vêm dos partidos como repasse do Fundo Especial de "
        "Financiamento de Campanha. A participação direta do eleitor "
        "como doador (pessoa física + financiamento coletivo) soma "
        "apenas 9,5% do total. Esta é a <b>estrutura material do voto "
        "proporcional em SP em 2024</b>: o eleitor escolhe o candidato, "
        "mas não o financia diretamente — isso é feito pelo partido "
        "através do dinheiro público."
    )
)

conteudo.append(h1("4. Recorte: candidatos com voto concentrado nas zonas-alvo (2024)"))
conteudo.append(
    p(
        "Para cada zona, tomamos os 6 candidatos a vereador com mais "
        "votos absolutos naquela zona (independentemente do resultado "
        "final — eleitos ou não). A tabela a seguir apresenta os três "
        "principais de cada zona do corredor das universidades, com a "
        "composição percentual das suas receitas:"
    )
)

conteudo.append(h2("4.1 Zonas ricas progressistas"))
dados_prog = [
    [_cb("Zona"), _cb("Candidato / Partido"), _cb("Votos"), _cb("Receita"), _cb("PF"), _cb("Partido"), _cb("FinColet")],
    [_c("Z1 Bela Vista"), _c("Amanda Paschoal (PSOL)"), _cc("2.348"), _cc("R$ 605k"), _cc("6%"), _cc("92%"), _cc("2%")],
    [_c(""), _c("Luana Alves (PSOL)"), _cc("1.675"), _cc("R$ 602k"), _cc("6%"), _cc("77%"), _cc("8%")],
    [_c(""), _c("Nabil Bonduki (PT)"), _cc("1.308"), _cc("R$ 1.250k"), _cc("<b>25%</b>"), _cc("71%"), _cc("2%")],
    [_c("Z2 Perdizes"), _c("Cristina Monteiro (NOVO)"), _cc("2.971"), _cc("R$ 1.358k"), _cc("16%"), _cc("82%"), _cc("1%")],
    [_c(""), _c("Nabil Bonduki (PT)"), _cc("2.229"), _cc("R$ 1.250k"), _cc("25%"), _cc("71%"), _cc("2%")],
    [_c(""), _c("Marina Bragante (REDE)"), _cc("1.790"), _cc("R$ 1.332k"), _cc("<b>28%</b>"), _cc("67%"), _cc("4%")],
    [_c("Z251 Pinheiros"), _c("Marina Bragante (REDE)"), _cc("2.912"), _cc("R$ 1.332k"), _cc("28%"), _cc("67%"), _cc("4%")],
    [_c(""), _c("Cristina Monteiro (NOVO)"), _cc("2.357"), _cc("R$ 1.358k"), _cc("16%"), _cc("82%"), _cc("1%")],
    [_c(""), _c("Nabil Bonduki (PT)"), _cc("2.057"), _cc("R$ 1.250k"), _cc("25%"), _cc("71%"), _cc("2%")],
    [_c(""), _c("Luana Alves (PSOL)"), _cc("1.784"), _cc("R$ 602k"), _cc("6%"), _cc("77%"), _cc("<b>8%</b>")],
]
conteudo.append(
    tabela_estilizada(
        dados_prog, [2.5 * cm, 5.2 * cm, 1.7 * cm, 2 * cm, 1.2 * cm, 1.6 * cm, 1.5 * cm]
    )
)
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(
    p(
        "Nas zonas ricas progressistas, três candidatos aparecem "
        "repetidamente no topo: <b>Nabil Bonduki (PT)</b>, com 25% de "
        "pessoa física, <b>Marina Bragante (REDE)</b>, com 28% PF + 4% "
        "crowdfunding, e <b>Luana Alves (PSOL)</b>, com 8% de "
        "financiamento coletivo — a maior taxa de crowdfunding entre "
        "candidatos com mais de mil votos no corredor. Cristina Monteiro "
        "(NOVO), única candidata de direita com voto forte nessas zonas, "
        "também tem 16% de PF — mais do que o dobro da média de "
        "candidatos de direita em outras zonas. <b>A infraestrutura de "
        "doador individual existe nessas zonas e é mobilizada por "
        "candidatos de ambos os campos ideológicos</b>, mas é mais "
        "intensa nos candidatos de esquerda, especialmente via "
        "financiamento coletivo."
    )
)

conteudo.append(h2("4.2 Zonas ricas conservadoras"))
dados_cons = [
    [_cb("Zona"), _cb("Candidato / Partido"), _cb("Votos"), _cb("Receita"), _cb("PF"), _cb("Partido"), _cb("FinColet")],
    [_c("Z5 Jd Paulista"), _c("Cristina Monteiro (NOVO)"), _cc("4.032"), _cc("R$ 1.358k"), _cc("16%"), _cc("82%"), _cc("1%")],
    [_c(""), _c("Marina Bragante (REDE)"), _cc("1.873"), _cc("R$ 1.332k"), _cc("28%"), _cc("67%"), _cc("4%")],
    [_c(""), _c("Janaína Paschoal (PP)"), _cc("1.363"), _cc("R$ 362k"), _cc("<b>0%</b>"), _cc("<b>100%</b>"), _cc("0%")],
    [_c(""), _c("Zoe Martinez (PL)"), _cc("1.086"), _cc("R$ 959k"), _cc("1%"), _cc("99%"), _cc("0%")],
    [_c("Z258 Indianópolis"), _c("Cristina Monteiro (NOVO)"), _cc("2.708"), _cc("R$ 1.358k"), _cc("16%"), _cc("82%"), _cc("1%")],
    [_c(""), _c("Janaína Paschoal (PP)"), _cc("1.758"), _cc("R$ 362k"), _cc("<b>0%</b>"), _cc("<b>100%</b>"), _cc("0%")],
    [_c(""), _c("Lucas Pavanato (PL)"), _cc("1.741"), _cc("R$ 1.078k"), _cc("7%"), _cc("93%"), _cc("0%")],
    [_c(""), _c("Zoe Martinez (PL)"), _cc("1.738"), _cc("R$ 959k"), _cc("1%"), _cc("99%"), _cc("0%")],
    [_c(""), _c("Murillo Lima (PP)"), _cc("1.346"), _cc("R$ 2.780k"), _cc("2%"), _cc("96%"), _cc("0%")],
]
conteudo.append(
    tabela_estilizada(
        dados_cons, [2.5 * cm, 5.2 * cm, 1.7 * cm, 2 * cm, 1.2 * cm, 1.6 * cm, 1.5 * cm]
    )
)
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(
    p(
        "O contraste com as zonas progressistas é visível no grupo de "
        "candidatos <b>PL + PP</b>: Janaína Paschoal (100% partido), "
        "Zoe Martinez (99%), Lucas Pavanato (93%) e Murillo Lima (96%) "
        "são <b>quase inteiramente dependentes do FEFC</b>. Pessoa física "
        "é 0–7%, financiamento coletivo é zero. Essa é a assinatura "
        "material da recomposição da direita nas zonas ricas: os "
        "candidatos do PL e PP que ocuparam o espaço do antigo PSDB "
        "<b>não herdaram a infraestrutura de doadores individuais</b> — "
        "chegam aos mesmos bairros levantados apenas pelo dinheiro "
        "público partidário."
    )
)
conteudo.append(
    p(
        "Cristina Monteiro (NOVO) e, em menor grau, Marina Bragante "
        "(REDE) são a exceção: captam PF em nível parecido ao dos "
        "candidatos de esquerda das mesmas zonas. Os dois partidos "
        "compartilham uma característica: <b>ambos têm base urbana "
        "educada e fazem captação digital ativa</b>, ainda que em "
        "direções ideológicas opostas. Isso sugere que a variável "
        "explicativa para a diferença de arrecadação via PF não é "
        "exclusivamente ideologia — é também <b>modelo partidário</b> "
        "(partidos com base urbana educada vs partidos com estrutura "
        "centralizada dependente de repasses)."
    )
)

conteudo.append(PageBreak())
conteudo.append(h1("5. Comparação com zonas de controle"))
conteudo.append(
    p(
        "Para colocar os achados em contexto, comparamos o perfil de "
        "financiamento em quatro zonas que servem como grupos de "
        "controle: duas periferias conservadoras (Vila Maria, Vila "
        "Sabrina) e duas periferias petistas (Perus, Cidade Tiradentes)."
    )
)

conteudo.append(h2("5.1 Perfil médio por grupo de zonas"))
dados_grupos = [
    [_cb("Grupo"), _cb("Zonas"), _cb("PF %"), _cb("Partido %"), _cb("FinColet %"), _cb("Próprio %")],
    [_c("Ricas progressistas"), _c("Bela Vista, Perdizes, Pinheiros"), _cc("13,6"), _cc("81,5"), _cc("<b>2,72</b>"), _cc("1,5")],
    [_c("Ricas conservadoras"), _c("Jd Paulista, Indianópolis"), _cc("10,9"), _cc("87,2"), _cc("1,19"), _cc("0,5")],
    [_c("Outras ricas"), _c("Santa Ifigênia, Vila Mariana, Butantã"), _cc("14,2"), _cc("81,4"), _cc("1,84"), _cc("2,0")],
    [_c("Periferia direita"), _c("Vila Maria, Vila Sabrina"), _cc("13,9"), _cc("85,0"), _cc("<b>0,00</b>"), _cc("1,0")],
    [_c("Periferia esquerda"), _c("Perus, Cidade Tiradentes"), _cc("8,0"), _cc("83,5"), _cc("0,26"), _cc("<b>6,3</b>")],
]
conteudo.append(
    tabela_estilizada(
        dados_grupos, [3.5 * cm, 5 * cm, 1.5 * cm, 2 * cm, 2 * cm, 1.8 * cm]
    )
)
conteudo.append(Spacer(1, 0.3 * cm))

conteudo.append(h2("5.2 Três padrões territoriais distintos"))
conteudo.append(
    p(
        "A comparação entre grupos revela três padrões materiais de "
        "financiamento de campanha claramente distinguíveis:"
    )
)
conteudo.append(
    p(
        "<b>(a) Financiamento coletivo (crowdfunding) é fenômeno quase "
        "exclusivo das zonas ricas progressistas</b>. 2,72% da receita "
        "média nessas zonas vem de financiamento coletivo, contra 1,19% "
        "nas ricas conservadoras e <b>zero</b> na periferia direita. "
        "Essa é a <b>assinatura mais limpa</b> da diferença entre campos "
        "ideológicos, e reflete a capacidade diferencial de mobilização "
        "digital de doadores individuais."
    )
)
conteudo.append(
    p(
        "<b>(b) Pessoa física existe em todas as zonas ricas, mas é "
        "reduzida na periferia esquerda</b>. A taxa média de 8% na "
        "periferia esquerda (Perus, Cidade Tiradentes) é a mais baixa "
        "de todos os grupos — inclusive menor que na periferia de "
        "direita (13,9%). Isso é relevante para o debate sobre "
        "\"esquerda caviar\": o voto petista periférico não é sustentado "
        "por doador individual local; é sustentado quase integralmente "
        "pelo repasse partidário (FEFC)."
    )
)
conteudo.append(
    p(
        "<b>(c) Autofinanciamento (recursos próprios) é notável na "
        "periferia esquerda</b>, com média de 6,3% — bem acima dos "
        "outros grupos. Isso é puxado por um caso extremo (Lucas Sorrillo, "
        "MDB em Cidade Tiradentes, 24% recursos próprios) que deve ser "
        "interpretado como padrão <b>clientelista-empresarial local</b> "
        "— dono de negócio com capital próprio que se lança candidato. "
        "Esse padrão não aparece nos outros grupos."
    )
)

conteudo.append(h1("6. Leitura substantiva para o projeto"))
conteudo.append(
    p(
        "Os achados permitem reforçar e qualificar as Hipóteses 3 e 4 "
        "do projeto, adicionando uma <b>dimensão material</b> ao "
        "argumento ideológico-cultural desenvolvido no relatório "
        "principal:"
    )
)
conteudo.append(
    p(
        "<b>Sobre H3</b> (centro-direita foi atraída pela direita/"
        "extrema-direita): a análise eleitoral anterior mostrou que o "
        "PSDB foi substituído por MDB, PRTB e Novo nas zonas ricas. A "
        "análise de financiamento mostra que essa substituição envolveu "
        "<b>mudança de modelo de captação</b>: os candidatos do PL e PP "
        "que ocupam hoje o espaço centro-direita/direita nas zonas "
        "ricas dependem quase integralmente de repasse partidário, "
        "enquanto o PSDB historicamente captava mais por pessoa física "
        "local. A exceção é o Novo, que mantém um modelo misto "
        "(captação digital + recursos partidários), e em 2024 foi "
        "provavelmente o maior herdeiro do antigo eleitor-doador "
        "tucano — hipótese testável com dados de 2012–2018, quando "
        "esses dois partidos coexistiam."
    )
)
conteudo.append(
    p(
        "<b>Sobre H4</b> (o voto de esquerda nos bairros ricos aponta "
        "para variáveis independentes de renda/escolaridade): a "
        "análise eleitoral mostrou que a esquerda nos bairros ricos "
        "conquista 57% das seções em Pinheiros, 40% em Bela Vista, "
        "35% em Perdizes. A análise de financiamento mostra que essa "
        "força eleitoral é sustentada por uma <b>infraestrutura "
        "material específica</b>: captação ativa de pessoa física e "
        "crowdfunding em níveis que só existem nessas zonas. O "
        "contraste com a periferia petista é revelador — mesmo sendo "
        "historicamente eleitora do PT, a periferia não mantém "
        "infraestrutura de doação pessoa física para candidatos. "
        "<b>A esquerda paulistana em 2024 depende do eleitor-doador "
        "dos bairros ricos</b> para além do FEFC, e a direita das "
        "mesmas zonas também consegue ativar esse recurso apenas "
        "pontualmente (NOVO)."
    )
)
conteudo.append(
    p(
        "Esse achado adiciona peso à interpretação de que a "
        "clivagem ideológica nos bairros ricos de SP não é "
        "epifenômeno cultural — ela tem <b>contrapartida material e "
        "organizacional</b>. A leitura de Rocha (2018) sobre a nova "
        "direita como fenômeno digital ganha um contraste empírico: "
        "a esquerda dos bairros ricos é, ela também, um fenômeno "
        "digital/mobilizacional, com capacidade de captação direta "
        "que não tem paralelo na direita tradicional (PL, PP) nem na "
        "periferia popular."
    )
)

conteudo.append(h1("7. Limitações"))
conteudo.append(
    p(
        "<b>Zonas ricas nas eleições pré-2018:</b> a análise temporal da "
        "seção 2 cobre a cidade de São Paulo inteira, mas a comparação "
        "entre candidatos específicos das zonas-alvo (seção 4) cobre só "
        "2024. Estender o cruzamento zona × financiamento para 2012, "
        "2016 e 2020 permitirá testar se o PSDB tucano em Pinheiros "
        "tinha perfil de PF mais alto do que os candidatos PL/PP que "
        "ocupam essa posição em 2024 — a principal hipótese causal "
        "deste relatório, ainda não testada ao nível do candidato."
    )
)
conteudo.append(
    p(
        "<b>Unidade de análise:</b> tratamos candidatos individuais como "
        "unidade, mas o partido também é um ator econômico relevante — "
        "o FEFC vai para o diretório e o diretório decide como repassar. "
        "A análise de orgãos partidários (dataset "
        "<i>prestacao_de_contas_eleitorais_orgaos_partidarios_2024</i>, "
        "também disponível no TSE) pode revelar o lado da oferta da "
        "estrutura de financiamento."
    )
)
conteudo.append(
    p(
        "<b>Causalidade:</b> os dados são observacionais — não é "
        "possível afirmar causalmente que a mudança no perfil de "
        "doadores <i>causou</i> o realinhamento ou que o "
        "realinhamento <i>causou</i> a mudança no perfil. É possível "
        "apenas documentar a <b>associação estrutural</b>. Métodos de "
        "identificação causal (diff-in-diff usando a reforma de 2015, "
        "como sugerido na proposta original) podem ser aplicados em "
        "extensão futura."
    )
)

conteudo.append(h1("8. Reprodutibilidade"))
conteudo.append(
    p(
        "Os dados vêm do arquivo <i>receitas_candidatos_2024_SP.csv</i> "
        "(parte do zip <i>prestacao_de_contas_eleitorais_candidatos_"
        "2024.zip</i> do TSE, CDN de dados abertos, ~1,28 GB). O "
        "processamento resulta no parquet "
        "<i>data/processed/receitas_vereador_sp_2024.parquet</i> "
        "(9.746 linhas, R$ 209 milhões). O cruzamento com votos usa "
        "<i>votacao_secao_2024_SP.parquet</i>. O script principal é "
        "<i>financiamento_zonas_ricas.py</i>, que gera os CSVs "
        "<i>outputs/financiamento_zonas_ricas.csv</i> e "
        "<i>outputs/financiamento_grupos.csv</i>."
    )
)
conteudo.append(
    p(
        "Código público: "
        "<font color='#1a4dd0'><u>github.com/miaguchi/democracia-em-dados</u></font>"
    )
)

SAIDA.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(
    str(SAIDA),
    pagesize=A4,
    leftMargin=2.5 * cm,
    rightMargin=2.5 * cm,
    topMargin=2 * cm,
    bottomMargin=2 * cm,
    title="Financiamento eleitoral - zonas ricas SP 2024",
    author="Thiago Suzuki Conti Miaguchi",
)
doc.build(conteudo)
print(f"PDF gerado: {SAIDA}")
print(f"Tamanho: {SAIDA.stat().st_size / 1024:.1f} KB")
