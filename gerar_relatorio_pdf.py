"""Gera PDF com resumo dos achados alinhados ao projeto de mestrado.

Estrutura acadêmica baseada em:
Miaguchi, T. S. C. (2023). "Disputa partidária e comportamento político nos
bairros ricos de São Paulo (2012-2022)". Proposta de dissertação, DCP/FFLCH-USP.
Orientadores: Bruno W. Speck, Glauco Peres da Silva.
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

SAIDA = Path("outputs/relatorio_zonas_ricas_sp.pdf")

# ---------- estilos ----------
styles = getSampleStyleSheet()
st_titulo = ParagraphStyle(
    "titulo",
    parent=styles["Title"],
    fontSize=16,
    leading=20,
    alignment=TA_CENTER,
    spaceAfter=10,
    textColor=colors.HexColor("#1a1a1a"),
)
st_subt = ParagraphStyle(
    "subt",
    parent=styles["Normal"],
    fontSize=11,
    alignment=TA_CENTER,
    spaceAfter=4,
    textColor=colors.HexColor("#444444"),
)
st_h1 = ParagraphStyle(
    "h1",
    parent=styles["Heading1"],
    fontSize=13,
    spaceBefore=14,
    spaceAfter=6,
    textColor=colors.HexColor("#1a1a1a"),
)
st_h2 = ParagraphStyle(
    "h2",
    parent=styles["Heading2"],
    fontSize=11,
    spaceBefore=10,
    spaceAfter=4,
    textColor=colors.HexColor("#333333"),
)
st_body = ParagraphStyle(
    "body",
    parent=styles["Normal"],
    fontSize=10,
    leading=14,
    alignment=TA_JUSTIFY,
    spaceAfter=6,
)
st_caption = ParagraphStyle(
    "caption",
    parent=styles["Italic"],
    fontSize=8,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#555555"),
    spaceAfter=10,
)
st_small = ParagraphStyle(
    "small",
    parent=styles["Normal"],
    fontSize=8,
    leading=11,
    alignment=TA_JUSTIFY,
)

# ---------- helpers ----------
def h1(texto):
    return Paragraph(texto, st_h1)


def h2(texto):
    return Paragraph(texto, st_h2)


def p(texto):
    return Paragraph(texto, st_body)


def fig(caminho, largura=16 * cm, legenda=None):
    elementos = []
    img = Image(caminho, width=largura, height=largura * 0.6, kind="proportional")
    elementos.append(img)
    if legenda:
        elementos.append(Paragraph(legenda, st_caption))
    return elementos


def tabela(dados, larguras=None):
    t = Table(dados, colWidths=larguras)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ]
        )
    )
    return t


# Estilo para células de tabela (word wrap automático)
st_cell = ParagraphStyle(
    "cell", parent=styles["Normal"], fontSize=8, leading=11, alignment=TA_LEFT
)
st_cell_bold = ParagraphStyle(
    "cell_bold",
    parent=styles["Normal"],
    fontSize=8,
    leading=11,
    fontName="Helvetica-Bold",
    alignment=TA_CENTER,
)


def _c(txt):
    return Paragraph(txt, st_cell)


def _cb(txt):
    return Paragraph(txt, st_cell_bold)


# ---------- conteúdo ----------
conteudo = []

# Capa
conteudo.append(
    Paragraph(
        "Comportamento político nos bairros ricos de São Paulo<br/>(2016–2024)",
        st_titulo,
    )
)
conteudo.append(
    Paragraph(
        "Relatório técnico preliminar — análise de dados eleitorais<br/>"
        "no âmbito do projeto de dissertação de mestrado",
        st_subt,
    )
)
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(
    Paragraph(
        "<b>Candidato:</b> Thiago Suzuki Conti Miaguchi<br/>"
        "<b>Programa:</b> Pós-Graduação em Ciência Política — DCP/FFLCH/USP<br/>"
        "<b>Orientação indicada:</b> Bruno Wilhelm Speck, Glauco Peres da Silva",
        st_subt,
    )
)
conteudo.append(Spacer(1, 0.6 * cm))

conteudo.append(h1("1. Introdução e pergunta de pesquisa"))
conteudo.append(
    p(
        "Este relatório apresenta achados empíricos preliminares alinhados com "
        "a pergunta central da proposta de dissertação (Miaguchi, 2023): <i>"
        "a nível infra-municipal, de 2012 a 2022 — estendido aqui a 2024 — "
        "em bairros ricos da cidade de São Paulo, as preferências eleitorais "
        "demarcam continuidades, oscilações ou rupturas ideológicas no voto?</i>"
    )
)
conteudo.append(
    p(
        "O recorte empírico segue o projeto original: zonas eleitorais mais "
        "homogêneas em perfil socioeconômico elevado, com ênfase no "
        "<b>corredor das universidades</b> (Sé, República, Bela Vista, "
        "Consolação, Jardim Paulista, Pinheiros, Alto de Pinheiros e Butantã) "
        "e nas zonas-chave explicitamente indicadas na proposta: <b>5ª "
        "(Jardim Paulista)</b>, <b>251ª (Pinheiros)</b> e <b>258ª "
        "(Indianópolis)</b>. A amostra é complementada por três outras zonas "
        "contíguas de perfil similar: <b>1ª (Bela Vista)</b>, <b>2ª (Perdizes)</b>, "
        "<b>3ª (Santa Ifigênia)</b>, <b>6ª (Vila Mariana)</b> e <b>346ª (Butantã)</b>."
    )
)
conteudo.append(
    p(
        "Os dados primários são do Tribunal Superior Eleitoral "
        "(<i>votacao_partido_munzona</i> e <i>votacao_secao</i>) para as "
        "eleições municipais de 2016, 2020 e 2024. A geometria dos locais de "
        "votação vem da base <i>EL2022_LV_ESP_CEM_V2</i> do Centro de Estudos "
        "da Metrópole (CEM/USP) e o polígono do município de São Paulo, do "
        "IBGE via <i>geobr</i>. A classificação ideológica dos partidos segue "
        "Bolognesi, Ribeiro &amp; Codato (2023), com escala contínua 0–10 "
        "baseada em <i>expert survey</i>."
    )
)

conteudo.append(h1("2. Metodologia"))
conteudo.append(
    p(
        "O relatório utiliza três métricas complementares para caracterizar "
        "o comportamento eleitoral por unidade geográfica (zona, local de "
        "votação ou seção eleitoral):"
    )
)
conteudo.append(
    p(
        "<b>a) Volatilidade eleitoral de Pedersen (1983)</b>, decomposta "
        "conforme Bartolini &amp; Mair (1990) em componentes <i>entre-blocos</i> "
        "e <i>dentro-blocos</i>, usando os escores do Bolognesi et al. em "
        "cortes tripartites e quintipartites."
    )
)
conteudo.append(
    p(
        "<b>b) Escore ideológico médio ponderado pelos votos</b> — para cada "
        "unidade, média dos escores Bolognesi dos partidos pesada pelos "
        "votos recebidos. Métrica contínua, sensível à intensidade "
        "ideológica dos partidos. Valores 4,5–5,5 = centro; abaixo de 4,5 = "
        "esquerda/centro-esquerda; acima de 5,5 = centro-direita/direita."
    )
)
conteudo.append(
    p(
        "<b>c) Plurality bipartite por seção ou local</b> — classifica cada "
        "unidade pelo bloco (ESQ = escore ≤ 4,49; DIR = escore &gt; 5,50) "
        "que somou mais votos naquela unidade. Responde diretamente à "
        "pergunta \"em que escola/seção o voto de esquerda ganhou em "
        "pontos absolutos?\". Métrica discreta, útil para identificação "
        "territorial."
    )
)
conteudo.append(
    p(
        "A escolha entre (b) e (c) não é neutra: a métrica contínua pode "
        "mostrar uma zona como \"centro-direita\" enquanto a métrica "
        "bipartite mostra que majoritariamente se votou à esquerda. "
        "Isso ocorre porque na escala Bolognesi 2018 os partidos de "
        "direita estão significativamente mais afastados do centro (média "
        "≈ 7,5) do que os de esquerda (média ≈ 3,5), de modo que cada "
        "voto de direita exerce maior \"alavancagem ideológica\" na "
        "média ponderada. <b>As duas métricas são reportadas</b>."
    )
)

conteudo.append(h1("3. Panorama: SP 2020 → 2024"))
conteudo.append(
    p(
        "A cidade como um todo deslocou-se à direita entre 2020 e 2024 no "
        "voto majoritário: o escore médio ponderado passou de "
        "<b>5,27 para 5,67</b> (Δ = +0,40). A composição partidária mudou "
        "drasticamente. O PSDB/Cidadania, que em 2020 somou 1,75 milhão de "
        "votos para prefeito (Covas), colapsou para 112 mil em 2024. O MDB "
        "(Nunes), antes inexpressivo, alcançou 1,80 milhão; e o PRTB "
        "(Marçal) saltou de 12 mil para 1,72 milhão. A volatilidade de "
        "Pedersen bruta da cidade foi de 0,673, mas a decomposição mostra "
        "que cerca de <b>94% desta volatilidade é intra-campo</b> (troca de "
        "sigla dentro da mesma família ideológica), não realinhamento "
        "entre campos opostos."
    )
)
conteudo.append(
    p(
        "Este dado contextualiza os achados das seções seguintes: a "
        "narrativa pública de \"virada à direita\" na capital paulistana "
        "em 2024 precisa ser qualificada — houve <b>rotação intra-direita</b> "
        "(PSDB → MDB + PRTB) e, nas zonas ricas, preservação — em alguns "
        "casos expansão — do voto progressista."
    )
)
conteudo.append(PageBreak())

conteudo.append(h1("4. Achados centrais por zona"))
conteudo.append(h2("4.1 Trajetória do escore ideológico 2016–2024"))
conteudo.append(
    p(
        "As oito zonas do corredor universitário apresentaram "
        "<b>deslocamento sistematicamente menor</b> à direita do que a média "
        "da cidade. Em particular, Pinheiros (Z251) e Bela Vista (Z1) "
        "permanecem praticamente imóveis no eixo ideológico:"
    )
)
dados_traj = [
    ["Zona", "Bairro", "Escore 2016", "2020", "2024", "Δ 2016–24"],
    ["1", "Bela Vista", "5,16", "5,03", "5,03", "−0,13"],
    ["251", "Pinheiros", "5,14", "5,04", "5,16", "+0,02"],
    ["2", "Perdizes", "5,21", "5,11", "5,28", "+0,06"],
    ["6", "Vila Mariana", "5,35", "5,29", "5,48", "+0,13"],
    ["346", "Butantã", "5,40", "5,36", "5,56", "+0,17"],
    ["5", "Jardim Paulista", "5,42", "5,42", "5,65", "+0,23"],
    ["3", "Santa Ifigênia", "5,27", "5,27", "5,52", "+0,25"],
    ["258", "Indianópolis", "5,51", "5,54", "5,88", "+0,37"],
    ["—", "média SP", "—", "5,27", "5,67", "+0,40 (2020→24)"],
]
conteudo.append(tabela(dados_traj, larguras=[1.2 * cm, 3.5 * cm, 2.5 * cm, 1.5 * cm, 1.5 * cm, 2.5 * cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(
    p(
        "<b>Bela Vista moveu-se à esquerda</b> (−0,13) entre 2016 e 2024 no "
        "voto para prefeito. Pinheiros permanece no mesmo ponto do espectro "
        "(+0,02). Indianópolis, no outro extremo do corredor, teve o maior "
        "deslocamento à direita da amostra (+0,37), mas ainda assim menor "
        "do que a média da cidade (+0,40 apenas para 2020→2024)."
    )
)

conteudo.extend(
    fig(
        "outputs/trajetoria_zonas_ricas_2016_2024.png",
        largura=16 * cm,
        legenda="Figura 1. Trajetórias do escore ideológico médio ponderado "
        "(painel superior) e do percentual de votos no bloco "
        "esquerda+centro-esquerda (painel inferior), por zona-alvo, 2016–2024. "
        "Fonte: elaboração própria a partir de TSE e Bolognesi et al. (2023).",
    )
)

conteudo.append(h2("4.2 Colapso do PSDB e recomposição da direita"))
conteudo.append(
    p(
        "Em todas as oito zonas-alvo, o PSDB/Cidadania era o partido "
        "majoritário em 2020 no voto para prefeito (33–44% do total). Em "
        "2024, esse mesmo partido recebeu entre 0,6% e 1,7%. A tabela "
        "abaixo mostra a composição antes e depois do colapso no agregado "
        "das oito zonas-alvo:"
    )
)
dados_recomp = [
    ["Partido", "2020 (%)", "2024 (%)", "Δ pp"],
    ["PSDB/Cidadania (Covas)", "~38,5", "~1,2", "−37,3"],
    ["MDB (Nunes)", "~0", "~28,6", "+28,6"],
    ["PRTB (Marçal)", "~0", "~21,8", "+21,8"],
    ["NOVO", "~0", "~2,5", "+2,5"],
    ["PSOL/Rede (Boulos)", "~26,5", "~33,1", "+6,6"],
    ["PSB (France / Tabata)", "~12,0", "~13,5", "+1,5"],
]
conteudo.append(tabela(dados_recomp, larguras=[6 * cm, 3 * cm, 3 * cm, 3 * cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(
    p(
        "A leitura central: <b>o campo centro-esquerda expandiu-se</b> (PSOL/"
        "Rede +6,6 pp; PSB +1,5 pp) enquanto o campo de direita passou por "
        "<b>recomposição completa</b>: o PSDB foi substituído por MDB + PRTB "
        "+ NOVO. A relação entre esses três novos partidos e o antigo voto "
        "tucano é uma das questões empíricas que a dissertação pode "
        "investigar com maior profundidade, incluindo trajetórias "
        "individuais de lideranças (Curi, 2022)."
    )
)

conteudo.append(PageBreak())
conteudo.append(h1("5. Análise espacial — mapa do corredor"))
conteudo.append(
    p(
        "A figura a seguir mostra o corredor das universidades com os "
        "locais de votação coloridos pelo bloco ideológico dominante "
        "(plurality bipartite sobre os votos agregados de todas as seções "
        "de cada local). No voto para prefeito em 2024, o corredor "
        "<b>inverte o padrão geral da cidade</b>: a esquerda vence por "
        "112 locais contra 97 (razão 1,15 : 1), enquanto na cidade inteira "
        "a direita vence por 1359 × 571 (razão 2,38 : 1)."
    )
)
conteudo.extend(
    fig(
        "outputs/mapa_blocos_secao_corredor_prefeito_2024.png",
        largura=16 * cm,
        legenda="Figura 2. Bloco dominante por local de votação no corredor "
        "universitário — prefeito 1T, São Paulo 2024. Cada ponto é uma "
        "escola/colégio; a cor indica qual bloco (esquerda+centro-esquerda "
        "vs centro-direita+direita) recebeu mais votos somados entre todas "
        "as seções daquele local.",
    )
)
conteudo.append(
    p(
        "Pinheiros (Z251) e Bela Vista (Z1) aparecem como os dois bunkers "
        "progressistas mais nítidos, com predomínio quase absoluto de "
        "pontos vermelhos. Indianópolis (Z258), em contraste, é um bloco "
        "azul quase homogêneo. Jardim Paulista, Perdizes, Santa Ifigênia, "
        "Vila Mariana e Butantã apresentam distribuição mista, com leve "
        "predomínio conforme a sub-área interna da zona."
    )
)

conteudo.append(PageBreak())
conteudo.append(h1("6. Seções como unidade de análise"))
conteudo.append(
    p(
        "Quando a análise desce ao nível da seção eleitoral — o patamar "
        "mais fino disponível nos dados do TSE, próximo do que Power &amp; "
        "Rodrigues-Silveira (2019) chamam de \"bairros ou quarteirões\" — "
        "o contraste interno ao corredor torna-se ainda mais nítido:"
    )
)
dados_secao = [
    ["Zona", "Bairro", "Seções (2024)", "% ESQ &gt; DIR"],
    ["251", "Pinheiros", "326", "57,1%"],
    ["1", "Bela Vista", "446", "39,7%"],
    ["2", "Perdizes", "438", "34,7%"],
    ["5", "Jardim Paulista", "341", "17,6%"],
    ["346", "Butantã", "511", "11,0%"],
    ["3", "Santa Ifigênia", "434", "7,4%"],
    ["6", "Vila Mariana", "444", "7,2%"],
    ["258", "Indianópolis", "550", "0,9%"],
]
conteudo.append(tabela(dados_secao, larguras=[1.5 * cm, 3.8 * cm, 3 * cm, 3 * cm]))
conteudo.append(Spacer(1, 0.2 * cm))
conteudo.append(
    p(
        "Em Pinheiros, <b>mais da metade das 326 seções eleitorais "
        "registraram plurality bipartite à esquerda</b> no voto para "
        "vereador em 2024. Indianópolis, na mesma posição socioeconômica "
        "do espectro de renda/escolaridade, tem 0,9% — apenas 5 seções "
        "entre 550. O gradiente interno ao corredor é de aproximadamente "
        "63 vezes."
    )
)
conteudo.append(
    p(
        "Isto constitui, na amostra analisada, <b>confirmação empírica "
        "direta da Hipótese 4</b> formulada na proposta do projeto: "
        "\"o voto da esquerda nos bairros ricos e homogêneos aponta "
        "para outras variáveis independentes do que a renda ou a "
        "escolaridade\". Pinheiros, Bela Vista e Perdizes — três dos "
        "bairros mais ricos e escolarizados da cidade — estão entre os "
        "que têm maior percentual de seções progressistas."
    )
)

conteudo.append(PageBreak())
conteudo.append(h1("7. Descrição institucional dos redutos de esquerda"))
conteudo.append(
    p(
        "Os locais de votação com maior percentual de voto para o bloco "
        "esquerda+centro-esquerda em 2024 não se distribuem aleatoriamente "
        "dentro do corredor universitário. Eles seguem um padrão "
        "institucional bem definido, reagrupável em quatro categorias:"
    )
)

conteudo.append(h2("7.1 Escolas particulares progressistas (\"construtivistas\")"))
conteudo.append(
    p(
        "Escolas particulares de tradição progressista, predominantemente "
        "de classe média-alta, aparecem sistematicamente no topo do "
        "ranking. No vereador 2024: Escola Oswald de Andrade (68,8%), "
        "Colégio Vera Cruz (63,7%), Escola Lumiar (62,0%), Colégio "
        "Horizontes (59,8%), Colégio Stella Maris (58,1%), Escola da "
        "Vila (57,2%), Colégio Equipe (prefeito: 73,5%), Colégio Itaca "
        "(prefeito: 65,3%). São instituições com identidade pedagógica "
        "explícita — Freinet, Piaget, Dewey — e público-alvo composto "
        "majoritariamente por famílias de profissionais liberais e "
        "acadêmicos."
    )
)

conteudo.append(h2("7.2 Universidades e suas áreas de influência"))
conteudo.append(
    p(
        "Locais de votação associados a universidades aparecem com "
        "frequência desproporcional no topo do ranking: USP-Faculdade "
        "de Direito (67,4% prefeito), Mackenzie Consolação (65,4%), "
        "Mackenzie Prédio 09 — Itambé (67,4%), PUC-SP Ciências Exatas "
        "(56,1% vereador), Uninove Barra Funda (66,7% prefeito), "
        "Faculdade Santa Marcelina (59,9%), Faculdade Phorte (72,5%). "
        "Este conjunto dá corpo empírico à ideia do \"corredor das "
        "universidades\" nomeada na proposta do projeto."
    )
)

conteudo.append(h2("7.3 Escolas públicas estaduais e municipais de prestígio"))
conteudo.append(
    p(
        "Instituições públicas tradicionalmente associadas a famílias de "
        "classe média culta, servidores públicos e professores: EE "
        "Caetano de Campos (74,0% prefeito), EE Fernão Dias Paes (61,5%), "
        "EE Godofredo Furtado (58,1%), EE Fidelino de Figueiredo (55,3%), "
        "EMEF Des Amorim Lima (74,6% — escola pública inovadora de fama "
        "nacional), EE Prof Clorinda Danti (71,3%). O achado confirma "
        "que <b>o voto progressista nos bairros ricos não se restringe à "
        "elite privada</b>, mas inclui uma fração significativa ligada "
        "institucionalmente ao setor público de ensino e cultura."
    )
)

conteudo.append(h2("7.4 Instituições culturais internacionais"))
conteudo.append(
    p(
        "Goethe-Institut (Pinheiros) registra 63,1% no vereador e 72,2% no "
        "prefeito. Representa simbolicamente o ambiente de cosmopolitismo "
        "cultural e contato internacional — distinção que na literatura "
        "de sociologia política aparece como marcador independente de "
        "posicionamento progressista, mesmo controlando por renda e "
        "escolaridade (Inglehart &amp; Norris; Bonikowski)."
    )
)

conteudo.append(PageBreak())
conteudo.append(h1("8. Descrição institucional dos redutos de direita"))
conteudo.append(
    p(
        "A análise simétrica — identificação dos locais de votação com maior "
        "percentual para o bloco direita+centro-direita em 2024 — revela um "
        "perfil institucional quase oposto ao descrito na seção anterior. O "
        "topo do ranking de direita em São Paulo <b>não</b> é composto por "
        "colégios confessionais tradicionais, clubes empresariais ou bairros "
        "centrais ricos, como a literatura mais antiga sobre \"voto de classe\" "
        "sugeriria. Quatro padrões emergem:"
    )
)

conteudo.append(h2("8.1 Vila Maria: a zona mais conservadora coerente da cidade"))
conteudo.append(
    p(
        "A 254ª zona eleitoral (Vila Maria), na zona norte-leste, concentra "
        "<b>nove dos 25 locais</b> com maior percentual de voto à direita no "
        "vereador 2024: EMEI Prof. Yukio Ozaki (88,5%), EMEF Dom Pedro I "
        "(88,5%), EMEF João Domingues Sampaio (87,2%), CEU Parque Novo Mundo "
        "(86,2%), EMEF Célia Regina Lekevicius (85,3%), EMEF Cel. Romão Gomes "
        "(85,0%), EE Heróis da FEB (84,3%), CEI Jardim Japão (84,2%) e EE "
        "Prof. Máximo Ribeiro Nunes (84,1%). É também dominante nos rankings "
        "de prefeito. Não há split-ticket territorial aqui: Vila Maria é "
        "coerentemente de direita em todos os cargos, ao contrário da "
        "polarização interna encontrada no corredor universitário. Traços "
        "locais que valem investigação qualitativa: herança de imigração "
        "italiana e japonesa, presença militar visível na toponímia urbana "
        "(Heróis da FEB, Cel. Romão Gomes, Almirante Tamandaré), e densidade "
        "de igrejas católicas tradicionais e evangélicas."
    )
)

conteudo.append(h2("8.2 Escolas com denominação cívico-militar"))
conteudo.append(
    p(
        "Um achado semântico e sociológico: os nomes das escolas com maior "
        "percentual de direita em Vila Maria e bairros vizinhos refletem "
        "uma <b>cultura cívica de culto militar</b>. A EE Heróis da FEB "
        "(Força Expedicionária Brasileira, batalha da Itália na Segunda "
        "Guerra, 84,3% direita), a EMEF Cel. Romão Gomes (oficial "
        "paulistano da Revolução Constitucionalista de 1932, 85,0%) e a "
        "EMEF Almirante Tamandaré (83,5%) compõem um cluster onomástico "
        "revelador. Essa associação entre identidade cívico-patriótica "
        "explícita nos nomes das instituições e voto atual no bolsonarismo "
        "merece análise específica, na linha dos estudos de autoritarismo "
        "subnacional e cultura política local."
    )
)

conteudo.append(h2("8.3 Periferia norte, leste e sul — base popular bolsonarista"))
conteudo.append(
    p(
        "Fora de Vila Maria, o voto de direita acima de 80% concentra-se "
        "em periferias tradicionais de perfil conservador-evangélico: "
        "Vila Sabrina (Z420) com quatro locais no top 25 do prefeito; "
        "Parelheiros rural (Z381) com Leonor Fernandes Costa Zacharias "
        "(84,3% vereador) e Ulysses Guimarães (79,3% prefeito); Tucuruvi "
        "(Z256), Vila Matilde (Z347), Vila Formosa (Z348), Jaçanã (Z349), "
        "Cangaíba (Z390), Vila Prudente (Z257), Capela do Socorro (Z280), "
        "Jabaquara (Z320), Brasilândia (Z376), Grajaú (Z371) e Teotônio "
        "Vilela (Z421). Perus (Z389), que também tem locais entre os mais "
        "à esquerda (via redutos PT históricos na zona noroeste), aparece "
        "simultaneamente no topo da direita — a EMEF Virginia Valeria é "
        "<b>a maior taxa de direita individual de toda a cidade</b> no "
        "vereador (89,2%). A periferia paulistana de 2024 é, portanto, "
        "<b>heterogênea internamente</b>, com microterritórios de cada "
        "campo coexistindo na mesma zona eleitoral."
    )
)

conteudo.append(h2("8.4 Split-ticket territorial: Parelheiros e vizinhas"))
conteudo.append(
    p(
        "Parelheiros (Z381) merece destaque. No LISA da análise espacial "
        "do vereador (Seção 5 deste relatório), Parelheiros aparece como "
        "<i>cluster Baixa-Baixa</i> — um reduto de estabilidade do "
        "eleitorado que sistematicamente não troca de sigla entre eleições. "
        "Ao mesmo tempo, no ranking por local, Parelheiros aparece <b>entre "
        "os mais à direita no vereador</b> (EE Leonor Fernandes Costa "
        "Zacharias, 84,3%) e <b>entre os mais à esquerda no prefeito</b> "
        "(EE Valdir Fernandes Pinto, 75,8% — embora em Teotônio Vilela, "
        "zona contígua). A coexistência dessas duas características "
        "parece sinalizar um split-ticket forte e estável, talvez "
        "relacionado à base religiosa evangélica (voto em vereadores "
        "evangélicos de direita independentemente do voto executivo)."
    )
)

conteudo.append(h2("8.5 Escolas particulares de direita: poucas e de nicho"))
conteudo.append(
    p(
        "Ao contrário do ranking de esquerda, <b>escolas particulares são "
        "exceção no top 25 de direita</b>. As únicas que aparecem são: "
        "Colégio Sir Isaac Newton (Jaçanã, 83,5% no vereador), escola "
        "inglesa de perfil elite-intermediária; Associação Educacional "
        "Eugênio Montale (Butantã, 73,8% no prefeito), escola italiana "
        "católica; e Colégio Soter (Vila Formosa, 73,3%), colégio "
        "confessional tradicional. Nenhum desses tem perfil análogo às "
        "escolas construtivistas progressistas (Vera Cruz, Vila, Equipe, "
        "Lumiar, Oswald de Andrade) do ranking de esquerda. O resultado "
        "sugere que o ambiente particular-privado-elitizado em São Paulo "
        "é majoritariamente <b>progressista institucionalmente</b>, com "
        "exceções de nicho confessional. Os colégios evangélicos e "
        "católicos tradicionais — que nas hipóteses de Rocha (2018) "
        "deveriam formar o polo contrário — <b>não aparecem entre os 25 "
        "mais à direita da cidade</b>, sinalizando que o voto bolsonarista "
        "em SP 2024 se estabelece majoritariamente em <b>escolas públicas "
        "periféricas</b>, e não em ambientes confessionais privados."
    )
)

conteudo.append(h1("9. Tabela comparativa: perfil institucional dos dois polos"))
conteudo.append(
    p(
        "A comparação lado a lado dos perfis institucionais dos redutos "
        "mais à esquerda e mais à direita permite visualizar com "
        "clareza a dualidade institucional identificada:"
    )
)
dados_comp = [
    [_cb("Eixo"), _cb("Redutos de esquerda"), _cb("Redutos de direita")],
    [
        _c("<b>Localização</b>"),
        _c(
            "Corredor universitário (Pinheiros, Bela Vista, Perdizes, "
            "Butantã) + periferia PT histórica (Cidade Tiradentes, Perus, "
            "São Miguel, Jd São Luís)"
        ),
        _c(
            "Vila Maria, Vila Sabrina, Parelheiros rural, Tucuruvi, Vila "
            "Matilde, Jaçanã, Vila Formosa, Brasilândia, Grajaú"
        ),
    ],
    [
        _c("<b>Escolas particulares</b>"),
        _c(
            "Vera Cruz, Oswald de Andrade, Equipe, Vila, Lumiar, "
            "Horizontes, Stella Maris, Itaca — escolas construtivistas de "
            "elite cultural"
        ),
        _c(
            "Sir Isaac Newton (nicho inglês), Eugênio Montale (nicho "
            "italiano), Soter (confessional) — exceções de perfil "
            "confessional ou internacional restrito"
        ),
    ],
    [
        _c("<b>Universidades</b>"),
        _c(
            "USP Faculdade de Direito, Mackenzie, PUC-SP, Uninove Barra "
            "Funda, Santa Marcelina — corpo docente, funcionários, "
            "estudantes"
        ),
        _c("Praticamente nenhuma universidade no top 25 de direita"),
    ],
    [
        _c("<b>Escolas públicas</b>"),
        _c(
            "Caetano de Campos, Fernão Dias Paes, Godofredo Furtado, "
            "Fidelino de Figueiredo, Des Amorim Lima, Clorinda Danti — "
            "rede pública de prestígio cultural"
        ),
        _c(
            "EE Heróis da FEB, Cel. Romão Gomes, Almirante Tamandaré, "
            "Dom Camilo Maria Cavalheiro — escolas públicas periféricas "
            "com cultura cívico-militar e presença evangélica"
        ),
    ],
    [
        _c("<b>Instituições culturais</b>"),
        _c(
            "Goethe-Institut (72% prefeito, 63% vereador) — cosmopolitismo "
            "cultural internacional"
        ),
        _c("Ausentes no top 25 de direita"),
    ],
    [
        _c("<b>Semântica dos nomes</b>"),
        _c(
            "Intelectuais, educadores progressistas, modernistas (Oswald "
            "de Andrade, Anita Malfatti, Mario de Andrade)"
        ),
        _c(
            "Oficiais militares, batalhas, tradições patrióticas (Heróis "
            "da FEB, Cel. Romão Gomes, Dom Pedro I, Almirante Tamandaré)"
        ),
    ],
]
tab_comp = Table(
    dados_comp,
    colWidths=[3.2 * cm, 6.5 * cm, 6.5 * cm],
)
tab_comp.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (1, 1), (1, -1), colors.HexColor("#fdecea")),
            ("BACKGROUND", (2, 1), (2, -1), colors.HexColor("#e6effa")),
        ]
    )
)
conteudo.append(tab_comp)
conteudo.append(Spacer(1, 0.3 * cm))
conteudo.append(
    p(
        "O padrão que emerge é inequívoco: em São Paulo 2024, o voto "
        "ideológico não está organizado pela dicotomia clássica <i>renda "
        "alta = direita, renda baixa = esquerda</i>, nem pela dicotomia "
        "<i>público = esquerda, privado = direita</i>. Ele está organizado "
        "por <b>pertencimento a ambientes institucionais educativos-"
        "culturais diferenciados</b>: instituições progressistas "
        "(construtivistas, universitárias, cosmopolitas) produzem voto de "
        "esquerda tanto em populações de alta quanto de baixa renda; "
        "instituições de tradição cívico-militar, confessional ou "
        "comunitário-periférica produzem voto de direita "
        "independentemente do nível socioeconômico. A variável explicativa "
        "relevante, nesta análise preliminar, parece ser institucional e "
        "sociocultural — não de classe em sentido estrito."
    )
)

conteudo.append(PageBreak())
conteudo.append(h1("10. O voto de esquerda em São Paulo é bimodal"))
conteudo.append(
    p(
        "Quando o ranking de locais mais à esquerda é produzido para a "
        "cidade inteira (não apenas o corredor), emerge uma das "
        "observações mais substantivas deste relatório: o eleitorado mais "
        "progressista de São Paulo, em 2024, é composto por <b>duas "
        "populações socialmente muito distintas</b>."
    )
)
conteudo.append(
    p(
        "No voto para prefeito (Boulos), os 25 locais com maior "
        "percentual de esquerda se dividem aproximadamente ao meio entre "
        "(a) periferia histórica do PT — Cidade Tiradentes, Perus, "
        "Ermelino Matarazzo, São Miguel Paulista, Jardim São Luís, "
        "Teotônio Vilela, Paraisópolis — e (b) corredor cultural-"
        "universitário — Pinheiros, Bela Vista, Perdizes, Butantã. O "
        "maior percentual individual é da EMEF Camilo Castelo Branco, "
        "em Cidade Tiradentes (79,8%), mas escolas como Amorim Lima "
        "(Butantã, 74,6%), Caetano de Campos (Bela Vista, 74,0%) e "
        "Stella Maris (Pinheiros, 72,2%) aparecem praticamente empatadas "
        "com os redutos da zona leste."
    )
)
conteudo.append(
    p(
        "No voto para vereador, este paralelismo <b>desaparece</b>: 16 dos "
        "25 locais mais à esquerda estão concentrados no corredor "
        "universitário. A periferia distribui seu voto progressista em "
        "centenas de vereadores de diversos partidos, inclusive de "
        "direita/centro-direita com agendas locais específicas, e não "
        "consegue manter a maioria dos votos somados à esquerda em "
        "poucas unidades territoriais."
    )
)
conteudo.append(
    p(
        "Este é um achado relevante para as hipóteses do projeto. A "
        "coalizão que elege candidatos de esquerda para o executivo "
        "municipal é <b>bimodal</b>: periferia popular + centro "
        "cultural/acadêmico. A variável que unifica os dois grupos não "
        "pode ser renda (opostas), nem escolaridade (opostas), nem "
        "religião (diversas). A literatura de sociologia política "
        "(Inglehart, Norris, Rocha, Almeida &amp; Carneiro) sugere "
        "que se trata de <b>ambiente institucional educativo-cultural</b> — "
        "escolas públicas populares com lideranças sindicais na "
        "periferia, e escolas particulares progressistas + universidades "
        "+ instituições culturais internacionais no centro."
    )
)

conteudo.append(PageBreak())
conteudo.append(h1("11. Síntese em relação às hipóteses do projeto"))

dados_hip = [
    [_cb("Hipótese"), _cb("Achado"), _cb("Estado")],
    [
        _c(
            "<b>H1:</b> há novo padrão, não apenas movimento pendular ou "
            "força centrípeta em torno da centro-direita"
        ),
        _c(
            "Confirmada. Não há pêndulo: houve colapso da centro-direita "
            "(PSDB −37pp) e expansão simultânea do campo esquerda nos "
            "bairros ricos."
        ),
        _c("<b>Confirmada</b>"),
    ],
    [
        _c(
            "<b>H2:</b> maior pluralização dos grupos de interesse implica "
            "nova competição, volatilidade e representação legislativa"
        ),
        _c(
            "Parcialmente confirmada. NEP caiu (menos partidos efetivos) "
            "mas a composição mudou qualitativamente; volatilidade "
            "Pedersen alta é substantivamente intra-campo."
        ),
        _c("<b>Parcial</b>"),
    ],
    [
        _c(
            "<b>H3:</b> a centro-direita foi atraída pela direita/"
            "extrema-direita ao longo do tempo"
        ),
        _c(
            "Confirmada estruturalmente. PSDB 33–44% → 0,6–1,7% nas 8 "
            "zonas; substituição por MDB + PRTB + NOVO, todos com escore "
            "Bolognesi 7,01+."
        ),
        _c("<b>Confirmada</b>"),
    ],
    [
        _c(
            "<b>H4:</b> o voto de esquerda nos bairros ricos aponta para "
            "variáveis independentes da renda e da escolaridade"
        ),
        _c(
            "Confirmada de forma dramática. Pinheiros tem 57,1% das "
            "seções ESQ; Indianópolis (mesma renda/escolaridade) tem "
            "0,9%. A análise simétrica dos redutos de direita (Seção 8) "
            "mostra que mesmo o voto bolsonarista em 2024 não se "
            "concentra em colégios confessionais ou clubes ricos, mas "
            "em escolas públicas periféricas com cultura cívico-militar. "
            "O fator explicativo é <b>institucional-ambiental</b>, não "
            "socioeconômico."
        ),
        _c("<b>Confirmada</b>"),
    ],
]
tab_hip = Table(dados_hip, colWidths=[5 * cm, 8.5 * cm, 2.5 * cm])
tab_hip.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            (
                "BACKGROUND",
                (2, 1),
                (2, 1),
                colors.HexColor("#c6e0c6"),
            ),
            (
                "BACKGROUND",
                (2, 2),
                (2, 2),
                colors.HexColor("#f0e6a0"),
            ),
            (
                "BACKGROUND",
                (2, 3),
                (2, 3),
                colors.HexColor("#c6e0c6"),
            ),
            (
                "BACKGROUND",
                (2, 4),
                (2, 4),
                colors.HexColor("#c6e0c6"),
            ),
        ]
    )
)
conteudo.append(tab_hip)

conteudo.append(h1("12. Limitações e próximos passos"))
conteudo.append(
    p(
        "<b>Período:</b> o projeto prevê o recorte 2012–2022; este "
        "relatório analisa com profundidade 2016, 2020 e 2024 (as três "
        "eleições municipais disponíveis). A expansão para 2012 exigirá "
        "download e tratamento adicional do arquivo <i>votacao_partido_"
        "munzona_2012</i>. As eleições gerais intermediárias (2014, 2018, "
        "2022) seguirão como análise paralela."
    )
)
conteudo.append(
    p(
        "<b>Controles sociodemográficos:</b> a análise atual usa zonas e "
        "seções como proxy de homogeneidade socioeconômica, mas não "
        "incorpora ainda variáveis de renda, escolaridade, raça, gênero "
        "e cobertura de políticas públicas por setor censitário. A "
        "integração com dados do IBGE Censo 2022 e do Centro de Estudos "
        "da Metrópole é o próximo passo metodológico prioritário."
    )
)
conteudo.append(
    p(
        "<b>Inferência ecológica:</b> métodos de Goodman (1953) e "
        "King, Tanner &amp; Rosen (2004) para estimar a transferência de "
        "votos entre candidatos, aplicados seção por seção, podem testar "
        "diretamente quanto do voto Covas 2020 foi para Nunes, quanto "
        "para Marçal e quanto para Boulos — uma questão diretamente "
        "relevante à H3."
    )
)
conteudo.append(
    p(
        "<b>Classificação ideológica:</b> os escores Bolognesi et al. "
        "(2023) foram levantados em survey de 2018 e podem estar "
        "defasados para partidos que se moveram no espectro desde "
        "então (notadamente PL, PSD e MDB). Uma réplica do <i>expert "
        "survey</i> para 2024 seria metodologicamente relevante, ou "
        "alternativamente o uso de métricas comportamentais (W-NOMINATE, "
        "votações na Câmara) para calibrar os escores."
    )
)
conteudo.append(
    p(
        "<b>Métodos qualitativos:</b> os ambientes institucionais "
        "identificados como redutos de esquerda nos bairros ricos "
        "(escolas construtivistas, universidades, instituições culturais) "
        "são candidatos naturais a <i>case studies</i> qualitativos — "
        "entrevistas com diretores, professores, lideranças comunitárias "
        "— para validar a hipótese de que a variável explicativa é "
        "ambiental/institucional, não socioeconômica."
    )
)

conteudo.append(h1("13. Reprodutibilidade e dados"))
conteudo.append(
    p(
        "Todo o código utilizado para gerar este relatório está "
        "disponível em repositório público no GitHub: "
        "<font color='#1a4dd0'><u>https://github.com/miaguchi/democracia-em-dados</u></font>. "
        "Os dados primários são do Tribunal Superior Eleitoral (CDN de "
        "dados abertos, parquets processados), da base geográfica CEM/"
        "USP (EL2022_LV_ESP_CEM_V2) e do IBGE (polígonos municipais via "
        "geobr). Os artefatos gerados — mapas, CSVs de ranking por "
        "seção e local, tabelas comparativas — estão no diretório "
        "<i>outputs/</i> do repositório."
    )
)
conteudo.append(
    p(
        "Principais scripts: <i>analise_volatilidade.py</i> "
        "(Pedersen e decomposição), <i>ideologia.py</i> (escores "
        "Bolognesi e classificação de blocos), <i>dossie_zonas_ricas.py</i> "
        "(métricas por zona), <i>secoes_zonas_ricas.py</i> (plurality "
        "bipartite por seção), <i>mapa_blocos_secao_sp.py</i> (mapas de "
        "bloco dominante), <i>trajetoria_zonas_ricas.py</i> (séries "
        "temporais 2016–2024)."
    )
)

conteudo.append(h1("Referências"))
conteudo.append(
    Paragraph(
        "Bartolini, S.; Mair, P. (1990). <i>Identity, Competition and Electoral "
        "Availability: The Stabilization of European Electorates 1885–1985</i>. "
        "Cambridge: Cambridge University Press.<br/><br/>"
        "Bolognesi, B.; Ribeiro, E.; Codato, A. (2023). \"Uma Nova Classificação "
        "Ideológica dos Partidos Políticos Brasileiros\". <i>Dados</i>, 66(2).<br/><br/>"
        "Curi, H. (2022). \"Ninho dos Tucanos: o PSDB em São Paulo (1994–2018)\". "
        "<i>Opinião Pública</i>, 27.<br/><br/>"
        "Limongi, F.; Mesquita, L. (2008). \"Estratégia partidária e preferência "
        "dos eleitores: as eleições municipais em São Paulo entre 1985 e 2004\". "
        "<i>Novos Estudos CEBRAP</i>, 81.<br/><br/>"
        "Miaguchi, T. S. C. (2023). \"Disputa partidária e comportamento político "
        "nos bairros ricos de São Paulo (2012–2022)\". Proposta de dissertação, "
        "DCP/FFLCH-USP.<br/><br/>"
        "Pedersen, M. N. (1979). \"The Dynamics of European Party Systems: "
        "Changing Patterns of Electoral Volatility\". <i>European Journal of "
        "Political Research</i>, 7(1).<br/><br/>"
        "Power, T. J.; Rodrigues-Silveira, R. (2019). \"Mapping Ideological "
        "Preferences in Brazilian Elections, 1994–2018: A Municipal-Level Study\". "
        "<i>Brazilian Political Science Review</i>, 13(1).",
        st_small,
    )
)

# ---------- gerar ----------
SAIDA.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(
    str(SAIDA),
    pagesize=A4,
    leftMargin=2.5 * cm,
    rightMargin=2.5 * cm,
    topMargin=2 * cm,
    bottomMargin=2 * cm,
    title="Relatório - Zonas ricas de SP",
    author="Thiago Suzuki Conti Miaguchi",
)
doc.build(conteudo)
print(f"PDF gerado: {SAIDA}")
print(f"Tamanho: {SAIDA.stat().st_size / 1024:.1f} KB")
