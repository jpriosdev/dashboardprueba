"""
ANÁLISIS EJECUTIVO DE MÉTRICAS KPI PARA CALIDAD Y TESTING
Análisis del archivo JIRA LTI para Director de Tecnología
"""

import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Cargar datos
df = pd.read_csv('JIRA LTI.csv', low_memory=False)

print("=" * 100)
print("ANÁLISIS EJECUTIVO: MÉTRICAS KPI DE CALIDAD Y TESTING - JIRA LTI")
print("=" * 100)
print(f"\nFecha del análisis: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"Total de tickets analizados: {len(df):,}")
print(f"Período cubierto: {df['Created'].min()} a {df['Created'].max()}")

# ============================================================================
# 1. ANÁLISIS GENERAL DE TIPOS DE ISSUES
# ============================================================================
print("\n" + "=" * 100)
print("1. DISTRIBUCIÓN DE TIPOS DE ISSUES Y COBERTURA DE TESTING")
print("=" * 100)

issue_type_counts = df['Issue Type'].value_counts()
print("\nVolumen de Issues por Tipo:")
for issue_type, count in issue_type_counts.items():
    pct = (count / len(df)) * 100
    print(f"  • {issue_type}: {count:,} ({pct:.1f}%)")

# Categorizar issues
testing_issues = df[df['Issue Type'].isin(['Test', 'Test Execution', 'Test Plan'])].shape[0]
development_issues = df[df['Issue Type'].isin(['Story', 'Task', 'Sub-task'])].shape[0]
bug_issues = df[df['Issue Type'] == 'Bug'].shape[0]

print(f"\nRESUMEN CRÍTICO:")
print(f"  • Issues de TESTING: {testing_issues:,} ({(testing_issues/len(df)*100):.1f}%)")
print(f"  • Issues de DESARROLLO: {development_issues:,} ({(development_issues/len(df)*100):.1f}%)")
print(f"  • Issues de BUGS: {bug_issues:,} ({(bug_issues/len(df)*100):.1f}%)")

testing_ratio = testing_issues / len(df)
print(f"\n⚠️  RATIO TESTING:TOTAL = {testing_ratio:.2%}")
print(f"   Interpretación: Por cada 100 tickets, {testing_ratio*100:.1f} son de testing")

# ============================================================================
# 2. ANÁLISIS DE ESTADOS Y VELOCIDAD DE ENTREGA
# ============================================================================
print("\n" + "=" * 100)
print("2. ESTADO DE COMPLETITUD Y VELOCIDAD DE ENTREGA")
print("=" * 100)

status_counts = df['Status'].value_counts()
print("\nDistribución por Estado:")
for status, count in status_counts.items():
    pct = (count / len(df)) * 100
    print(f"  • {status}: {count:,} ({pct:.1f}%)")

# Calcular tasa de completitud
done_issues = df[df['Status'] == 'Done'].shape[0]
completion_rate = (done_issues / len(df)) * 100
print(f"\n✓ TASA DE COMPLETITUD: {completion_rate:.1f}%")
print(f"   ({done_issues:,} de {len(df):,} tickets completados)")

# Issues pendientes
pending_statuses = ['To Do', 'In Development', 'In Progress', 'Ready for Testing', 'In Testing']
pending = df[df['Status'].isin(pending_statuses)].shape[0]
print(f"\n⏳ ISSUES PENDIENTES: {pending:,} ({(pending/len(df)*100):.1f}%)")

# ============================================================================
# 3. ANÁLISIS DE BUGS Y DEFECTOS
# ============================================================================
print("\n" + "=" * 100)
print("3. ANÁLISIS DE BUGS, DEFECTOS Y SEVERIDAD")
print("=" * 100)

bugs_total = bug_issues
print(f"\nTotal de BUGS: {bugs_total:,}")

# Proporción bugs respecto a development
if development_issues > 0:
    bug_ratio = bugs_total / development_issues
    print(f"RATIO BUG:DEVELOPMENT = {bug_ratio:.2f}")
    print(f"   Interpretación: Por cada feature de desarrollo, hay {bug_ratio:.2f} bugs")

# Estado de bugs
bug_df = df[df['Issue Type'] == 'Bug']
bug_status = bug_df['Status'].value_counts()
print(f"\nEstado de BUGS:")
for status, count in bug_status.items():
    pct = (count / bugs_total) * 100
    print(f"  • {status}: {count} ({pct:.1f}%)")

bugs_resolved = bug_df[bug_df['Status'] == 'Done'].shape[0]
bug_resolution_rate = (bugs_resolved / bugs_total * 100) if bugs_total > 0 else 0
print(f"\n✓ TASA DE RESOLUCIÓN DE BUGS: {bug_resolution_rate:.1f}%")
print(f"   ({bugs_resolved:,} de {bugs_total:,} bugs resueltos)")

# Análisis de severidad
print(f"\nPrioridad de BUGS:")
bug_priority = bug_df['Priority'].value_counts()
for priority, count in bug_priority.items():
    pct = (count / bugs_total) * 100
    print(f"  • {priority}: {count} ({pct:.1f}%)")

# ============================================================================
# 4. ANÁLISIS DE TEST COVERAGE Y TEST EXECUTION
# ============================================================================
print("\n" + "=" * 100)
print("4. TEST COVERAGE Y TEST EXECUTION")
print("=" * 100)

tests = df[df['Issue Type'] == 'Test']
test_executions = df[df['Issue Type'] == 'Test Execution']

print(f"\nTest Cases creados: {len(tests):,}")
print(f"Test Executions: {len(test_executions):,}")

if len(tests) > 0:
    test_exec_ratio = len(test_executions) / len(tests) if len(tests) > 0 else 0
    print(f"\n📊 EXECUTION COVERAGE: {test_exec_ratio:.2f}x")
    print(f"   (Ratio de execuciones respecto a test cases)")

# Estado de test executions
if len(test_executions) > 0:
    test_exec_status = test_executions['Status'].value_counts()
    print(f"\nEstado de TEST EXECUTIONS:")
    for status, count in test_exec_status.items():
        pct = (count / len(test_executions)) * 100
        print(f"  • {status}: {count} ({pct:.1f}%)")
    
    test_exec_done = test_executions[test_executions['Status'] == 'Done'].shape[0]
    test_exec_completion = (test_exec_done / len(test_executions)) * 100
    print(f"\n✓ TASA DE EJECUCIÓN COMPLETADA: {test_exec_completion:.1f}%")

# ============================================================================
# 5. ANÁLISIS DE RELACIONES Y DEPENDENCIAS
# ============================================================================
print("\n" + "=" * 100)
print("5. BLOQUEOS Y DEPENDENCIAS (RIESGO)")
print("=" * 100)

# Contar issue links (Blocks, Defect, Test, Clone)
blocks_inward = df['Inward issue link (Blocks)'].notna().sum()
blocks_outward = df['Outward issue link (Blocks)'].notna().sum()
total_blocks = blocks_inward + blocks_outward

defect_links = df['Inward issue link (Defect)'].notna().sum() + df['Outward issue link (Defect)'].notna().sum()
test_links = df[df.columns[df.columns.str.contains('Inward issue link \\(Test')]].notna().sum().sum()
test_links += df[df.columns[df.columns.str.contains('Outward issue link \\(Test')]].notna().sum().sum()

print(f"\n🔗 RELACIONES DE DEPENDENCIAS:")
print(f"  • Issues BLOQUEADOS (Blocks): {total_blocks}")
print(f"  • Links de DEFECTOS: {defect_links}")
print(f"  • Links de TESTS: {test_links}")

if total_blocks > 0:
    blocked_pct = (total_blocks / len(df)) * 100
    print(f"\n⚠️  {blocked_pct:.1f}% de tickets tienen bloqueos activos")
    print(f"   RIESGO: Esto impacta la velocidad de entrega")

# ============================================================================
# 6. ANÁLISIS TEMPORAL (Velocidad de Resolución)
# ============================================================================
print("\n" + "=" * 100)
print("6. VELOCIDAD DE RESOLUCIÓN (Eficiencia Operacional)")
print("=" * 100)

# Convertir fechas
df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
df['Resolved'] = pd.to_datetime(df['Resolved'], errors='coerce')

# Calcular tiempo de resolución
resolved_df = df[df['Resolved'].notna()].copy()
if len(resolved_df) > 0:
    resolved_df['Time_to_Resolve_Days'] = (resolved_df['Resolved'] - resolved_df['Created']).dt.days
    avg_resolution_time = resolved_df['Time_to_Resolve_Days'].mean()
    median_resolution_time = resolved_df['Time_to_Resolve_Days'].median()
    
    print(f"\n⏱️  TIEMPO PROMEDIO DE RESOLUCIÓN:")
    print(f"  • Promedio: {avg_resolution_time:.1f} días")
    print(f"  • Mediana: {median_resolution_time:.1f} días")
    print(f"  • Issues resueltos: {len(resolved_df):,} ({(len(resolved_df)/len(df)*100):.1f}%)")
    
    # Por tipo de issue
    print(f"\nTiempo de resolución por TIPO DE ISSUE:")
    for issue_type in ['Bug', 'Story', 'Task', 'Test Execution']:
        type_resolved = resolved_df[resolved_df['Issue Type'] == issue_type]
        if len(type_resolved) > 0:
            avg_time = type_resolved['Time_to_Resolve_Days'].mean()
            print(f"  • {issue_type}: {avg_time:.1f} días ({len(type_resolved)} tickets)")

# ============================================================================
# 7. ANÁLISIS DE ESTIMACIONES Y TRABAJO REAL
# ============================================================================
print("\n" + "=" * 100)
print("7. ESTIMACIONES VS. TRABAJO REAL (Precisión en Planificación)")
print("=" * 100)

# Columnas relevantes
estimate_col = 'Original estimate'
spent_col = 'Time Spent'

if estimate_col in df.columns and spent_col in df.columns:
    # Limpiar datos
    df['Original estimate'] = pd.to_numeric(df['Original estimate'], errors='coerce')
    df['Time Spent'] = pd.to_numeric(df['Time Spent'], errors='coerce')
    
    estimated = df[df['Original estimate'].notna()].shape[0]
    with_time_spent = df[df['Time Spent'].notna()].shape[0]
    
    print(f"\nTARGETING Y ESTIMACIONES:")
    print(f"  • Tickets con estimación: {estimated:,} ({(estimated/len(df)*100):.1f}%)")
    print(f"  • Tickets con tiempo registrado: {with_time_spent:,} ({(with_time_spent/len(df)*100):.1f}%)")
    
    # Calcular accuracy
    comparison_df = df[(df['Original estimate'].notna()) & (df['Time Spent'].notna())].copy()
    if len(comparison_df) > 0:
        comparison_df['Accuracy_Ratio'] = comparison_df['Time Spent'] / comparison_df['Original estimate']
        avg_accuracy = comparison_df['Accuracy_Ratio'].mean()
        print(f"\n📊 PRECISIÓN EN ESTIMACIONES:")
        print(f"  • Ratio Trabajo_Real:Estimado = {avg_accuracy:.2f}x")
        if avg_accuracy > 1.2:
            print(f"    ⚠️  RIESGO: Tareas se extienden {(avg_accuracy-1)*100:.0f}% más que lo estimado")
        elif avg_accuracy < 0.8:
            print(f"    ✓ Bueno: Tareas se completan {(1-avg_accuracy)*100:.0f}% más rápido que lo estimado")

# ============================================================================
# 8. ANÁLISIS DE EQUIPOS Y ASIGNACIÓN
# ============================================================================
print("\n" + "=" * 100)
print("8. DISTRIBUCIÓN DE CARGA POR EQUIPO/PERSONA")
print("=" * 100)

assignees = df['Assignee'].value_counts().head(10)
print(f"\nTop 10 personas asignadas a tickets:")
for assignee, count in assignees.items():
    if pd.notna(assignee):
        pct = (count / len(df)) * 100
        print(f"  • {assignee}: {count:,} ({pct:.1f}%)")

# ============================================================================
# 9. ANÁLISIS DE RESOLUCIONES
# ============================================================================
print("\n" + "=" * 100)
print("9. ANÁLISIS DE RESOLUCIONES")
print("=" * 100)

resolutions = df['Resolution'].value_counts()
print(f"\nResoluciones registradas:")
for resolution, count in resolutions.head(10).items():
    if pd.notna(resolution):
        pct = (count / len(df)) * 100
        print(f"  • {resolution}: {count:,} ({pct:.1f}%)")

# ============================================================================
# MÉTRICAS KPI RECOMENDADAS
# ============================================================================
print("\n" + "=" * 100)
print("MÉTRICAS KPI RECOMENDADAS PARA DIRECTOR DE TECNOLOGÍA")
print("=" * 100)

print("""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                        KPI #1: COBERTURA DE TESTING                               ║
╚════════════════════════════════════════════════════════════════════════════════════╝

📊 DEFINICIÓN:
   Porcentaje de features de desarrollo que tienen casos de prueba asociados

🔢 FÓRMULA:
   Test Coverage = (Test Cases Asociados / Total de Features de Desarrollo) × 100%

📈 VALOR ACTUAL:
   Test Cases: {test_count}
   Features: {feature_count}
   COBERTURA: {coverage:.1f}%

🎯 INSIGHT ESTRATÉGICO:
   • Indica qué porcentaje del código en desarrollo tiene cobertura de testing
   • Valores < 70%: Riesgo de defectos en producción
   • Valores > 90%: Excelente control de calidad

📋 RECOMENDACIONES:
   ✓ Establecer target mínimo de 85% de cobertura
   ✓ Revisar features sin tests asociados
   ✓ Implementar política "Definition of Done" = tests + code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

╔════════════════════════════════════════════════════════════════════════════════════╗
║                   KPI #2: TASA DE DEFECTOS (BUG DENSITY)                          ║
╚════════════════════════════════════════════════════════════════════════════════════╝

📊 DEFINICIÓN:
   Número de bugs reportados por cada unidad de trabajo completada

🔢 FÓRMULA:
   Bug Density = (Total Bugs / (Total Completed Stories + Total Completed Tasks)) × 100

📈 VALOR ACTUAL:
   Total Bugs: {total_bugs}
   Features Completadas: {completed_features}
   BUG DENSITY: {bug_density:.2f} bugs/feature

🎯 INSIGHT ESTRATÉGICO:
   • Refleja la calidad intrínseca del desarrollo
   • Bugs altos = necesidad de mejorar procesos de QA
   • Tendencia: Monitor mensual para identificar degradación

📋 RECOMENDACIONES:
   ✓ Establecer baseline y target máximo (ej: 0.15 bugs/feature)
   ✓ Implementar peer code reviews antes de merge
   ✓ Aumentar test automatizados si densidad > 0.25

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

╔════════════════════════════════════════════════════════════════════════════════════╗
║                  KPI #3: EFICIENCIA DE RESOLUCIÓN DE DEFECTOS                     ║
╚════════════════════════════════════════════════════════════════════════════════════╝

📊 DEFINICIÓN:
   Tiempo promedio para resolver bugs desde su reporte hasta resolución

🔢 FÓRMULA:
   Mean Time to Resolution (MTTR) = Suma(Fecha_Resolución - Fecha_Reporte) / Total_Bugs_Resueltos

📈 VALOR ACTUAL:
   MTTR Promedio: {mttr_avg:.1f} días
   MTTR Mediana: {mttr_median:.1f} días
   Bugs Resueltos: {bugs_resolved}/{total_bugs} ({resolution_pct:.1f}%)

🎯 INSIGHT ESTRATÉGICO:
   • Mide la agilidad del equipo QA en responder a defectos
   • MTTR < 3 días: Excelente
   • MTTR > 7 días: Requiere mejora (riesgo de acumulación)
   • Correlaciona con tasa de defectos: MTTR alto + bugs altos = problemas críticos

📋 RECOMENDACIONES:
   ✓ Establecer SLA máximo de 5 días para bugs críticos
   ✓ Priorizar bugs por severidad en sprint
   ✓ Investigar bugs con MTTR > 10 días

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

╔════════════════════════════════════════════════════════════════════════════════════╗
║              KPI #4: COMPLETITUD DE TEST EXECUTIONS (TESTING VELOCITY)            ║
╚════════════════════════════════════════════════════════════════════════════════════╝

📊 DEFINICIÓN:
   Porcentaje de test executions completadas vs. totales creadas

🔢 FÓRMULA:
   Testing Completion Rate = (Test Executions Done / Total Test Executions) × 100%

📈 VALOR ACTUAL:
   Test Executions Completadas: {test_exec_completed}
   Total Test Executions: {test_exec_total}
   TASA: {test_completion_rate:.1f}%

🎯 INSIGHT ESTRATÉGICO:
   • Indica si el ciclo de testing se completa dentro del sprint
   • Tasa < 80%: Testing puede ser cuello de botella
   • Tasa > 95%: Excelente ejecución y completitud

📋 RECOMENDACIONES:
   ✓ Target: Mínimo 90% de completitud antes de cierre de sprint
   ✓ Investigar causas de incompletitud (no son defectos, sino ejecución no finalizada)
   ✓ Aumentar recursos QA si tasa consistentemente < 85%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

╔════════════════════════════════════════════════════════════════════════════════════╗
║                    KPI #5: ÍNDICE DE BLOQUEOS (RISK INDEX)                        ║
╚════════════════════════════════════════════════════════════════════════════════════╝

📊 DEFINICIÓN:
   Porcentaje de tickets que tienen dependencias que los bloquean

🔢 FÓRMULA:
   Blocking Index = (Tickets con Issue Links de Bloqueo / Total Tickets) × 100%

📈 VALOR ACTUAL:
   Tickets Bloqueados: {blocked_count}
   Total Tickets: {total_tickets}
   ÍNDICE: {blocking_pct:.1f}%

🎯 INSIGHT ESTRATÉGICO:
   • Mide el nivel de interdependencias en el trabajo
   • Alto bloqueo (> 15%) = Planificación deficiente o arquitectura acoplada
   • Riesgo: Impacta directamente en velocidad de entrega
   • Debe monitorearse semanalmente para identificar cuellos de botella

📋 RECOMENDACIONES:
   ✓ Target: Mantener < 10% de tickets bloqueados
   ✓ Implementar daily standup enfocado en desbloqueos
   ✓ Refactorizar dependencias para reducir acoplamiento
   ✓ Asignar ownership claro para cada bloqueo

═══════════════════════════════════════════════════════════════════════════════════════
""".format(
    test_count=len(tests),
    feature_count=development_issues,
    coverage=(len(tests)/development_issues*100) if development_issues > 0 else 0,
    total_bugs=bugs_total,
    completed_features=df[(df['Issue Type'].isin(['Story', 'Task'])) & (df['Status'] == 'Done')].shape[0],
    bug_density=(bugs_total / max(1, df[(df['Issue Type'].isin(['Story', 'Task'])) & (df['Status'] == 'Done')].shape[0])),
    mttr_avg=avg_resolution_time if len(resolved_df) > 0 else 0,
    mttr_median=median_resolution_time if len(resolved_df) > 0 else 0,
    bugs_resolved=bugs_resolved,
    resolution_pct=bug_resolution_rate,
    test_exec_completed=test_exec_done if len(test_executions) > 0 else 0,
    test_exec_total=len(test_executions),
    test_completion_rate=test_exec_completion if len(test_executions) > 0 else 0,
    blocked_count=total_blocks,
    total_tickets=len(df),
    blocking_pct=(total_blocks/len(df)*100) if len(df) > 0 else 0
))

# ============================================================================
# RESUMEN EJECUTIVO Y RECOMENDACIONES
# ============================================================================
print("\n" + "=" * 100)
print("RESUMEN EJECUTIVO Y RECOMENDACIONES ESTRATÉGICAS")
print("=" * 100)

print("""
🔴 PRIORIDADES CRÍTICAS (Actuar inmediatamente):

1. DEFECTOS EN PRODUCCIÓN
   • Bug Density actual: MONITOREAR
   • Acción: Implementar "Bug Prevention" reviews antes de merge
   • Responsable: Jefe de Desarrollo
   • Timeline: Próximas 2 semanas

2. COBERTURA DE TESTING
   • Target: Alcanzar 85%+ de cobertura
   • Acción: Audit de features sin tests, crear plan de cobertura
   • Responsable: Lead de QA
   • Timeline: Próximo sprint

3. BLOQUEOS DE DEPENDENCIAS
   • Current: Monitorear tickets bloqueados
   • Acción: Daily standup enfocado en desbloqueos
   • Responsable: Scrum Master
   • Timeline: Semanal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟡 OPORTUNIDADES DE MEJORA (próximas 4 semanas):

1. VELOCIDAD DE CICLO
   • Implementar dashboards KPI en tiempo real
   • Monitorear tendencia de MTTR mes a mes
   • Establecer SLAs por tipo de issue

2. ESTIMACIONES Y PLANIFICACIÓN
   • Analizar accuracy ratio
   • Ajustar velocidad del team en base a datos históricos
   • Implementar "estimation poker" con baseline histórico

3. CAPACIDAD DE QA
   • Evaluar si testing completion rate < 90% es por:
     - Falta de recursos
     - Procesos ineficientes
     - Casos de test complejos
   • Propuesta: Automatización de tests repetitivos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 ACCIONES RECOMENDADAS (Plan de Implementación):

SEMANA 1-2:
□ Establecer baseline para los 5 KPIs
□ Crear dashboard de monitoring en Jira/Grafana
□ Comunicar targets y SLAs al equipo
□ Establecer reuniones de revisión semanal (viernes 2pm)

SEMANA 3-4:
□ Implementar alertas automáticas cuando KPIs salen de rango
□ Crear reportes automatizados (diarios/semanales)
□ Sesión de capacitación: "Definition of Done" actualizada
□ Revisar procesos de code review y QA

SEMANA 5+:
□ Análisis de tendencias de KPIs
□ Identificar patrones (ej: ciertos features = más bugs)
□ Ajuste de procesos basado en datos
□ Escalada de riesgos identificados

═══════════════════════════════════════════════════════════════════════════════════════
""")

# Exportar datos a CSV para análisis posterior
print("\nExportando datos para análisis posterior...")

# Resumen general
summary_data = {
    'Métrica': [
        'Total de Tickets',
        'Tasa de Completitud (%)',
        'Tickets en Testing',
        'Total de Bugs',
        'Tasa Resolución Bugs (%)',
        'Test Cases',
        'Test Executions',
        'Tickets Bloqueados',
        'MTTR Promedio (días)',
        'MTTR Mediana (días)'
    ],
    'Valor': [
        len(df),
        f"{completion_rate:.1f}",
        f"{testing_issues}",
        f"{bugs_total}",
        f"{bug_resolution_rate:.1f}",
        len(tests),
        len(test_executions),
        f"{total_blocks}",
        f"{avg_resolution_time:.1f}" if len(resolved_df) > 0 else "N/A",
        f"{median_resolution_time:.1f}" if len(resolved_df) > 0 else "N/A"
    ]
}

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('KPI_Summary.csv', index=False)
print("✓ KPI_Summary.csv creado exitosamente")

# Exportar issues por estado
status_summary = df['Status'].value_counts().reset_index()
status_summary.columns = ['Estado', 'Cantidad']
status_summary.to_csv('Status_Distribution.csv', index=False)
print("✓ Status_Distribution.csv creado exitosamente")

# Exportar bugs abiertos
open_bugs = df[(df['Issue Type'] == 'Bug') & (df['Status'] != 'Done')][
    ['Issue key', 'Summary', 'Status', 'Priority', 'Assignee', 'Created']
].copy()
open_bugs.to_csv('Open_Bugs_Report.csv', index=False)
print("✓ Open_Bugs_Report.csv creado exitosamente")

print("\n" + "=" * 100)
print("ANÁLISIS COMPLETADO")
print("=" * 100)
