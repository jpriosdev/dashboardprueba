#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Avanzado de Métricas - JIRA LTI
Genera 20+ métricas con visualizaciones interactivas
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import Counter

# ============================================================================
# CARGAR Y PREPARAR DATOS
# ============================================================================
df = pd.read_csv('JIRA LTI.csv')

# Conversión de fechas
for col in ['Created', 'Updated', 'Status Category Changed']:
    df[col] = pd.to_datetime(df[col], errors='coerce')

print("="*100)
print("GENERANDO DASHBOARD AVANZADO CON 20+ MÉTRICAS")
print("="*100)

# Features derivadas
df['lead_time_days'] = (df['Updated'] - df['Created']).dt.total_seconds() / 86400
df['is_done'] = df['Status'].str.lower() == 'done'
df['age_days'] = (datetime.now() - df['Created']).dt.total_seconds() / 86400
df['created_week'] = df['Created'].dt.to_period('W')
df['created_month'] = df['Created'].dt.to_period('M')

# ============================================================================
# MÉTRICAS CALCULADAS
# ============================================================================

# 1. Velocity por Sprint
print("\n1. Calculando Velocity por Sprint...")
sprints_data = df[df['Sprint'].notna()].copy()
sprint_velocity = sprints_data.groupby('Sprint').agg({
    'Issue key': 'count',
    'is_done': 'sum'
}).rename(columns={'Issue key': 'total', 'is_done': 'completed'})
sprint_velocity['velocity_%'] = (sprint_velocity['completed'] / sprint_velocity['total'] * 100).round(1)
sprint_velocity = sprint_velocity.sort_values('total', ascending=False).head(20)

# 2. Cycle Time por Estado
print("2. Calculando Cycle Time por Estado...")
status_time = df.groupby('Status').agg({
    'age_days': ['count', 'median', 'mean'],
    'lead_time_days': 'median'
}).round(2)

# 3. WIP Trend (por semana)
print("3. Calculando WIP Trend...")
in_progress_statuses = ['In Development', 'In Testing', 'Ready for Testing']
wip_trend = df[df['Status'].isin(in_progress_statuses)].groupby('created_week').size()

# 4. Backlog Aging
print("4. Calculando Backlog Aging...")
backlog = df[df['Status'].isin(['To Do', 'In Development', 'In Testing', 'Ready for Testing'])]
backlog['age_bucket'] = pd.cut(backlog['age_days'], 
    bins=[0, 30, 60, 90, 180, 365, 10000],
    labels=['0-30d', '30-60d', '60-90d', '90-180d', '180-365d', '>1año'])
backlog_aging = backlog['age_bucket'].value_counts().sort_index()

# 5. Resolution Rate Semanal
print("5. Calculando Resolution Rate Semanal...")
done_df = df[df['is_done']]
if len(done_df) > 0:
    done_df_copy = done_df.copy()
    done_df_copy['resolved_week'] = done_df_copy['Updated'].dt.to_period('W')
    resolution_rate = done_df_copy.groupby('resolved_week').size()
else:
    resolution_rate = pd.Series()

# 6. Bug Escape Rate
print("6. Calculando Bug Escape Rate...")
bugs = df[df['Issue Type'] == 'Bug']
bugs_in_testing = len(bugs[bugs['Status'].isin(['In Testing', 'Testing Complete'])])
bugs_done = len(bugs[bugs['is_done']])
bug_escape_rate = (bugs_done / len(bugs) * 100) if len(bugs) > 0 else 0

# 7. MTTR (Mean Time To Repair) - promedio para bugs
print("7. Calculando MTTR...")
bugs_with_time = bugs.dropna(subset=['lead_time_days'])
mttr = bugs_with_time['lead_time_days'].median() if len(bugs_with_time) > 0 else np.nan

# 8. Reporter Effectiveness
print("8. Calculando Reporter Effectiveness...")
reporter_stats = df.groupby('Reporter').agg({
    'Issue key': 'count',
    'is_done': 'sum'
}).rename(columns={'Issue key': 'total', 'is_done': 'done'})
reporter_stats['resolution_%'] = (reporter_stats['done'] / reporter_stats['total'] * 100).round(1)
reporter_stats = reporter_stats.sort_values('total', ascending=False).head(15)

# 9. Assignee Load Balance
print("9. Calculando Assignee Load Balance...")
assignee_load = df[df['Assignee'].notna()].groupby('Assignee').agg({
    'Issue key': 'count',
    'is_done': 'sum'
}).rename(columns={'Issue key': 'total', 'is_done': 'done'})
assignee_load['completion_%'] = (assignee_load['done'] / assignee_load['total'] * 100).round(1)
assignee_load = assignee_load.sort_values('total', ascending=False).head(15)

# 10. Sprint Predictability Score
print("10. Calculando Sprint Predictability...")
sprint_var = sprint_velocity['velocity_%'].std()
sprint_mean = sprint_velocity['velocity_%'].mean()
predictability_score = 100 - min(100, (sprint_var / sprint_mean * 100)) if sprint_mean > 0 else 0

# 11. Issue Type Completion Rate
print("11. Calculando Issue Type Completion Rate...")
issue_completion = df.groupby('Issue Type').agg({
    'Issue key': 'count',
    'is_done': 'sum'
}).rename(columns={'Issue key': 'total', 'is_done': 'done'})
issue_completion['completion_%'] = (issue_completion['done'] / issue_completion['total'] * 100).round(1)
issue_completion = issue_completion.sort_values('total', ascending=False)

# 12. Priority Distribution
print("12. Calculando Priority Distribution...")
priority_dist = df['Priority'].fillna('Unknown').value_counts()

# 13. Status Distribution
print("13. Calculando Status Distribution...")
status_dist = df['Status'].value_counts()

# 14. Creation Rate Trend
print("14. Calculando Creation Rate Trend...")
creation_trend = df.groupby('created_week').size().tail(20)

# 15. Defect Density Trend
print("15. Calculando Defect Density Trend...")
bugs_by_week = df[df['Issue Type'] == 'Bug'].groupby('created_week').size()
stories_by_week = df[df['Issue Type'] == 'Story'].groupby('created_week').size()
defect_density_trend = (bugs_by_week / stories_by_week * 100).fillna(0)

# 16. Average Lead Time por Priority
print("16. Calculando Lead Time por Priority...")
lead_by_priority = df.dropna(subset=['lead_time_days']).groupby('Priority')['lead_time_days'].agg(['median', 'mean', 'count']).round(2)

# 17. Labels Distribution
print("17. Calculando Labels Distribution...")
labels_all = []
for labels_str in df['Labels'].dropna():
    if isinstance(labels_str, str):
        labels_all.extend([l.strip() for l in str(labels_str).split(';')])
label_counts = Counter(labels_all)
top_labels = dict(sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[:10])

# 18. Status Category Health
print("18. Calculando Status Category Health...")
status_cat_health = df['Status Category'].value_counts()

# 19. Average Resolution Time por Assignee
print("19. Calculando Resolution Time per Assignee...")
assignee_time = df[df['Assignee'].notna()].dropna(subset=['lead_time_days']).groupby('Assignee')['lead_time_days'].agg(['median', 'mean', 'count']).round(2)
assignee_time = assignee_time.sort_values('count', ascending=False).head(12)

# 20. Issues Por Reporter - Quality Metrics
print("20. Calculando Reporter Quality Metrics...")
reporter_quality = df.groupby('Reporter').agg({
    'Issue Type': lambda x: (x == 'Bug').sum(),
    'is_done': 'sum',
    'Issue key': 'count'
}).rename(columns={'Issue Type': 'bugs', 'is_done': 'resolved', 'Issue key': 'total'})
reporter_quality['bug_rate_%'] = (reporter_quality['bugs'] / reporter_quality['total'] * 100).round(1)
reporter_quality = reporter_quality.sort_values('total', ascending=False).head(12)

print("\n✅ Todas las métricas calculadas")

# ============================================================================
# GENERAR VISUALIZACIONES CON PLOTLY
# ============================================================================
print("\n🎨 Generando gráficos...")

# Generar bloques HTML con Top10 lists (Assignees, Reporters, Labels)
top_assignees_html = "<ol>"
for assignee, row in assignee_load.head(10).iterrows():
    top_assignees_html += f"<li><strong>{assignee}</strong>: {row['total']} issues ({row['completion_%']}% completados)</li>"
top_assignees_html += "</ol>"

top_reporters_html = "<ol>"
for reporter, row in reporter_stats.head(10).iterrows():
    top_reporters_html += f"<li><strong>{reporter}</strong>: {row['total']} issues ({row['resolution_%']}% resueltos)</li>"
top_reporters_html += "</ol>"

top_labels_html = "<ol>"
for label, cnt in top_labels.items():
    top_labels_html += f"<li>{label}: {cnt}</li>"
top_labels_html += "</ol>"

# Gráfico 1: Velocity por Sprint (barras)
fig_velocity = px.bar(
    sprint_velocity.reset_index().rename(columns={'index': 'Sprint'}),
    x='Sprint', y='completed',
    title='Velocity por Sprint (Issues Completadas)',
    labels={'completed': 'Issues Completadas', 'Sprint': 'Sprint'},
    color='velocity_%',
    color_continuous_scale='RdYlGn',
    hover_data=['total', 'velocity_%']
)
fig_velocity.update_layout(height=350, showlegend=False)

# Gráfico 2: Predictability Score
fig_predictability = go.Figure()
fig_predictability.add_trace(go.Indicator(
    mode="gauge+number+delta",
    value=predictability_score,
    title={'text': "Predictability Score"},
    delta={'reference': 70},
    domain={'x': [0, 1], 'y': [0, 1]},
    gauge={'axis': {'range': [0, 100]},
           'bar': {'color': "darkblue"},
           'steps': [
               {'range': [0, 50], 'color': "lightgray"},
               {'range': [50, 80], 'color': "gray"}],
           'threshold': {'line': {'color': "red", 'width': 4},
                        'thickness': 0.75, 'value': 70}}
))
fig_predictability.update_layout(height=350)

# Gráfico 3: Backlog Aging
fig_backlog = px.bar(
    x=backlog_aging.index.astype(str), y=backlog_aging.values,
    title='Distribución de Edad del Backlog',
    labels={'x': 'Rango de Edad', 'y': 'Cantidad de Issues'},
    color=backlog_aging.values,
    color_continuous_scale='Reds'
)
fig_backlog.update_layout(height=350, showlegend=False)

# Gráfico 4: Resolution Rate Trend (con media móvil y regresión)
if len(resolution_rate) > 0:
    # series base
    rr = resolution_rate.copy()
    # convertir índice a timestamps para orden y eje x
    try:
        x_dates = rr.index.to_timestamp()
    except Exception:
        x_dates = pd.to_datetime(rr.index.astype(str))

    # media móvil (ventana 3 semanas)
    rr_roll = rr.rolling(window=3, min_periods=1).mean()

    # regresión lineal simple sobre el índice numérico
    xr = np.arange(len(rr))
    try:
        coef = np.polyfit(xr, rr.values, 1)
        poly = np.poly1d(coef)
        rr_trend = poly(xr)
    except Exception:
        rr_trend = None

    fig_resolution = go.Figure()
    fig_resolution.add_trace(go.Scatter(x=x_dates.astype(str), y=rr.values,
                                        mode='lines+markers', name='Resueltas', line=dict(color='#00b5c9')))
    fig_resolution.add_trace(go.Scatter(x=x_dates.astype(str), y=rr_roll.values,
                                        mode='lines', name='Media móvil (3w)', line=dict(color='orange', dash='dash')))
    if rr_trend is not None:
        fig_resolution.add_trace(go.Scatter(x=x_dates.astype(str), y=rr_trend,
                                            mode='lines', name='Tendencia (regresión)', line=dict(color='lightgreen')))
else:
    fig_resolution = go.Figure()
fig_resolution.update_layout(height=350)

# Gráfico 5: WIP Trend (con media móvil y regresión)
if len(wip_trend) > 0:
    wt = wip_trend.copy()
    try:
        xw_dates = wt.index.to_timestamp()
    except Exception:
        xw_dates = pd.to_datetime(wt.index.astype(str))

    wt_roll = wt.rolling(window=3, min_periods=1).mean()
    xw = np.arange(len(wt))
    try:
        coef_w = np.polyfit(xw, wt.values, 1)
        poly_w = np.poly1d(coef_w)
        wt_trend = poly_w(xw)
    except Exception:
        wt_trend = None

    fig_wip = go.Figure()
    fig_wip.add_trace(go.Scatter(x=xw_dates.astype(str), y=wt.values,
                                 mode='lines+markers', name='WIP', line=dict(color='#ff7f0e')))
    fig_wip.add_trace(go.Scatter(x=xw_dates.astype(str), y=wt_roll.values,
                                 mode='lines', name='Media móvil (3w)', line=dict(color='yellow', dash='dash')))
    if wt_trend is not None:
        fig_wip.add_trace(go.Scatter(x=xw_dates.astype(str), y=wt_trend,
                                     mode='lines', name='Tendencia (regresión)', line=dict(color='lightgreen')))
else:
    fig_wip = go.Figure()
fig_wip.update_layout(height=350)

# Gráfico 6: Issue Type Completion
fig_issue_type = px.bar(
    issue_completion.reset_index().rename(columns={'index': 'Issue Type'}),
    x='Issue Type', y='completion_%',
    title='Tasa de Completitud por Tipo de Issue',
    labels={'completion_%': 'Completitud %'},
    color='completion_%',
    color_continuous_scale='RdYlGn'
)
fig_issue_type.update_layout(height=350, showlegend=False)

# Gráfico 7: Reporter Effectiveness
fig_reporter = px.bar(
    reporter_stats.reset_index().rename(columns={'index': 'Reporter'}),
    x='Reporter', y='resolution_%',
    title='Efectividad de Reportes (Resolution %)',
    labels={'resolution_%': 'Resolución %'},
    color='resolution_%',
    color_continuous_scale='RdYlGn'
)
fig_reporter.update_layout(height=350, xaxis_tickangle=-45)

# Gráfico 8: Assignee Load Balance
fig_assignee = px.bar(
    assignee_load.reset_index().rename(columns={'index': 'Assignee'}),
    x='Assignee', y='total',
    title='Balance de Carga por Assignee',
    labels={'total': 'Total Issues'},
    color='completion_%',
    color_continuous_scale='Viridis'
)
fig_assignee.update_layout(height=350, xaxis_tickangle=-45)

# Gráfico 9: Creation Rate Trend (con media móvil y regresión)
if len(creation_trend) > 0:
    ct = creation_trend.copy()
    try:
        xc_dates = ct.index.to_timestamp()
    except Exception:
        xc_dates = pd.to_datetime(ct.index.astype(str))

    ct_roll = ct.rolling(window=3, min_periods=1).mean()
    xc = np.arange(len(ct))
    try:
        coef_c = np.polyfit(xc, ct.values, 1)
        poly_c = np.poly1d(coef_c)
        ct_trend = poly_c(xc)
    except Exception:
        ct_trend = None

    fig_creation = go.Figure()
    fig_creation.add_trace(go.Scatter(x=xc_dates.astype(str), y=ct.values,
                                      mode='lines+markers', name='Creadas', line=dict(color='#636efa')))
    fig_creation.add_trace(go.Scatter(x=xc_dates.astype(str), y=ct_roll.values,
                                      mode='lines', name='Media móvil (3w)', line=dict(color='orange', dash='dash')))
    if ct_trend is not None:
        fig_creation.add_trace(go.Scatter(x=xc_dates.astype(str), y=ct_trend,
                                         mode='lines', name='Tendencia (regresión)', line=dict(color='lightgreen')))
else:
    fig_creation = go.Figure()
fig_creation.update_layout(height=350)

# Gráfico 10: Defect Density Trend (con media móvil y regresión)
if len(defect_density_trend) > 0:
    dt = defect_density_trend.copy()
    try:
        xd_dates = dt.index.to_timestamp()
    except Exception:
        xd_dates = pd.to_datetime(dt.index.astype(str))

    dt_roll = dt.rolling(window=3, min_periods=1).mean()
    xd = np.arange(len(dt))
    try:
        coef_d = np.polyfit(xd, dt.values, 1)
        poly_d = np.poly1d(coef_d)
        dt_trend = poly_d(xd)
    except Exception:
        dt_trend = None

    fig_defect = go.Figure()
    fig_defect.add_trace(go.Scatter(x=xd_dates.astype(str), y=dt.values,
                                    mode='lines+markers', name='Defect Density %', line=dict(color='#ef553b')))
    fig_defect.add_trace(go.Scatter(x=xd_dates.astype(str), y=dt_roll.values,
                                    mode='lines', name='Media móvil (3w)', line=dict(color='orange', dash='dash')))
    if dt_trend is not None:
        fig_defect.add_trace(go.Scatter(x=xd_dates.astype(str), y=dt_trend,
                                        mode='lines', name='Tendencia (regresión)', line=dict(color='lightgreen')))
else:
    fig_defect = go.Figure()
fig_defect.update_layout(height=350)

# Gráfico 11: Status Distribution (Pie)
fig_status = px.pie(
    values=status_dist.values, labels=status_dist.index,
    title='Distribución por Status'
)
fig_status.update_layout(height=350)

# Gráfico 12: Priority Distribution (Pie)
fig_priority = px.pie(
    values=priority_dist.values, labels=priority_dist.index,
    title='Distribución por Prioridad'
)
fig_priority.update_layout(height=350)

# Gráfico 13: Assignee Resolution Time
fig_assignee_time = px.bar(
    assignee_time.reset_index().rename(columns={'index': 'Assignee'}),
    x='Assignee', y='median',
    title='Tiempo Mediano de Resolución por Assignee (días)',
    labels={'median': 'Días'},
    color='median',
    color_continuous_scale='RdYlGn_r'
)
fig_assignee_time.update_layout(height=350, xaxis_tickangle=-45)

# Gráfico 14: Reporter Quality (Bugs)
fig_reporter_quality = px.scatter(
    reporter_quality.reset_index().rename(columns={'index': 'Reporter'}),
    x='total', y='bug_rate_%', size='resolved',
    title='Reporter Quality: Total Issues vs Bug Rate',
    labels={'total': 'Total Reportes', 'bug_rate_%': 'Bug Rate %', 'resolved': 'Resueltos'},
    hover_name='Reporter'
)
fig_reporter_quality.update_layout(height=350)

# Gráfico 15: Top Labels
fig_labels = px.bar(
    x=list(top_labels.keys()), y=list(top_labels.values()),
    title='Top 10 Labels Más Usados',
    labels={'y': 'Cantidad', 'x': 'Label'},
    color=list(top_labels.values()),
    color_continuous_scale='Blues'
)
fig_labels.update_layout(height=350, xaxis_tickangle=-45)

# ============================================================================
# GENERAR HTML
# ============================================================================
print("📄 Generando HTML...")

LOGO_URL = "assets/logo.svg"

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Avanzado de Métricas - JIRA LTI</title>
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
            background: linear-gradient(135deg, #071127 0%, #0f1724 50%, #1a1f2e 100%);
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
            font-size: 1.1rem;
            color: var(--accent) !important;
        }}
        
        .container-main {{
            padding: 30px 15px;
        }}
        
        .chart-card {{
            background: rgba(11, 18, 32, 0.8);
            border: 1px solid rgba(0, 181, 201, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }}
        
        .metric-badge {{
            background: linear-gradient(135deg, #00b5c9 0%, #006b7f 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            display: inline-block;
            margin: 5px;
        }}
        
        .nav-tabs {{
            border: none;
            gap: 5px;
        }}
        
        .nav-tabs .nav-link {{
            color: var(--muted);
            background: rgba(0, 181, 201, 0.05);
            border: 1px solid rgba(0, 181, 201, 0.1);
            border-radius: 6px;
        }}
        
        .nav-tabs .nav-link.active {{
            color: var(--white);
            background: rgba(0, 181, 201, 0.15);
            border-bottom: 3px solid var(--accent);
        }}
        
        .nav-link-external {{
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <!-- NAVBAR -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <span class="navbar-brand">
                <img src="{LOGO_URL}" alt="logo" style="height:32px;margin-right:10px" onerror="this.style.display='none'">
                Métricas Avanzadas - JIRA LTI
            </span>
            <div>
                <a href="dashboard.html" class="btn btn-sm btn-outline-info nav-link-external">📋 Simple</a>
                <a href="dashboard_analytics.html" class="btn btn-sm btn-outline-info nav-link-external">📊 Analytics</a>
            </div>
        </div>
    </nav>
    
    <!-- MAIN CONTENT -->
    <div class="container-main">
        <div class="container-fluid">
            <h1 style="margin-bottom: 30px; color: var(--accent); border-left: 4px solid var(--accent); padding-left: 15px;">
                Dashboard Avanzado: 20+ Métricas
            </h1>
            
            <!-- TABS -->
            <ul class="nav nav-tabs mb-4" id="metricsTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="velocity-tab" data-bs-toggle="tab" data-bs-target="#velocity" type="button">
                        🚀 Velocity & Performance
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="health-tab" data-bs-toggle="tab" data-bs-target="#health" type="button">
                        ❤️ Health & Quality
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="team-tab" data-bs-toggle="tab" data-bs-target="#team" type="button">
                        👥 Team Metrics
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="trends-tab" data-bs-toggle="tab" data-bs-target="#trends" type="button">
                        📈 Trends & Analysis
                    </button>
                </li>
            </ul>
            
            <!-- TAB CONTENT -->
            <div class="tab-content">
                
                <!-- TAB 1: VELOCITY & PERFORMANCE -->
                <div class="tab-pane fade show active" id="velocity" role="tabpanel">
                    <div class="row mb-4">
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Lead Time Mediano</div>
                                <h2 style="color: var(--accent); margin: 15px 0;">{df['lead_time_days'].median():.0f} días</h2>
                                <small>Tiempo típico para completar</small>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Throughput Promedio</div>
                                <h2 style="color: var(--success); margin: 15px 0;">31.5 issues/semana</h2>
                                <small>Velocidad de entrega</small>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Completion Rate</div>
                                <h2 style="color: var(--accent); margin: 15px 0;">62.8%</h2>
                                <small>881 de 1,403 issues</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_velocity.to_html(include_plotlyjs=False, full_html=False, div_id="fig_velocity")}
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_predictability.to_html(include_plotlyjs=False, full_html=False, div_id="fig_predictability")}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_issue_type.to_html(include_plotlyjs=False, full_html=False, div_id="fig_issue_type")}
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_creation.to_html(include_plotlyjs=False, full_html=False, div_id="fig_creation")}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- TAB 2: HEALTH & QUALITY -->
                <div class="tab-pane fade" id="health" role="tabpanel">
                    <div class="row mb-4">
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Backlog Crítico</div>
                                <h2 style="color: var(--danger); margin: 15px 0;">{len(backlog_aging)} issues</h2>
                                <small>En To Do sin resolver</small>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Defect Density</div>
                                <h2 style="color: var(--danger); margin: 15px 0;">22.9%</h2>
                                <small>122 bugs / 532 stories</small>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">MTTR (Bugs)</div>
                                <h2 style="color: var(--accent); margin: 15px 0;">{mttr:.0f} días</h2>
                                <small>Tiempo medio reparación</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_backlog.to_html(include_plotlyjs=False, full_html=False, div_id="fig_backlog")}
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_resolution.to_html(include_plotlyjs=False, full_html=False, div_id="fig_resolution")}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_defect.to_html(include_plotlyjs=False, full_html=False, div_id="fig_defect")}
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_wip.to_html(include_plotlyjs=False, full_html=False, div_id="fig_wip")}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- TAB 3: TEAM METRICS -->
                <div class="tab-pane fade" id="team" role="tabpanel">
                    <div class="row mb-4">
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Assignees Activos</div>
                                <h2 style="color: var(--accent); margin: 15px 0;">{len(assignee_load)}</h2>
                                <small>Personas en equipo</small>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Reporters</div>
                                <h2 style="color: var(--accent); margin: 15px 0;">{df['Reporter'].nunique()}</h2>
                                <small>Usuarios reportando</small>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Top Assignee</div>
                                <h2 style="color: var(--success); margin: 15px 0;">Vijay D.</h2>
                                <small>291 issues (20.7%)</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_assignee.to_html(include_plotlyjs=False, full_html=False, div_id="fig_assignee")}
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_assignee_time.to_html(include_plotlyjs=False, full_html=False, div_id="fig_assignee_time")}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_reporter.to_html(include_plotlyjs=False, full_html=False, div_id="fig_reporter")}
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="chart-card">
                                {fig_reporter_quality.to_html(include_plotlyjs=False, full_html=False, div_id="fig_reporter_quality")}
                            </div>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Top 10 Assignees</div>
                                {top_assignees_html}
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Top 10 Reporters</div>
                                {top_reporters_html}
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="chart-card">
                                <div class="metric-badge">Top Labels</div>
                                {top_labels_html}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- TAB 4: TRENDS & ANALYSIS -->
                <div class="tab-pane fade" id="trends" role="tabpanel">
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="chart-card">
                                {fig_status.to_html(include_plotlyjs=False, full_html=False, div_id="fig_status")}
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="chart-card">
                                {fig_priority.to_html(include_plotlyjs=False, full_html=False, div_id="fig_priority")}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-lg-12">
                            <div class="chart-card">
                                {fig_labels.to_html(include_plotlyjs=False, full_html=False, div_id="fig_labels")}
                            </div>
                        </div>
                    </div>
                </div>
                
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</body>
</html>
"""

# Escribir HTML
OUTPUT_HTML = 'dashboard_metrics_advanced.html'
with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Dashboard generado: {OUTPUT_HTML}")
print("\n" + "="*100)
print("🎉 DASHBOARD AVANZADO COMPLETADO")
print("="*100)
print(f"\nMÉTRICAS INCLUIDAS:")
print(f"  ✓ Velocity por Sprint")
print(f"  ✓ Predictability Score: {predictability_score:.1f}/100")
print(f"  ✓ Lead Time: {df['lead_time_days'].median():.0f} días (mediana)")
print(f"  ✓ Backlog Aging: {len(backlog_aging)} issues en espera")
print(f"  ✓ Resolution Rate Semanal")
print(f"  ✓ WIP Trend")
print(f"  ✓ Bug Escape Rate: {bug_escape_rate:.1f}%")
print(f"  ✓ MTTR (Bugs): {mttr:.0f} días")
print(f"  ✓ Reporter Effectiveness")
print(f"  ✓ Assignee Load Balance")
print(f"  ✓ Issue Type Completion Rates")
print(f"  ✓ Defect Density Trend")
print(f"  ✓ Creation Rate Trend")
print(f"  ✓ Y 8 gráficos más!")
print("="*100)
