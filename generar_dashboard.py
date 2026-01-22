"""
GENERADOR DE DASHBOARD HTML - MÉTRICAS KPI DE TESTING Y CALIDAD
"""

html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard KPI - Testing & Calidad - JIRA LTI</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        header h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        header .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        header .date {
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }
        
        .metric-card.critical {
            border-left-color: #e74c3c;
            background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);
        }
        
        .metric-card.warning {
            border-left-color: #f39c12;
            background: linear-gradient(135deg, #fffbf0 0%, #fff3e0 100%);
        }
        
        .metric-card.success {
            border-left-color: #27ae60;
            background: linear-gradient(135deg, #f0fff4 0%, #e6ffed 100%);
        }
        
        .metric-label {
            font-size: 0.85em;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .metric-card.critical .metric-value {
            color: #e74c3c;
        }
        
        .metric-card.warning .metric-value {
            color: #f39c12;
        }
        
        .metric-card.success .metric-value {
            color: #27ae60;
        }
        
        .metric-status {
            font-size: 0.9em;
            padding: 8px 12px;
            border-radius: 4px;
            display: inline-block;
            font-weight: 600;
        }
        
        .status-critical {
            background: #fecaca;
            color: #991b1b;
        }
        
        .status-warning {
            background: #fed7aa;
            color: #92400e;
        }
        
        .status-success {
            background: #bbf7d0;
            color: #065f46;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .chart-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .chart-container canvas {
            max-height: 300px;
        }
        
        .recommendations {
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .recommendations h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        .rec-item {
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
            border-radius: 4px;
        }
        
        .rec-item.critical {
            border-left-color: #e74c3c;
            background: #fff5f5;
        }
        
        .rec-item.warning {
            border-left-color: #f39c12;
            background: #fffbf0;
        }
        
        .rec-item.success {
            border-left-color: #27ae60;
            background: #f0fff4;
        }
        
        .rec-item strong {
            display: block;
            margin-bottom: 5px;
            font-size: 1.1em;
        }
        
        .rec-item p {
            color: #666;
            font-size: 0.9em;
            line-height: 1.5;
        }
        
        .action-items {
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .action-items h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        .action-timeline {
            list-style: none;
        }
        
        .action-timeline li {
            padding: 15px;
            padding-left: 50px;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            position: relative;
            border-left: 3px solid #667eea;
        }
        
        .action-timeline li::before {
            content: "";
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            background: #667eea;
            border-radius: 50%;
            border: 3px solid white;
        }
        
        .timeline-label {
            font-weight: 600;
            color: #667eea;
            font-size: 0.85em;
            text-transform: uppercase;
        }
        
        footer {
            text-align: center;
            color: white;
            padding: 20px;
            font-size: 0.9em;
        }
        
        .benchmark-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .benchmark-table td, .benchmark-table th {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .benchmark-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #667eea;
        }
        
        @media (max-width: 768px) {
            .metrics-grid {
                grid-template-columns: 1fr;
            }
            
            .charts-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Dashboard de KPI - Testing & Calidad</h1>
            <p class="subtitle">Análisis de JIRA LTI - Métricas para Director de Tecnología</p>
            <p class="date">Análisis: 20 de enero de 2026 | Período: Abril 2025 - Octubre 2025</p>
        </header>
        
        <!-- MÉTRICAS PRINCIPALES -->
        <div class="metrics-grid">
            <!-- KPI 1: Test Coverage -->
            <div class="metric-card critical">
                <div class="metric-label">Test Coverage</div>
                <div class="metric-value">15.2%</div>
                <div class="metric-status status-critical">CRÍTICO</div>
                <div style="margin-top: 10px; font-size: 0.85em; color: #999;">
                    145 tests / 956 features
                </div>
            </div>
            
            <!-- KPI 2: Bug Density -->
            <div class="metric-card warning">
                <div class="metric-label">Bug Density</div>
                <div class="metric-value">0.19</div>
                <div class="metric-status status-warning">REQUIERE MEJORA</div>
                <div style="margin-top: 10px; font-size: 0.85em; color: #999;">
                    122 bugs / 632 features
                </div>
            </div>
            
            <!-- KPI 3: Tasa de Resolución de Bugs -->
            <div class="metric-card success">
                <div class="metric-label">Tasa de Resolución Bugs</div>
                <div class="metric-value">77.9%</div>
                <div class="metric-status status-success">BUENO</div>
                <div style="margin-top: 10px; font-size: 0.85em; color: #999;">
                    95 resueltos / 122 total
                </div>
            </div>
            
            <!-- KPI 4: Testing Completion -->
            <div class="metric-card success">
                <div class="metric-label">Testing Completion Rate</div>
                <div class="metric-value">92.6%</div>
                <div class="metric-status status-success">EXCELENTE</div>
                <div style="margin-top: 10px; font-size: 0.85em; color: #999;">
                    25 completadas / 27 total
                </div>
            </div>
            
            <!-- KPI 5: Bloqueos -->
            <div class="metric-card success">
                <div class="metric-label">Índice de Bloqueos</div>
                <div class="metric-value">0.1%</div>
                <div class="metric-status status-success">EXCELENTE</div>
                <div style="margin-top: 10px; font-size: 0.85em; color: #999;">
                    2 bloqueados / 1,403 total
                </div>
            </div>
            
            <!-- Tasa de Completitud General -->
            <div class="metric-card warning">
                <div class="metric-label">Tasa de Completitud General</div>
                <div class="metric-value">62.8%</div>
                <div class="metric-status status-warning">MODERADO</div>
                <div style="margin-top: 10px; font-size: 0.85em; color: #999;">
                    881 completados / 1,403 total
                </div>
            </div>
        </div>
        
        <!-- GRÁFICOS -->
        <div class="charts-grid">
            <!-- Distribución de Issues -->
            <div class="chart-container">
                <div class="chart-title">📈 Distribución de Tipos de Issues</div>
                <canvas id="issueTypeChart"></canvas>
            </div>
            
            <!-- Estado de Tickets -->
            <div class="chart-container">
                <div class="chart-title">📊 Distribución por Estado</div>
                <canvas id="statusChart"></canvas>
            </div>
            
            <!-- Bugs por Estado -->
            <div class="chart-container">
                <div class="chart-title">🐛 Estado de Bugs</div>
                <canvas id="bugStatusChart"></canvas>
            </div>
            
            <!-- Testing Coverage vs No Coverage -->
            <div class="chart-container">
                <div class="chart-title">🔬 Test Coverage: Features con vs sin Tests</div>
                <canvas id="coverageChart"></canvas>
            </div>
        </div>
        
        <!-- RECOMENDACIONES -->
        <div class="recommendations">
            <h2>⚡ Recomendaciones Estratégicas</h2>
            
            <div class="rec-item critical">
                <strong>🔴 CRÍTICO: Aumentar Test Coverage a 85%+</strong>
                <p>
                    Con solo 15.2% de features con tests, el riesgo de defectos es alto.
                    Acción inmediata: Audit de 50 features críticas y crear plan de cobertura.
                    Timeline: Próximas 4 semanas.
                </p>
            </div>
            
            <div class="rec-item critical">
                <strong>🔴 CRÍTICO: Implementar "Definition of Done" v2</strong>
                <p>
                    Requiere que TODA feature tenga test asociado antes de considerar como "Done".
                    Esto previene nuevos features sin cobertura.
                </p>
            </div>
            
            <div class="rec-item warning">
                <strong>🟡 IMPORTANTE: Reducir Bug Density de 0.19 a 0.10</strong>
                <p>
                    Implementar code review obligatorio + CI/CD gates.
                    Invertir en herramientas de análisis estático y testing automatizado.
                </p>
            </div>
            
            <div class="rec-item warning">
                <strong>🟡 IMPORTANTE: Clasificar bugs correctamente</strong>
                <p>
                    Actualmente TODOS están marcados como "Trivial". Revisar severidad real.
                    Establecer SLAs de resolución por severidad.
                </p>
            </div>
            
            <div class="rec-item success">
                <strong>✓ MANTENER: Excelente velocidad de test execution</strong>
                <p>
                    92.6% completitud es excelente. Equipo QA tiene capacidad disponible.
                    Usarla para escalar testing sin aumentar recursos.
                </p>
            </div>
        </div>
        
        <!-- PLAN DE ACCIÓN -->
        <div class="action-items">
            <h2>📋 Plan de Implementación (12 Semanas)</h2>
            <ul class="action-timeline">
                <li>
                    <div class="timeline-label">Semana 1-2</div>
                    <strong>Establecer Baselines & Comunicar</strong>
                    <p>Confirmar datos, crear dashboard, comunicar hallazgos al liderazgo</p>
                </li>
                <li>
                    <div class="timeline-label">Semana 3-4</div>
                    <strong>Testing - PRIORIDAD MÁXIMA</strong>
                    <p>Audit de features sin tests, crear test cases para top 50 críticas, actualizar Definition of Done</p>
                </li>
                <li>
                    <div class="timeline-label">Semana 5-6</div>
                    <strong>Bug Management</strong>
                    <p>Reclasificar bugs, establecer SLAs, asignar owners</p>
                </li>
                <li>
                    <div class="timeline-label">Semana 7-8</div>
                    <strong>Code Quality</strong>
                    <p>Code review obligatorio, CI/CD gates, test coverage minimums</p>
                </li>
                <li>
                    <div class="timeline-label">Semana 9-12</div>
                    <strong>Optimización & Consolidación</strong>
                    <p>Monitoreo semanal de KPIs, ajustes basados en datos, celebrar mejoras</p>
                </li>
            </ul>
        </div>
        
        <!-- BENCHMARKS -->
        <div class="recommendations">
            <h2>🎯 Benchmarks de Industria vs. Valores Actuales</h2>
            <table class="benchmark-table">
                <tr>
                    <th>Métrica</th>
                    <th>Actual</th>
                    <th>Excelente</th>
                    <th>Brecha</th>
                </tr>
                <tr>
                    <td><strong>Test Coverage</strong></td>
                    <td style="color: #e74c3c; font-weight: bold;">15.2%</td>
                    <td>&gt; 85%</td>
                    <td style="color: #e74c3c;">⬇️ -69.8pp</td>
                </tr>
                <tr>
                    <td><strong>Bug Density</strong></td>
                    <td style="color: #f39c12; font-weight: bold;">0.19 bugs/feature</td>
                    <td>&lt; 0.05</td>
                    <td style="color: #f39c12;">⬇️ -73%</td>
                </tr>
                <tr>
                    <td><strong>Testing Completion</strong></td>
                    <td style="color: #27ae60; font-weight: bold;">92.6%</td>
                    <td>&gt; 95%</td>
                    <td style="color: #27ae60;">✓ Cerca</td>
                </tr>
                <tr>
                    <td><strong>Tasa Resolución Bugs</strong></td>
                    <td style="color: #27ae60; font-weight: bold;">77.9%</td>
                    <td>&gt; 90%</td>
                    <td style="color: #f39c12;">⬇️ -12.1pp</td>
                </tr>
                <tr>
                    <td><strong>Índice Bloqueos</strong></td>
                    <td style="color: #27ae60; font-weight: bold;">0.1%</td>
                    <td>&lt; 5%</td>
                    <td style="color: #27ae60;">✓ Excelente</td>
                </tr>
            </table>
        </div>
        
        <footer>
            <p>Dashboard generado automáticamente | Próxima revisión: 24 de enero de 2026</p>
            <p style="margin-top: 10px; font-size: 0.8em;">Para consultas contactar al Director de Calidad</p>
        </footer>
    </div>
    
    <script>
        // Gráfico 1: Distribución de Tipos de Issues
        const issueTypeCtx = document.getElementById('issueTypeChart').getContext('2d');
        new Chart(issueTypeCtx, {
            type: 'doughnut',
            data: {
                labels: ['Stories', 'Tasks', 'Tests', 'Bugs', 'Epics', 'Otros'],
                datasets: [{
                    data: [532, 385, 145, 122, 102, 117],
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#e74c3c',
                        '#3498db',
                        '#95a5a6'
                    ],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        // Gráfico 2: Distribución por Estado
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {
            type: 'bar',
            data: {
                labels: ['Done', 'To Do', 'In Dev', 'In Testing', 'Otros'],
                datasets: [{
                    label: 'Tickets',
                    data: [881, 395, 52, 24, 51],
                    backgroundColor: '#667eea',
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            callback: function(value) {
                                return value + ' tickets';
                            }
                        }
                    }
                }
            }
        });
        
        // Gráfico 3: Estado de Bugs
        const bugStatusCtx = document.getElementById('bugStatusChart').getContext('2d');
        new Chart(bugStatusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Resueltos', 'Pendientes'],
                datasets: [{
                    data: [95, 27],
                    backgroundColor: [
                        '#27ae60',
                        '#e74c3c'
                    ],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        // Gráfico 4: Test Coverage
        const coverageCtx = document.getElementById('coverageChart').getContext('2d');
        new Chart(coverageCtx, {
            type: 'bar',
            data: {
                labels: ['Con Tests', 'Sin Tests'],
                datasets: [{
                    label: 'Features',
                    data: [145, 811],
                    backgroundColor: ['#27ae60', '#95a5a6'],
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

# Guardar el HTML
with open('dashboard_kpi_testing_calidad.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✓ Dashboard HTML creado: dashboard_kpi_testing_calidad.html")
print("  Abrir en navegador para ver visualización interactiva")
