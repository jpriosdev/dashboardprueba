import pandas as pd
import numpy as np
from datetime import datetime

df = pd.read_csv('JIRA LTI.csv')

# Conversión de fechas
for col in ['Created', 'Updated', 'Status Category Changed']:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# ============================================================================
# ANÁLISIS 1: VELOCITY POR SPRINT
# ============================================================================
print("="*90)
print("📈 ANÁLISIS 1: VELOCITY POR SPRINT (Issues completadas por sprint)")
print("="*90)

sprints_df = df[df['Sprint'].notna()].copy()
sprints_df['is_done'] = sprints_df['Status'].str.lower() == 'done'

sprint_velocity = sprints_df.groupby('Sprint').agg({
    'Issue key': 'count',  # Total issues en sprint
    'is_done': 'sum'  # Issues completadas
}).rename(columns={'Issue key': 'total', 'is_done': 'completed'})

sprint_velocity['velocity_%'] = (sprint_velocity['completed'] / sprint_velocity['total'] * 100).round(1)
sprint_velocity = sprint_velocity.sort_values('completed', ascending=False)

print(f"\nTop 5 sprints por productividad:")
for idx, (sprint, row) in enumerate(sprint_velocity.head().iterrows(), 1):
    print(f"  {idx}. {sprint:30} | Completadas: {row['completed']:3.0f}/{row['total']:3.0f} ({row['velocity_%']:5.1f}%)")

# ============================================================================
# ANÁLISIS 2: CYCLE TIME POR ESTADO
# ============================================================================
print("\n" + "="*90)
print("⏱️  ANÁLISIS 2: TIEMPO PROMEDIO EN CADA ESTADO")
print("="*90)

# Status transitions (simplificado)
status_counts = df['Status'].value_counts().sort_values(ascending=False)
print("\nDistribución actual por estado:")
for status, count in status_counts.items():
    pct = count/len(df)*100
    print(f"  {status:30} | {count:4.0f} issues ({pct:5.1f}%)")

# ============================================================================
# ANÁLISIS 3: WIP ANALYSIS
# ============================================================================
print("\n" + "="*90)
print("🔄 ANÁLISIS 3: WIP (Work In Progress)")
print("="*90)

in_progress_statuses = ['In Development', 'In Testing', 'Ready for Testing']
wip = df[df['Status'].isin(in_progress_statuses)]

print(f"\nTotal WIP actual: {len(wip)} issues ({len(wip)/len(df)*100:.1f}% del total)")
print("\nDesglose por estado:")
for status in in_progress_statuses:
    count = len(df[df['Status'] == status])
    print(f"  {status:30} | {count:4.0f} issues")

print(f"\nWIP promedio por assignee:")
wip_per_assignee = wip['Assignee'].value_counts().head(10)
for assignee, count in wip_per_assignee.items():
    print(f"  {assignee:30} | {count:3.0f} issues en progreso")

# ============================================================================
# ANÁLISIS 4: REPORTER ANALYSIS (Quién reporta problemas)
# ============================================================================
print("\n" + "="*90)
print("👥 ANÁLISIS 4: REPORTES POR USUARIO (Calidad de reportes)")
print("="*90)

reporter_stats = df.groupby('Reporter').agg({
    'Issue key': 'count',
    'Issue Type': lambda x: (x == 'Bug').sum(),
    'Status': lambda x: (x == 'Done').sum()
}).rename(columns={
    'Issue key': 'total_reportes',
    'Issue Type': 'bugs_reportados',
    'Status': 'resueltos'
})

reporter_stats['resolution_%'] = (reporter_stats['resueltos'] / reporter_stats['total_reportes'] * 100).round(1)
reporter_stats = reporter_stats.sort_values('total_reportes', ascending=False)

print("\nTop 10 reporters:")
for idx, (reporter, row) in enumerate(reporter_stats.head(10).iterrows(), 1):
    print(f"  {idx:2}. {str(reporter)[:30]:30} | Reportes: {row['total_reportes']:4.0f} | Bugs: {row['bugs_reportados']:3.0f} | Resueltos: {row['resolution_%']:5.1f}%")

# ============================================================================
# ANÁLISIS 5: ISSUE TYPE DISTRIBUTION & TRENDS
# ============================================================================
print("\n" + "="*90)
print("📋 ANÁLISIS 5: DISTRIBUCIÓN POR TIPO DE ISSUE (Tendencias)")
print("="*90)

issue_type_stats = df.groupby('Issue Type').agg({
    'Issue key': 'count',
    'Status': lambda x: (x == 'Done').sum(),
}).rename(columns={'Issue key': 'total', 'Status': 'done'})

issue_type_stats['completion_%'] = (issue_type_stats['done'] / issue_type_stats['total'] * 100).round(1)
issue_type_stats = issue_type_stats.sort_values('total', ascending=False)

print("\nPor tipo de issue:")
for issue_type, row in issue_type_stats.iterrows():
    print(f"  {issue_type:20} | Total: {row['total']:4.0f} | Completadas: {row['done']:4.0f} ({row['completion_%']:5.1f}%)")

# ============================================================================
# ANÁLISIS 6: ISSUES MUY ANTIGUAS (AGING BACKLOG)
# ============================================================================
print("\n" + "="*90)
print("🚨 ANÁLISIS 6: BACKLOG CRÍTICO (Issues muy antiguas)")
print("="*90)

now = datetime.now()
df['age_days'] = (now - df['Created']).dt.days

backlog = df[df['Status'].isin(['To Do', 'In Development', 'In Testing', 'Ready for Testing'])]
backlog_old = backlog[backlog['age_days'] > 180].sort_values('age_days', ascending=False)

print(f"\n⚠️  Issues en To Do con >6 meses: {len(backlog_old)}")
if len(backlog_old) > 0:
    print("\nTop 10 issues más antiguas sin completar:")
    for idx, (_, row) in enumerate(backlog_old.head(10).iterrows(), 1):
        print(f"  {idx:2}. {row['Issue key']:12} | Edad: {row['age_days']:3.0f} días | {row['Summary'][:50]}")

# ============================================================================
# ANÁLISIS 7: RESOLVER RATE TRENDS
# ============================================================================
print("\n" + "="*90)
print("📊 ANÁLISIS 7: TASA DE RESOLUCIÓN (Productividad)")
print("="*90)

df['created_week'] = df['Created'].dt.to_period('W')
weekly_creation = df['created_week'].value_counts().sort_index()
print(f"\nPromedio issues creadas por semana: {weekly_creation.mean():.1f}")
print(f"Máximo en una semana: {weekly_creation.max():.0f}")
print(f"Mínimo en una semana: {weekly_creation.min():.0f}")

# ============================================================================
# ANÁLISIS 8: LABELS/TAGS QUE MÁS APARECEN
# ============================================================================
print("\n" + "="*90)
print("🏷️  ANÁLISIS 8: LABELS/TAGS (Categorización)")
print("="*90)

if 'Labels' in df.columns:
    labels_all = []
    for labels_str in df['Labels'].dropna():
        if isinstance(labels_str, str):
            labels_all.extend([l.strip() for l in str(labels_str).split(';')])
    
    from collections import Counter
    label_counts = Counter(labels_all)
    print(f"\nTop 15 labels más usados:")
    for idx, (label, count) in enumerate(label_counts.most_common(15), 1):
        print(f"  {idx:2}. {label:30} | {count:4.0f} issues")

# ============================================================================
# ANÁLISIS 9: PREDICTABILITY (Varianza en sprints)
# ============================================================================
print("\n" + "="*90)
print("🎯 ANÁLISIS 9: PREDICTIBILIDAD DE SPRINTS")
print("="*90)

sprint_completion = sprint_velocity['velocity_%'].dropna()
print(f"\nVariabilidad en velocidad de sprints:")
print(f"  Promedio: {sprint_completion.mean():.1f}%")
print(f"  Desviación estándar: {sprint_completion.std():.1f}%")
print(f"  Mínimo: {sprint_completion.min():.1f}%")
print(f"  Máximo: {sprint_completion.max():.1f}%")
print(f"  Coef. Variación: {(sprint_completion.std()/sprint_completion.mean()*100):.1f}%")

if (sprint_completion.std()/sprint_completion.mean()*100) > 30:
    print(f"  ⚠️  Baja predictibilidad (varianza > 30%)")
else:
    print(f"  ✓ Buena predictibilidad")

# ============================================================================
# ANÁLISIS 10: CUSTOM FIELD DATA
# ============================================================================
print("\n" + "="*90)
print("🔧 ANÁLISIS 10: DATOS CUSTOMIZADOS (Status Category)")
print("="*90)

status_cat = df['Status Category'].value_counts()
print("\nCategorías de estado:")
for cat, count in status_cat.items():
    print(f"  {cat:30} | {count:4.0f} issues ({count/len(df)*100:5.1f}%)")

print("\n" + "="*90)
print("✅ ANÁLISIS COMPLETO")
print("="*90)
