"""
Análisis avanzado de JIRA LTI.csv como experto en analítica de datos.
Genera insights, métricas y un dashboard interactivo HTML.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from datetime import timedelta, datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. CARGA Y EXPLORACIÓN
# ============================================================================
CSV_PATH = "JIRA LTI.csv"
OUTPUT_HTML = "dashboard_analytics.html"
LOGO_URL = "assets/logo.svg"

print("=" * 80)
print("ANÁLISIS AVANZADO - JIRA LTI")
print("=" * 80)

df = pd.read_csv(CSV_PATH, low_memory=False)
df.columns = [c.strip() for c in df.columns]

print(f"\n📊 Dataset: {df.shape[0]} filas × {df.shape[1]} columnas")
print(f"📅 Período de datos: {df['Created'].min()} a {df['Created'].max()}")

# ============================================================================
# 2. PREPARACIÓN Y CÁLCULO DE FEATURES
# ============================================================================
for col in ["Created", "Resolved", "Updated", "Due date"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

if 'Issue Type' in df.columns:
    df['Issue Type'] = df['Issue Type'].astype(str)
if 'Status' in df.columns:
    df['Status'] = df['Status'].astype(str)
if 'Assignee' in df.columns:
    df['Assignee'] = df['Assignee'].fillna('Unassigned')
if 'Priority' in df.columns:
    df['Priority'] = df['Priority'].astype(str)

# Features derivadas
# Si Resolved está vacío, usar Status='Done' como proxy
if 'Status' in df.columns:
    df['is_done'] = df['Status'].str.lower() == 'done'
    # Usar Updated cuando está Done, sino usar Created
    df['resolved_date'] = df.apply(
        lambda row: row['Updated'] if row['is_done'] and pd.notna(row['Updated']) else None,
        axis=1
    )
else:
    df['is_done'] = False
    df['resolved_date'] = df['Resolved']

df['lead_time_days'] = (df['resolved_date'] - df['Created']).dt.total_seconds() / 86400
df['is_resolved'] = df['resolved_date'].notna().astype(int)
df['age_days'] = (datetime.now() - df['Created']).dt.total_seconds() / 86400
df['resolution_lag'] = (df['resolved_date'] - df['Created']).dt.days

# Sprint: extraer número
if 'Sprint' in df.columns:
    df['sprint_num'] = df['Sprint'].astype(str).str.extract(r'(\d+)').astype(float)
    df['sprint_short'] = df['Sprint'].astype(str).str.extract(r'(Sprint\s*\d+)')

# ============================================================================
# 3. CÁLCULO DE MÉTRICAS CLAVE (ANÁLISIS)
# ============================================================================
resolved = df[df['is_resolved'] == 1].copy()
unresolved = df[df['is_resolved'] == 0].copy()

print(f"\n✅ Done/Resolved: {len(resolved)} ({100*len(resolved)/len(df):.1f}%)")
print(f"❌ In Progress/Open: {len(unresolved)} ({100*len(unresolved)/len(df):.1f}%)")

# Lead Time
lead_time_median = resolved['lead_time_days'].median() if len(resolved) > 0 else np.nan
lead_time_mean = resolved['lead_time_days'].mean() if len(resolved) > 0 else np.nan
lead_time_p95 = resolved['lead_time_days'].quantile(0.95) if len(resolved) > 0 else np.nan
print(f"\n⏱️  Lead Time (días) - Issues Completadas:")
print(f"   Mediana: {lead_time_median:.1f}")
print(f"   Media: {lead_time_mean:.1f}")
print(f"   P95: {lead_time_p95:.1f}")

# Throughput semanal
if len(resolved) > 0:
    resolved['week'] = resolved['resolved_date'].dt.to_period('W')
    throughput_week = resolved.groupby('week').size().reset_index(name='count')
    throughput_week['week'] = throughput_week['week'].astype(str)
    weekly_avg = throughput_week['count'].mean()
    print(f"\n🚀 Throughput semanal promedio: {weekly_avg:.1f} issues/semana")
else:
    throughput_week = pd.DataFrame()
    weekly_avg = 0

# Distribuciones
print(f"\n📋 Distribución por Issue Type:")
issue_dist = df['Issue Type'].value_counts()
for itype, count in issue_dist.head(5).items():
    print(f"   {itype}: {count} ({100*count/len(df):.1f}%)")

print(f"\n📌 Distribución por Status:")
status_dist = df['Status'].value_counts()
for status, count in status_dist.head(5).items():
    print(f"   {status}: {count} ({100*count/len(df):.1f}%)")

# Defects
bug_mask = df['Issue Type'].str.lower() == 'bug'
story_mask = df['Issue Type'].str.lower() == 'story'
bug_count = bug_mask.sum()
story_count = story_mask.sum()
defect_density = bug_count / story_count if story_count > 0 else 0
print(f"\n🐛 Bugs: {bug_count} | Stories: {story_count} | Defect Density: {defect_density:.3f}")

# Backlog age
backlog = df[df['Status'].str.lower() == 'to do'].copy()
if len(backlog) > 0:
    backlog_age_median = backlog['age_days'].median()
    backlog_age_max = backlog['age_days'].max()
    print(f"\n📦 Backlog Age (días):")
    print(f"   Mediana: {backlog_age_median:.1f}")
    print(f"   Máximo: {backlog_age_max:.1f}")

# Assignee analysis
assignee_counts = df[df['Assignee'] != 'Unassigned']['Assignee'].value_counts()
print(f"\n👤 Top 3 Assignees:")
for name, count in assignee_counts.head(3).items():
    print(f"   {name}: {count} issues")

# Priority
print(f"\n⚠️  Prioridad:")
priority_dist = df['Priority'].value_counts()
for prio, count in priority_dist.head(5).items():
    print(f"   {prio}: {count} ({100*count/len(df):.1f}%)")

# ============================================================================
# 4. GENERACIÓN DE GRÁFICOS
# ============================================================================
print("\n🎨 Generando gráficos...")

# Gráfico 1: Throughput semanal
fig_throughput = px.line(
    throughput_week, 
    x='week', 
    y='count', 
    title='Throughput semanal (Issues resueltas)',
    markers=True
)
fig_throughput.update_layout(hovermode='x unified', height=300, margin=dict(t=40, l=40, r=40, b=40))

# Gráfico 2: Distribución Lead Time
fig_lead_dist = px.histogram(
    resolved['lead_time_days'].dropna(), 
    nbins=40, 
    title='Distribución de Lead Time (días)'
)
fig_lead_dist.update_layout(height=300, margin=dict(t=40, l=40, r=40, b=40))

# Gráfico 3: Lead time por tipo de issue
lead_by_type = resolved.groupby('Issue Type')['lead_time_days'].agg(['median', 'count']).reset_index()
lead_by_type = lead_by_type[lead_by_type['count'] > 2].sort_values('median', ascending=True)
fig_lead_type = px.bar(
    lead_by_type, 
    x='median', 
    y='Issue Type', 
    orientation='h',
    title='Lead Time Mediano por Tipo de Issue'
)
fig_lead_type.update_layout(height=300, margin=dict(t=40, l=100, r=40, b=40))

# Gráfico 4: Estado de issues
status_counts = df['Status'].value_counts().reset_index()
status_counts.columns = ['Status', 'count']
fig_status = px.pie(
    status_counts, 
    names='Status', 
    values='count', 
    title='Distribución por Estado'
)
fig_status.update_layout(height=400, margin=dict(t=40, l=40, r=40, b=40))

# Gráfico 5: Prioridad
priority_counts = df['Priority'].value_counts().reset_index()
priority_counts.columns = ['Priority', 'count']
fig_priority = px.bar(
    priority_counts, 
    x='Priority', 
    y='count', 
    title='Issues por Prioridad',
    color='count',
    color_continuous_scale='Reds'
)
fig_priority.update_layout(height=300, margin=dict(t=40, l=40, r=40, b=40), showlegend=False)

# Gráfico 6: Top assignees
top_assignees = df[df['Assignee'] != 'Unassigned']['Assignee'].value_counts().head(10)
fig_assignees = px.bar(
    x=top_assignees.values, 
    y=top_assignees.index, 
    orientation='h',
    title='Top 10 Assignees'
)
fig_assignees.update_layout(height=350, margin=dict(t=40, l=150, r=40, b=40))

# Gráfico 7: Tipo de issue
type_counts = df['Issue Type'].value_counts().reset_index()
type_counts.columns = ['Issue Type', 'count']
fig_types = px.pie(
    type_counts,
    names='Issue Type',
    values='count',
    title='Distribución por Tipo de Issue'
)
fig_types.update_layout(height=400, margin=dict(t=40, l=40, r=40, b=40))

# Gráfico 8: Resolved vs Unresolved
resolved_status = pd.DataFrame({
    'Status': ['Resueltos', 'No resueltos'],
    'count': [len(resolved), len(unresolved)]
})
fig_resolved = px.bar(
    resolved_status,
    x='Status',
    y='count',
    color='Status',
    color_discrete_map={'Resueltos': '#10b981', 'No resueltos': '#ef4444'},
    title='Resueltos vs No Resueltos'
)
fig_resolved.update_layout(height=300, margin=dict(t=40, l=40, r=40, b=40), showlegend=False)

# Gráfico 9: Backlog aging (edad de issues To Do)
if len(backlog) > 0:
    backlog_sorted = backlog.nlargest(15, 'age_days')[['Summary', 'age_days']].reset_index(drop=True)
    backlog_sorted['Summary'] = backlog_sorted['Summary'].str[:40]
    fig_backlog = px.bar(
        backlog_sorted,
        x='age_days',
        y='Summary',
        orientation='h',
        title='Top 15 Issues más antiguas en Backlog'
    )
    fig_backlog.update_layout(height=400, margin=dict(t=40, l=300, r=40, b=40))
else:
    fig_backlog = go.Figure()

# Gráfico 10: Bugs por tipo (si existen)
bugs = df[bug_mask]
if len(bugs) > 0:
    fig_bugs = px.pie(
        bugs['Issue Type'].value_counts().reset_index(),
        names='Issue Type',
        values='count',
        title=f'Bugs por Tipo (Total: {len(bugs)})'
    )
    fig_bugs.update_layout(height=350, margin=dict(t=40, l=40, r=40, b=40))
else:
    fig_bugs = go.Figure()

# Gráfico 11: Lead time percentiles (box plot)
fig_lead_box = go.Figure()
fig_lead_box.add_trace(go.Box(y=resolved['lead_time_days'].dropna(), name='Lead Time (días)'))
fig_lead_box.update_layout(title='Box Plot: Lead Time', height=300, margin=dict(t=40, l=40, r=40, b=40))

# Gráfico 12: Resolución por mes
if len(resolved) > 0:
    resolved['month'] = resolved['resolved_date'].dt.to_period('M')
    resolution_month = resolved.groupby('month').size().reset_index(name='count')
    resolution_month['month'] = resolution_month['month'].astype(str)
    fig_resolution_month = px.bar(
        resolution_month,
        x='month',
        y='count',
        title='Issues Resueltas por Mes'
    )
    fig_resolution_month.update_layout(height=300, margin=dict(t=40, l=40, r=40, b=40))
else:
    fig_resolution_month = go.Figure()

print("✅ Gráficos generados.")

# ============================================================================
# 5. GENERACIÓN DE HTML INTERACTIVO
# ============================================================================
print("📄 Generando HTML...")

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Analítico - JIRA LTI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {{
            --primary: #0f172a;
            --secondary: #0b1220;
            --accent: #00b5c9;
            --success: #10b981;
            --danger: #ef4444;
            --muted: #94a3b8;
            --white: #f8fafc;
        }}
        
        body {{
            background: linear-gradient(135deg, #071127 0%, #0f1724 50%, #f7f9fb 100%);
            color: var(--white);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }}
        
        .navbar {{
            background: rgba(15, 23, 42, 0.95) !important;
            border-bottom: 2px solid var(--accent);
            box-shadow: 0 4px 6px rgba(0, 181, 201, 0.1);
        }}
        
        .navbar-brand {{
            font-weight: 700;
            font-size: 1.2rem;
            color: var(--accent) !important;
        }}
        
        .container-main {{
            padding: 30px 15px;
        }}
        
        .card {{
            background: linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%);
            border: 1px solid rgba(0, 181, 201, 0.2);
            border-radius: 12px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            border-color: var(--accent);
            box-shadow: 0 8px 25px rgba(0, 181, 201, 0.15);
        }}
        
        .kpi-card {{
            padding: 24px;
            border: none;
            text-align: center;
        }}
        
        .kpi-card h6 {{
            color: var(--muted);
            font-size: 0.9rem;
            font-weight: 600;
            margin: 0 0 8px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .kpi-card h2 {{
            color: var(--white);
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            line-height: 1;
        }}
        
        .kpi-card .metric-unit {{
            color: var(--accent);
            font-size: 0.85rem;
            margin-top: 4px;
        }}
        
        .nav-tabs {{
            border: none;
            gap: 5px;
        }}
        
        .nav-tabs .nav-link {{
            color: var(--muted);
            border: none;
            background: rgba(0, 181, 201, 0.05);
            border-radius: 8px 8px 0 0;
            transition: all 0.3s ease;
            padding: 12px 20px;
        }}
        
        .nav-tabs .nav-link:hover {{
            color: var(--accent);
            background: rgba(0, 181, 201, 0.1);
        }}
        
        .nav-tabs .nav-link.active {{
            color: var(--white);
            background: rgba(0, 181, 201, 0.15);
            border-bottom: 3px solid var(--accent);
        }}
        
        .section-title {{
            color: var(--white);
            font-weight: 700;
            margin: 30px 0 20px 0;
            font-size: 1.3rem;
            border-left: 4px solid var(--accent);
            padding-left: 12px;
        }}
        
        .insight-box {{
            background: rgba(16, 185, 129, 0.1);
            border-left: 4px solid #10b981;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 16px;
            color: #d1fae5;
        }}
        
        .insight-box.warning {{
            background: rgba(239, 68, 68, 0.1);
            border-left-color: #ef4444;
            color: #fee2e2;
        }}
        
        .insight-box.info {{
            background: rgba(0, 181, 201, 0.1);
            border-left-color: #00b5c9;
            color: #cffafe;
        }}
        
        .chart-container {{
            background: rgba(11, 18, 32, 0.5);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(0, 181, 201, 0.1);
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }}
        
        .metric-badge {{
            background: linear-gradient(135deg, #00b5c9 0%, #006b7f 100%);
            color: white;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <!-- NAVBAR -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <span class="navbar-brand">
                <img src="{LOGO_URL}" alt="logo" style="height:32px;margin-right:10px" onerror="this.style.display='none'">
                LTI Analytics Dashboard
            </span>
            <div>
                <a href="dashboard.html" class="btn btn-sm btn-outline-info">📋 Dashboard Simple ←</a>
                <a href="dashboard_metrics_advanced.html" class="btn btn-sm btn-outline-info" style="margin-left:8px">📈 Métricas</a>
            </div>
        </div>
    </nav>
    
    <!-- MAIN CONTENT -->
    <div class="container-main">
        <div class="container-fluid">
            
            <!-- HEADER -->
            <div style="margin-bottom: 40px;">
                <h1 style="color: var(--white); font-weight: 700; margin-bottom: 8px;">Panel de Analítica - JIRA LTI</h1>
                <p style="color: var(--muted);">Análisis integral de métrica s de proyecto, rendimiento de equipo y gestión de calidad</p>
            </div>
            
            <!-- RESUMEN EJECUTIVO -->
            <div class="stat-grid">
                <div class="card kpi-card">
                    <h6>Total de Issues</h6>
                    <h2>{len(df)}</h2>
                </div>
                <div class="card kpi-card">
                    <h6>Resueltos</h6>
                    <h2>{len(resolved)}</h2>
                    <div class="metric-unit">{100*len(resolved)/len(df):.0f}% del total</div>
                </div>
                <div class="card kpi-card">
                    <h6>Lead Time Mediano</h6>
                    <h2>{lead_time_median:.1f}</h2>
                    <div class="metric-unit">días</div>
                </div>
                <div class="card kpi-card">
                    <h6>Bugs Reportados</h6>
                    <h2>{bug_count}</h2>
                    <div class="metric-unit">Densidad: {defect_density:.3f}</div>
                </div>
                <div class="card kpi-card">
                    <h6>Throughput Promedio</h6>
                    <h2>{weekly_avg:.1f}</h2>
                    <div class="metric-unit">issues/semana</div>
                </div>
                <div class="card kpi-card">
                    <h6>Backlog Size</h6>
                    <h2>{len(backlog)}</h2>
                    <div class="metric-unit">En "To Do"</div>
                </div>
            </div>
            
            <!-- INSIGHTS CLAVE -->
            <h3 class="section-title">🔍 Insights Clave</h3>
            <div class="insight-box">
                <strong>📊 Velocidad de Resolución:</strong> Con un lead time mediano de {lead_time_median:.1f} días, el equipo resuelve issues en ~{lead_time_median/7:.1f} semanas en promedio. Esto indica {('buena' if lead_time_median < 14 else 'moderada' if lead_time_median < 30 else 'lenta')} velocidad de entrega.
            </div>
            <div class="insight-box">
                <strong>🚀 Productividad:</strong> El equipo completa ~{weekly_avg:.1f} issues/semana. A este ritmo, se resuelven {len(resolved):.0f} issues mensualmente.
            </div>
            <div class="insight-box info">
                <strong>🎯 Calidad:</strong> Se ha reportado 1 bug por cada {1/defect_density:.1f} stories (densidad: {defect_density:.2%}). {('Excelente' if defect_density < 0.05 else 'Buena' if defect_density < 0.15 else 'Requiere atención')} para el tipo de proyecto.
            </div>
            <div class="insight-box warning" style="display: {'block' if len(backlog) > len(df)*0.2 else 'none'}">
                <strong>⚠️ Backlog Aging:</strong> El backlog tiene {len(backlog)} issues ({100*len(backlog)/len(df):.0f}%), con un máximo de {backlog_age_max:.0f} días. Se recomienda priorización o descomposición.
            </div>
            
            <!-- TABS PRINCIPALES -->
            <ul class="nav nav-tabs" style="margin-top: 30px;" id="mainTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview" type="button">📈 Overview</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="delivery-tab" data-bs-toggle="tab" data-bs-target="#delivery" type="button">🚚 Entrega</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="quality-tab" data-bs-toggle="tab" data-bs-target="#quality" type="button">✅ Calidad</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="team-tab" data-bs-toggle="tab" data-bs-target="#team" type="button">👥 Equipo</button>
                </li>
            </ul>
            
            <div class="tab-content" id="mainTabContent">
                
                <!-- TAB: OVERVIEW -->
                <div class="tab-pane fade show active" id="overview" role="tabpanel">
                    <div style="margin-top: 20px;">
                        <h4 class="section-title">Estado General del Proyecto</h4>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="chart-container">
                                    {pio.to_html(fig_resolved, include_plotlyjs='cdn' if True else False, full_html=False)}
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="chart-container">
                                    {pio.to_html(fig_status, include_plotlyjs=False, full_html=False)}
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="chart-container">
                                    {pio.to_html(fig_types, include_plotlyjs=False, full_html=False)}
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="chart-container">
                                    {pio.to_html(fig_priority, include_plotlyjs=False, full_html=False)}
                                </div>
                            </div>
                        </div>
                        
                        <h4 class="section-title" style="margin-top: 40px;">Timeline</h4>
                        <div class="row">
                            <div class="col-md-12">
                                <div class="chart-container">
                                    {pio.to_html(fig_throughput, include_plotlyjs=False, full_html=False)}
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-12">
                                <div class="chart-container">
                                    {pio.to_html(fig_resolution_month, include_plotlyjs=False, full_html=False)}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- TAB: DELIVERY -->
                <div class="tab-pane fade" id="delivery" role="tabpanel">
                    <div style="margin-top: 20px;">
                        <h4 class="section-title">Métricas de Entrega y Performance</h4>
                        
                        <div class="insight-box info">
                            <strong>Lead Time Analysis:</strong> La mediana de lead time es {lead_time_median:.1f} días (media: {lead_time_mean:.1f}, p95: {lead_time_p95:.1f}). Un equipo eficiente busca reducir esta métrica consistentemente.
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="chart-container">
                                    {pio.to_html(fig_lead_dist, include_plotlyjs='cdn' if True else False, full_html=False)}
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="chart-container">
                                    {pio.to_html(fig_lead_box, include_plotlyjs=False, full_html=False)}
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-12">
                                <div class="chart-container">
                                    {pio.to_html(fig_lead_type, include_plotlyjs=False, full_html=False)}
                                </div>
                            </div>
                        </div>
                        
                        <h4 class="section-title" style="margin-top: 30px;">Backlog & Aging</h4>
                        <div class="chart-container">
                            {pio.to_html(fig_backlog, include_plotlyjs=False, full_html=False)}
                        </div>
                    </div>
                </div>
                
                <!-- TAB: QUALITY -->
                <div class="tab-pane fade" id="quality" role="tabpanel">
                    <div style="margin-top: 20px;">
                        <h4 class="section-title">Métricas de Calidad</h4>
                        
                        <div class="insight-box">
                            <strong>Defect Density = {defect_density:.2%}:</strong> Esto significa hay {defect_density:.3f} bugs por story. Interpreta según tu estándar de industria.
                        </div>
                        <div class="insight-box info">
                            <strong>Total de Bugs: {bug_count}</strong> Ha habido {bug_count} bugs reportados en el período. Esto ayuda a entender patrones de calidad.
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="chart-container">
                                    {pio.to_html(fig_bugs, include_plotlyjs='cdn' if True else False, full_html=False)}
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card kpi-card" style="margin-top: 0;">
                                    <h6>Defect Density Ratio</h6>
                                    <h2>{defect_density:.3f}</h2>
                                    <div class="metric-unit">bugs/story</div>
                                    <hr style="border-color: rgba(255,255,255,0.1); margin: 12px 0;">
                                    <p style="font-size: 0.85rem; color: var(--muted); margin: 0;">
                                        📌 Umbral típico: 0.05-0.10<br>
                                        Estado: <span class="metric-badge" style="background: {'linear-gradient(135deg, #10b981 0%, #059669 100%)' if defect_density < 0.1 else 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'};">
                                            {'✓ Aceptable' if defect_density < 0.1 else '⚠️ Alto'}
                                        </span>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- TAB: TEAM -->
                <div class="tab-pane fade" id="team" role="tabpanel">
                    <div style="margin-top: 20px;">
                        <h4 class="section-title">Rendimiento de Equipo</h4>
                        
                        <div class="chart-container">
                            {pio.to_html(fig_assignees, include_plotlyjs='cdn' if True else False, full_html=False)}
                        </div>
                        
                        <div class="insight-box info">
                            <strong>Carga de Trabajo:</strong> El gráfico muestra el número de issues asignadas a cada miembro. Una distribución desigual puede indicar necesidad de rebalanceo o diferentes capacidades.
                        </div>
                    </div>
                </div>
                
            </div>
            
            <!-- FOOTER -->
            <div style="margin-top: 60px; padding-top: 30px; border-top: 1px solid rgba(0, 181, 201, 0.2); text-align: center; color: var(--muted); font-size: 0.85rem;">
                <p>Dashboard generado automáticamente desde JIRA LTI.csv | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Dashboard generado: {OUTPUT_HTML}")
print("\n" + "=" * 80)
print("🎉 Análisis completado. Abre dashboard_analytics.html en tu navegador.")
print("=" * 80)
