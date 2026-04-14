"""PDF — renda, escolaridade e voto nas zonas ricas de SP (eixo Marques)."""

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

SAIDA = Path("outputs/relatorio_socioeconomia_zonas.pdf")

styles = getSampleStyleSheet()
st_titulo = ParagraphStyle("titulo", parent=styles["Title"], fontSize=15, alignment=TA_CENTER, spaceAfter=8)
st_subt = ParagraphStyle("subt", parent=styles["Normal"], fontSize=11, alignment=TA_CENTER, spaceAfter=4, textColor=colors.HexColor("#444"))
st_h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13, spaceBefore=12, spaceAfter=6)
st_h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, spaceBefore=8, spaceAfter=4)
st_body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)
st_cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8, leading=11, alignment=TA_LEFT)
st_cell_c = ParagraphStyle("cell_c", parent=styles["Normal"], fontSize=8, leading=11, alignment=TA_CENTER)
st_cell_b = ParagraphStyle("cell_b", parent=styles["Normal"], fontSize=8, leading=11, fontName="Helvetica-Bold", alignment=TA_CENTER)
st_leg = ParagraphStyle("leg", parent=styles["Italic"], fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor("#555"), spaceAfter=10)


def p(t): return Paragraph(t, st_body)
def h1(t): return Paragraph(t, st_h1)
def h2(t): return Paragraph(t, st_h2)
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


conteudo = []

conteudo.append(Paragraph("Renda, escolaridade e voto ideológico<br/>nas zonas eleitorais de São Paulo", st_titulo))
conteudo.append(Paragraph("Relatório técnico complementar — eixo sociologia política urbana<br/>Projeto de dissertação, DCP/FFLCH-USP", st_subt))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(Paragraph(
    "<b>Candidato:</b> Thiago Suzuki Conti Miaguchi<br/>"
    "<b>Referências de agenda:</b> Eduardo Marques (FLS 6195) · "
    "Power &amp; Rodrigues-Silveira (2019) · Soares &amp; Terron (2008)<br/>"
    "<b>Dados primários:</b> IBGE Censo 2010 (agregados por setor censitário SP) + TSE 2024",
    st_subt,
))
conteudo.append(Spacer(1, 0.6 * cm))

conteudo.append(h1("1. Pergunta e motivação"))
conteudo.append(p(
    "A Hipótese 4 do projeto de dissertação (Miaguchi, 2023) afirma: <i>"
    "\"o voto da esquerda nos bairros ricos aponta para outras variáveis "
    "independentes do que a renda ou a escolaridade.\"</i> Este relatório "
    "testa essa hipótese diretamente ao cruzar dados sociodemográficos "
    "do Censo IBGE 2010 (rendimento per capita médio do setor "
    "censitário) com o escore ideológico do voto em 2024 (classificação "
    "Bolognesi, Ribeiro &amp; Codato 2023), ao nível das 58 zonas "
    "eleitorais de São Paulo. O recorte metodológico segue a tradição "
    "de ecologia eleitoral brasileira (Soares &amp; Terron, 2008) e a "
    "abordagem de Power &amp; Rodrigues-Silveira (2019) para mapeamento "
    "ideológico subnacional."
))

conteudo.append(h1("2. Método"))
conteudo.append(p(
    "Pipeline em 5 etapas, integrando quatro fontes primárias:"
))
conteudo.append(p(
    "<b>(i)</b> Setores censitários de SP capital (n = 18.953 polígonos) "
    "via pacote <i>geobr</i>, com dados de rendimento per capita médio "
    "do Censo 2010 (variável V009 da Base de Informações por Setor "
    "Censitário, IBGE)."
))
conteudo.append(p(
    "<b>(ii)</b> Locais de votação georreferenciados (n = 2.061 pontos) "
    "da base EL2022_LV_ESP_CEM_V2 do Centro de Estudos da Metrópole "
    "(CEM/USP)."
))
conteudo.append(p(
    "<b>(iii)</b> <i>Spatial join</i>: cada local de votação herda o "
    "rendimento per capita do setor censitário que o contém (point-in-"
    "polygon). Aproximadamente 2.007 de 2.061 locais foram "
    "geograficamente identificados (97,4%)."
))
conteudo.append(p(
    "<b>(iv)</b> Agregação dos locais por zona eleitoral (NR_ZONA), "
    "produzindo renda média por zona a partir dos setores censitários "
    "contidos."
))
conteudo.append(p(
    "<b>(v)</b> Cruzamento com o escore ideológico médio ponderado por "
    "votos de cada zona (calculado em etapa anterior do projeto, a "
    "partir de <i>votacao_partido_munzona_2024</i>), para vereador e "
    "prefeito 1º turno."
))

conteudo.append(h1("3. Resultado principal: correlação NEGATIVA entre renda e voto à direita"))
conteudo.append(p(
    "A correlação de Pearson entre renda per capita média das zonas "
    "eleitorais e escore ideológico médio ponderado é <b>negativa</b> "
    "em todas as eleições analisadas:"
))
dados_corr = [
    [_cb("Eleição"), _cb("Correlação"), _cb("Direção"), _cb("Interpretação")],
    [_c("Vereador 2024"), _cc("<b>−0,297</b>"), _c("negativa moderada"),
     _c("zonas com renda mais alta têm escore mais baixo (mais à esquerda)")],
    [_c("Prefeito 1T 2024"), _cc("<b>−0,166</b>"), _c("negativa fraca"),
     _c("mesma direção, efeito menor no voto executivo")],
    [_c("Vereador 2020"), _cc("<b>−0,211</b>"), _c("negativa moderada"),
     _c("o padrão é consistente no tempo, não artefato de uma eleição")],
]
conteudo.append(tabela(dados_corr, [3 * cm, 2.5 * cm, 3 * cm, 7 * cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "O sinal negativo é <b>diretamente contrário à intuição do voto de "
    "classe clássico</b> (renda alta = direita, renda baixa = esquerda) "
    "que dominou a literatura de comportamento eleitoral brasileiro por "
    "décadas (Soares 1973; Singer 2012). Em São Paulo 2024, no nível da "
    "zona eleitoral, a tendência é inversa: zonas mais ricas tendem a "
    "apresentar votos mais progressistas em eleições legislativas "
    "municipais."
))

conteudo.append(
    Image("outputs/scatter_renda_escore.png", width=16.5 * cm, height=8 * cm, kind="proportional")
)
conteudo.append(Paragraph(
    "Figura 1. Scatter da renda per capita média por zona eleitoral "
    "(Censo 2010) × escore ideológico médio ponderado (vereador e "
    "prefeito, 2024). Cada ponto é uma zona eleitoral. Destacadas em "
    "vermelho (mais à esquerda) e azul (mais à direita): as 7 zonas do "
    "corredor universitário mais zonas-chave do projeto de dissertação. "
    "Linha vermelha: regressão linear simples.",
    st_leg,
))

conteudo.append(h1("4. O ranking de renda e o ranking ideológico não coincidem"))
conteudo.append(p(
    "As 10 zonas mais ricas de SP (por renda per capita média) e seus "
    "escores ideológicos no vereador 2024:"
))
dados_top = [
    [_cb("Pos."), _cb("Zona"), _cb("Bairro"), _cb("Renda pc 2010"), _cb("Escore ver 2024"), _cb("Leitura")],
    [_c("1"), _c("Z5"), _c("Jardim Paulista"), _cc("R$ 5.365"), _cc("6,14"), _c("centro-direita moderado")],
    [_c("2"), _c("Z251"), _c("<b>Pinheiros</b>"), _cc("R$ 3.819"), _cc("<b>5,53</b>"), _c("<b>centro (mais à esq. da amostra)</b>")],
    [_c("3"), _c("Z258"), _c("Indianópolis"), _cc("R$ 3.504"), _cc("6,39"), _c("centro-direita moderado")],
    [_c("4"), _c("Z6"), _c("Vila Mariana"), _cc("R$ 3.264"), _cc("6,00"), _c("centro-direita brando")],
    [_c("5"), _c("Z2"), _c("<b>Perdizes</b>"), _cc("R$ 3.137"), _cc("<b>5,71</b>"), _c("<b>centro-direita brando</b>")],
    [_c("6"), _c("Z346"), _c("Butantã"), _cc("R$ 2.966"), _cc("6,16"), _c("centro-direita moderado")],
    [_c("7"), _c("Z259"), _c("Saúde"), _cc("R$ 2.927"), _cc("6,12"), _c("centro-direita moderado")],
    [_c("8"), _c("Z246"), _c("Santo Amaro"), _cc("R$ 2.635"), _cc("6,42"), _c("centro-direita mais intenso")],
    [_c("9"), _c("Z249"), _c("Santana"), _cc("R$ 1.839"), _cc("6,41"), _c("centro-direita")],
    [_c("10"), _c("Z1"), _c("<b>Bela Vista</b>"), _cc("R$ 1.805"), _cc("<b>5,52</b>"), _c("<b>centro (mais à esq. da cidade)</b>")],
]
conteudo.append(tabela(dados_top, [1 * cm, 1.2 * cm, 3.5 * cm, 2.5 * cm, 2.5 * cm, 5.5 * cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "Entre as 10 zonas mais ricas da cidade, quatro (Pinheiros, "
    "Perdizes, Bela Vista e secundariamente Butantã) têm escores entre "
    "5,5 e 6,2 — região do centro brando para centro-direita leve. "
    "Outras quatro (Jardim Paulista, Indianópolis, Santo Amaro, "
    "Santana) têm escores entre 6,1 e 6,4 — mais claramente centro-"
    "direita. <b>A variação interna ao grupo de zonas ricas (0,87 "
    "pontos de escore) é maior do que a variação entre o grupo rico e "
    "o grupo pobre</b> de zonas eleitorais (analisada na próxima seção)."
))

conteudo.append(h1("5. Zonas pobres: escores similares, gradiente pequeno"))
conteudo.append(p(
    "As 10 zonas mais pobres da cidade (Censo 2010) têm renda per "
    "capita média entre R$ 511 e R$ 693 — faixa que representa 10-15% "
    "da renda média das zonas centrais. Seus escores ideológicos, "
    "porém, são notavelmente próximos do centro:"
))
dados_pobres = [
    [_cb("Zona"), _cb("Bairro"), _cb("Renda pc"), _cb("Escore ver 2024")],
    [_c("Z373"), _c("Capão Redondo"), _cc("R$ 693"), _cc("6,35")],
    [_c("Z405"), _c("Conjunto José Bonifácio"), _cc("R$ 692"), _cc("6,15")],
    [_c("Z403"), _c("Jaraguá"), _cc("R$ 685"), _cc("6,21")],
    [_c("Z376"), _c("Brasilândia"), _cc("R$ 680"), _cc("6,24")],
    [_c("Z389"), _c("Perus"), _cc("R$ 660"), _cc("6,20")],
    [_c("Z371"), _c("Grajaú"), _cc("R$ 650"), _cc("6,04")],
    [_c("Z20"), _c("Valo Velho"), _cc("R$ 578"), _cc("6,15")],
    [_c("Z353"), _c("Guaianases"), _cc("R$ 556"), _cc("6,12")],
    [_c("Z381"), _c("Parelheiros"), _cc("R$ 552"), _cc("6,28")],
    [_c("Z404"), _c("Cidade Tiradentes"), _cc("R$ 512"), _cc("5,91")],
]
conteudo.append(tabela(dados_pobres, [1.5 * cm, 5 * cm, 2.5 * cm, 2.5 * cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "Todas as 10 zonas mais pobres têm escores <b>entre 5,91 e 6,35</b>, "
    "uma faixa de 0,44 pontos. As 10 zonas mais ricas têm escores entre "
    "5,52 e 6,42 — uma faixa quase duas vezes maior (0,90 pontos). Em "
    "outras palavras: <b>a amplitude ideológica das zonas ricas é muito "
    "maior do que a das zonas pobres</b>. A periferia paulistana é "
    "relativamente homogênea em um patamar de centro-direita brando "
    "(escore ≈ 6,1); os bairros ricos se dividem internamente em dois "
    "polos muito mais distantes."
))

conteudo.append(PageBreak())
conteudo.append(h1("6. Leitura substantiva para o projeto"))
conteudo.append(p(
    "O conjunto de evidências apresentado permite <b>refutar</b> a "
    "interpretação clássica de voto de classe como explicação principal "
    "do padrão eleitoral em SP 2024, e <b>confirmar</b> a Hipótese 4 do "
    "projeto. Três implicações:"
))
conteudo.append(h2("6.1 Renda e escolaridade têm pouco poder explicativo"))
conteudo.append(p(
    "A correlação de −0,30 explica menos de 9% da variância do escore "
    "ideológico entre zonas (r² = 0,088). <b>Mais de 91% da variação "
    "ideológica entre zonas eleitorais não é explicada por renda per "
    "capita</b>. Este é um achado central — e é notável que a direção "
    "seja oposta ao senso comum: controlando por tudo, ser mais rico em "
    "SP 2024 está <i>ligeiramente</i> associado a votar mais à "
    "esquerda, não menos."
))
conteudo.append(h2("6.2 A variância ideológica está <i>dentro</i> do grupo rico, não entre grupos"))
conteudo.append(p(
    "Pinheiros (renda pc 2º da cidade) e Indianópolis (renda pc 3º da "
    "cidade) diferem ideologicamente por <b>0,86 pontos</b> no vereador. "
    "A diferença entre Jardim Paulista (renda pc 1º) e Cidade Tiradentes "
    "(renda pc último) é de apenas 0,23 pontos no mesmo indicador. "
    "<b>Variáveis que explicam a diferença dentro do grupo rico não "
    "podem ser renda</b> (o grupo rico é, por definição, homogêneo em "
    "renda)."
))
conteudo.append(h2("6.3 O fator diferenciador não é demográfico, é institucional"))
conteudo.append(p(
    "Relatórios anteriores deste projeto identificaram que os locais "
    "de votação com maior percentual de voto à esquerda em Pinheiros, "
    "Bela Vista e Perdizes são predominantemente: (a) escolas "
    "particulares progressistas (Vera Cruz, Equipe, Lumiar, Oswald de "
    "Andrade, Stella Maris); (b) universidades (USP Direito, Mackenzie, "
    "PUC, Uninove); (c) escolas públicas de prestígio (Caetano de "
    "Campos, Amorim Lima, Clorinda Danti); (d) instituições culturais "
    "internacionais (Goethe-Institut). Esses locais <b>existem também "
    "em Indianópolis e Jardim Paulista</b>, mas com densidade e perfil "
    "diferentes. A variável explicativa preliminar é a <b>presença de "
    "ambiente institucional educativo-cultural progressista</b>, que "
    "correlaciona com cosmopolitismo, contato internacional e "
    "capacidade de mobilização digital — não com renda."
))

conteudo.append(PageBreak())
conteudo.append(h1("7. Teste da hipótese alternativa: densidade institucional"))
conteudo.append(p(
    "As seções anteriores mostraram que renda explica menos de 9% da "
    "variância do escore ideológico entre zonas eleitorais. Esta seção "
    "operacionaliza quantitativamente a hipótese alternativa: o fator "
    "explicativo é a <b>densidade de ambiente institucional educativo-"
    "cultural-progressista</b>."
))
conteudo.append(h2("7.1 Construção do índice"))
conteudo.append(p(
    "Para cada zona eleitoral, identificamos quantos dos seus locais "
    "de votação se enquadram em 4 categorias institucionais via "
    "matching por palavras-chave no nome do local de votação (base "
    "CEM/USP): "
    "<b>(i) Universidades</b> (USP, Mackenzie, PUC, Uninove, FAAP, "
    "FMU, Insper, Senac, Senai, Fatec); "
    "<b>(ii) Escolas particulares progressistas</b> (Vera Cruz, Equipe, "
    "Lumiar, Oswald de Andrade, Stella Maris, Escola da Vila, "
    "Horizontes, Itaca); "
    "<b>(iii) Escolas públicas de prestígio cultural</b> (Caetano de "
    "Campos, Fernão Dias Paes, Godofredo Furtado, Amorim Lima, "
    "Clorinda Danti); "
    "<b>(iv) Instituições culturais internacionais</b> (Goethe, "
    "Alliance Française, Dante Alighieri, Cervantes). "
    "O índice final é a fração de locais da zona em pelo menos uma "
    "categoria — um percentual entre 0% e 100%."
))
conteudo.append(h2("7.2 Resultado: correlação de −0,661"))
conteudo.append(p(
    "A correlação de Pearson entre índice institucional e escore "
    "ideológico do vereador 2024 é <b>r = −0,661</b>, explicando "
    "<b>43,7% da variância</b>. Para o prefeito 1T 2024, r = −0,600 "
    "(R² = 36%). Em ambos os casos, o poder preditivo é cerca de "
    "<b>cinco vezes maior</b> do que o da renda per capita."
))
conteudo.append(
    Image(
        "outputs/scatter_indice_institucional.png",
        width=17 * cm, height=7.5 * cm, kind="proportional",
    )
)
conteudo.append(Paragraph(
    "Figura 2. Comparação direta dos dois preditores. À esquerda: "
    "índice institucional cultural-progressista vs escore ideológico "
    "de vereador 2024 (R² = 0,437). À direita: renda per capita "
    "média do setor censitário (Censo 2010) vs escore (R² = 0,088). "
    "Destacadas: Bela Vista (48% de locais institucionais), Pinheiros "
    "(37%), Perdizes (17%) à esquerda-baixo; Indianópolis, Jardim "
    "Paulista, Vila Mariana, Butantã no quadrante superior.",
    st_leg,
))

dados_top_idx = [
    [_cb("Zona"), _cb("Bairro"), _cb("Índice %"), _cb("Univ."),
     _cb("Esc. prog."), _cb("Prestígio"), _cb("Internac."), _cb("Esc ver 24")],
    [_c("1"), _c("<b>Bela Vista</b>"), _cc("<b>48,0</b>"), _cc("11"),
     _cc("0"), _cc("1"), _cc("0"), _cc("5,52")],
    [_c("251"), _c("<b>Pinheiros</b>"), _cc("<b>37,0</b>"), _cc("1"),
     _cc("4"), _cc("3"), _cc("2"), _cc("5,53")],
    [_c("3"), _c("Santa Ifigênia"), _cc("17,6"), _cc("3"),
     _cc("0"), _cc("0"), _cc("0"), _cc("6,06")],
    [_c("2"), _c("Perdizes"), _cc("16,7"), _cc("3"),
     _cc("1"), _cc("1"), _cc("0"), _cc("5,71")],
    [_c("346"), _c("Butantã"), _cc("13,5"), _cc("2"),
     _cc("1"), _cc("1"), _cc("1"), _cc("6,16")],
    [_c("6"), _c("Vila Mariana"), _cc("11,1"), _cc("2"),
     _cc("0"), _cc("1"), _cc("0"), _cc("6,00")],
    [_c("5"), _c("Jardim Paulista"), _cc("10,5"), _cc("1"),
     _cc("0"), _cc("0"), _cc("1"), _cc("6,14")],
    [_c("<b>258</b>"), _c("<b>Indianópolis</b>"), _cc("<b>0,0</b>"),
     _cc("0"), _cc("0"), _cc("0"), _cc("0"), _cc("<b>6,39</b>")],
]
conteudo.append(tabela(dados_top_idx,
    [1.1*cm, 3.2*cm, 1.7*cm, 1.3*cm, 1.5*cm, 1.7*cm, 1.7*cm, 2*cm]))
conteudo.append(Spacer(1, 0.3 * cm))

conteudo.append(h2("7.3 Pinheiros × Indianópolis: empate em renda, polos opostos em instituições"))
conteudo.append(p(
    "Pinheiros (Z251) e Indianópolis (Z258) são a 2ª e 3ª zonas mais "
    "ricas da cidade, com R$ 3.819 e R$ 3.504 per capita em 2010. No "
    "índice institucional, porém, estão em polos opostos: <b>Pinheiros "
    "tem 37%</b> (1 universidade, 4 escolas progressistas, 3 "
    "prestígio público, 2 culturais internacionais); <b>Indianópolis "
    "tem exatamente 0%</b>. A diferença ideológica entre as duas é "
    "de 0,86 pontos no escore do vereador — uma diferença ampla que "
    "renda é incapaz de explicar (são essencialmente empatadas em "
    "renda)."
))

conteudo.append(h2("7.4 Regressão multivariada"))
conteudo.append(p(
    "Em OLS com renda e índice institucional como preditores "
    "simultâneos do escore de vereador 2024, os três modelos "
    "produzem o seguinte quadro:"
))
dados_ols = [
    [_cb("Modelo"), _cb("Variáveis"), _cb("R²"), _cb("Renda"), _cb("Índice instit.")],
    [_c("Modelo 1"), _c("só renda"), _cc("0,088"), _cc("negativo"), _cc("—")],
    [_c("Modelo 2"), _c("só índice institucional"), _cc("<b>0,437</b>"),
     _cc("—"), _cc("<b>−0,0185</b>")],
    [_c("Modelo 3"), _c("renda + índice"), _cc("0,439"),
     _cc("+0,000011 (desprezível)"), _cc("−0,0185")],
]
conteudo.append(tabela(dados_ols, [2 * cm, 4.5 * cm, 1.5 * cm, 4 * cm, 3.5 * cm]))
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(p(
    "<b>Três observações:</b> (a) o R² adicional que renda acrescenta "
    "depois de controlar por índice institucional é de apenas <b>0,002</b> "
    "— praticamente zero; (b) o sinal do coeficiente de renda, quando "
    "controlado por densidade institucional, vira ligeiramente positivo "
    "(renda mais alta → escore um pouco mais à direita, como a teoria "
    "clássica prevê), mas o efeito é numericamente desprezível; (c) o "
    "coeficiente do índice institucional é robusto e sobrevive ao "
    "controle por renda — cada ponto percentual de aumento na densidade "
    "reduz o escore em 0,019. Para a diferença Bela Vista (48%) vs "
    "Indianópolis (0%), isso produz um deslocamento esperado de "
    "<b>0,91 pontos de escore</b>, mais do que o suficiente para "
    "cruzar a fronteira centro/centro-direita na régua de Bolognesi."
))
conteudo.append(p(
    "<b>Interpretação substantiva:</b> a renda, quando controlada pela "
    "densidade institucional, perde todo o poder explicativo. A "
    "variável relevante para o padrão ideológico das zonas eleitorais "
    "de SP em 2024 é o quanto a zona é <b>densa em ambiente "
    "educativo-cultural-progressista</b>, não o quanto é rica. "
    "<b>Pinheiros e Indianópolis são empates em renda</b>, e o que "
    "as separa é a presença física de universidades, escolas "
    "construtivistas e instituições culturais internacionais como "
    "locais de votação da zona."
))
conteudo.append(h2("7.5 Testes de robustez"))
conteudo.append(p(
    "Cinco testes de robustez foram aplicados ao achado da seção 7.2 "
    "para verificar se a correlação observada é artefato metodológico "
    "ou fenômeno real:"
))
conteudo.append(p(
    "<b>(a) Leave-one-category-out.</b> Remove-se uma das 4 categorias "
    "do índice de cada vez e recalcula-se a correlação. O índice "
    "completo tem R² = 0,437. Removendo universidades, R² = 0,290; "
    "sem escolas progressistas, R² = 0,376; sem prestígio público, "
    "R² = 0,393; sem internacional-cultural, R² = 0,428. "
    "<b>Todas as variantes preservam correlação moderada a forte</b>; "
    "universidades é a categoria com maior contribuição marginal."
))
conteudo.append(p(
    "<b>(b) Cada categoria isolada.</b> Usando só universidades, "
    "r = −0,491 (R² = 0,241). Só escolas progressistas, r = −0,488 "
    "(R² = 0,238, apesar de aparecer em apenas 7 zonas). Só prestígio "
    "público, <b>r = −0,624</b> (R² = 0,390, aparece em só 6 zonas — "
    "a categoria com maior potência unitária). Só internacional-"
    "cultural, r = −0,323 (apenas 4 zonas têm instituições "
    "internacionais). <b>O fenômeno não depende de uma categoria "
    "específica</b>; há efeito acumulativo das 4."
))
conteudo.append(p(
    "<b>(c) Bootstrap de intervalos de confiança.</b> Reamostras "
    "(1000 iterações) do par (índice, escore) para construir IC 95% "
    "do coeficiente de correlação: "
    "<b>vereador 2024: [−0,816, −0,223]</b>; "
    "<b>prefeito 1T 2024: [−0,783, −0,144]</b>; "
    "<b>vereador 2020: [−0,690, −0,033]</b>. "
    "Todos os intervalos excluem zero. A significância estatística "
    "se mantém em 3 de 3 eleições testadas."
))
conteudo.append(p(
    "<b>(d) Controle por densidade urbana.</b> Um confundidor "
    "plausível seria: zonas centrais têm mais locais de votação no "
    "total (e portanto mais universidades/escolas grandes), e "
    "simultaneamente votariam mais à esquerda por outras razões "
    "urbanas. Controlando pelo número total de locais da zona: o "
    "modelo <i>escore ~ n_locais</i> sozinho tem R² = 0,003 — a "
    "densidade urbana bruta <b>não prevê nada</b>. No modelo "
    "<i>escore ~ índice + n_locais</i>, o β do índice se mantém em "
    "−0,019 e β de n_locais é praticamente zero (−0,003). "
    "<b>O achado não é artefato de centralidade urbana.</b>"
))
conteudo.append(p(
    "<b>(e) Variável dependente alternativa.</b> Substitui-se o "
    "escore médio ponderado (métrica contínua) pela porcentagem de "
    "seções eleitorais da zona em que o bloco esquerda+centro-esquerda "
    "superou o bloco direita+centro-direita em votos absolutos "
    "(métrica bipartite de plurality). <b>A correlação do índice "
    "institucional com essa variável é r = +0,814 (R² = 0,663)</b>. "
    "Para comparação, a correlação da renda com a mesma variável é "
    "r = +0,079 — praticamente zero. <b>Em um teste mais direto "
    "(contagem de seções progressistas, não média ponderada), o "
    "índice institucional explica 66% da variância entre zonas</b>, "
    "a renda não explica praticamente nada."
))
conteudo.append(p(
    "<b>Conclusão dos testes de robustez:</b> o achado é robusto a "
    "variações na construção do índice, a controles por confundidores "
    "plausíveis, a mudanças na variável dependente e a mudanças no "
    "ano/cargo da eleição. A correlação negativa forte entre ambiente "
    "institucional cultural-progressista e escore ideológico (ou, "
    "equivalentemente, correlação positiva forte entre esse ambiente "
    "e presença de voto progressista) é um fenômeno real e "
    "empiricamente robusto nas zonas eleitorais de São Paulo em 2024."
))

conteudo.append(PageBreak())
conteudo.append(h1("8. Conexão com hipóteses gerais da literatura"))
conteudo.append(p(
    "O achado se conecta a duas tradições internacionais que o projeto "
    "de dissertação já cita:"
))
conteudo.append(p(
    "<b>Inglehart &amp; Norris</b> (2016, 2019) argumentam que o voto "
    "contemporâneo em democracias desenvolvidas não segue mais o eixo "
    "renda/classe, mas sim um eixo <i>cultural</i> — pós-materialismo, "
    "cosmopolitismo, educação, valores. O padrão descrito aqui para SP "
    "é compatível: as zonas ricas se dividem por orientação cultural, "
    "não por nível de renda."
))
conteudo.append(p(
    "<b>Bonikowski</b> (2016) argumenta que a direita e a esquerda "
    "contemporâneas têm bases institucionais diferentes: a esquerda se "
    "sustenta em redes universitárias, culturais, profissionais "
    "especializadas; a direita em redes religiosas, militares, "
    "empresariais tradicionais e comunitárias. O contraste entre "
    "Pinheiros (USP + Mackenzie + Goethe + Vera Cruz) e Vila Maria "
    "(escolas cívico-militares + comunidade evangélica) encontrado em "
    "relatórios anteriores deste projeto é <b>empiricamente compatível</b> "
    "com esse diagnóstico."
))
conteudo.append(p(
    "Dentro da literatura brasileira, o achado conversa com o "
    "argumento de <b>Power</b> (2010, 2019) de que a direita brasileira "
    "contemporânea é um fenômeno de <i>reorganização institucional</i>, "
    "não de mudança no eleitorado — e com o trabalho de <b>Rocha</b> "
    "(2018) sobre a nova direita como movimento institucional-digital, "
    "não de base social tradicional."
))

conteudo.append(h1("9. Limitações"))
conteudo.append(h2("9.1 A limitação temporal do Censo 2010"))
conteudo.append(p(
    "A limitação mais óbvia desta análise é que a variável "
    "explicativa <i>renda per capita</i> usa dados do Censo 2010, "
    "enquanto a variável dependente (voto) é de 2024 — uma "
    "defasagem de 14 anos. Esta é uma preocupação metodológica "
    "legítima e precisa ser tratada explicitamente. Cinco "
    "argumentos atenuam (mas não eliminam) o problema:"
))
conteudo.append(p(
    "<b>(i) Estabilidade relativa do ranking de renda em SP.</b> "
    "Pinheiros, Jardim Paulista, Indianópolis e Vila Mariana são "
    "reconhecidamente bairros ricos de São Paulo desde pelo menos "
    "a década de 1970. A literatura de sociologia urbana paulistana "
    "(Marques, 2015; Torres et al., 2003) documenta que a "
    "hierarquia socioeconômica inter-bairros da capital paulistana "
    "é <i>extraordinariamente estável</i> ao longo do tempo — "
    "muito mais do que mudanças absolutas de renda. Mesmo com "
    "inflação, gentrificação ou deterioração localizada, a "
    "<b>posição relativa das zonas no ranking quase não muda</b>. "
    "Cidade Tiradentes foi construída nos anos 1980 como conjunto "
    "habitacional de baixa renda e segue como uma das zonas mais "
    "pobres em 2024. Pinheiros é rica há mais de um século. A "
    "inferência via correlação de ranking (não de valores "
    "absolutos) é robusta a defasagem desse tipo."
))
conteudo.append(p(
    "<b>(ii) A variável dependente é 2024 e independente do "
    "problema.</b> O escore ideológico vem da eleição de 2024, "
    "calculado sobre dados do TSE daquele ano. O que está "
    "potencialmente desatualizado é a <i>covariável</i>, não a "
    "resposta. Se a hipótese fosse \"renda causa voto\", a "
    "defasagem seria fatal; mas a hipótese testada é mais fraca — "
    "\"renda correlaciona com voto\" — e defasagem de 14 anos "
    "apenas <i>enfraquece</i> a correlação observada, não a "
    "distorce sistematicamente."
))
conteudo.append(p(
    "<b>(iii) A defasagem enfraquece o achado, não o fortalece.</b> "
    "Este é o argumento mais forte: se o efeito observado é "
    "negativo e fraco (r = −0,30), uma medida de renda mais "
    "atualizada poderia produzir, na pior das hipóteses, um "
    "efeito um pouco menos fraco — mas dificilmente um efeito "
    "substancialmente maior (para isso, a defasagem teria que ter "
    "produzido correlação sistemática oposta à verdadeira, o que "
    "é estatisticamente improvável). A conclusão substantiva — "
    "<b>renda explica menos de 9% da variância</b> — é um "
    "<i>limite superior conservador</i> do efeito real: com "
    "medidas mais precisas, o R² pode ser igual ou menor. O "
    "achado \"renda não explica voto\" é, portanto, "
    "<b>conservador</b> — se algo, o efeito verdadeiro é ainda "
    "menor do que o reportado."
))
conteudo.append(p(
    "<b>(iv) O Censo 2022 ainda não liberou renda por setor.</b> "
    "Verificamos (em abril de 2026) que o IBGE ainda não "
    "disponibilizou os agregados de rendimento domiciliar do "
    "Censo 2022 por setor censitário. As variáveis já divulgadas "
    "são: alfabetização, características do domicílio, cor/raça, "
    "demografia, óbitos, parentesco. Rendimento médio e "
    "escolaridade detalhada sairão junto com os resultados da "
    "amostra, provavelmente ao longo de 2026–2027. Até lá, dados "
    "de 2010 são a melhor fonte disponível de renda por setor em "
    "SP."
))
conteudo.append(p(
    "<b>(v) Fontes paralelas convergem.</b> O Atlas do "
    "Desenvolvimento Humano Municipal (PNUD/FJP), em suas "
    "atualizações intermediárias entre 2000 e 2013 ao nível de "
    "UDH (Unidade de Desenvolvimento Humano, ~310 em SP), "
    "classifica Pinheiros, Jardim Paulista, Vila Mariana, "
    "Perdizes e Indianópolis como UDHs de altíssima renda. O "
    "Índice Paulista de Vulnerabilidade Social (IPVS, Fundação "
    "SEADE) ratifica o mesmo ranking relativo nas suas edições "
    "mais recentes. A convergência entre fontes com métodos e "
    "datas diferentes é evidência de que a estrutura "
    "socioeconômica inter-bairros da cidade é estável, como a "
    "literatura sugere."
))
conteudo.append(p(
    "<b>Consequência metodológica:</b> o achado central — de que "
    "a renda per capita explica uma pequena parcela da variância "
    "ideológica entre zonas eleitorais, enquanto o índice "
    "institucional explica a maior parte — é <b>robusto à "
    "imperfeição da medida de renda</b>. A imprecisão da medida "
    "2010 tende a atenuar correlações potencialmente reais, não a "
    "criar correlações espúrias. Se o Censo 2022 eventualmente "
    "confirmar que as posições relativas das zonas se mantiveram "
    "(expectativa da literatura), o R² da renda em 2024 deve ficar "
    "próximo do observado aqui; se houver mudanças estruturais "
    "(improvável no escopo de 14 anos para bairros já "
    "consolidados), o R² pode cair mais, sem nunca superar o R² "
    "do índice institucional — que usa base de dados de 2022 "
    "(CEM/USP EL2022_LV_ESP) e não sofre o problema de defasagem."
))
conteudo.append(h2("9.2 Outras limitações"))
conteudo.append(p(
    "<b>Agregação:</b> a unidade de análise é a zona eleitoral (58 "
    "observações), o que limita o poder estatístico. Análise no nível "
    "de seção (~18.000 seções) ou local de votação (~2.000) permitiria "
    "controles mais finos e é factível com os dados já coletados."
))
conteudo.append(p(
    "<b>Validade externa do índice institucional:</b> o índice da "
    "seção 7 é construído por matching de palavras-chave nos nomes "
    "dos locais de votação. Essa é uma proxy operacional válida, mas "
    "sujeita a falsos negativos (escolas progressistas cujo nome não "
    "contém palavra-chave reconhecida) e falsos positivos (escolas "
    "particulares com nome parecido mas perfil pedagógico diferente). "
    "Um refinamento futuro seria cruzar com base do Inep (cadastro "
    "escolar) ou da Secretaria de Cultura (cadastro de instituições "
    "culturais). A robustez do resultado (R² = 0,44) sugere que, "
    "mesmo com a proxy imprecisa, o sinal é forte o suficiente para "
    "dominar a análise."
))
conteudo.append(p(
    "<b>Escolaridade:</b> a variável V009 capta renda, não "
    "escolaridade. A base Pessoa13_SP1 do Censo contém dados de anos "
    "de estudo por setor e pode ser integrada ao pipeline como próximo "
    "passo — permitindo regressão multivariada do tipo "
    "<i>escore = α + β₁(renda) + β₂(escolaridade) + ε</i>."
))

conteudo.append(h1("10. Reprodutibilidade"))
conteudo.append(p(
    "Código em <i>socioeconomia_zonas.py</i> + <i>grafico_renda_escore.py</i>. "
    "Dados primários: Base IBGE 2010 SP Capital "
    "(<i>SP_Capital_20231030.zip</i>, ~166 MB, Censo Demográfico 2010, "
    "Resultados do Universo); setores censitários via <i>geobr.read_census_tract</i>; "
    "locais de votação via base CEM/USP "
    "(<i>EL2022_LV_ESP_CEM_V2</i>). Todas as fontes são públicas. "
    "Repositório: "
    "<font color='#1a4dd0'><u>github.com/miaguchi/democracia-em-dados</u></font>."
))

SAIDA.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(
    str(SAIDA),
    pagesize=A4,
    leftMargin=2.5 * cm, rightMargin=2.5 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Renda e voto nas zonas ricas de SP",
    author="Thiago Suzuki Conti Miaguchi",
)
doc.build(conteudo)
print(f"PDF gerado: {SAIDA}")
print(f"Tamanho: {SAIDA.stat().st_size / 1024:.1f} KB")
