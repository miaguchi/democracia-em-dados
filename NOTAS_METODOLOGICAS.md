# 2026-04-16 — achado sobre teste placebo

N=3 locais não-educacionais nas 8 zonas ricas é insuficiente 
para regressão placebo restrita a essas zonas.

Decisão: expandir placebo para SP inteiro (58 zonas).

## Especificação do teste placebo

### Lógica
O índice institucional original (Cap. III) calcula, para cada uma das
58 zonas de SP, a fração de locais de votação em categorias
cultural-progressistas. Resultado: R²=0,44 contra escore ideológico
(vs R²=0,088 para renda).

O placebo testa: um índice construído com categorias *não-educacionais*
(sem relação teórica com voto progressista) prediz o escore? Se R² ≈ 0,
o efeito original é específico. Se R² alto, o achado fica comprometido.

### Categorias do placebo
Duas versões para robustez:

**Placebo estrito** (sem ambiguidade teórica):
- Prisional: CDP, PENIT, FUND CASA, CPP
- Saúde: POSTO SAUDE, UBS

**Placebo amplo** (todas as não-educacionais):
- Prisional + Saúde (acima)
- Associações: ASSOC, ASSOC CULT, COOP, ASSIST SOC
- Religioso: IGREJA, PASTORAL
- Esportivo: CLUBE, CLUBE ATL, CDC
- Assistência social: CREAS, CCA
- Administrativo: AUTARQUIA, SECRETARIA
- Cultural: ESP CULT, BIBLI, GURI
- Equipamento público: EQUIP PUB
- CEU puro (sem escola no tipo)
- Comunidade/assentamento: BAIRRO, ASSENT
- Outros: NUCLEO, 2 FUND que são lares

### Fórmula
Mesma do índice original para manter comparabilidade:
fração de locais da zona em pelo menos uma categoria do placebo.

### Hipótese nula
R² do índice placebo contra escore ideológico ≈ 0
(ou significativamente menor que 0,44 do índice original).

### Verificações prévias à regressão
- Distribuição do índice placebo por zona (se volume muito menor
  que o original, a comparação fica injusta — registrar isso)
- Verificar se há zonas com zero locais não-educacionais

### Risco metodológico
CEUs têm componente cultural/educacional — não são placebo puro.
Solução: a versão estrita (só prisional + saúde) resolve.
Se ambas as versões derem R² baixo, conclusão robusta.

### Próximo passo
Implementar cálculo do índice placebo (estrito e amplo) para as
58 zonas, regredir contra escore ideológico, comparar R² com
o índice original. Commit separado.
