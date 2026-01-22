import pandas as pd
import numpy as np

df = pd.read_csv('JIRA LTI.csv')

print('='*90)
print('ANÁLISIS DE COLUMNAS Y OPORTUNIDADES DE MÉTRICAS')
print('='*90)

print(f'\n📊 DATASET: {len(df)} issues × {len(df.columns)} columnas')
print(f'📅 Período: {df["Created"].min()} → {df["Created"].max()}')

print('\n' + '='*90)
print('COLUMNAS CLAVE CON DATOS ÚTILES:')
print('='*90)

# Mostrar columnas por completitud
cols_info = []
for col in df.columns:
    completud = (1 - df[col].isna().sum() / len(df)) * 100
    dtype = str(df[col].dtype)
    unique = df[col].nunique()
    cols_info.append((col, completud, dtype, unique))

# Filtrar columnas con al menos 50% completud
cols_info = sorted([x for x in cols_info if x[1] >= 50], key=lambda x: x[1], reverse=True)

for i, (col, completud, dtype, unique) in enumerate(cols_info[:30], 1):
    print(f'{i:2}. {col:40} | Completud: {completud:5.1f}% | Tipo: {dtype:15} | Únicos: {unique}')

print('\n' + '='*90)
print('NUEVAS MÉTRICAS QUE PODEMOS CALCULAR:')
print('='*90)

# Analizar si hay datos de estimación
has_estimate = 'Story Points' in df.columns or 'Estimate' in df.columns or 'Time Estimate' in df.columns
print(f'✓ Story Points/Estimación disponible: {has_estimate}')

# Analizar si hay datos de Sprints
sprints = df['Sprint'].dropna().unique()
print(f'✓ Sprints disponibles: {len(sprints)} sprints únicos')

# Analizar si hay Labels/Tags
has_labels = 'Labels' in df.columns
print(f'✓ Labels/Tags disponible: {has_labels}')

# Componentes
has_components = 'Components' in df.columns
print(f'✓ Componentes disponible: {has_components}')

print('\n' + '='*90)
print('PREGUNTAS QUE PODEMOS RESPONDER:')
print('='*90)

preguntas = [
    '1. ¿Cuál es la velocidad (velocity) del equipo por sprint?',
    '2. ¿Cuáles son los cuellos de botella (estados donde más se quedan)?',
    '3. ¿Cuál es el tiempo de ciclo (cycle time) en cada fase?',
    '4. ¿Cuál es el WIP (Work In Progress) óptimo?',
    '5. ¿Cuál es la predictibilidad de entregas (desviación)?',
    '6. ¿Qué sprint tuvo mejor rendimiento?',
    '7. ¿Hay tendencia de mejora en el tiempo de resolución?',
    '8. ¿Cuál es la distribución de trabajo por component?',
    '9. ¿Cuál es la tasa de bugs por tipo de componente?',
    '10. ¿Hay issues que requieren escalación (muy antiguas)?',
]

for q in preguntas:
    print(f'  {q}')

print('\n' + '='*90)
print('MÉTRICAS AVANZADAS RECOMENDADAS:')
print('='*90)

metricas = {
    'Velocity por Sprint': 'Issues completadas / sprint (valor vs capacidad)',
    'Burndown': 'Gráfico de trabajo restante vs tiempo por sprint',
    'Flow Efficiency': 'Tiempo activo / tiempo total en proceso',
    'Cycle Time': 'Tiempo promedio en cada estado (To Do → In Dev → Testing → Done)',
    'Lead Time vs Cycle Time': 'Comparación para ver setup/esperas',
    'WIP Trend': 'Evolución de trabajo en progreso',
    'Bug Escape Rate': 'Bugs en testing vs en producción',
    'Resolution Rate': 'Porcentaje issues resueltas por semana/mes',
    'MTTR (Mean Time To Repair)': 'Tiempo promedio para resolver bugs',
    'Assignment Balance': 'Carga de trabajo balanceada entre equipo',
    'Component Quality': 'Defect density por componente',
    'Sprint Predictability': 'Varianza en completitud de sprints',
    'Aging Backlog Analysis': 'Issues antiguas en To Do por rango de edad',
    'Time to First Response': 'Cuánto tarda en moverse un issue del estado inicial',
}

for i, (metrica, desc) in enumerate(metricas.items(), 1):
    print(f'{i:2}. {metrica:30} - {desc}')
