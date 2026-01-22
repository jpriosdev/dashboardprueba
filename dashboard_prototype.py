import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from datetime import timedelta

# Ruta al CSV (mismo directorio)
CSV_PATH = "JIRA LTI.csv"
OUTPUT_HTML = "dashboard.html"
# Logo: cambia por la URL de tu logo público o deja el placeholder `assets/logo.svg`.
LOGO_URL = "assets/logo.svg"

# Leer CSV
df = pd.read_csv(CSV_PATH, low_memory=False)

# Normalizar nombres de columnas (trim)
df.columns = [c.strip() for c in df.columns]

# Parsear fechas relevantes
for col in ["Created", "Resolved", "Updated"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Tipos útiles
if 'Issue Type' in df.columns:
    df['Issue Type'] = df['Issue Type'].astype(str)
if 'Status' in df.columns:
    df['Status'] = df['Status'].astype(str)
if 'Assignee' in df.columns:
    df['Assignee'] = df['Assignee'].fillna('Unassigned')

# Métricas básicas
# Lead time (días)
df['lead_time_days'] = (df['Resolved'] - df['Created']).dt.total_seconds() / 86400

# Throughput semanal (issues resueltas por semana)
resolved = df.dropna(subset=['Resolved']).copy()
if not resolved.empty:
    resolved['week'] = resolved['Resolved'].dt.to_period('W').apply(lambda r: r.start_time if pd.notnull(r) else pd.NaT)
    throughput = resolved.groupby('week').size().reset_index(name='resolved_count')
else:
    throughput = pd.DataFrame(columns=['week','resolved_count'])

# Lead time distribution (solo issues resueltas)
lead_hist = resolved['lead_time_days'].dropna()

# TI: top assignees por tiempo medio de resolución
assignee_lt = resolved.groupby('Assignee')['lead_time_days'].median().reset_index().sort_values('lead_time_days')

# QA: defect counts (Bug) y defect density
bug_mask = df['Issue Type'].str.lower()=='bug' if 'Issue Type' in df.columns else False
story_mask = df['Issue Type'].str.lower()=='story' if 'Issue Type' in df.columns else False
bug_count = df[bug_mask].shape[0] if 'Issue Type' in df.columns else 0
story_count = df[story_mask].shape[0] if 'Issue Type' in df.columns else 0
defect_density = bug_count / story_count if story_count>0 else None

# Bugs por semana
bugs = df[bug_mask].copy() if 'Issue Type' in df.columns else pd.DataFrame()
if not bugs.empty and 'Resolved' in bugs.columns:
    bugs['week'] = bugs['Resolved'].dt.to_period('W').apply(lambda r: r.start_time if pd.notnull(r) else pd.NaT)
    bugs_week = bugs.groupby('week').size().reset_index(name='bug_count')
else:
    bugs_week = pd.DataFrame(columns=['week','bug_count'])

# Distribución por estado y prioridad
status_counts = df['Status'].value_counts().reset_index(name='count') if 'Status' in df.columns else pd.DataFrame()
priority_counts = df['Priority'].value_counts().reset_index(name='count') if 'Priority' in df.columns else pd.DataFrame()

# Sprint parsing: extraer nombre corto como "Sprint 167"
if 'Sprint' in df.columns:
    df['sprint_short'] = df['Sprint'].astype(str).str.extract(r'(Sprint\s*\d+)', expand=False)
    sprint_velocity = df.dropna(subset=['Resolved','sprint_short']).groupby('sprint_short').size().reset_index(name='completed')
else:
    sprint_velocity = pd.DataFrame(columns=['sprint_short','completed'])

# Figures
# TI - Throughput línea
fig_throughput = px.line(throughput, x='week', y='resolved_count', title='Throughput semanal (issues resueltas)')
fig_throughput.update_layout(margin=dict(t=50,l=30,r=30,b=30))

# TI - Lead time histograma
fig_lead = px.histogram(lead_hist, nbins=40, title='Distribución de Lead Time (días)')
fig_lead.update_layout(margin=dict(t=50,l=30,r=30,b=30))

# TI - Top assignees (mediana lead time)
top_assignees = assignee_lt.head(15)
fig_assignees = px.bar(top_assignees, x='lead_time_days', y='Assignee', orientation='h', title='Mediana de Lead Time por Assignee')
fig_assignees.update_layout(margin=dict(t=50,l=120,r=30,b=30))

# QA - Defect density tarjeta (usaremos un gauge simplificado)
if defect_density is None:
    defect_density_text = 'N/A'
else:
    defect_density_text = f"{defect_density:.3f}"

# QA - Bugs por semana
fig_bugs = px.bar(bugs_week, x='week', y='bug_count', title='Bugs resueltos por semana')
fig_bugs.update_layout(margin=dict(t=50,l=30,r=30,b=30))

# QA - Tabla recientes bugs
recent_bugs = bugs[['Summary','Issue key','Status','Created','Resolved','Assignee']].sort_values('Created', ascending=False).head(15) if not bugs.empty else pd.DataFrame()
fig_table = go.Figure(data=[go.Table(
    header=dict(values=list(recent_bugs.columns), fill_color='paleturquoise', align='left'),
    cells=dict(values=[recent_bugs[col].astype(str) for col in recent_bugs.columns], fill_color='white', align='left'))])
fig_table.update_layout(title='Bugs recientes')

# Más gráficos: estado, prioridad, sprint velocity, lead time por tipo
fig_status = px.pie(status_counts, names='Status', values='count', title='Distribución por estado') if not status_counts.empty else go.Figure()
fig_priority = px.bar(priority_counts, x='Priority', y='count', title='Issues por prioridad') if not priority_counts.empty else go.Figure()
fig_sprint = px.bar(sprint_velocity.sort_values('completed'), x='sprint_short', y='completed', title='Velocidad por sprint (issues completadas)') if not sprint_velocity.empty else go.Figure()
lead_by_type = resolved.groupby('Issue Type')['lead_time_days'].median().reset_index() if 'Issue Type' in resolved.columns else pd.DataFrame()
fig_lead_type = px.bar(lead_by_type, x='Issue Type', y='lead_time_days', title='Mediana Lead Time por Issue Type') if not lead_by_type.empty else go.Figure()

# Ensamblar HTML con pestañas simples
html_parts = []
html_parts.append("<html><head><meta charset='utf-8'><title>Tablero TI & QA - Prototipo</title>")
# Incluir bootstrap mínimo para tabs
html_parts.append("<link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css\" rel=\"stylesheet\">")
html_parts.append("</head><body>")
html_parts.append("<div class=\"container-fluid p-3\">")
html_parts.append("<div class=\"d-flex align-items-center mb-2\"><img src=\"%s\" alt=\"logo\" style=\"height:44px;margin-right:12px\" onerror=\"this.style.display='none'\"><div><h2 style=\"margin:0;color:#fff\">Tablero LTI - TI & QA</h2><small style=\"color:#9aa8bf\">Prototipo interactivo extraído de JIRA CSV</small></div></div>" % LOGO_URL)
html_parts.append("<ul class=\"nav nav-tabs mt-2\" id=\"myTab\" role=\"tablist\">")
html_parts.append("  <li class=\"nav-item\" role=\"presentation\"><button class=\"nav-link active\" id=\"ti-tab\" data-bs-toggle=\"tab\" data-bs-target=\"#ti\" type=\"button\">TI</button></li>")
html_parts.append("  <li class=\"nav-item\" role=\"presentation\"><button class=\"nav-link\" id=\"qa-tab\" data-bs-toggle=\"tab\" data-bs-target=\"#qa\" type=\"button\">QA</button></li>")
html_parts.append("</ul>")
html_parts.append("<div class=\"tab-content mt-3\">")

# TI tab
html_parts.append("<div class=\"tab-pane fade show active\" id=\"ti\" role=\"tabpanel\">")
html_parts.append("<div class=\"row mb-3\">")
html_parts.append(f"<div class=\"col-md-3\"><div class=\"card p-3 kpi\"><h6>Throughput (última semana)</h6><h3>{int(throughput['resolved_count'].iloc[-1]) if not throughput.empty else 0}</h3></div></div>")
html_parts.append(f"<div class=\"col-md-3\"><div class=\"card p-3 kpi\"><h6>Lead time mediano (días)</h6><h3>{round(resolved['lead_time_days'].median(),1) if not resolved.empty else 'N/A'}</h3></div></div>")
html_parts.append(f"<div class=\"col-md-3\"><div class=\"card p-3 kpi\"><h6>Backlog (To Do)</h6><h3>{df[df['Status'].str.lower()=='to do'].shape[0] if 'Status' in df.columns else 0}</h3></div></div>")
html_parts.append(f"<div class=\"col-md-3\"><div class=\"card p-3 kpi\"><h6>MTTR aprox. (días)</h6><h3>{round(resolved['lead_time_days'].mean(),1) if not resolved.empty else 'N/A'}</h3></div></div>")
html_parts.append("</div>")

html_parts.append("<div class=\"row\">")
html_parts.append("<div class=\"col-md-6\">" + pio.to_html(fig_throughput, include_plotlyjs='cdn', full_html=False) + "</div>")
html_parts.append("<div class=\"col-md-6\">" + pio.to_html(fig_lead, include_plotlyjs=False, full_html=False) + "</div>")
html_parts.append("</div>")
html_parts.append("<div class=\"row mt-3\">")
html_parts.append("<div class=\"col-md-6\">" + pio.to_html(fig_assignees, include_plotlyjs=False, full_html=False) + "</div>")
html_parts.append("<div class=\"col-md-6\">" + pio.to_html(fig_lead_type, include_plotlyjs=False, full_html=False) + "</div>")
html_parts.append("</div>")
html_parts.append("</div>")

# QA tab
html_parts.append("<div class=\"tab-pane fade\" id=\"qa\" role=\"tabpanel\">")
html_parts.append("<div class=\"row mb-3\">")
html_parts.append(f"<div class=\"col-md-3\"><div class=\"card p-3 kpi\"><h6>Bug count</h6><h3>{bug_count}</h3></div></div>")
html_parts.append(f"<div class=\"col-md-3\"><div class=\"card p-3 kpi\"><h6>Story count</h6><h3>{story_count}</h3></div></div>")
html_parts.append(f"<div class=\"col-md-3\"><div class=\"card p-3 kpi\"><h6>Defect density</h6><h3>{defect_density_text}</h3></div></div>")
html_parts.append(f"<div class=\"col-md-3\"><div class=\"card p-3 kpi\"><h6>Reopen rate</h6><h3>N/A</h3></div></div>")
html_parts.append("</div>")

html_parts.append("<div class=\"row\">")
html_parts.append("<div class=\"col-md-6\">" + pio.to_html(fig_bugs, include_plotlyjs='cdn', full_html=False) + "</div>")
html_parts.append("<div class=\"col-md-6\">" + pio.to_html(fig_table, include_plotlyjs=False, full_html=False) + "</div>")
html_parts.append("</div>")
html_parts.append("<div class=\"row mt-3\">")
html_parts.append("<div class=\"col-md-6\">" + pio.to_html(fig_status, include_plotlyjs=False, full_html=False) + "</div>")
html_parts.append("<div class=\"col-md-6\">" + pio.to_html(fig_priority, include_plotlyjs=False, full_html=False) + "</div>")
html_parts.append("</div>")
html_parts.append("<div class=\"row mt-3\"><div class=\"col-md-12\">" + pio.to_html(fig_sprint, include_plotlyjs=False, full_html=False) + "</div></div>")
html_parts.append("</div>")

html_parts.append("</div></div>")
# Bootstrap JS
html_parts.append("<script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js\"></script>")
html_parts.append("</body></html>")

html = '\n'.join(html_parts)
with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Generado {OUTPUT_HTML} en el directorio actual. Abrelo en un navegador para ver el prototipo.')
