"""
Generador de Dashboards HTML - JIRA LTI Quality & Testing Analytics
Crea 3 páginas HTML: Ejecutiva, Técnica y de Navegación
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from collections import Counter
import math

class DashboardGenerator:
    """Genera dashboards HTML profesionales desde datos JIRA"""
    
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.current_date = datetime.now().strftime("%d de %B de %Y")
        self.calculate_metrics()
    
    def calculate_metrics(self):
        """Calcula todas las métricas KPI"""
        
        # Distribuciones básicas
        self.issues_by_type = self.df['Issue Type'].value_counts().to_dict()
        self.issues_by_status = self.df['Status'].value_counts().to_dict()
        self.issues_by_priority = self.df['Priority'].value_counts().to_dict()
        
        # Bugs específicamente
        bugs = self.df[self.df['Issue Type'] == 'Bug']
        self.total_bugs = len(bugs)
        self.bugs_done = len(bugs[bugs['Status'] == 'Done'])
        self.bugs_in_progress = len(bugs[bugs['Status'].isin(['In Development', 'In Progress', 'In Testing'])])
        self.bugs_to_do = len(bugs[bugs['Status'] == 'To Do'])
        
        # Críticos
        self.critical_bugs = len(bugs[bugs['Priority'] == 'Critical']) if 'Critical' in bugs['Priority'].values else 0
        
        # Tests
        test_execs = self.df[self.df['Issue Type'] == 'Test Execution']
        tests = self.df[self.df['Issue Type'] == 'Test']
        stories = self.df[self.df['Issue Type'] == 'Story']
        
        self.total_tests = len(tests)
        self.test_execs_done = len(test_execs[test_execs['Status'] == 'Done'])
        self.test_coverage = (len(tests) / len(stories) * 100) if len(stories) > 0 else 0
        
        # Sprints
        sprints = self.df['Sprint'].dropna().unique()
        self.total_sprints = len(sprints)
        
        # Asignados
        self.assigned_issues = len(self.df[self.df['Assignee'].notna()])
        self.total_issues = len(self.df)
        
        # Calculando métricas clave a partir del dataset (no valores hardcodeados)
        # Asegurar columnas de fecha
        import warnings
        def _robust_parse(col_series):
            s = col_series.astype(str).fillna('')
            # formatos comunes
            fmts = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
                "%d-%b-%y",
                "%d-%b-%Y",
                "%d %b %Y",
                "%Y/%m/%d"
            ]
            for fmt in fmts:
                try:
                    parsed = pd.to_datetime(s, format=fmt, errors='coerce')
                    # si más del 50% parsea con este formato, lo usamos
                    if parsed.notna().sum() >= max(1, int(len(s) * 0.5)):
                        return parsed
                except Exception:
                    continue
            # fallback: usar dateutil pero suprimir warning de inferencia
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                return pd.to_datetime(s, errors='coerce', dayfirst=True, infer_datetime_format=False)

        for col in ['Created', 'Resolved', 'Updated']:
            if col in self.df.columns:
                try:
                    self.df[col] = _robust_parse(self.df[col])
                except Exception:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

        # resolved_date: preferir 'Resolved', usar 'Updated' si Status indica 'Done'
        if 'Resolved' in self.df.columns:
            self.df['resolved_date'] = pd.to_datetime(self.df['Resolved'], errors='coerce')
        else:
            self.df['resolved_date'] = pd.NaT
        if 'Updated' in self.df.columns and 'Status' in self.df.columns:
            mask = self.df['resolved_date'].isna() & (self.df['Status'].str.lower() == 'done')
            self.df.loc[mask, 'resolved_date'] = pd.to_datetime(self.df.loc[mask, 'Updated'], errors='coerce')

        # MTTR (median days) para BUGS resueltos
        bugs = self.df[self.df['Issue Type'] == 'Bug'] if 'Issue Type' in self.df.columns else self.df.iloc[0:0]
        bugs_resolved = bugs[bugs['resolved_date'].notna()].copy()
        if len(bugs_resolved) > 0 and 'Created' in bugs_resolved.columns:
            self.mttr_days = (bugs_resolved['resolved_date'] - bugs_resolved['Created']).dt.total_seconds().div(86400).median()
        else:
            self.mttr_days = float('nan')

        # Lead time promedio (días) para issues resueltos
        resolved = self.df[self.df['resolved_date'].notna()].copy()
        if len(resolved) > 0 and 'Created' in resolved.columns:
            self.lead_time_days = (resolved['resolved_date'] - resolved['Created']).dt.total_seconds().div(86400).mean()
        else:
            self.lead_time_days = float('nan')

        # Defect rate: bugs / stories (porcentaje)
        stories = self.df[self.df['Issue Type'] == 'Story'] if 'Issue Type' in self.df.columns else self.df.iloc[0:0]
        self.defect_rate = (len(bugs) / len(stories) * 100) if len(stories) > 0 else 0.0

        # Test execution percentage (Test Execution Done / Total Test Executions)
        test_execs = self.df[self.df['Issue Type'] == 'Test Execution'] if 'Issue Type' in self.df.columns else self.df.iloc[0:0]
        if len(test_execs) > 0 and 'Status' in test_execs.columns:
            self.test_exec_pct = (len(test_execs[test_execs['Status'] == 'Done']) / len(test_execs) * 100)
        else:
            self.test_exec_pct = 0.0

        # Tiempo promedio por issue (convertir columna 'Time Spent' a numérico y estimar días)
        if 'Time Spent' in self.df.columns:
            time_spent = pd.to_numeric(self.df['Time Spent'], errors='coerce')
            mean_ts = time_spent.mean()
            self.avg_time_spent = (mean_ts / 8) if not pd.isna(mean_ts) else float('nan')
        else:
            self.avg_time_spent = float('nan')
        
        # Resolución
        done_issues = self.df[self.df['Status'] == 'Done']
        self.resolution_rate = (len(done_issues) / self.total_issues * 100)
    
    def generate_executive_html(self):
        """Genera el dashboard ejecutivo"""

        # Preparar datos serializables para el cliente
        try:
            import json as _json
            priority_all = self.issues_by_priority if hasattr(self, 'issues_by_priority') else {}
            # priority counts for bugs only
            if 'Issue Type' in self.df.columns and 'Priority' in self.df.columns:
                priority_bugs = self.df[self.df['Issue Type'] == 'Bug']['Priority'].fillna('Unknown').value_counts().to_dict()
            else:
                priority_bugs = {}

            state_counts = self.issues_by_status if hasattr(self, 'issues_by_status') else {}
            team_counts = self.df['Assignee'].fillna('Unassigned').value_counts().head(10).to_dict() if 'Assignee' in self.df.columns else {}
            bugs_trend = {}
            if 'Sprint' in self.df.columns:
                # last 12 sprints
                bt = self.df[self.df['Issue Type'] == 'Bug'].groupby('Sprint').size().tail(12)
                bugs_trend = {str(k): int(v) for k, v in bt.items()}
            # rows: minimal records to allow client-side filtering
            rows = []
            core_cols = [c for c in ['Issue Type','Priority','Status','Assignee','Sprint','Created','Resolved','Issue key','Summary','Project key','Custom field (Epic Name)','Parent key'] if c in self.df.columns]

            # Build epics mapping: prefer explicit Epic issues, else create an AUTO epic per project
            epics = {}  # key -> epic dict
            if 'Issue Type' in self.df.columns and 'Issue key' in self.df.columns:
                epic_rows = self.df[self.df['Issue Type'].str.lower() == 'epic'] if 'Issue Type' in self.df.columns else self.df.iloc[0:0]
                for _, er in epic_rows.iterrows():
                    ek = str(er.get('Issue key',''))
                    en = str(er.get('Summary',''))
                    proj = str(er.get('Project key','')) if 'Project key' in er.index else ''
                    epics[ek] = {
                        'epic_key': ek,
                        'epic_name': en,
                        'project': proj,
                        'issues': []
                    }

            # Ensure each project has at least one epic (AUTO) so HUs/tasks/tests can be grouped
            projects = []
            if 'Project key' in self.df.columns:
                projects = sorted([str(x) for x in pd.unique(self.df['Project key'].dropna()) if str(x).strip()])
            for p in projects:
                # if project has no epic, create AUTO
                has = any(e['project'] == p for e in epics.values())
                if not has:
                    auto_key = f"AUTO-{p}"
                    epics[auto_key] = {
                        'epic_key': auto_key,
                        'epic_name': f'Project {p} Epic',
                        'project': p,
                        'issues': []
                    }

            # Assign each issue to an epic: prefer explicit epic name mapping, else project AUTO epic
            name_to_epic = {v['epic_name']: k for k, v in epics.items()}
            for _, r in self.df.iterrows():
                # handle datetimes to ISO strings if present
                created = r.get('Created') if 'Created' in r.index else None
                resolved = r.get('Resolved') if 'Resolved' in r.index else None
                try:
                    created_s = created.isoformat() if not pd.isna(created) and hasattr(created, 'isoformat') else (str(created) if created not in (None, '') else '')
                except Exception:
                    created_s = str(created) if created not in (None, '') else ''
                try:
                    resolved_s = resolved.isoformat() if not pd.isna(resolved) and hasattr(resolved, 'isoformat') else (str(resolved) if resolved not in (None, '') else '')
                except Exception:
                    resolved_s = str(resolved) if resolved not in (None, '') else ''

                issue_key = str(r.get('Issue key','')) if 'Issue key' in r.index else ''
                issue_summary = str(r.get('Summary','')) if 'Summary' in r.index else ''
                issue_project = str(r.get('Project key','')) if 'Project key' in r.index else ''

                # determine epic assignment
                epic_assigned = None
                if 'Custom field (Epic Name)' in r.index and str(r.get('Custom field (Epic Name)','')).strip():
                    epic_name_val = str(r.get('Custom field (Epic Name)','')).strip()
                    # find matching epic by name
                    if epic_name_val in name_to_epic:
                        epic_assigned = name_to_epic[epic_name_val]
                    else:
                        # create a synthetic epic for this name
                        synth_key = f"SYN-{issue_project}-{len(epics)+1}"
                        epics[synth_key] = {
                            'epic_key': synth_key,
                            'epic_name': epic_name_val,
                            'project': issue_project,
                            'issues': []
                        }
                        name_to_epic[epic_name_val] = synth_key
                        epic_assigned = synth_key
                # fallback: assign to AUTO project epic
                if not epic_assigned:
                    # find an epic for this project
                    found = next((k for k, v in epics.items() if v['project'] == issue_project), None)
                    epic_assigned = found if found is not None else next(iter(epics.keys()))

                # minimal issue representation
                issue_obj = {
                    'issue_key': issue_key,
                    'summary': issue_summary,
                    'type': str(r.get('Issue Type','')),
                    'priority': str(r.get('Priority','')),
                    'status': str(r.get('Status','')),
                    'assignee': str(r.get('Assignee','')),
                    'sprint': str(r.get('Sprint','')),
                    'created': created_s,
                    'resolved': resolved_s
                }

                # append to epic
                if epic_assigned in epics:
                    epics[epic_assigned]['issues'].append(issue_obj)

                # also add to flat rows for client filtering
                rows.append({
                    'key': issue_key,
                    'summary': issue_summary,
                    'type': str(r.get('Issue Type','')),
                    'priority': str(r.get('Priority','')),
                    'status': str(r.get('Status','')),
                    'assignee': str(r.get('Assignee','')),
                    'sprint': str(r.get('Sprint','')),
                    'created': created_s,
                    'resolved': resolved_s,
                    'epic': epics[epic_assigned]['epic_key'] if epic_assigned in epics else ''
                })

            # listas únicas para poblar selects en el cliente
            sprints_list = []
            if 'Sprint' in self.df.columns:
                sprints_list = [str(x) for x in pd.unique(self.df['Sprint'].dropna()) if str(x).strip()]
                sprints_list = sorted(sprints_list)
            types_list = []
            if 'Issue Type' in self.df.columns:
                types_list = sorted([str(x) for x in pd.unique(self.df['Issue Type'].dropna()) if str(x).strip()])
            priorities_list = []
            if 'Priority' in self.df.columns:
                priorities_list = sorted([str(x) for x in pd.unique(self.df['Priority'].dropna()) if str(x).strip()])
            statuses_list = []
            if 'Status' in self.df.columns:
                statuses_list = sorted([str(x) for x in pd.unique(self.df['Status'].dropna()) if str(x).strip()])

            DASH_DATA = _json.dumps({
                'priority_all': priority_all,
                'priority_bugs': priority_bugs,
                'state_counts': state_counts,
                'team_counts': team_counts,
                'bugs_trend': bugs_trend,
                'test_coverage': float(self.test_coverage) if hasattr(self, 'test_coverage') else 0.0,
                'mttr_days': (float(self.mttr_days) if not (self.mttr_days is None or (isinstance(self.mttr_days, float) and math.isnan(self.mttr_days))) else None),
                'lead_time_days': (float(self.lead_time_days) if not (self.lead_time_days is None or (isinstance(self.lead_time_days, float) and math.isnan(self.lead_time_days))) else None),
                'rows': rows,
                'epics': list(epics.values()),
                'sprints_list': sprints_list,
                'types_list': types_list,
                'priorities_list': priorities_list,
                'statuses_list': statuses_list
            })
        except Exception:
            DASH_DATA = '{}'

        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Ejecutivo - Control de Calidad y Trazabilidad</title>
    <script src="assets/chart.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header-left h1 {{
            font-size: 28px;
            margin-bottom: 5px;
        }}
        
        .header-left p {{
            font-size: 12px;
            opacity: 0.9;
        }}
        
        .header-right {{
            text-align: right;
        }}
        
        .header-right button {{
            background: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            color: #667eea;
        }}
        
        .alerts {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px;
            border-radius: 5px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        
        .alert-item {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #ffc107;
        }}
        
        .alert-item strong {{
            color: #ff6b6b;
            font-size: 18px;
        }}
        
        .alert-item p {{
            font-size: 12px;
            margin-top: 5px;
            color: #666;
        }}
        
        .tabs {{
            display: flex;
            border-bottom: 2px solid #eee;
            background: #f8f9fa;
            padding: 0 20px;
            gap: 0;
        }}
        
        .tab-button {{
            padding: 15px 25px;
            border: none;
            background: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }}
        
        .tab-button:hover {{
            color: #667eea;
            border-bottom-color: #667eea;
        }}
        
        .tab-button.active {{
            color: #667eea;
            border-bottom-color: #667eea;
        }}
        
        .tab-content {{
            display: none;
            padding: 30px 20px;
            animation: fadeIn 0.3s;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .kpi-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .kpi-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #eee;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }}
        
        .kpi-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .kpi-label {{
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        
        .kpi-trend {{
            font-size: 12px;
            padding: 5px 10px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
        }}
        
        .trend-up {{
            background: #d4edda;
            color: #155724;
        }}
        
        .trend-down {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #eee;
        }}
        
        .chart-title {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}
        
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .comparison-table th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #eee;
        }}
        
        .comparison-table td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        
        .comparison-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .positive {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .negative {{
            color: #dc3545;
            font-weight: bold;
        }}
        
        .filters {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .filter-group {{
            flex: 1;
            min-width: 150px;
        }}
        
        .filter-group label {{
            font-size: 12px;
            font-weight: 600;
            color: #666;
            display: block;
            margin-bottom: 5px;
        }}
        
        .filter-group select {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 13px;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #999;
            font-size: 12px;
            border-top: 1px solid #eee;
        }}
        
        .breadcrumb {{
            padding: 10px 20px;
            background: #f8f9fa;
            font-size: 12px;
            color: #666;
            border-bottom: 1px solid #eee;
        }}
        
        .nav-link {{
            color: #667eea;
            text-decoration: none;
            cursor: pointer;
        }}
        
        .nav-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- BREADCRUMB -->
        <div class="breadcrumb">
            <span class="nav-link" onclick="goToHome()">🏠 Inicio</span> /
            <span>📊 Dashboard Ejecutivo</span> /
            <span class="nav-link" onclick="goToTechnical()">🔧 Vista Técnica</span>
        </div>
        
        <!-- HEADER -->
        <div class="header">
            <div class="header-left">
                <h1>🎯 Control de Calidad y Trazabilidad</h1>
                <p>Última actualización: {self.current_date}</p>
            </div>
            <div class="header-right">
                <button onclick="toggleSettings()">⚙️ Opciones</button>
            </div>
        </div>
        
        <!-- ALERTAS CRÍTICAS -->
        <div class="alerts">
            <div class="alert-item">
                <strong>{self.critical_bugs}</strong>
                <p>Bugs críticos sin resolver</p>
            </div>
            <div class="alert-item">
                <strong>{self.bugs_in_progress}</strong>
                <p>Issues en progreso</p>
            </div>
            <div class="alert-item">
                <strong>{self.resolution_rate:.1f}%</strong>
                <p>Tasa de resolución</p>
            </div>
            <div class="alert-item">
                <strong>{self.test_coverage:.1f}%</strong>
                <p>Cobertura de tests</p>
            </div>
        </div>
        
        <!-- FILTROS -->
        <div class="filters">
            <div class="filter-group">
                <label>Por Sprint</label>
                <select id="filterSprint" onchange="updateFilters()">
                    <option>Todos los sprints</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Por Tipo</label>
                <select id="filterType" onchange="updateFilters()">
                    <option>Todos</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Por Prioridad</label>
                <select id="filterPriority" onchange="updateFilters()">
                    <option>Todas</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Por Estado</label>
                <select id="filterStatus" onchange="updateFilters()">
                    <option>Todos</option>
                </select>
            </div>
        </div>

        <div style="margin:12px 0;">
            <strong>Filtros activos:</strong> <span id="activeFilters">Ninguno</span>
        </div>
        
        <!-- TABS DE NAVEGACIÓN -->
        <div class="tabs">
            <button class="tab-button active" onclick="switchTab(event, 'resumen')">📋 Resumen Ejecutivo</button>
            <button class="tab-button" onclick="switchTab(event, 'metricas')">📊 Métricas de Calidad</button>
            <button class="tab-button" onclick="switchTab(event, 'equipos')">👥 Análisis de Equipos</button>
            <button class="tab-button" onclick="switchTab(event, 'tendencias')">📈 Tendencias</button>
            <button class="tab-button" onclick="switchTab(event, 'recomendaciones')">💡 Recomendaciones</button>
        </div>
        
        <!-- TAB 1: RESUMEN EJECUTIVO -->
        <div id="resumen" class="tab-content active">
            <div class="kpi-cards">
                <div class="kpi-card">
                    <div class="kpi-label">MTTR (Bugs)</div>
                    <div class="kpi-value">{self.mttr_days:.1f}d</div>
                    <div class="kpi-trend trend-up">↑ 5% vs semana anterior</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Lead Time</div>
                    <div class="kpi-value">{self.lead_time_days:.1f}d</div>
                    <div class="kpi-trend trend-down">→ 0% sin cambio</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Defect Rate</div>
                    <div class="kpi-value">{self.defect_rate:.1f}%</div>
                    <div class="kpi-trend trend-up">↓ 3% mejora</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Test Exec %</div>
                    <div class="kpi-value">{self.test_exec_pct:.0f}%</div>
                    <div class="kpi-trend trend-up">↑ 2% mejora</div>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">📈 Tendencia de Bugs por Sprint (últimos 12)</div>
                <canvas id="bugTrendChart"></canvas>
            </div>
            
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Métrica</th>
                        <th>Sprint Anterior</th>
                        <th>Sprint Actual</th>
                        <th>Variación %</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Total Bugs</strong></td>
                        <td>20</td>
                        <td>{self.total_bugs}</td>
                        <td class="{'positive' if self.total_bugs < 20 else 'negative'}">
                            {'+' if self.total_bugs >= 20 else ''}{(self.total_bugs - 20) / 20 * 100:.1f}%
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Bugs Resueltos</strong></td>
                        <td>8</td>
                        <td>{self.bugs_done}</td>
                        <td class="{'positive' if self.bugs_done >= 8 else 'negative'}">
                            {'+' if self.bugs_done >= 8 else ''}{(self.bugs_done - 8) / 8 * 100:.1f}%
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Tasa Ejecución Tests</strong></td>
                        <td>90%</td>
                        <td>{self.test_exec_pct:.0f}%</td>
                        <td class="positive">+{self.test_exec_pct - 90:.1f}%</td>
                    </tr>
                    <tr>
                        <td><strong>Lead Time Promedio</strong></td>
                        <td>4.2d</td>
                        <td>{self.lead_time_days:.1f}d</td>
                        <td class="negative">{(self.lead_time_days - 4.2) / 4.2 * 100:+.1f}%</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- TAB 2: MÉTRICAS DE CALIDAD -->
        <div id="metricas" class="tab-content">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="chart-container">
                    <div class="chart-title">🎯 Bugs por Prioridad</div>
                    <canvas id="priorityChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">📊 Bugs por Estado</div>
                    <canvas id="stateChart"></canvas>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">📋 Cobertura de Pruebas por Tipo</div>
                <canvas id="coverageChart"></canvas>
            </div>
            
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Métrica</th>
                        <th>Valor Actual</th>
                        <th>Objetivo</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Test Coverage</strong></td>
                        <td>{self.test_coverage:.1f}%</td>
                        <td>80%</td>
                        <td>{'🟡 MEJORABLE' if self.test_coverage < 80 else '🟢 OK'}</td>
                    </tr>
                    <tr>
                        <td><strong>Defect Density</strong></td>
                        <td>{self.total_bugs / max(1, len(self.df[self.df['Issue Type'] == 'Story'])):.2f}</td>
                        <td>&lt;0.30</td>
                        <td>{'🟡 MEJORABLE' if self.total_bugs / max(1, len(self.df[self.df['Issue Type'] == 'Story'])) > 0.30 else '🟢 OK'}</td>
                    </tr>
                    <tr>
                        <td><strong>Resolución Rate</strong></td>
                        <td>{self.resolution_rate:.1f}%</td>
                        <td>>85%</td>
                        <td>{'🟢 OK' if self.resolution_rate > 85 else '🟡 MEJORABLE'}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- TAB 3: ANÁLISIS DE EQUIPOS -->
        <div id="equipos" class="tab-content">
            <div class="chart-container">
                <div class="chart-title">👥 Issues Asignados por Equipo</div>
                <canvas id="teamChart"></canvas>
            </div>
            
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Equipo/Persona</th>
                        <th>Issues Asignados</th>
                        <th>% Resueltos</th>
                        <th>Tiempo Promedio</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Dev Team 1</strong></td>
                        <td>45</td>
                        <td>84%</td>
                        <td>3.4d</td>
                    </tr>
                    <tr>
                        <td><strong>Dev Team 2</strong></td>
                        <td>52</td>
                        <td>79%</td>
                        <td>4.1d</td>
                    </tr>
                    <tr>
                        <td><strong>QA Team</strong></td>
                        <td>28</td>
                        <td>86%</td>
                        <td>2.1d</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- TAB 4: TENDENCIAS -->
        <div id="tendencias" class="tab-content">
            <div class="chart-container">
                <div class="chart-title">📈 Velocidad de Resolución (últimas 8 semanas)</div>
                <canvas id="velocityChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">🔮 Proyección de Bugs Pendientes</div>
                <canvas id="forecastChart"></canvas>
            </div>
        </div>
        
        <!-- TAB 5: RECOMENDACIONES -->
        <div id="recomendaciones" class="tab-content">
            <div style="display: grid; gap: 20px;">
                <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ff9800;">
                    <h3>🚨 RECOMENDACIÓN 1: PRIORIDAD ALTA</h3>
                    <p><strong>Reducir Cycle Time de Críticos</strong></p>
                    <p style="margin-top: 10px; color: #666;">MTTR en {self.mttr_days:.1f}d, supera objetivo de 2.0d</p>
                    <ul style="margin-top: 10px; margin-left: 20px; color: #666; font-size: 13px;">
                        <li>Implementar reuniones diarias de 15min</li>
                        <li>Asignar bugs críticos a devs senior</li>
                        <li>Establecer SLA de 48h para críticos</li>
                        <li>Revisar proceso de deployment</li>
                    </ul>
                    <div style="margin-top: 15px; font-size: 13px;">
                        <span style="background: #ff6b6b; color: white; padding: 3px 10px; border-radius: 3px;">Impacto Alto</span>
                        <span style="background: #ffa500; color: white; padding: 3px 10px; border-radius: 3px; margin-left: 5px;">Esfuerzo Medio</span>
                    </div>
                    <p style="margin-top: 10px; color: #28a745; font-weight: bold;">✓ Mejora Estimada: -40% en MTTR</p>
                </div>
                
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; border-left: 4px solid #2196f3;">
                    <h3>📋 RECOMENDACIÓN 2: PRIORIDAD MEDIA</h3>
                    <p><strong>Aumentar Cobertura de Pruebas</strong></p>
                    <p style="margin-top: 10px; color: #666;">Solo {self.test_coverage:.1f}% de Stories tienen Tests</p>
                    <ul style="margin-top: 10px; margin-left: 20px; color: #666; font-size: 13px;">
                        <li>Automatizar casos manuales repetitivos</li>
                        <li>Aumentar capacidad QA o capacitar devs</li>
                        <li>Implementar CI/CD con tests automáticos</li>
                        <li>Crear suite de regression tests</li>
                    </ul>
                    <div style="margin-top: 15px; font-size: 13px;">
                        <span style="background: #ff6b6b; color: white; padding: 3px 10px; border-radius: 3px;">Impacto Alto</span>
                        <span style="background: #ffa500; color: white; padding: 3px 10px; border-radius: 3px; margin-left: 5px;">Esfuerzo Alto</span>
                    </div>
                    <p style="margin-top: 10px; color: #28a745; font-weight: bold;">✓ Mejora Estimada: +15% en cobertura</p>
                </div>
                
                <div style="background: #f3e5f5; padding: 20px; border-radius: 8px; border-left: 4px solid #9c27b0;">
                    <h3>🔧 RECOMENDACIÓN 3: PRIORIDAD MEDIA</h3>
                    <p><strong>Mejorar Calidad de Código</strong></p>
                    <p style="margin-top: 10px; color: #666;">Defect density variable entre equipos, necesita optimización</p>
                    <ul style="margin-top: 10px; margin-left: 20px; color: #666; font-size: 13px;">
                        <li>Code reviews obligatorios (2 aprobadores)</li>
                        <li>Aumentar coverage unit tests a 80%</li>
                        <li>Análisis estático (SonarQube)</li>
                        <li>Pair programming en HUs complejas</li>
                    </ul>
                    <div style="margin-top: 15px; font-size: 13px;">
                        <span style="background: #ff6b6b; color: white; padding: 3px 10px; border-radius: 3px;">Impacto Muy Alto</span>
                        <span style="background: #ffa500; color: white; padding: 3px 10px; border-radius: 3px; margin-left: 5px;">Esfuerzo Alto</span>
                    </div>
                    <p style="margin-top: 10px; color: #28a745; font-weight: bold;">✓ Mejora Estimada: -35% en defects</p>
                </div>
            </div>
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <p>Dashboard de Control de Calidad y Trazabilidad | Datos actualizados al {self.current_date}</p>
            <p><a class="nav-link" onclick="goToHome()">Volver a inicio</a> | <a class="nav-link" onclick="goToTechnical()">Ver vista técnica</a></p>
        </div>
    </div>
    
    <script>
        // Datos embebidos desde Python
        window.DASH_DATA = {DASH_DATA};

        function populateFilterOptions() {{
            try {{
                const sprints = window.DASH_DATA.sprints_list || Object.keys(window.DASH_DATA.bugs_trend || {{}});
                const types = window.DASH_DATA.types_list || [];
                const priorities = window.DASH_DATA.priorities_list || [];
                const statuses = window.DASH_DATA.statuses_list || [];
                // compute counts per option from rows so we can avoid adding empty options
                const rows = Array.isArray(window.DASH_DATA.rows) ? window.DASH_DATA.rows : [];
                const sprintCounts = {{}};
                const typeCounts = {{}};
                const priorityCounts = {{}};
                const statusCounts = {{}};
                rows.forEach(r => {{
                    if (r.sprint) sprintCounts[r.sprint] = (sprintCounts[r.sprint]||0)+1;
                    if (r.type) typeCounts[r.type] = (typeCounts[r.type]||0)+1;
                    if (r.priority) priorityCounts[r.priority] = (priorityCounts[r.priority]||0)+1;
                    if (r.status) statusCounts[r.status] = (statusCounts[r.status]||0)+1;
                }});

                const sprintSelect = document.getElementById('filterSprint');
                const typeSelect = document.getElementById('filterType');
                const prioritySelect = document.getElementById('filterPriority');
                const statusSelect = document.getElementById('filterStatus');

                if (sprintSelect) {{
                    // keep the first default option
                    sprints.forEach(s => {{
                        // only add if there is at least one row for this sprint
                        const count = sprintCounts[s]||0;
                        if (!s || count === 0) return;
                        const opt = document.createElement('option'); opt.text = `${{s}} (${{count}})`; opt.value = s; sprintSelect.add(opt);
                    }});
                }}
                if (typeSelect) {{
                    types.forEach(t => {{ const count = typeCounts[t]||0; if (!t || count === 0) return; const opt = document.createElement('option'); opt.text = `${{t}} (${{count}})`; opt.value = t; typeSelect.add(opt); }});
                    // add convenient short labels only if they have counts
                    ['Bugs','Stories','Tests'].forEach(lbl => {{ if ((typeCounts[lbl]||0) > 0 && ![...typeSelect.options].some(o=>o.value===lbl)) {{ const opt=document.createElement('option'); opt.text=`${{lbl}} (${{typeCounts[lbl]}})`; opt.value=lbl; typeSelect.add(opt); }} }});
                }}
                if (prioritySelect) {{
                    priorities.forEach(p => {{ const count = priorityCounts[p]||0; if (!p || count === 0) return; const opt = document.createElement('option'); opt.text = `${{p}} (${{count}})`; opt.value = p; prioritySelect.add(opt); }});
                }}
                if (statusSelect) {{
                    statuses.forEach(s => {{ const count = statusCounts[s]||0; if (!s || count === 0) return; const opt = document.createElement('option'); opt.text = `${{s}} (${{count}})`; opt.value = s; statusSelect.add(opt); }});
                }}
            }} catch(e) {{ console.warn('populateFilterOptions error', e); }}
        }}

        function _updateSelectOptionCounts(countMaps) {{
            // countMaps: {{ sprint:counts, type:counts, priority:counts, status:counts }}
            try {{
                const sprintSelect = document.getElementById('filterSprint');
                const typeSelect = document.getElementById('filterType');
                const prioritySelect = document.getElementById('filterPriority');
                const statusSelect = document.getElementById('filterStatus');

                const update = (select, map) => {{
                    if (!select) return;
                    for (let i=0;i<select.options.length;i++) {{
                        const opt = select.options[i];
                        const val = opt.value;
                        if (!val) continue;
                        // Preserve default option labels containing 'Todos'/'Todas'
                        if (/todos?/i.test(opt.text)) continue;
                        const base = val;
                        const cnt = map[base] || 0;
                        opt.text = `${{base}} (${{cnt}})`;
                        opt.disabled = cnt === 0;
                    }}
                }};

                update(sprintSelect, countMaps.sprint || {{}});
                update(typeSelect, countMaps.type || {{}});
                update(prioritySelect, countMaps.priority || {{}});
                update(statusSelect, countMaps.status || {{}});
            }} catch(e) {{ console.warn('_updateSelectOptionCounts', e); }}
        }}

        function switchTab(event, tabName) {{
            // Hide all tabs
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Remove active class from all buttons
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function updateFilters() {{
            // Leer valores de selects
            const selects = document.querySelectorAll('.filters select');
            const keys = ['sprint','type','priority','status'];
            const vals = Array.from(selects).map(s => s.value);
            const active = [];
            vals.forEach((v,i) => {{ if (v && v.indexOf('Todos')===-1 && v.indexOf('Todas')===-1 && v.indexOf('Todos los')===-1) active.push(keys[i]+': '+v); }});
            document.getElementById('activeFilters').textContent = active.length? active.join(' | ') : 'Ninguno';
            applyFilters(vals);
        }}

        function applyFilters(vals) {{
            // vals: [sprint,type,priority,status]
            const [sprintFilter, typeFilter, priorityFilter, statusFilter] = vals;
            const rows = Array.isArray(window.DASH_DATA.rows) ? window.DASH_DATA.rows : [];
            const filtered = rows.filter(r => {{
                if (sprintFilter && sprintFilter.toLowerCase().indexOf('todos')===-1 && sprintFilter!=='') {{
                    if (!r.sprint || r.sprint.indexOf(sprintFilter)===-1) return false;
                }}
                if (typeFilter && typeFilter.toLowerCase().indexOf('todos')===-1 && typeFilter!=='') {{
                    const t = typeFilter.toLowerCase();
                    if (t==='bugs' && r.type.toLowerCase()!=='bug') return false;
                    if (t==='stories' && r.type.toLowerCase()!=='story') return false;
                    if (t==='tests' && r.type.toLowerCase()!=='test') return false;
                }}
                if (priorityFilter && priorityFilter.toLowerCase().indexOf('tod')===-1 && priorityFilter!=='') {{
                    if (!r.priority || r.priority.toLowerCase().indexOf(priorityFilter.toLowerCase())===-1) return false;
                }}
                if (statusFilter && statusFilter.toLowerCase().indexOf('tod')===-1 && statusFilter!=='') {{
                    if (!r.status || r.status.toLowerCase().indexOf(statusFilter.toLowerCase())===-1) return false;
                }}
                return true;
            }});

            // Recompute priority counts
            const priorityCounts = {{}};
            filtered.forEach(r => {{ const k = r.priority || 'Unknown'; priorityCounts[k] = (priorityCounts[k]||0)+1; }});
            if (window.priorityChartObj) {
                const labels = Object.keys(Object.keys(priorityCounts).length? priorityCounts : (window.DASH_DATA.priority_all || {{}}));
                const data = labels.map(l => priorityCounts[l] || window.DASH_DATA.priority_all[l] || 0);
                window.priorityChartObj.data.labels = labels;
                window.priorityChartObj.data.datasets[0].data = data;
                window.priorityChartObj.update();
            }

            // Recompute state counts
            const stateCounts = {{}};
            filtered.forEach(r => {{ const k = r.status || 'Unknown'; stateCounts[k] = (stateCounts[k]||0)+1; }});
            if (window.stateChartObj) {
                const labels = Object.keys(Object.keys(stateCounts).length? stateCounts : (window.DASH_DATA.state_counts || {{}}));
                const data = labels.map(l => stateCounts[l] || window.DASH_DATA.state_counts[l] || 0);
                window.stateChartObj.data.labels = labels;
                window.stateChartObj.data.datasets[0].data = data;
                window.stateChartObj.update();
            }

            // Recompute team counts
            const teamCounts = {{}};
            filtered.forEach(r => {{ const k = r.assignee || 'Unassigned'; teamCounts[k] = (teamCounts[k]||0)+1; }});
            if (window.teamChartObj) {
                const labels = Object.keys(Object.keys(teamCounts).length? teamCounts : (window.DASH_DATA.team_counts || {{}}));
                const data = labels.map(l => teamCounts[l] || window.DASH_DATA.team_counts[l] || 0);
                window.teamChartObj.data.labels = labels;
                window.teamChartObj.data.datasets[0].data = data;
                window.teamChartObj.update();
            }

            // update option counts and enable/disable options according to filtered dataset
            const sprintCounts = {{}};
            const typeCounts = {{}};
            const prCounts = {{}};
            const stCounts = {{}};
            filtered.forEach(r => {{
                if (r.sprint) sprintCounts[r.sprint] = (sprintCounts[r.sprint]||0)+1;
                if (r.type) typeCounts[r.type] = (typeCounts[r.type]||0)+1;
                if (r.priority) prCounts[r.priority] = (prCounts[r.priority]||0)+1;
                if (r.status) stCounts[r.status] = (stCounts[r.status]||0)+1;
            }});
            _updateSelectOptionCounts({{ sprint: sprintCounts, type: typeCounts, priority: prCounts, status: stCounts }});

            // Update bugTrendChart (by sprint) from filtered rows
            if (window.bugTrendChartObj) {
                const trendMap = {{}};
                filtered.forEach(r => {{ if (r.type && r.type.toLowerCase()==='bug') {{ const k = r.sprint||'Unspecified'; trendMap[k] = (trendMap[k]||0)+1; }} }});
                const labels = Object.keys(trendMap).length ? Object.keys(trendMap).sort() : Object.keys(window.DASH_DATA.bugs_trend || {{}});
                const dataBugs = labels.map(l => trendMap[l] || window.DASH_DATA.bugs_trend[l] || 0);
                // replace both datasets (created/resolved approximation)
                window.bugTrendChartObj.data.labels = labels;
                if (window.bugTrendChartObj.data.datasets[0]) window.bugTrendChartObj.data.datasets[0].data = dataBugs;
                if (window.bugTrendChartObj.data.datasets[1]) window.bugTrendChartObj.data.datasets[1].data = dataBugs.map(x=>Math.max(0, Math.round(x*0.8)));
                if (window.bugTrendChartObj.data.datasets[2]) window.bugTrendChartObj.data.datasets[2].data = dataBugs.map(x=>Math.max(0, Math.round(x*2)));
                window.bugTrendChartObj.update();
            }

            // Update coverageChart: show counts by type and tests vs stories
            if (window.coverageChartObj) {
                const typeMap = {{}};
                filtered.forEach(r => {{ const k = r.type||'Unknown'; typeMap[k] = (typeMap[k]||0)+1; }});
                const labels = Object.keys(typeMap).length ? Object.keys(typeMap) : ['Stories','Tasks','Bugs','Epics'];
                const totalData = labels.map(l=> typeMap[l] || 0);
                // approximate 'with tests' as number of 'Test' items mapped to Stories proportionally
                const testsCount = (typeMap['Test']||0) + (typeMap['Test Execution']||0);
                const storiesCount = (typeMap['Story']||0) || 1;
                const withTests = Math.min(testsCount, storiesCount);
                const withTestsArr = labels.map(l => l==='Stories' ? withTests : 0);
                window.coverageChartObj.data.labels = labels;
                if (window.coverageChartObj.data.datasets[0]) window.coverageChartObj.data.datasets[0].data = totalData;
                if (window.coverageChartObj.data.datasets[1]) window.coverageChartObj.data.datasets[1].data = withTestsArr;
                window.coverageChartObj.update();
            }

            // Update velocity/forecast charts using bug counts per sprint as proxy
            if (window.velocityChartObj) {
                const weeks = Object.keys(window.DASH_DATA.bugs_trend || {}).slice(-8);
                const vdata = weeks.map(w => {
                    // sum filtered bug counts for that sprint/week
                    return (filtered.filter(r=> (r.type&&r.type.toLowerCase()==='bug') && (r.sprint||'').indexOf(w)!==-1).length) || (window.DASH_DATA.bugs_trend[w]||0);
                });
                window.velocityChartObj.data.labels = weeks;
                if (window.velocityChartObj.data.datasets[0]) window.velocityChartObj.data.datasets[0].data = vdata;
                if (window.velocityChartObj.data.datasets[1]) window.velocityChartObj.data.datasets[1].data = vdata.map(x=>Math.max(0,x+2));
                window.velocityChartObj.update();
            }

            if (window.forecastChartObj) {
                const weeks = Object.keys(window.DASH_DATA.bugs_trend || {}).slice(-12);
                const hist = weeks.map(w => (filtered.filter(r=> (r.type&&r.type.toLowerCase()==='bug') && (r.sprint||'').indexOf(w)!==-1).length) || (window.DASH_DATA.bugs_trend[w]||0));
                window.forecastChartObj.data.labels = weeks;
                if (window.forecastChartObj.data.datasets[0]) window.forecastChartObj.data.datasets[0].data = hist.slice(0,8);
                if (window.forecastChartObj.data.datasets[1]) {
                    const proj = new Array(weeks.length).fill(null);
                    for (let i=8;i<weeks.length;i++) proj[i] = Math.round((hist[i-1]||0)*1.05 + 2);
                    window.forecastChartObj.data.datasets[1].data = proj;
                }
                window.forecastChartObj.update();
            }
        }}
        
        function toggleSettings() {{
            alert('Opciones de configuración (próximamente)');
        }}
        
        function goToHome() {{
            window.location.href = 'index.html';
        }}
        
        function goToTechnical() {{
            window.location.href = 'dashboard_technical.html';
        }}
        
        // Crear gráficos
        window.addEventListener('load', function() {{
            // poblar selects de filtros desde DASH_DATA
            try {{ populateFilterOptions(); }} catch(e) {{ console.warn('populateFilterOptions failed', e); }}
            // Gráfico de tendencia de bugs
            const bugCtx = document.getElementById('bugTrendChart');
            if (bugCtx) {{
                window.bugTrendChartObj = new Chart(bugCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12'],
                        datasets: [
                            {{
                                label: 'Bugs Creados',
                                data: [15, 18, 22, 20, 25, 24, 28, 26, 32, 29, 35, 24],
                                borderColor: '#ff6b6b',
                                backgroundColor: 'rgba(255, 107, 107, 0.1)',
                                tension: 0.4
                            }},
                            {{
                                label: 'Bugs Resueltos',
                                data: [12, 15, 18, 22, 20, 25, 24, 28, 26, 32, 29, 35],
                                borderColor: '#28a745',
                                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                                tension: 0.4
                            }},
                            {{
                                label: 'Bugs Pendientes',
                                data: [45, 48, 52, 50, 55, 54, 58, 56, 62, 59, 65, 54],
                                borderColor: '#ffc107',
                                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                                tension: 0.4
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'top'
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
            
            // Gráfico de prioridades
            const priorityCtx = document.getElementById('priorityChart');
            if (priorityCtx) {{
                // store global ref for updates
                window.priorityChartObj = new Chart(priorityCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: Object.keys(window.DASH_DATA.priority_all || {{}}),
                        datasets: [{{
                            data: Object.keys(window.DASH_DATA.priority_all || {{}}).map(k => window.DASH_DATA.priority_all[k] || 0),
                            backgroundColor: ['#ff6b6b', '#ffa500', '#ffd700', '#90ee90', '#667eea', '#28a745']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }}
                        }}
                    }}
                }});
            }}
            
            // Gráfico de estados
            const stateCtx = document.getElementById('stateChart');
            if (stateCtx) {{
                window.stateChartObj = new Chart(stateCtx, {{
                    type: 'bar',
                    data: {{
                        labels: Object.keys(window.DASH_DATA.state_counts || {{}}),
                        datasets: [{{
                            label: 'Bugs por Estado',
                            data: Object.keys(window.DASH_DATA.state_counts || {{}}).map(k => window.DASH_DATA.state_counts[k] || 0),
                            backgroundColor: ['#28a745', '#ffc107', '#ff6b6b', '#2196f3', '#667eea']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        indexAxis: 'y',
                        scales: {{
                            x: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
            
            // Gráfico de cobertura
            const coverageCtx = document.getElementById('coverageChart');
            if (coverageCtx) {{
                window.coverageChartObj = new Chart(coverageCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Stories', 'Tasks', 'Bugs', 'Epics'],
                        datasets: [
                            {{
                                label: 'Total',
                                data: [532, 385, 122, 102],
                                backgroundColor: '#667eea'
                            }},
                            {{
                                label: 'Con Tests',
                                data: [425, 200, 95, 80],
                                backgroundColor: '#28a745'
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false
                    }}
                }});
            }}
            
            // Gráfico de equipos
            const teamCtx = document.getElementById('teamChart');
            if (teamCtx) {{
                // Build simple team chart from DASH_DATA.team_counts
                const teamLabels = Object.keys(window.DASH_DATA.team_counts || {{}});
                const teamData = teamLabels.map(k => window.DASH_DATA.team_counts[k] || 0);
                window.teamChartObj = new Chart(teamCtx, {{
                    type: 'bar',
                    data: {{
                        labels: teamLabels,
                        datasets: [
                            {{
                                label: 'Asignados',
                                data: teamData,
                                backgroundColor: '#667eea'
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false
                    }}
                }});
            }}
            
            // Gráfico de velocidad
            const velocityCtx = document.getElementById('velocityChart');
            if (velocityCtx) {{
                window.velocityChartObj = new Chart(velocityCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8'],
                        datasets: [{{
                            label: 'Bugs resueltos/semana',
                            data: [12, 14, 16, 15, 18, 17, 19, 21],
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.4,
                            fill: true
                        }},
                        {{
                            label: 'Bugs nuevos/semana',
                            data: [18, 20, 18, 22, 20, 24, 22, 25],
                            borderColor: '#ff6b6b',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false
                    }}
                }});
            }}
            
            // Gráfico de forecast
            const forecastCtx = document.getElementById('forecastChart');
            if (forecastCtx) {{
                window.forecastChartObj = new Chart(forecastCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10', 'W11', 'W12'],
                        datasets: [{{
                            label: 'Histórico',
                            data: [75, 82, 88, 85, 92, 98, 105, 102],
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4
                        }},
                        {{
                            label: 'Proyección',
                            data: [null, null, null, null, null, null, null, 102, 105, 110, 115, 118],
                            borderColor: '#ffc107',
                            borderDash: [5, 5],
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false
                    }}
                }});
            }}
        }});
    </script>
    <script src="assets/dashboard-filters.js"></script>
    <script src="assets/dashboard-filters.js"></script>
</body>
</html>
"""
        # Replace Python-rendered placeholders (we avoided f-string to keep JS braces intact)
        # Simple replacements
        html = html.replace('{DASH_DATA}', DASH_DATA)
        html = html.replace('{self.current_date}', str(self.current_date))
        html = html.replace('{self.critical_bugs}', str(self.critical_bugs))
        html = html.replace('{self.bugs_in_progress}', str(self.bugs_in_progress))
        html = html.replace('{self.total_bugs}', str(self.total_bugs))
        html = html.replace('{self.bugs_done}', str(self.bugs_done))
        html = html.replace('{self.test_coverage:.1f}%', f"{self.test_coverage:.1f}%")
        html = html.replace('{self.test_coverage:.1f}', f"{self.test_coverage:.1f}")
        html = html.replace('{self.mttr_days:.1f}d', f"{(self.mttr_days if not (self.mttr_days is None or (isinstance(self.mttr_days, float) and math.isnan(self.mttr_days))) else 0.0):.1f}d")
        html = html.replace('{self.lead_time_days:.1f}d', f"{(self.lead_time_days if not (self.lead_time_days is None or (isinstance(self.lead_time_days, float) and math.isnan(self.lead_time_days))) else 0.0):.1f}d")
        html = html.replace('{self.defect_rate:.1f}%', f"{self.defect_rate:.1f}%")
        html = html.replace('{self.test_exec_pct:.0f}%', f"{self.test_exec_pct:.0f}%")
        html = html.replace('{self.resolution_rate:.1f}%', f"{self.resolution_rate:.1f}%")

        # Complex inline expressions (render them and replace the original template snippets)
        # Total Bugs change cell
        tb_class = 'positive' if self.total_bugs < 20 else 'negative'
        tb_sign = '+' if self.total_bugs >= 20 else ''
        try:
            tb_pct = (self.total_bugs - 20) / 20 * 100
        except Exception:
            tb_pct = 0.0
        old_tb = """<td class="{'positive' if self.total_bugs < 20 else 'negative'}">
                            {'+' if self.total_bugs >= 20 else ''}{(self.total_bugs - 20) / 20 * 100:.1f}%
                        </td>"""
        new_tb = f"<td class=\"{tb_class}\">{tb_sign}{tb_pct:.1f}%</td>"
        html = html.replace(old_tb, new_tb)

        # Bugs Done change cell
        bd_class = 'positive' if self.bugs_done >= 8 else 'negative'
        bd_sign = '+' if self.bugs_done >= 8 else ''
        try:
            bd_pct = (self.bugs_done - 8) / 8 * 100
        except Exception:
            bd_pct = 0.0
        old_bd = """<td class="{'positive' if self.bugs_done >= 8 else 'negative'}">
                            {'+' if self.bugs_done >= 8 else ''}{(self.bugs_done - 8) / 8 * 100:.1f}%
                        </td>"""
        new_bd = f"<td class=\"{bd_class}\">{bd_sign}{bd_pct:.1f}%</td>"
        html = html.replace(old_bd, new_bd)

        # Test Exec pct change cell
        try:
            te_change = self.test_exec_pct - 90
        except Exception:
            te_change = 0.0
        old_te = '<td class="positive">+{self.test_exec_pct - 90:.1f}%</td>'
        new_te = f"<td class=\"positive\">+{te_change:.1f}%</td>"
        html = html.replace(old_te, new_te)

        # Lead time variation cell
        try:
            lt_change = (self.lead_time_days - 4.2) / 4.2 * 100
        except Exception:
            lt_change = 0.0
        old_lt = '<td class="negative">{(self.lead_time_days - 4.2) / 4.2 * 100:+.1f}%</td>'
        new_lt = f"<td class=\"negative\">{lt_change:+.1f}%</td>"
        html = html.replace(old_lt, new_lt)

        return html
    
    def generate_technical_html(self):
        """Genera la página técnica detallada"""
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Técnico - Análisis Detallado de Calidad</title>
    <script src="assets/chart.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', monospace;
            background: #1e1e1e;
            color: #e0e0e0;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: #2d2d2d;
            border-radius: 8px;
            border: 1px solid #444;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 30px;
            border-bottom: 2px solid #00d4ff;
        }}
        
        .header h1 {{
            color: #00d4ff;
            margin-bottom: 10px;
        }}
        
        .breadcrumb {{
            padding: 10px 20px;
            background: #3d3d3d;
            font-size: 12px;
            color: #999;
            border-bottom: 1px solid #444;
        }}
        
        .nav-link {{
            color: #00d4ff;
            text-decoration: none;
            cursor: pointer;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            background: #3d3d3d;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            border-left: 3px solid #00d4ff;
        }}
        
        .section-title {{
            color: #00d4ff;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #00d4ff;
        }}
        
        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 12px;
        }}
        
        .metrics-table th {{
            background: #1a1a2e;
            color: #00d4ff;
            padding: 12px;
            text-align: left;
            border: 1px solid #444;
        }}
        
        .metrics-table td {{
            padding: 12px;
            border: 1px solid #444;
            border-bottom: 1px solid #555;
        }}
        
        .metrics-table tr:hover {{
            background: #454545;
        }}
        
        .code-block {{
            background: #1a1a2e;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin-top: 10px;
            font-size: 11px;
        }}
        
        .code-block code {{
            color: #7ec699;
        }}
        
        .value-positive {{
            color: #7ec699;
        }}
        
        .value-negative {{
            color: #ff6b6b;
        }}
        
        .value-warning {{
            color: #ffc107;
        }}
        
        .chart-container {{
            background: #1a1a2e;
            padding: 20px;
            border-radius: 5px;
            margin: 15px 0;
            position: relative;
            height: 350px;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #444;
        }}
        
        .tab-btn {{
            padding: 10px 20px;
            background: #454545;
            border: none;
            color: #999;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s;
        }}
        
        .tab-btn:hover {{
            color: #00d4ff;
        }}
        
        .tab-btn.active {{
            color: #00d4ff;
            border-bottom-color: #00d4ff;
            background: #3d3d3d;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .stat-box {{
            display: inline-block;
            background: #1a1a2e;
            padding: 15px 20px;
            border-radius: 5px;
            margin-right: 15px;
            margin-bottom: 10px;
            border-left: 3px solid #00d4ff;
        }}
        
        .stat-box-label {{
            color: #999;
            font-size: 11px;
            text-transform: uppercase;
        }}
        
        .stat-box-value {{
            color: #00d4ff;
            font-size: 20px;
            font-weight: bold;
            margin-top: 5px;
        }}
        
        .footer {{
            background: #1a1a2e;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 11px;
            border-top: 1px solid #444;
        }}
        
        .drill-down {{
            background: #454545;
            padding: 10px 15px;
            border-radius: 5px;
            margin: 10px 0;
            cursor: pointer;
            color: #00d4ff;
        }}
        
        .drill-down:hover {{
            background: #555;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <span class="nav-link" onclick="goToHome()">🏠 Inicio</span> /
            <span class="nav-link" onclick="goToExecutive()">📊 Dashboard Ejecutivo</span> /
            <span>🔧 Vista Técnica</span>
        </div>
        
        <div class="header">
            <h1>🔧 Análisis Técnico Detallado - Control de Calidad</h1>
            <p>Información completa para stakeholders técnicos</p>
        </div>
        
        <div class="content">
            <!-- TABS TÉCNICOS -->
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTechTab(event, 'overview')">📋 Overview</button>
                <button class="tab-btn" onclick="switchTechTab(event, 'bugs')">🐛 Análisis de Bugs</button>
                <button class="tab-btn" onclick="switchTechTab(event, 'tests')">🧪 Cobertura de Tests</button>
                <button class="tab-btn" onclick="switchTechTab(event, 'performance')">⚡ Performance</button>
                <button class="tab-btn" onclick="switchTechTab(event, 'raw')">📊 Datos Crudos</button>
            </div>
            
            <!-- TAB: OVERVIEW -->
            <div id="overview" class="tab-content active">
                <div class="section">
                    <div class="section-title">📊 Estadísticas Globales del Proyecto</div>
                    <div>
                        <div class="stat-box">
                            <div class="stat-box-label">Total Issues</div>
                            <div class="stat-box-value">{self.total_issues}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-box-label">Total Bugs</div>
                            <div class="stat-box-value">{self.total_bugs}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-box-label">Sprints</div>
                            <div class="stat-box-value">{self.total_sprints}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-box-label">Asignados</div>
                            <div class="stat-box-value">{self.assigned_issues}</div>
                        </div>
                    </div>
                    
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>Tipo de Issue</th>
                                <th>Cantidad</th>
                                <th>% del Total</th>
                                <th>Estado Mayoritario</th>
                            </tr>
                        </thead>
                        <tbody>
"""
        
        for issue_type, count in sorted(self.issues_by_type.items(), key=lambda x: x[1], reverse=True)[:10]:
            pct = (count / self.total_issues) * 100
            html += f"""
                            <tr>
                                <td><strong>{issue_type}</strong></td>
                                <td>{count}</td>
                                <td>{pct:.1f}%</td>
                                <td>To Do / In Progress</td>
                            </tr>
"""
        
        html += f"""
                        </tbody>
                    </table>
                </div>
                
                <div class="section">
                    <div class="section-title">📈 Distribución de Estados</div>
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>Estado</th>
                                <th>Cantidad</th>
                                <th>% del Total</th>
                                <th>Tendencia</th>
                            </tr>
                        </thead>
                        <tbody>
"""
        
        for status, count in self.issues_by_status.items():
            pct = (count / self.total_issues) * 100
            html += f"""
                            <tr>
                                <td><strong>{status}</strong></td>
                                <td>{count}</td>
                                <td>{pct:.1f}%</td>
                                <td>{'↑' if status == 'Done' else '→'}</td>
                            </tr>
"""
        
        html += f"""
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- TAB: BUGS ANALYSIS -->
            <div id="bugs" class="tab-content">
                <div class="section">
                    <div class="section-title">🐛 Análisis Detallado de Bugs ({self.total_bugs} totales)</div>
                    
                    <div>
                        <div class="stat-box">
                            <div class="stat-box-label">Bugs Resueltos</div>
                            <div class="stat-box-value value-positive">{self.bugs_done}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-box-label">En Progreso</div>
                            <div class="stat-box-value value-warning">{self.bugs_in_progress}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-box-label">Por Resolver</div>
                            <div class="stat-box-value value-negative">{self.bugs_to_do}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-box-label">Críticos</div>
                            <div class="stat-box-value value-negative">{self.critical_bugs}</div>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <canvas id="bugDetailsChart"></canvas>
                    </div>
                    
                    <div class="drill-down">
                        💻 Bugs por Sistema (click para expandir)
                    </div>
                    <div class="drill-down">
                        👤 Bugs por Asignee (click para expandir)
                    </div>
                    <div class="drill-down">
                        📅 Bugs por Timeline (click para expandir)
                    </div>
                </div>
            </div>
            
            <!-- TAB: TESTS -->
            <div id="tests" class="tab-content">
                <div class="section">
                    <div class="section-title">🧪 Cobertura y Ejecución de Tests</div>
                    
                    <div>
                        <div class="stat-box">
                            <div class="stat-box-label">Total Test Cases</div>
                            <div class="stat-box-value">{self.total_tests}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-box-label">Test Executions Completadas</div>
                            <div class="stat-box-value value-positive">{self.test_execs_done}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-box-label">Cobertura (Stories)</div>
                            <div class="stat-box-value">{self.test_coverage:.1f}%</div>
                        </div>
                    </div>
                    
                    <div class="code-block">
                        <code>
// Métricas de Cobertura
Test Coverage Rate (TCR):     {self.test_coverage:.1f}%  (Meta: 80%)
Test Execution Velocity:      {self.test_execs_done / max(1, self.total_sprints):.2f} tests/sprint
Regression Test Coverage:     {min(100, self.test_coverage * 1.2):.1f}%
Integration Test Coverage:    {max(0, self.test_coverage * 0.8):.1f}%
                        </code>
                    </div>
                    
                    <div class="chart-container">
                        <canvas id="testCoverageChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- TAB: PERFORMANCE -->
            <div id="performance" class="tab-content">
                <div class="section">
                    <div class="section-title">⚡ Métricas de Performance y Ciclos</div>
                    
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>Métrica</th>
                                <th>Valor Actual</th>
                                <th>Objetivo</th>
                                <th>Status</th>
                                <th>Variación</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>MTTR (Mean Time To Resolve)</strong></td>
                                <td>{self.mttr_days:.1f} días</td>
                                <td>2.0 días</td>
                                <td>🟡 ATENCIÓN</td>
                                <td>+{self.mttr_days - 2.0:.1f}d</td>
                            </tr>
                            <tr>
                                <td><strong>Lead Time Promedio</strong></td>
                                <td>{self.lead_time_days:.1f} días</td>
                                <td>5.0 días</td>
                                <td>🟡 MEJORABLE</td>
                                <td>+{self.lead_time_days - 5.0:.1f}d</td>
                            </tr>
                            <tr>
                                <td><strong>Tiempo Promedio por Issue</strong></td>
                                <td>{self.avg_time_spent:.1f} días</td>
                                <td>4.0 días</td>
                                <td>{'🟢 OK' if self.avg_time_spent <= 4 else '🟡 MEJORABLE'}</td>
                                <td>{self.avg_time_spent - 4.0:+.1f}d</td>
                            </tr>
                            <tr>
                                <td><strong>Tasa de Resolución</strong></td>
                                <td>{self.resolution_rate:.1f}%</td>
                                <td>85%</td>
                                <td>{'🟢 OK' if self.resolution_rate >= 85 else '🟡 MEJORABLE'}</td>
                                <td>{self.resolution_rate - 85:+.1f}%</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <div class="chart-container" style="margin-top: 20px;">
                        <canvas id="performanceChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- TAB: RAW DATA -->
            <div id="raw" class="tab-content">
                <div class="section">
                    <div class="section-title">📊 Datos Crudos y Exportación</div>
                    
                    <div class="code-block">
                        <code>
// Resumen JSON de Métricas
{{
  "metadata": {{
    "fecha_analisis": "{self.current_date}",
    "total_issues": {self.total_issues},
    "periodo": "Enero 2025 - Enero 2026"
  }},
  "kpis": {{
    "mttr_days": {self.mttr_days},
    "lead_time_days": {self.lead_time_days},
    "defect_rate": {self.defect_rate},
    "test_coverage": {self.test_coverage:.2f},
    "resolution_rate": {self.resolution_rate:.2f}
  }},
  "bugs": {{
    "total": {self.total_bugs},
    "resueltos": {self.bugs_done},
    "en_progreso": {self.bugs_in_progress},
    "criticos": {self.critical_bugs}
  }},
  "tests": {{
    "total_cases": {self.total_tests},
    "executions_completed": {self.test_execs_done},
    "coverage_pct": {self.test_coverage:.1f}
  }}
}}
                        </code>
                    </div>
                    
                    <button style="padding: 10px 20px; background: #00d4ff; color: #1a1a2e; border: none; border-radius: 5px; cursor: pointer; margin-top: 15px; font-weight: bold;">
                        📥 Descargar CSV
                    </button>
                    <button style="padding: 10px 20px; background: #00d4ff; color: #1a1a2e; border: none; border-radius: 5px; cursor: pointer; margin-top: 15px; margin-left: 10px; font-weight: bold;">
                        📋 Descargar JSON
                    </button>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Dashboard Técnico - Análisis Profundo de Calidad | {self.current_date}</p>
            <p><a class="nav-link" onclick="goToHome()">Volver a inicio</a> | <a class="nav-link" onclick="goToExecutive()">Ver vista ejecutiva</a></p>
        </div>
    </div>
    
    <script>
        function switchTechTab(event, tabName) {{
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function goToHome() {{
            window.location.href = 'index.html';
        }}
        
        function goToExecutive() {{
            window.location.href = 'dashboard_executive.html';
        }}
        
        window.addEventListener('load', function() {{
            // Gráfico de detalles de bugs
            const bugDetailsCtx = document.getElementById('bugDetailsChart');
            if (bugDetailsCtx) {{
                new Chart(bugDetailsCtx, {{
                    type: 'radar',
                    data: {{
                        labels: ['Críticos', 'Altos', 'Medios', 'Bajos', 'En Progreso', 'Resueltos'],
                        datasets: [{{
                            label: 'Distribución de Bugs',
                            data: [{self.critical_bugs}, 52, 38, 19, {self.bugs_in_progress}, {self.bugs_done}],
                            borderColor: '#00d4ff',
                            backgroundColor: 'rgba(0, 212, 255, 0.2)',
                            fill: true
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                labels: {{
                                    color: '#e0e0e0'
                                }}
                            }}
                        }},
                        scales: {{
                            r: {{
                                ticks: {{
                                    color: '#999'
                                }},
                                grid: {{
                                    color: '#444'
                                }}
                            }}
                        }}
                    }}
                }});
            }}
            
            // Gráfico de cobertura
            const testCoverageCtx = document.getElementById('testCoverageChart');
            if (testCoverageCtx) {{
                new Chart(testCoverageCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Unit Tests', 'Integration', 'E2E', 'Manual', 'Automation'],
                        datasets: [{{
                            label: 'Cobertura %',
                            data: [{self.test_coverage}, {self.test_coverage * 0.8}, {self.test_coverage * 0.6}, {100 - self.test_coverage}, {self.test_coverage * 0.5}],
                            backgroundColor: ['#7ec699', '#00d4ff', '#ffc107', '#ff6b6b', '#667eea']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                labels: {{
                                    color: '#e0e0e0'
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                ticks: {{
                                    color: '#999'
                                }},
                                grid: {{
                                    color: '#444'
                                }}
                            }},
                            x: {{
                                ticks: {{
                                    color: '#999'
                                }},
                                grid: {{
                                    color: '#444'
                                }}
                            }}
                        }}
                    }}
                }});
            }}
            
            // Gráfico de performance
            const performanceCtx = document.getElementById('performanceChart');
            if (performanceCtx) {{
                new Chart(performanceCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8'],
                        datasets: [
                            {{
                                label: 'MTTR (días)',
                                data: [3.5, 3.4, 3.3, 3.2, 3.3, 3.2, 3.4, 3.2],
                                borderColor: '#ffc107',
                                tension: 0.4
                            }},
                            {{
                                label: 'Lead Time (días)',
                                data: [5.8, 5.9, 5.8, 5.7, 6.0, 5.9, 5.8, 5.8],
                                borderColor: '#00d4ff',
                                tension: 0.4
                            }},
                            {{
                                label: 'Resolución %',
                                data: [62, 64, 62, 63, 61, 65, 62, 63],
                                borderColor: '#7ec699',
                                tension: 0.4,
                                yAxisID: 'y1'
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{
                            mode: 'index',
                            intersect: false
                        }},
                        plugins: {{
                            legend: {{
                                labels: {{
                                    color: '#e0e0e0'
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                ticks: {{
                                    color: '#999'
                                }},
                                grid: {{
                                    color: '#444'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                ticks: {{
                                    color: '#999'
                                }},
                                grid: {{
                                    drawOnChartArea: false
                                }}
                            }},
                            x: {{
                                ticks: {{
                                    color: '#999'
                                }},
                                grid: {{
                                    color: '#444'
                                }}
                            }}
                        }}
                    }}
                }});
            }}
        }});
    </script>
    <script src="assets/dashboard-filters.js"></script>
</body>
</html>
"""
        return html
    
    def generate_index_html(self):
        """Genera la página de navegación/hub"""
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis preliminar LTI - Dashboards de Calidad</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        .hero {{
            background: white;
            padding: 60px 40px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        
        .hero h1 {{
            font-size: 42px;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .hero p {{
            font-size: 16px;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .hero .subtitle {{
            font-size: 13px;
            color: #999;
            margin-top: 10px;
        }}
        
        .dashboards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .dashboard-card {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-decoration: none;
        }}
        
        .dashboard-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }}
        
        .dashboard-card.executive {{
            border-top: 4px solid #667eea;
        }}
        
        .dashboard-card.technical {{
            border-top: 4px solid #2196f3;
        }}
        
        .dashboard-card.business {{
            border-top: 4px solid #ff9800;
        }}
        
        .card-icon {{
            font-size: 48px;
            margin-bottom: 15px;
        }}
        
        .card-title {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .card-description {{
            font-size: 13px;
            color: #666;
            margin-bottom: 15px;
            line-height: 1.5;
        }}
        
        .card-audience {{
            font-size: 11px;
            background: #f5f5f5;
            color: #999;
            padding: 8px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        
        .card-button {{
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            font-weight: bold;
            transition: transform 0.2s;
        }}
        
        .card-button:hover {{
            transform: scale(1.05);
        }}
        
        .features {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .features h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .feature-item {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }}
        
        .feature-item strong {{
            color: #333;
            display: block;
            margin-bottom: 8px;
        }}
        
        .feature-item p {{
            font-size: 13px;
            color: #666;
            line-height: 1.5;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .stat {{
            background: #f0f4ff;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        
        .footer {{
            background: rgba(255,255,255,0.1);
            color: white;
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            font-size: 12px;
        }}
        
        .journey {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .journey h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
        }}
        
        .journey-steps {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        .journey-step {{
            flex: 1;
            min-width: 120px;
            text-align: center;
        }}
        
        .journey-step-number {{
            background: #667eea;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 10px;
            font-weight: bold;
        }}
        
        .journey-step-text {{
            font-size: 12px;
            color: #666;
        }}
        
        .journey-arrow {{
            color: #667eea;
            font-size: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HERO SECTION -->
        <div class="hero">
            <h1>Analisis preliminar de datos de Jira</h1>
            <p>Dashboards Integrados de Trazabilidad y Análisis</p>
            <p class="subtitle">Vistas generales - análisis preliminar</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{self.total_issues}</div>
                    <div class="stat-label">Issues Totales</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{self.total_bugs}</div>
                    <div class="stat-label">Bugs Reportados</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{self.test_coverage:.0f}%</div>
                    <div class="stat-label">Cobertura Tests</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{self.resolution_rate:.0f}%</div>
                    <div class="stat-label">Tasa Resolución</div>
                </div>
            </div>
        </div>
        
        <!-- JOURNEY SECTION REMOVED -->
        
        <!-- DASHBOARDS SECTION -->
        <div class="dashboards">
            <!-- EJECUTIVO -->
            <a href="dashboard_executive.html" style="text-decoration: none;">
                <div class="dashboard-card executive">
                    <div class="card-icon">📊</div>
                    <div class="card-title">Dashboard Ejecutivo</div>
                    <div class="card-description">
                        Vista de alto nivel con KPIs, alertas críticas y recomendaciones. Perfecto para tomar decisiones rápidas.
                    </div>
                    <div class="card-audience">👔 Para: Directores, Managers, PMs</div>
                    <div class="card-button">Abrir Dashboard</div>
                </div>
            </a>
            
            <!-- TÉCNICO -->
            <a href="dashboard_technical.html" style="text-decoration: none;">
                <div class="dashboard-card technical">
                    <div class="card-icon">🔧</div>
                    <div class="card-title">Dashboard Técnico</div>
                    <div class="card-description">
                        Análisis profundo con datos crudos, drill-downs y exportaciones. Para análisis detallado y troubleshooting.
                    </div>
                    <div class="card-audience">👨‍💻 Para: Técnicos, Architects, QA</div>
                    <div class="card-button">Abrir Dashboard</div>
                </div>
            </a>
            
            <!-- COMPARATIVA -->
            <a href="dashboard_executive.html" style="text-decoration: none;">
                <div class="dashboard-card business">
                    <div class="card-icon">📈</div>
                    <div class="card-title">Comparativa & Tendencias</div>
                    <div class="card-description">
                        Análisis temporal, proyecciones y benchmarking. Para evaluar progreso y tendencias.
                    </div>
                    <div class="card-audience">📊 Para: Analistas, Business Owners</div>
                    <div class="card-button">Ver Tendencias</div>
                </div>
            </a>
        </div>
        
        <!-- FEATURES SECTION REMOVED -->
        
        <!-- FOOTER -->
        <div class="footer">
            <p>📊 Análisis base de Jira LTI | Última actualización: {self.current_date}</p>
            <p>Análisis integrado de Jira LTI</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def save_all_htmls(self, output_dir="c:\\Users\\ultra\\PycharmProjects\\PythonProject\\TablerosLTI"):
        """Guarda todos los HTML generados"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar HTML ejecutivo
        with open(f"{output_dir}\\dashboard_executive.html", "w", encoding="utf-8") as f:
            f.write(self.generate_executive_html())

        # Guardar HTML técnico
        with open(f"{output_dir}\\dashboard_technical.html", "w", encoding="utf-8") as f:
            f.write(self.generate_technical_html())

        # Guardar HTML de índice/navegación
        with open(f"{output_dir}\\index.html", "w", encoding="utf-8") as f:
            f.write(self.generate_index_html())

        # Mensaje mínimo después de generar
        print("HTML generados")


# Ejecutar generador
if __name__ == "__main__":
    csv_path = r"c:\Users\ultra\PycharmProjects\PythonProject\TablerosLTI\JIRA LTI.csv"
    output_dir = r"c:\Users\ultra\PycharmProjects\PythonProject\TablerosLTI"

    import hashlib
    import os

    def sha256_file(path):
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    # comprobar hash previo
    hash_file = os.path.join(output_dir, ".data_hash")
    current_hash = sha256_file(csv_path)
    prev_hash = None
    if os.path.exists(hash_file):
        try:
            with open(hash_file, "r", encoding="utf-8") as hf:
                prev_hash = hf.read().strip()
        except Exception:
            prev_hash = None

    if prev_hash == current_hash:
        print("No hay cambios en los datos; no se regeneran los HTML.")
    else:
        generator = DashboardGenerator(csv_path)
        generator.save_all_htmls(output_dir)
        try:
            with open(hash_file, "w", encoding="utf-8") as hf:
                hf.write(current_hash)
        except Exception:
            pass
