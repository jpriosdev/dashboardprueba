# 📊 VISUALIZACIONES & GRÁFICOS DE ANÁLISIS
## Métricas de Calidad y Testing - JIRA LTI

---

## 1. ESTADO ACTUAL VS. METAS

```
TEST COVERAGE RATE (TCR)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Actual:  11.5%  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  CRÍTICO
Meta:    80.0%  ████████████████████████████████████████  

Brecha:  -68.5 puntos porcentuales
Tiempo para recuperar: ~10 semanas (si se implementa plan)

[Graph]
100% ┤                                        ▁▁▁▁▁▁▁▁▁▁
     │                               ▂▂▂▂▂▂▂▂▂
  80% ┤────────── META ─────────────▬
     │                        ▂▂▂▂▂
  60% ┤                 ▂▂▂▂▂
     │          ▂▂▂▂▂
  40% ┤    ▂▂▂▂
     │ ▂▂
  20% ┤
     │ ⬤ ← ACTUAL
   0% ┼─────────────────────────────────────────────────────────
     W1  W2  W3  W4  W5  W6  W7  W8  W9  W10 W11 W12
    
    ⬤ = Actual (11.5%)  ─ = Meta (80%)  ▂ = Proyección


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

```
TEST EXECUTION VELOCITY (TEV)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Actual:   0.06 tests/día  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  CRÍTICO
Meta:     1.0  tests/día  ██████████████████████████████████

Brecha:   -0.94 tests/día (16.6x más lento)
Impacto:  Cada feature toma ~16 días para testing (vs 1 día target)

[Graph]
1.5 tests/día ┤                                          ▁▁▁▁▁▁
              │                               ▁▁▁▁▁▁▁▁▁▁
   1.0 tests/día ┤────────── META ──────────────▬
              │                        ▁▁▁▁▁
   0.5 tests/día ┤                 ▁▁▁▁
              │          ▁▁▁
   0.1 tests/día ┤    ▁▁
              │ ⬤ ← ACTUAL
   0.0 tests/día ┼─────────────────────────────────────────
              W1  W2  W3  W4  W5  W6  W7  W8  W9  W10 W11 W12


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

```
QUALITY GATE PASS RATE (QGPR)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Actual:   62.8%  ████████████████████████░░░░░░░░  MEJORABLE
Meta:     70.0%  ████████████████████████░░░░░░░░

Brecha:   -7.2 puntos porcentuales
Impacto:  37.2% de issues requieren rework

[Graph]
100% ┤
     │
  80% ┤                                      ▁▁▁▁▁▁▁▁
     │
     │                              ▁▁▁▁▁▁▁▁
  70% ┤────── META ───────────────▬──────
     │                   ▁▁▁▁▁▁▁▁▁
     │            ▁▁▁▁▁
     │     ▁▁▁▁▁
  60% ┤ ⬤ ← ACTUAL
     │
  50% ┼─────────────────────────────────────────
     W1  W2  W3  W4  W5  W6  W7  W8  W9  W10 W11


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 2. DISTRIBUCIÓN DE TIPOS DE ISSUES

```
DESGLOSE DE 1,403 ISSUES TOTALES

Story          [████████████████░░░░] 532 (37.9%)
Task           [███████████░░░░░░░░░] 385 (27.4%)
Test           [████░░░░░░░░░░░░░░░░] 145 (10.3%)
Bug            [███░░░░░░░░░░░░░░░░░] 122 (8.7%)
Epic           [███░░░░░░░░░░░░░░░░░] 102 (7.3%)
Sub-task       [█░░░░░░░░░░░░░░░░░░░]  39 (2.8%)
Test Execution [█░░░░░░░░░░░░░░░░░░░]  27 (1.9%)
Unplanned Task [█░░░░░░░░░░░░░░░░░░░]  26 (1.9%)
Sub Test Exec  [░░░░░░░░░░░░░░░░░░░░]  21 (1.5%)
Otros          [░░░░░░░░░░░░░░░░░░░░]   4 (0.3%)

CRÍTICA: Solo 27 Test Executions para 532 Stories
Razón: TCR = 5.1% en historias (aún peor que 11.5% general)
```