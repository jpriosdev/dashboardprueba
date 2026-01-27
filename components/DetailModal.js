/**
 * DetailModal.js - Refactorizado y alineado
 * Detailed drill-down modal for KPIs and metrics
 * Estructura normalizada SQL/CSV, lógica mejorada, validación robusta
 * Todas las referencias alineadas con nueva estructura de datos
 */
// components/DetailModal.js
import React from 'react';
import { X, TrendingUp, TrendingDown, AlertCircle, CheckCircle, BarChart3, Info, Target, Activity, Users, AlertTriangle, Bug } from 'lucide-react';
import { RecommendationEngine } from '../utils/recommendationEngine';
import ModuleAnalysis from './ModuleAnalysis';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
);

export default function DetailModal({ modal, onClose, recommendations }) {
  if (!modal) return null;

  const { type, title, data, sparklineData, sprints } = modal;

  // Componente de gráfico de líneas usando Chart.js
  const TrendChart = ({ data: chartData, label, color = '#754bde', sprints, yAxisLabel = 'Valor' }) => {
    if (!chartData || chartData.length === 0) return null;
    
    // If there is little data, show warning
    if (chartData.length < 2) {
      return (
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> {label} requires more data points to show a meaningful trend.
          </p>
        </div>
      );
    }
    // If there are few sprints, show warning
    if (!sprints || sprints.length < 2) {
      return (
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> {label} requires multiple sprints to show trend. Select more sprints in the filter.
          </p>
        </div>
      );
    }
    
    const labels = sprints.map(s => s.sprint || s.name || 'Sprint');
    
    // Construir datasets locales a partir del prop `chartData`
    const datasetsLocal = Array.isArray(chartData) ? [{ label, data: chartData, color }] : (chartData && Array.isArray(chartData.datasets) ? chartData.datasets : [{ label, data: chartData || [], color }]);
    const targetsLocal = {}; // no hay targets por defecto aquí

    const validDatasets = (datasetsLocal || [])
      .filter(dataset => dataset.data && dataset.data.length > 0)
      .map((dataset) => {
        const target = targetsLocal?.[dataset.label] || 0;
        const pointColors = dataset.data.map(value => value <= target ? '#10b981' : '#ef4444');
        return {
          label: dataset.label,
          data: dataset.data,
          borderColor: dataset.color,
          backgroundColor: pointColors,
          tension: 0.3,
          fill: false,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: pointColors,
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
          borderWidth: 1.5,
          showLine: true
        };
      });

    if (validDatasets.length === 0) return null;

    const chartConfig = {
      labels: labels,
      datasets: validDatasets
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 10,
            font: {
              size: 11
            },
            generateLabels: function(chart) {
              return (datasetsLocal || []).map((dataset, idx) => ({
                text: `${dataset.label}${targetsLocal[dataset.label] ? ` (target: ${targetsLocal[dataset.label]}d)` : ''}`,
                fillStyle: dataset.color,
                strokeStyle: dataset.color,
                lineWidth: 1.5,
                pointStyle: 'circle',
                datasetIndex: idx
              }));
            }
          }
        },
        title: {
          display: true,
          text: label,
          font: {
            size: 13,
            weight: 'bold',
          },
          padding: {
            bottom: 12
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 10,
          cornerRadius: 6,
          titleFont: {
            size: 12,
            weight: 'bold'
          },
          bodyFont: {
            size: 11
          },
          callbacks: {
            title: function(context) {
              return context[0].label || '';
            },
            label: function(context) {
              const value = context.parsed.y;
              const target = targetsLocal[context.dataset.label] || 0;
              const status = target ? (value <= target ? '✓ Cumple' : '✗ No cumple') : '';
              return `${context.dataset.label}: ${value}${yAxisLabel === 'Días' ? 'd' : ''}${status ? ` (${status})` : ''}`;
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Sprints',
            font: {
              size: 11,
              weight: 'bold'
            }
          },
          grid: {
            display: false
          },
          ticks: {
            font: {
              size: 10
            }
          }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: yAxisLabel,
            font: {
              size: 11,
              weight: 'bold'
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.06)',
            drawBorder: false
          },
          ticks: {
            font: {
              size: 10
            }
          }
        },
      },
    };
    
    return (
      <div className="mt-4 bg-white p-3 rounded-lg border border-gray-200">
        <div className="h-64">
          <Line data={chartConfig} options={options} />
        </div>
      </div>
    );
  };

  // Componente de gráfico con puntos de cumplimiento (verde/rojo según target)
  const TrendChartWithTargets = ({ datasets, label, sprints, yAxisLabel = 'Días', targets = {} }) => {
    if (!datasets || datasets.length === 0) return null;
    
    // Si hay pocos sprints, mostrar advertencia
    if (!sprints || sprints.length < 2) {
      return (
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> {label} requires multiple sprints to show trend. Available sprints: {sprints?.length || 0}
          </p>
        </div>
      );
    }
    
    const labels = sprints.map(s => s.sprint || s.name || 'Sprint');
    
    const validDatasets = datasets
      .filter(dataset => dataset.data && dataset.data.length > 0)
      .map((dataset) => {
        const target = targets?.[dataset.label] || 0;
        const pointColors = dataset.data.map(value => value <= target ? '#10b981' : '#ef4444');
        return {
          label: dataset.label,
          data: dataset.data,
          borderColor: dataset.color,
          backgroundColor: pointColors,
          tension: 0.3,
          fill: false,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: pointColors,
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
          borderWidth: 1.5,
          showLine: true
        };
      });

    if (validDatasets.length === 0) return null;

    const chartConfig = {
      labels: labels,
      datasets: validDatasets
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 10,
            font: {
              size: 11
            },
            generateLabels: function(chart) {
              return datasets.map((dataset, idx) => ({
                text: `${dataset.label}${targets[dataset.label] ? ` (target: ${targets[dataset.label]}d)` : ''}`,
                fillStyle: dataset.color,
                strokeStyle: dataset.color,
                lineWidth: 1.5,
                pointStyle: 'circle',
                datasetIndex: idx
              }));
            }
          }
        },
        title: {
          display: true,
          text: label,
          font: {
            size: 13,
            weight: 'bold',
          },
          padding: {
            bottom: 12
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 10,
          cornerRadius: 6,
          titleFont: {
            size: 12,
            weight: 'bold'
          },
          bodyFont: {
            size: 11
          },
          callbacks: {
            title: function(context) {
              return context[0].label || '';
            },
            label: function(context) {
              const value = context.parsed.y;
              const target = targets[context.dataset.label] || 0;
              const status = target ? (value <= target ? '✓ Cumple' : '✗ No cumple') : '';
              return `${context.dataset.label}: ${value}d${status ? ` (${status})` : ''}`;
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Sprints',
            font: {
              size: 11,
              weight: 'bold'
            }
          },
          grid: { display: false },
          ticks: { font: { size: 10 } }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: { display: true, text: yAxisLabel, font: { size: 11, weight: 'bold' } },
          grid: { color: 'rgba(0,0,0,0.06)', drawBorder: false },
          ticks: { font: { size: 10 } }
        }
      }
    };

    return (
      <div className="mt-4 bg-white p-3 rounded-lg border border-gray-200">
        <div className="h-64">
          <Line data={chartConfig} options={options} />
        </div>
      </div>
    );
  };

  // Componente de gráfico de líneas múltiples usando Chart.js
  const TrendChartMultiple = ({ datasets, label, sprints, yAxisLabel = 'Valor', isPercentage = false }) => {
    if (!datasets || datasets.length === 0) return null;
    
    // Si hay pocos sprints, mostrar advertencia
    if (!sprints || sprints.length < 2) {
      return (
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> {label} requires multiple sprints to show trend. Available sprints: {sprints?.length || 0}
          </p>
        </div>
      );
    }
    
    const validDatasets = datasets.filter(d => d && d.data && d.data.length > 0);
    if (validDatasets.length === 0) return null;
    
    const labels = sprints.map(s => s.sprint || s.name || 'Sprint');
    
    const chartConfig = {
      labels: labels,
      datasets: validDatasets.map(dataset => ({
        label: dataset.label,
        data: dataset.data,
        borderColor: dataset.color,
        backgroundColor: dataset.color,
        tension: 0.4,
        fill: false,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: '#ffffff',
        pointBorderColor: dataset.color,
        pointBorderWidth: 2.5,
        borderWidth: 2.5,
      }))
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 15,
            font: {
              size: 12
            }
          }
        },
        title: {
          display: true,
          text: label,
          font: {
            size: 14,
            weight: 'bold',
          },
          padding: {
            bottom: 15
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          cornerRadius: 8,
          titleFont: {
            size: 13,
            weight: 'bold'
          },
          bodyFont: {
            size: 12
          },
          callbacks: {
            title: function(context) {
              return context[0].label || '';
            },
            label: function(context) {
              const value = context.parsed.y;
              return `${context.dataset.label}: ${value}${isPercentage ? '%' : ''}`;
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Sprints',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          grid: {
            display: false
          },
          ticks: {
            font: {
              size: 11
            }
          }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          beginAtZero: true,
          min: 0,
          title: {
            display: true,
            text: yAxisLabel,
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.06)',
            drawBorder: false
          },
          ticks: {
            font: {
              size: 11
            },
            stepSize: 1,
            callback: function(value) {
              return isPercentage ? `${value}%` : value;
            }
          }
        },
      },
    };
    
    return (
      <div className="mt-4 bg-white p-3 rounded-lg border border-gray-200">
        <div className="h-64">
          <Line data={chartConfig} options={options} />
        </div>
      </div>
    );
  };

  // Specialized chart: Executed vs Planned with percent tooltip
  const ExecutionComparisonChart = ({ executed = [], planned = [], sprints = [] }) => {
    if (!sprints || sprints.length === 0) return null;
    const labels = sprints.map(s => s.sprint || s.name || 'Sprint');

    const chartConfig = {
      labels,
      datasets: [
        {
          label: 'Planned',
          data: planned,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59,130,246,0.08)',
          tension: 0.3,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6,
          borderDash: [6, 4]
        },
        {
          label: 'Executed',
          data: executed,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16,185,129,0.06)',
          tension: 0.3,
          fill: false,
          pointRadius: 5,
          pointHoverRadius: 7
        }
      ]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: true, position: 'top' },
        tooltip: {
          backgroundColor: 'rgba(0,0,0,0.8)',
          callbacks: {
            title: (ctx) => ctx[0]?.label || '',
            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y}`,
            afterBody: (ctx) => {
              const idx = ctx[0]?.dataIndex || 0;
              const exec = Number(executed[idx] || 0);
              const plan = Number(planned[idx] || 0);
              const pct = plan > 0 ? Math.round((exec / plan) * 100) : 0;
              return `Executed/Planned: ${exec}/${plan} (${pct}%)`;
            }
          }
        }
      },
      scales: {
        x: { display: true, title: { display: true, text: 'Sprints' } },
        y: {
          display: true,
          title: { display: true, text: 'Cases' },
          beginAtZero: true,
          min: 0,
          max: 50,
          ticks: { stepSize: 5 }
        }
      }
    };

    return (
      <div className="mt-4 bg-white p-3 rounded-lg border border-gray-200">
        <div className="h-64">
          <Line data={chartConfig} options={options} />
        </div>
      </div>
    );
  };

  const renderCycleTimeDetail = (data) => (
    <div className="space-y-6">
      {/* Resumen general */}
      <div className="bg-orange-50 p-6 rounded-lg border border-orange-200">
        <h3 className="text-2xl font-bold text-executive-600 mb-2">
          {data.avg} days
        </h3>
        <p className="text-sm text-gray-600">Average resolution time</p>
      </div>

      {/* Breakdown by priority */}
      <div>
        <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-executive-600" />
          Cycle Time by Priority
        </h4>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(data.byPriority || {}).map(([priority, days]) => {
            const priorityConfig = {
              critical: { label: 'Critical', color: 'bg-danger-500', target: 3 },
              high: { label: 'High', color: 'bg-warning-500', target: 5 },
              medium: { label: 'Medium', color: 'bg-blue-500', target: 7 },
              low: { label: 'Low', color: 'bg-gray-500', target: 10 }
            };
            const config = priorityConfig[priority];
            if (!config) return null;
            const isGood = days <= config.target;

            return (
              <div key={priority} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <div className="text-sm text-gray-600 mb-1">{config.label}</div>
                <div className="text-2xl font-bold">{days} <span className="text-sm text-gray-500 ml-1">days</span></div>
              
                <div className="mt-2">
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                    <span>Target: {config.target}d</span>
                    <span className={isGood ? 'text-success-600 font-medium' : 'text-warning-600 font-medium'}>
                      {isGood ? '✓ Ok' : `+${days - config.target}d`}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`${config.color} h-2 rounded-full transition-all`}
                      style={{ width: `${Math.min((days / (config.target * 2)) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Gráfico de tendencia con puntos de cumplimiento por prioridad */}
      {sprints && sprints.length > 0 ? (() => {
        // Calcular datos separados por prioridad basado en eficiencia real del sprint
        const criticalData = sprints.map(sprint => {
          const resolutionRate = sprint.bugsResolved / (sprint.bugs || 1);
          const complexity = sprint.bugs / (sprint.velocity || 1);
          return Math.max(2, Math.min(5, Math.round(3 + complexity - resolutionRate * 2)));
        });
        
        const highData = sprints.map(sprint => {
          const resolutionRate = sprint.bugsResolved / (sprint.bugs || 1);
          const complexity = sprint.bugs / (sprint.velocity || 1);
          return Math.max(4, Math.min(8, Math.round(5 + complexity - resolutionRate * 1.5)));
        });
        
        const mediumData = sprints.map(sprint => {
          const resolutionRate = sprint.bugsResolved / (sprint.bugs || 1);
          const complexity = sprint.bugs / (sprint.velocity || 1);
          return Math.max(6, Math.min(12, Math.round(8 + complexity * 1.5 - resolutionRate)));
        });
        
        const lowData = sprints.map(sprint => {
          const resolutionRate = sprint.bugsResolved / (sprint.bugs || 1);
          const complexity = sprint.bugs / (sprint.velocity || 1);
          return Math.max(10, Math.min(18, Math.round(12 + complexity * 2 - resolutionRate * 0.5)));
        });
        
        const datasets = [
          { label: 'Critical', data: criticalData, color: '#dc2626' },
          { label: 'High', data: highData, color: '#f97316' },
          { label: 'Medium', data: mediumData, color: '#3b82f6' },
          { label: 'Low', data: lowData, color: '#9ca3af' }
        ];
        
        const targets = {
          'Critical': 3,
          'High': 5,
          'Medium': 7,
          'Low': 10
        };
        
        return (
          <TrendChartWithTargets 
            datasets={datasets} 
            label="Evolution of Resolution Time by Sprint" 
            sprints={sprints} 
            yAxisLabel="Days"
            targets={targets}
          />
        );
      })() : (
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200 text-yellow-800">
          <p className="text-sm">No sprint data available to display the trend</p>
        </div>
      )}

      {/* Recommendations section */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" />
          Recommendations
        </h4>
        <ul className="space-y-2 text-sm text-blue-800">
          {RecommendationEngine.getRecommendations('cycleTime', data, recommendations).map((rec, idx) => (
            <li key={idx} dangerouslySetInnerHTML={{ __html: `${rec.icon} ${rec.text.includes(':') ? `<strong>${rec.text.split(':')[0]}:</strong>${rec.text.split(':').slice(1).join(':')}` : rec.text}` }} />
          ))}
        </ul>
      </div>
    </div>
  );

  const renderAutomationCoverageDetail = (data) => (
    <div className="space-y-6">
      {/* Resumen general */}
      <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
        <h3 className="text-2xl font-bold text-purple-600 mb-2">
          {data.coverage}%
        </h3>
        <p className="text-sm text-gray-600">Test automation coverage</p>
      </div>

      {/* Main metrics */}
      <div>
        <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-purple-600" />
          Test Distribution
        </h4>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{data.automated}</div>
              <div className="text-xs text-gray-500 mt-1">Automated</div>
              <div className="text-xs text-purple-600 font-medium mt-1">{data.coverage}%</div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600">{data.manual}</div>
              <div className="text-xs text-gray-500 mt-1">Manual</div>
              <div className="text-xs text-gray-600 font-medium mt-1">{100 - data.coverage}%</div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{data.total}</div>
              <div className="text-xs text-gray-500 mt-1">Total Tests</div>
              <div className="text-xs text-blue-600 font-medium mt-1">100%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Niveles de madurez */}
      <div>
        <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
          <Target className="w-5 h-5 mr-2 text-purple-600" />
          Automation Maturity Level
        </h4>
        <div className="space-y-2">
          <div className="flex items-center">
            <div className={`w-full bg-gray-200 rounded-full h-3 relative`}>
              <div className={`h-3 rounded-full transition-all ${
                data.coverage >= 80 ? 'bg-success-500' :
                data.coverage >= 60 ? 'bg-blue-500' :
                data.coverage >= 40 ? 'bg-warning-500' : 'bg-danger-500'
              }`} style={{ width: `${data.coverage}%` }}></div>
              {/* Marcadores de nivel */}
              <div className="absolute top-0 left-[40%] w-0.5 h-3 bg-gray-400"></div>
              <div className="absolute top-0 left-[60%] w-0.5 h-3 bg-gray-400"></div>
              <div className="absolute top-0 left-[80%] w-0.5 h-3 bg-gray-400"></div>
            </div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 px-1">
            <span>0%</span>
            <span className="-ml-2">40%</span>
            <span className="-ml-2">60%</span>
            <span className="-ml-2">80%</span>
            <span>100%</span>
          </div>
          <div className="mt-3 grid grid-cols-4 gap-2 text-xs">
            <div className={`p-2 rounded text-center ${
              data.coverage < 40 ? 'bg-danger-100 text-danger-700 font-semibold' : 'bg-gray-100 text-gray-500'
            }`}>
              <div>Initial</div>
              <div className="text-xs mt-1">&lt;40%</div>
            </div>
            <div className={`p-2 rounded text-center ${
              data.coverage >= 40 && data.coverage < 60 ? 'bg-warning-100 text-warning-700 font-semibold' : 'bg-gray-100 text-gray-500'
            }`}>
              <div>Basic</div>
              <div className="text-xs mt-1">40-59%</div>
            </div>
            <div className={`p-2 rounded text-center ${
              data.coverage >= 60 && data.coverage < 80 ? 'bg-blue-100 text-blue-700 font-semibold' : 'bg-gray-100 text-gray-500'
            }`}>
              <div>Advanced</div>
              <div className="text-xs mt-1">60-79%</div>
            </div>
            <div className={`p-2 rounded text-center ${
              data.coverage >= 80 ? 'bg-success-100 text-success-700 font-semibold' : 'bg-gray-100 text-gray-500'
            }`}>
              <div>Optimal</div>
              <div className="text-xs mt-1">≥80%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Gráfico de tendencia */}
      {data.trend && data.trend.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">Automation Coverage Evolution by Sprint</h4>
          <TrendChartMultiple 
            datasets={[{ 
              label: 'Automation Coverage', 
              data: data.trend, 
              color: '#9333ea' 
            }]} 
            label="Coverage (%)" 
            sprints={sprints}
            isPercentage={true}
          />
        </div>
      )}

      {/* Beneficios e Impacto */}
      <div>
        <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
          <CheckCircle className="w-5 h-5 mr-2 text-purple-600" />
          Benefits of Increased Automation
        </h4>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-purple-50 p-3 rounded-lg border border-purple-100">
            <div className="flex items-start">
              <TrendingUp className="w-4 h-4 text-purple-600 mt-0.5 mr-2" />
              <div>
                <div className="text-sm font-medium text-purple-900">Speed</div>
                <div className="text-xs text-purple-700 mt-1">Faster test execution</div>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 p-3 rounded-lg border border-purple-100">
            <div className="flex items-start">
              <Activity className="w-4 h-4 text-purple-600 mt-0.5 mr-2" />
              <div>
                <div className="text-sm font-medium text-purple-900">Consistency</div>
                <div className="text-xs text-purple-700 mt-1">Reproducible results</div>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 p-3 rounded-lg border border-purple-100">
            <div className="flex items-start">
              <Users className="w-4 h-4 text-purple-600 mt-0.5 mr-2" />
              <div>
                <div className="text-sm font-medium text-purple-900">Resources</div>
                <div className="text-xs text-purple-700 mt-1">QA focused on strategic tasks</div>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 p-3 rounded-lg border border-purple-100">
            <div className="flex items-start">
              <AlertTriangle className="w-4 h-4 text-purple-600 mt-0.5 mr-2" />
              <div>
                <div className="text-sm font-medium text-purple-900">Detection</div>
                <div className="text-xs text-purple-700 mt-1">Bugs found earlier</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations section (generic) */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" />
          Recommendations
        </h4>
        <ul className="space-y-2 text-sm text-blue-800">
          {data.coverage < 40 && (
            <>
              <li>⚠️ <strong>High Priority:</strong> Define an automation strategy and identify critical cases to automate first.</li>
              <li>🛠️ <strong>Infrastructure:</strong> Establish an automation framework (Selenium, Cypress, Playwright) and CI/CD.</li>
              <li>🎯 <strong>Goal:</strong> Reach 40% in 2 sprints by automating main regression cases.</li>
            </>
          )}
          {data.coverage >= 40 && data.coverage < 60 && (
            <>
              <li>📈 <strong>Continue Growth:</strong> Automate integration test cases and main workflows.</li>
              <li>🔄 <strong>Regression:</strong> Prioritize automation of regression cases to reduce execution time.</li>
              <li>🎯 <strong>Goal:</strong> Reach 60% in 3 sprints with focus on critical tests.</li>
            </>
          )}
          {data.coverage >= 60 && data.coverage < 80 && (
            <>
              <li>✅ <strong>Good Level:</strong> Maintain coverage and expand to API and component tests.</li>
              <li>🔍 <strong>Optimization:</strong> Review and refactor existing tests to improve maintainability.</li>
              <li>🎯 <strong>Goal:</strong> Reach 80% in 4 sprints including edge case tests.</li>
            </>
          )}
          {data.coverage >= 80 && (
            <>
              <li>🏆 <strong>Excellent Coverage:</strong> Maintain optimal level and focus on test quality.</li>
              <li>🛡️ <strong>Maintenance:</strong> Review tests regularly, remove redundancies and update according to changes.</li>
              <li>📊 <strong>Monitoring:</strong> Analyze effectiveness metrics (bugs detected by automated tests).</li>
            </>
          )}
        </ul>
      </div>
    </div>
  );

  const renderDefectDensityDetail = (data) => (
    <div className="space-y-6">
      {/* Resumen general */}
      <div className="bg-orange-50 p-6 rounded-lg border border-orange-200">
        <h3 className="text-2xl font-bold text-orange-600 mb-2">
          {data.avg} bugs/sprint
        </h3>
        <p className="text-sm text-gray-600">Average bugs detected per sprint</p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Total Bugs</div>
          <div className="text-2xl font-bold text-gray-900">{data.total}</div>
          <div className="text-xs text-gray-500 mt-1">En {data.sprints} sprints</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Maximum</div>
          <div className="text-2xl font-bold text-danger-600">{data.max}</div>
          <div className="text-xs text-gray-500 mt-1">Worst sprint</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Minimum</div>
          <div className="text-2xl font-bold text-success-600">{data.min}</div>
          <div className="text-xs text-gray-500 mt-1">Best sprint</div>
        </div>
      </div>

      {/* Quality analysis */}
      <div>
        <h4 className="font-semibold text-gray-800 mb-3">Process Quality Analysis</h4>
        <div className="space-y-3">
          {data.avg <= 15 && (
            <div className="flex items-start p-3 bg-success-50 rounded-lg border border-success-200">
              <CheckCircle className="w-5 h-5 text-success-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <div className="font-medium text-success-900">Exceptional Quality</div>
                <div className="text-sm text-success-700">Low defect density per sprint. Development process is robust and quality practices are effective.</div>
              </div>
            </div>
          )}
          {data.avg > 15 && data.avg <= 25 && (
            <div className="flex items-start p-3 bg-blue-50 rounded-lg border border-blue-200">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <div className="font-medium text-blue-900">Acceptable Quality</div>
                <div className="text-sm text-blue-700">Density within normal range for agile development. Maintain current testing and code review practices.</div>
              </div>
            </div>
          )}
          {data.avg > 25 && data.avg <= 35 && (
            <div className="flex items-start p-3 bg-warning-50 rounded-lg border border-warning-200">
              <AlertCircle className="w-5 h-5 text-warning-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <div className="font-medium text-warning-900">Attention Required</div>
                <div className="text-sm text-warning-700">High defect density. Consider increasing unit test coverage and code review before QA.</div>
              </div>
            </div>
          )}
          {data.avg > 35 && (
            <div className="flex items-start p-3 bg-danger-50 rounded-lg border border-danger-200">
              <AlertCircle className="w-5 h-5 text-danger-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <div className="font-medium text-danger-900">Critical Level</div>
                <div className="text-sm text-danger-700">Very high density. Requires immediate intervention: review development process, increase pre-testing and root cause analysis.</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Benchmark */}
      <div>
        <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">Reference Ranges
          <div className="group relative">
            <Info className="w-4 h-4 text-gray-400 cursor-help" />
            <div className="absolute left-0 top-6 hidden group-hover:block bg-gray-900 text-white text-xs rounded-lg p-3 shadow-lg z-50 w-80">
              <div className="font-semibold mb-1">💡 Configurable References</div>
              <div className="text-gray-200">
                These values are configurable references depending on the project context.
                They depend on: product complexity, team maturity, automation level,
                sprint scope and feature types. Set your own targets based on historical capacity
                and adjust periodically.
              </div>
            </div>
          </div>
        </h4>
        <div className="grid grid-cols-4 gap-3 text-center">
          <div className="p-3 bg-success-50 rounded-lg">
            <div className="text-xs text-success-700 font-medium mb-1">Excellent</div>
            <div className="text-sm font-bold text-success-600">≤ 15</div>
            <div className="text-xs text-success-600 mt-1">bugs/sprint</div>
          </div>
          <div className="p-3 bg-blue-50 rounded-lg">
            <div className="text-xs text-blue-700 font-medium mb-1">Good</div>
            <div className="text-sm font-bold text-blue-600">16 - 25</div>
            <div className="text-xs text-blue-600 mt-1">bugs/sprint</div>
          </div>
          <div className="p-3 bg-warning-50 rounded-lg">
            <div className="text-xs text-warning-700 font-medium mb-1">Needs Improvement</div>
            <div className="text-sm font-bold text-warning-600">26 - 35</div>
            <div className="text-xs text-warning-600 mt-1">bugs/sprint</div>
          </div>
          <div className="p-3 bg-danger-50 rounded-lg">
            <div className="text-xs text-danger-700 font-medium mb-1">Critical</div>
            <div className="text-sm font-bold text-danger-600">&gt; 35</div>
            <div className="text-xs text-danger-600 mt-1">bugs/sprint</div>
          </div>
        </div>
      </div>
      
      {/* Gráfico de tendencia */}
      <TrendChart data={sparklineData} label="Bug Evolution by Sprint" color="#f97316" sprints={sprints} yAxisLabel="Bugs" />

      {/* Recommended actions */}
      <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
        <h4 className="font-semibold text-orange-900 mb-2 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" />
          Recommended Actions
        </h4>
        <ul className="space-y-2 text-sm text-orange-800">
          {data.avg > 30 && (
            <>
              <li>⚠️ <strong>Urgent:</strong> Analyze root causes of high bug density. Review development and unit testing process.</li>
              <li>🔍 <strong>Code Review:</strong> Implement or strengthen code reviews before moving to QA.</li>
              <li>🧪 <strong>Preventive Testing:</strong> Increase unit and integration test coverage during development.</li>
            </>
          )}
          {data.avg > 20 && data.avg <= 30 && (
            <>
              <li>📊 <strong>Monitoring:</strong> Identify modules or features with higher bug density and focus improvements.</li>
              <li>🎯 <strong>Prevention:</strong> Establish stricter Definition of Done before passing to QA.</li>
              <li>🤝 <strong>Collaboration:</strong> Pair programming sessions in complex areas to reduce errors.</li>
            </>
          )}
          {data.avg <= 20 && (
            <>
              <li>✅ <strong>Maintain:</strong> Continue current practices that are delivering good results.</li>
              <li>📈 <strong>Optimize:</strong> Look for automation opportunities to detect bugs earlier.</li>
              <li>🎓 <strong>Share:</strong> Document and share best practices with the team.</li>
            </>
          )}
        </ul>
      </div>
    </div>
  );

  const renderTestCasesDetail = (data) => (
    <div className="space-y-6">
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="text-2xl font-bold text-blue-600 mb-2">
          {data.avg} test cases/sprint
        </h3>
        <p className="text-sm text-gray-600">Average test cases executed per sprint</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="text-sm text-gray-600 mb-1">Total Executed</div>
          <div className="text-2xl font-bold text-gray-900">{data.total}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="text-sm text-gray-600 mb-1">Sprints Analyzed</div>
          <div className="text-2xl font-bold text-gray-900">{data.sprints}</div>
        </div>
      </div>

      <div>
          <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">Test Coverage Scale
          <div className="group relative">
            <Info className="w-4 h-4 text-gray-400 cursor-help" />
            <div className="absolute left-0 top-6 hidden group-hover:block bg-gray-900 text-white text-xs rounded-lg p-3 shadow-lg z-50 w-80">
              <div className="font-semibold mb-1">💡 Configurable References</div>
              <div className="text-gray-200">
                These values are configurable references, not industry standards.
                They assume a QA team of 2-3 testers in a 2-week sprint. Optimal numbers vary by team size,
                product complexity, sprint duration, automation level and test types. Set targets based on
                historical team capacity and adjust periodically.
              </div>
            </div>
          </div>
        </h4>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="p-3 bg-success-50 rounded-lg">
            <div className="text-xs text-success-700 font-medium mb-1">Excellent</div>
            <div className="text-sm font-bold text-success-600">≥ 170</div>
          </div>
          <div className="p-3 bg-blue-50 rounded-lg">
            <div className="text-xs text-blue-700 font-medium mb-1">Good</div>
            <div className="text-sm font-bold text-blue-600">120-169</div>
          </div>
          <div className="p-3 bg-warning-50 rounded-lg">
            <div className="text-xs text-warning-700 font-medium mb-1">Improvement Needed</div>
            <div className="text-sm font-bold text-warning-600">&lt; 120</div>
          </div>
        </div>
      </div>
      
      {/* Trend chart */}
      <TrendChart data={sparklineData} label="Evolution of Executed Test Cases by Sprint" color="#60a5fa" sprints={sprints} yAxisLabel="Cases" />

      {/* Recommendations (test cases) */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" />
          Recommendations
        </h4>
        <ul className="space-y-2 text-sm text-blue-800">
          {RecommendationEngine.getRecommendations('testCases', data, recommendations).map((rec, idx) => (
            <li key={idx} dangerouslySetInnerHTML={{ __html: `${rec.icon} ${rec.text.includes(':') ? `<strong>${rec.text.split(':')[0]}:</strong>${rec.text.split(':').slice(1).join(':')}` : rec.text}` }} />
          ))}
        </ul>
      </div>
    </div>
  );

  const renderResolutionEfficiencyDetail = (data) => (
    <div className="space-y-6">
      <div className="bg-green-50 p-6 rounded-lg border border-green-200">
        <h3 className="text-2xl font-bold text-success-600 mb-2">
          {data.efficiency}%
        </h3>
        <p className="text-sm text-gray-600">Resolution Efficiency</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Total Bugs</div>
          <div className="text-2xl font-bold text-gray-900">{data.total}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Resolved Bugs</div>
          <div className="text-2xl font-bold text-success-600">{data.resolved}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Pending Bugs</div>
          <div className="text-2xl font-bold text-warning-600">{data.pending}</div>
        </div>
      </div>

      <div>
        <h4 className="font-semibold text-gray-800 mb-3">Capacity Analysis</h4>
        <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
          <div
            className="bg-green-500 h-4 rounded-full transition-all flex items-center justify-end pr-2"
            style={{ width: `${data.efficiency}%` }}
          >
            <span className="text-xs font-bold text-white">{data.efficiency}%</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="p-3 bg-success-50 rounded-lg">
          <div className="text-xs text-success-700 font-medium mb-1">Excellent</div>
          <div className="text-sm font-bold text-success-600">≥ 80%</div>
        </div>
        <div className="p-3 bg-blue-50 rounded-lg">
          <div className="text-xs text-blue-700 font-medium mb-1">Good</div>
          <div className="text-sm font-bold text-blue-600">70-79%</div>
        </div>
        <div className="p-3 bg-warning-50 rounded-lg">
          <div className="text-xs text-warning-700 font-medium mb-1">Improvement Needed</div>
          <div className="text-sm font-bold text-warning-600">&lt; 70%</div>
        </div>
      </div>
      
      {/* Gráfico de tendencia por criticidad */}
      {(() => {
        // Calcular eficiencia de resolución por criticidad
        const masAltaEfficiency = sprints ? sprints.map(sprint => {
          const sprintBugs = sprint.bugs || 0;
          const masAltaTotal = Math.round(sprintBugs * 0.05);
          const masAltaResolved = Math.round(masAltaTotal * (sprint.bugsResolved / (sprint.bugs || 1)));
          return masAltaTotal > 0 ? Math.round((masAltaResolved / masAltaTotal) * 100) : 0;
        }) : [];
        
        const altaEfficiency = sprints ? sprints.map(sprint => {
          const sprintBugs = sprint.bugs || 0;
          const altaTotal = Math.round(sprintBugs * 0.30);
          const altaResolved = Math.round(altaTotal * (sprint.bugsResolved / (sprint.bugs || 1)));
          return altaTotal > 0 ? Math.round((altaResolved / altaTotal) * 100) : 0;
        }) : [];
        
        const mediaEfficiency = sprints ? sprints.map(sprint => {
          const sprintBugs = sprint.bugs || 0;
          const mediaTotal = Math.round(sprintBugs * 0.55);
          const mediaResolved = Math.round(mediaTotal * (sprint.bugsResolved / (sprint.bugs || 1)));
          return mediaTotal > 0 ? Math.round((mediaResolved / mediaTotal) * 100) : 0;
        }) : [];
        
        const bajaEfficiency = sprints ? sprints.map(sprint => {
          const sprintBugs = sprint.bugs || 0;
          const bajaTotal = Math.round(sprintBugs * 0.08);
          const bajaResolved = Math.round(bajaTotal * (sprint.bugsResolved / (sprint.bugs || 1)));
          return bajaTotal > 0 ? Math.round((bajaResolved / bajaTotal) * 100) : 0;
        }) : [];
        
        const masBajaEfficiency = sprints ? sprints.map(sprint => {
          const sprintBugs = sprint.bugs || 0;
          const masBajaTotal = Math.round(sprintBugs * 0.02);
          const masBajaResolved = Math.round(masBajaTotal * (sprint.bugsResolved / (sprint.bugs || 1)));
          return masBajaTotal > 0 ? Math.round((masBajaResolved / masBajaTotal) * 100) : 0;
        }) : [];
        
        const datasets = [
          {
            label: 'Major',
            data: masAltaEfficiency,
            color: '#dc2626'
          },
          {
            label: 'High',
            data: altaEfficiency,
            color: '#f97316'
          },
          {
            label: 'Medium',
            data: mediaEfficiency,
            color: '#3b82f6'
          },
          {
            label: 'Low',
            data: bajaEfficiency,
            color: '#a3a3a3'
          },
          {
            label: 'Trivial',
            data: masBajaEfficiency,
            color: '#d4d4d4'
          }
        ];
        
        return (
          <TrendChartMultiple 
            datasets={datasets} 
            label="Evolution of Resolution Efficiency by Criticality" 
            sprints={sprints} 
            yAxisLabel="Percentage (%)"
            isPercentage={true}
          />
        );
      })()}

      {/* Recomendaciones al final */}
      <div className="bg-success-50 p-4 rounded-lg border border-success-200">
        <h4 className="font-semibold text-success-900 mb-2 flex items-center">
          <CheckCircle className="w-5 h-5 mr-2" />
          Recommendations
        </h4>
        <ul className="space-y-2 text-sm text-success-800">
          {RecommendationEngine.getRecommendations('resolutionEfficiency', data, recommendations).map((rec, idx) => (
            <li key={idx} dangerouslySetInnerHTML={{ __html: `${rec.icon} ${rec.text.includes(':') ? `<strong>${rec.text.split(':')[0]}:</strong>${rec.text.split(':').slice(1).join(':')}` : rec.text}` }} />
          ))}
        </ul>
      </div>
    </div>
  );

  const renderRegressionRateDetail = (data) => (
    <div className="space-y-6">
      {/* Resumen general */}
      <div className="bg-orange-50 p-6 rounded-lg border border-orange-200">
        <h3 className="text-2xl font-bold text-orange-600 mb-2">
          {data.regressionRate}%
        </h3>
        <p className="text-sm text-gray-600">Regression rate (reopened findings)</p>
      </div>

      {/* Métricas de detalles */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Reopened Findings</span>
            <TrendingUp className="w-4 h-4 text-orange-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-gray-900">{data.reopened || 0}</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Closed Findings</span>
            <CheckCircle className="w-4 h-4 text-success-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-gray-900">{data.closed || 0}</span>
          </div>
        </div>
      </div>

      {/* Interpretation */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
          <Info className="w-4 h-4 mr-2" />
          Interpretation
        </h4>
        <div className="text-sm text-blue-800 space-y-1">
          {data.regressionRate <= 2 && (
            <>
              <p>✓ <strong>Excellent:</strong> Less than 2% regression indicates high-quality fixes.</p>
              <p>The team is resolving findings correctly on the first attempt.</p>
            </>
          )}
          {data.regressionRate > 2 && data.regressionRate <= 5 && (
            <>
              <p>⚠️ <strong>Acceptable:</strong> Between 2-5% is normal but requires attention.</p>
              <p>Consider reviewing the pre-closure testing process for findings.</p>
            </>
          )}
          {data.regressionRate > 5 && (
            <>
              <p>🔴 <strong>Critical:</strong> More than 5% indicates quality issues in fixes.</p>
              <p>Implement mandatory technical review before closing critical findings.</p>
            </>
          )}
        </div>
      </div>

      {/* Gráfico de tendencia */}
      {sparklineData && sprints && (
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <TrendChart
            data={sparklineData}
            label="Regression Rate by Sprint"
            color="#f97316"
            sprints={sprints}
            yAxisLabel="%"
          />
        </div>
      )}

      {/* Recomendaciones */}
      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
        <h4 className="font-semibold text-gray-800 mb-3">Recommendations to Reduce Regression</h4>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>✓ Execute related test cases after each fix</li>
          <li>✓ Review code changes with mandatory peer review</li>
          <li>✓ Automate regression tests for critical findings</li>
          <li>✓ Document root cause of each reopened finding</li>
          <li>✓ Training in root cause analysis (RCA)</li>
        </ul>
      </div>
    </div>
  );

  const renderTestExecutionRateDetail = (data) => (
    <div className="space-y-6">
      {/* Resumen general */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="text-2xl font-bold text-blue-600 mb-2">
          {data.executionRate}%
        </h3>
        <p className="text-sm text-gray-600">Test case execution rate</p>
      </div>

      {/* Métricas de detalles */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">Executed</span>
              <CheckCircle className="w-4 h-4 text-success-500" />
            </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-gray-900">{data.executed || 0}</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Planned</span>
            <Target className="w-4 h-4 text-blue-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-gray-900">{data.planned || 0}</span>
          </div>
        </div>
      </div>

      {/* Barra de progreso */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Execution Coverage</span>
          <span className="text-sm font-bold text-blue-600">{data.executionRate}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all"
            style={{ width: `${Math.min(data.executionRate, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Interpretation */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
          <Info className="w-4 h-4 mr-2" />
          Interpretation
        </h4>
        <div className="text-sm text-blue-800 space-y-1">
          {data.executionRate >= 95 && (
            <>
              <p>✓ <strong>Excellent:</strong> Above 95% coverage is the ideal target.</p>
              <p>Almost all planned test cases are being executed.</p>
            </>
          )}
          {data.executionRate >= 80 && data.executionRate < 95 && (
            <>
              <p>⚠️ <strong>Acceptable:</strong> Between 80-95% requires improvement.</p>
              <p>Investigate why not all planned test cases were executed.</p>
            </>
          )}
          {data.executionRate < 80 && (
            <>
              <p>🔴 <strong>Critical:</strong> Less than 80% is insufficient.</p>
              <p>Too many test cases are being skipped. Requires immediate action.</p>
            </>
          )}
        </div>
      </div>

      {/* Trend chart */}
      {/* Combined chart: Planned vs Executed (single chart, y-axis max 50) */}
      {data.plannedSeries && data.executedSeries && sprints && sprints.length > 0 && (
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <ExecutionComparisonChart
            planned={data.plannedSeries}
            executed={data.executedSeries}
            sprints={sprints}
          />
        </div>
      )}

      {/* Recommendations by severity */}
      <div className="bg-red-50 p-4 rounded-lg border border-red-200">
        <h4 className="font-semibold text-red-900 mb-3">Recommended Actions by Severity</h4>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>📊 Maintaining coverage ≥95% is critical for complete validation</li>
          <li>🔍 Analyze why test cases are skipped (resources, time, blocking defects)</li>
          <li>⏱️ If there are changes, document the impact on test scope</li>
          <li>✓ Implement automation to increase coverage</li>
        </ul>
      </div>
    </div>
  );

  const renderRiskMatrixDetail = (data) => (
    <div className="space-y-6">
      {/* Resumen general */}
      <div className="bg-red-50 p-6 rounded-lg border border-red-200">
        <h3 className="text-2xl font-bold text-red-600 mb-2">
          {data.critical || 0} Critical Findings
        </h3>
        <p className="text-sm text-gray-600">Distribution of criticality by severity</p>
      </div>

      {/* Matriz de desglose por prioridad */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-danger-50 p-4 rounded-lg border-2 border-danger-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-danger-800">Major</span>
            <AlertTriangle className="w-4 h-4 text-danger-600" />
          </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-danger-600">{data.critical || 0}</span>
          </div>
        </div>

        <div className="bg-warning-50 p-4 rounded-lg border-2 border-warning-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-warning-800">Alta</span>
            <AlertCircle className="w-4 h-4 text-warning-600" />
          </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-warning-600">{data.high || 0}</span>
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-800">Media</span>
          </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-blue-600">{data.medium || 0}</span>
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Baja</span>
          </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-gray-600">{data.low || 0}</span>
          </div>
        </div>
      </div>

      {/* Gráfico circular con todas las severidades */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <h4 className="font-semibold text-gray-800 mb-3">Distribution by Severity</h4>
        <div className="flex flex-col md:flex-row gap-6 items-center">
          {/* Gráfico circular SVG */}
          <div className="flex-shrink-0">
            <svg width="200" height="200" viewBox="0 0 200 200" className="mx-auto">
              {(() => {
                const masAlta = data.critical || 0;
                const alta = data.high || 0;
                const media = data.medium || 0;
                const baja = data.low || 0;
                const total = masAlta + alta + media + baja || 1;
                
                const colors = {
                  'Major': '#dc2626',
                  'High': '#f59e0b',
                  'Medium': '#3b82f6',
                  'Low': '#9ca3af'
                };

                const values = [
                  { label: 'Major', value: masAlta, color: colors['Major'] },
                  { label: 'High', value: alta, color: colors['High'] },
                  { label: 'Medium', value: media, color: colors['Medium'] },
                  { label: 'Low', value: baja, color: colors['Low'] }
                ].filter(v => v.value > 0);
                
                let currentAngle = -90;
                const centerX = 100;
                const centerY = 100;
                const radius = 70;
                
                return (
                  <g>
                    {values.map((item, idx) => {
                      const percentage = (item.value / total) * 100;
                      const angle = (percentage / 100) * 360;
                      const startAngle = currentAngle;
                      const endAngle = currentAngle + angle;
                      
                      const startRad = (startAngle * Math.PI) / 180;
                      const endRad = (endAngle * Math.PI) / 180;
                      
                      const x1 = centerX + radius * Math.cos(startRad);
                      const y1 = centerY + radius * Math.sin(startRad);
                      const x2 = centerX + radius * Math.cos(endRad);
                      const y2 = centerY + radius * Math.sin(endRad);
                      
                      const largeArc = angle > 180 ? 1 : 0;
                      
                      const path = `M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;
                      
                      currentAngle = endAngle;
                      
                      return (
                        <path
                          key={idx}
                          d={path}
                          fill={item.color}
                          stroke="#ffffff"
                          strokeWidth="2"
                        />
                      );
                    })}
                  </g>
                );
              })()}
            </svg>
          </div>

          {/* Leyenda */}
          <div className="flex-1">
            {(() => {
              const masAlta = data.critical || 0;
              const alta = data.high || 0;
              const media = data.medium || 0;
              const baja = data.low || 0;
              const total = masAlta + alta + media + baja || 1;
              
              const items = [
                { label: 'Major', value: masAlta, color: 'bg-danger-500' },
                { label: 'High', value: alta, color: 'bg-warning-500' },
                { label: 'Medium', value: media, color: 'bg-blue-500' },
                { label: 'Low', value: baja, color: 'bg-gray-500' }
              ];

              const bgColorMap = {
                'Major': 'bg-red-50',
                'High': 'bg-orange-50',
                'Medium': 'bg-blue-50',
                'Low': 'bg-gray-50'
              };

              const textColorMap = {
                'Major': 'text-red-700',
                'High': 'text-orange-700',
                'Medium': 'text-blue-700',
                'Low': 'text-gray-700'
              };
              
              return (
                <div className="space-y-2">
                  {items.map((item, idx) => (
                    <div key={idx} className={`flex items-center justify-between p-2 rounded ${bgColorMap[item.label]}`}>
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${item.color}`}></div>
                        <span className={`text-sm font-medium ${textColorMap[item.label]}`}>{item.label}</span>
                      </div>
                      <span className={`text-sm font-semibold ${textColorMap[item.label]}`}>
                        {item.value} ({total > 0 ? Math.round((item.value / total) * 100) : 0}%)
                      </span>
                    </div>
                  ))}
                </div>
              );
            })()}
          </div>
        </div>
        <div className="mt-3 p-2 bg-gray-50 rounded border border-gray-200 text-xs text-gray-700">
          <p><strong>Total:</strong> {(data.critical || 0) + (data.high || 0) + (data.medium || 0) + (data.low || 0)} hallazgos</p>
          <p className="text-xs mt-1">🔴 Critical Risk (Major + High): {(data.critical || 0) + (data.high || 0)}</p>
        </div>
      </div>

      {/* Gráfico de tendencia de Hallazgos Críticos - Todas las severidades */}
      {sprints && sprints.length > 0 && (
        <div className="bg-white p-2 rounded-lg border border-gray-200">
          <h5 className="text-xs font-semibold text-gray-700 mb-2 px-2">Critical Findings by Sprint</h5>
          <div className="h-40">
          {(() => {
            // Generar datos por severidad desde los sprints
            const sprintLabels = sprints.map(s => s.sprint || s.name || 'Sprint');
            
            // Estimate distribution of findings by severity in each sprint
            // Usar proporción actual para interpolar datos históricos
            const total = (data.critical || 0) + (data.high || 0) + (data.medium || 0) + (data.low || 0);
            const critPct = total > 0 ? (data.critical || 0) / total : 0.25;
            const altPct = total > 0 ? (data.high || 0) / total : 0.25;
            const medPct = total > 0 ? (data.medium || 0) / total : 0.25;
            const bajPct = total > 0 ? (data.low || 0) / total : 0.25;
            
            // Extraer bugs por sprint
            const criticoData = sprints.map(sprint => {
              const totalBugs = sprint.bugs || 0;
              return Math.round(totalBugs * critPct);
            });
            
            const altoData = sprints.map(sprint => {
              const totalBugs = sprint.bugs || 0;
              return Math.round(totalBugs * altPct);
            });
            
            const mediaData = sprints.map(sprint => {
              const totalBugs = sprint.bugs || 0;
              return Math.round(totalBugs * medPct);
            });
            
            const bajaData = sprints.map(sprint => {
              const totalBugs = sprint.bugs || 0;
              return Math.round(totalBugs * bajPct);
            });
            
            const chartData = {
              labels: sprintLabels,
              datasets: [
                {
                  label: 'Major',
                  data: criticoData,
                  borderColor: '#dc2626',
                  backgroundColor: 'rgba(220, 38, 38, 0.1)',
                  borderWidth: 2,
                  tension: 0.4,
                  fill: false,
                  pointBackgroundColor: '#dc2626',
                  pointRadius: 3.5,
                  pointHoverRadius: 5
                },
                {
                  label: 'High',
                  data: altoData,
                  borderColor: '#f59e0b',
                  backgroundColor: 'rgba(245, 158, 11, 0.1)',
                  borderWidth: 2,
                  tension: 0.4,
                  fill: false,
                  pointBackgroundColor: '#f59e0b',
                  pointRadius: 3.5,
                  pointHoverRadius: 5
                },
                {
                  label: 'Medium',
                  data: mediaData,
                  borderColor: '#3b82f6',
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                  borderWidth: 2,
                  tension: 0.4,
                  fill: false,
                  pointBackgroundColor: '#3b82f6',
                  pointRadius: 3.5,
                  pointHoverRadius: 5
                },
                {
                  label: 'Low',
                  data: bajaData,
                  borderColor: '#9ca3af',
                  backgroundColor: 'rgba(156, 163, 175, 0.1)',
                  borderWidth: 2,
                  tension: 0.4,
                  fill: false,
                  pointBackgroundColor: '#9ca3af',
                  pointRadius: 3.5,
                  pointHoverRadius: 5
                }
              ]
            };
            
            const chartOptions = {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: 'top',
                  labels: {
                    font: { size: 10 },
                    padding: 8,
                    usePointStyle: true,
                    boxWidth: 6
                  }
                },
                tooltip: {
                  mode: 'index',
                  intersect: false,
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  padding: 8,
                  cornerRadius: 6,
                  callbacks: {
                    title: function(context) {
                      return context[0].label;
                    },
                    label: function(context) {
                      return context.dataset.label + ': ' + context.parsed.y;
                    }
                  }
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    stepSize: 1,
                    font: { size: 10 }
                  },
                  grid: {
                    color: 'rgba(0, 0, 0, 0.04)'
                  }
                },
                x: {
                  ticks: {
                    font: { size: 10 }
                  },
                  grid: {
                    display: false
                  }
                }
              }
            };
            
            return <Line data={chartData} options={chartOptions} />;
          })()}
          </div>
        </div>
      )}

      {/* Recomendaciones */}
      <div className="bg-red-50 p-4 rounded-lg border border-red-200">
        <h4 className="font-semibold text-red-900 mb-3">Acciones Recomendadas por Severidad</h4>
        <ul className="space-y-2 text-sm text-red-800">
          <li>🔴 <strong>Más Alta:</strong> Resolver TODOS antes de cualquier release</li>
          <li>🟠 <strong>Alta:</strong> Priorizar en las siguientes 2 semanas</li>
          <li>🔵 <strong>Media:</strong> Planificar resolución en el siguiente sprint</li>
          <li>⚪ <strong>Baja:</strong> Agendar para cuando haya capacidad disponible</li>
          <li>📈 Tendencia: Evitar que Más Alta y Alta crezcan sprint a sprint</li>
        </ul>
      </div>
    </div>
  );

  const renderBugLeakageRateDetail = (data) => (
    <div className="space-y-6">
      {/* Resumen general */}
      <div className="bg-red-50 p-6 rounded-lg border border-red-200">
        <h3 className="text-2xl font-bold text-red-600 mb-2">
          {data.leakageRate}%
        </h3>
        <p className="text-sm text-gray-600">Findings that escaped to production</p>
      </div>

      {/* Métricas de detalles */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">In Production</span>
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-gray-900">{data.productionBugs || 0}</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Total Findings</span>
            <Bug className="w-4 h-4 text-warning-500" />
          </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-gray-900">{data.totalBugs || 0}</span>
          </div>
        </div>
      </div>

      {/* Barra de progreso */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Leak Rate</span>
          <span className="text-sm font-bold text-red-600">{data.leakageRate}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-red-500 to-red-600 h-3 rounded-full transition-all"
            style={{ width: `${Math.min(data.leakageRate, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Interpretación */}
      <div className="bg-red-50 p-4 rounded-lg border border-red-200">
        <h4 className="font-semibold text-red-900 mb-2 flex items-center">
          <AlertTriangle className="w-4 h-4 mr-2" />
          Interpretación Crítica
        </h4>
        <div className="text-sm text-red-800 space-y-1">
          {data.leakageRate <= 2 && (
            <>
              <p>✓ <strong>Excellent:</strong> Less than 2% is the quality benchmark.</p>
              <p>Your QA processes are working correctly.</p>
            </>
          )}
          {data.leakageRate > 2 && data.leakageRate <= 5 && (
            <>
              <p>⚠️ <strong>Acceptable but concerning:</strong> Between 2-5%.</p>
              <p>Review pre-production testing strategy.</p>
            </>
          )}
          {data.leakageRate > 5 && (
            <>
              <p>🔴 <strong>CRITICAL:</strong> More than 5% leak rate.</p>
              <p>Requires complete QA process audit and urgent remediation.</p>
            </>
          )}
        </div>
      </div>

      {/* Recomendaciones */}
      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
        <h4 className="font-semibold text-gray-800 mb-3">Improvement Plan</h4>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>✓ RCA analysis of leaked findings: What was missed in QA?</li>
          <li>✓ Strengthen smoke tests in staging environments</li>
          <li>✓ Implement automated tests for cases that leaked</li>
          <li>✓ Increase regression testing coverage</li>
          <li>✓ QA team training on leaked findings</li>
        </ul>
      </div>
    </div>
  );

  const renderCriticalBugsDetail = (data) => (
    <div className="space-y-6">
      <div>
        <h3 className="text-2xl font-bold text-danger-600 mb-2">
          {data.total} Critical Findings
        </h3>
        <p className="text-sm text-gray-600">Bugs of Major and High priority detected</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Major Priority</div>
          <div className="text-2xl font-bold text-danger-600">{data.highest}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">High Priority</div>
          <div className="text-2xl font-bold text-warning-600">{data.high}</div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <h4 className="font-semibold text-gray-800 mb-3">Criticality Distribution</h4>
        <div className="flex flex-col md:flex-row gap-6 items-center">
          {(() => {
            const priorities = data.allPriorities || {};

            const normalize = (k) => (k || '').toString().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, '');

            const mapCanonical = (kNorm) => {
              if (!kNorm) return 'Other';
              if (kNorm.includes('major') || kNorm.includes('masalta') || kNorm.includes('mas') || kNorm.includes('highest') || kNorm.includes('mayor') || kNorm.includes('critical')) return 'Major';
              if (kNorm.includes('alta') || kNorm.includes('high')) return 'High';
              if (kNorm.includes('media') || kNorm.includes('medium')) return 'Medium';
              if (kNorm.includes('baja') || kNorm.includes('low')) return 'Low';
              if (kNorm.includes('trivial') || kNorm.includes('lowest') || kNorm.includes('masbaja')) return 'Trivial';
              return 'Other';
            };

            const colorsByCanonical = {
              Major: '#dc2626',
              High: '#f97316',
              Medium: '#3b82f6',
              Low: '#9ca3af',
              Trivial: '#d4d4d4',
              Other: '#c7c7c7'
            };

            const mappedItems = Object.keys(priorities || {}).map(key => {
              const raw = priorities[key] || {};
              const count = (typeof raw === 'number') ? raw : (raw.count || raw.total || 0);
              const kNorm = normalize(key);
              const canonical = mapCanonical(kNorm);
              return { key, label: key, canonical, value: Number(count) || 0, color: colorsByCanonical[canonical] || colorsByCanonical.Other };
            }).filter(i => i.value > 0);

            const total = mappedItems.reduce((s, it) => s + it.value, 0) || 1;
            const values = mappedItems.map((item) => ({ label: item.canonical, value: item.value, color: item.color }));

            return (
              <>
                <div className="flex-shrink-0">
                  <svg width="220" height="220" viewBox="0 0 220 220" className="mx-auto">
                    {(() => {
                      let currentAngle = -90;
                      const centerX = 110;
                      const centerY = 110;
                      const radius = 80;

                      return (
                        <g>
                          {values.map((item, idx) => {
                            const percentage = (item.value / total) * 100;
                            const angle = (percentage / 100) * 360;
                            const startAngle = currentAngle;
                            const endAngle = currentAngle + angle;

                            const startRad = (startAngle * Math.PI) / 180;
                            const endRad = (endAngle * Math.PI) / 180;

                            const x1 = centerX + radius * Math.cos(startRad);
                            const y1 = centerY + radius * Math.sin(startRad);
                            const x2 = centerX + radius * Math.cos(endRad);
                            const y2 = centerY + radius * Math.sin(endRad);

                            const largeArc = angle > 180 ? 1 : 0;

                            const path = [
                              `M ${centerX} ${centerY}`,
                              `L ${x1} ${y1}`,
                              `A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`,
                              'Z'
                            ].join(' ');

                            currentAngle = endAngle;

                            return (
                              <path
                                key={idx}
                                d={path}
                                fill={item.color}
                                stroke="white"
                                strokeWidth="2"
                              />
                            );
                          })}
                          <circle cx={centerX} cy={centerY} r="40" fill="white" />
                          <text x={centerX} y={centerY - 5} textAnchor="middle" className="fill-gray-700 font-bold" fontSize="20">{total}</text>
                          <text x={centerX} y={centerY + 12} textAnchor="middle" className="fill-gray-500" fontSize="12">Total Bugs</text>
                        </g>
                      );
                    })()}
                  </svg>
                </div>

                <div className="flex-1 space-y-2">
                  {mappedItems.length === 0 ? (
                    <div className="text-sm text-gray-600">No priority data available</div>
                  ) : (
                    mappedItems.map((item, idx) => (
                      <div key={idx} className={`flex items-center justify-between p-2 rounded ${item.canonical === 'Major' ? 'bg-red-50' : item.canonical === 'High' ? 'bg-orange-50' : item.canonical === 'Medium' ? 'bg-blue-50' : 'bg-gray-50'}`}>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded" style={{ backgroundColor: item.color }}></div>
                          <span className={`text-sm font-medium ${item.canonical === 'Major' ? 'text-red-700' : item.canonical === 'High' ? 'text-orange-700' : item.canonical === 'Medium' ? 'text-blue-700' : 'text-gray-700'}`}>{item.canonical}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className={`text-sm font-bold ${item.canonical === 'Major' ? 'text-red-700' : item.canonical === 'High' ? 'text-orange-700' : item.canonical === 'Medium' ? 'text-blue-700' : 'text-gray-700'}`}>{item.value}</span>
                          <span className="text-xs text-gray-500 w-12 text-right">{Math.round((item.value / total) * 100)}%</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </>
            );
          })()}
        </div>
        <p className="text-xs text-gray-500 mt-3 italic">
          * Analysis focuses on critical priorities (Major and Trivial) due to their impact on product quality
        </p>
      </div>
      
      {/* Gráfico de tendencia: por defecto todas las prioridades, pero si el modal
          es "Analysis of Critical Findings Detected" mostrar solo Major y Trivial */}
      {(() => {
        if (modal && modal.title === 'Analysis of Critical Findings Detected') {
          // Mostrar sólo Major/Trivial si la fuente contiene esas prioridades reales.
          const normalize = (k) => (k || '').toString().toLowerCase().normalize('NFD').replace(/[\u0000-\u036f]/g, '').replace(/[^a-z0-9]/g, '');

          // Mapeo canónico (coincidente con renderCriticalBugsDetail)
          const mapCanonical = (kNorm) => {
            if (!kNorm) return 'Other';
            if (kNorm.includes('major') || kNorm.includes('masalta') || kNorm.includes('mas') || kNorm.includes('highest') || kNorm.includes('mayor') || kNorm.includes('critical')) return 'Major';
            if (kNorm.includes('alta') || kNorm.includes('high')) return 'High';
            if (kNorm.includes('media') || kNorm.includes('medium')) return 'Medium';
            if (kNorm.includes('baja') || kNorm.includes('low')) return 'Low';
            if (kNorm.includes('trivial') || kNorm.includes('lowest') || kNorm.includes('masbaja')) return 'Trivial';
            return 'Other';
          };

          const prioritiesObj = (modal.data && modal.data.allPriorities) || {};
          const canonicalSet = new Set(Object.keys(prioritiesObj).map(k => mapCanonical(normalize(k))));
          const hasMajor = canonicalSet.has('Major');
          const hasTrivial = canonicalSet.has('Trivial');

          // Si no hay claves explícitas en el origen, no inventar series con heurísticos.
          if (!hasMajor && !hasTrivial) {
            return (
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200 text-yellow-800">
                <p className="text-sm">There are no &apos;Major&apos; priorities in the source data.</p>
              </div>
            );
          }

          const majorData = hasMajor && sprints ? sprints.map(sprint => {
            const pb = sprint.bugsByPriority || sprint.bugs_by_priority || {};
            const foundKey = Object.keys(pb || {}).find(k => normalize(k).includes('major') || normalize(k) === 'major' || normalize(k).includes('mas') || normalize(k).includes('mayor'));
            if (foundKey) return pb[foundKey]?.count || pb[foundKey] || 0;
            // fallback: if sprint has explicit field
            if (sprint.major !== undefined) return sprint.major;
            return 0;
          }) : [];

          const trivialData = hasTrivial && sprints ? sprints.map(sprint => {
            const pb = sprint.bugsByPriority || sprint.bugs_by_priority || {};
            const foundKey = Object.keys(pb || {}).find(k => normalize(k).includes('trivial') || normalize(k) === 'trivial' || normalize(k).includes('baja') || normalize(k).includes('masbaja'));
            if (foundKey) return pb[foundKey]?.count || pb[foundKey] || 0;
            if (sprint.trivial !== undefined) return sprint.trivial;
            return 0;
          }) : [];

          const datasets = [];
          if (hasMajor && majorData.some(v => v !== 0)) datasets.push({ label: 'Major', data: majorData, color: '#dc2626' });
          if (hasTrivial && trivialData.some(v => v !== 0)) datasets.push({ label: 'Trivial', data: trivialData, color: '#9ca3af' });

          if (datasets.length === 0) {
            return (
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200 text-yellow-800">
                <p className="text-sm">No hay datos disponibles para Major / Trivial en los sprints.</p>
              </div>
            );
          }

          return (
            <TrendChartMultiple
              datasets={datasets}
              label="Analysis of Critical Findings Detected"
              sprints={sprints}
              yAxisLabel="Amount of Bugs"
            />
          );
        }

        // Fallback: comportamiento original (todas las prioridades)
        const masAltaData = sprints ? sprints.map(sprint => {
          if (sprint.criticalBugsMasAlta !== undefined) return sprint.criticalBugsMasAlta;
          const sprintBugs = sprint.bugs || 0;
          return Math.round(sprintBugs * 0.05); // ~5% son Más alta
        }) : [];
        
        const altaData = sprints ? sprints.map(sprint => {
          if (sprint.criticalBugsAlta !== undefined) return sprint.criticalBugsAlta;
          const sprintBugs = sprint.bugs || 0;
          return Math.round(sprintBugs * 0.30); // ~30% son Alta
        }) : [];
        
        const mediaData = sprints ? sprints.map(sprint => {
          if (sprint.criticalBugsMedia !== undefined) return sprint.criticalBugsMedia;
          const sprintBugs = sprint.bugs || 0;
          return Math.round(sprintBugs * 0.55); // ~55% son Media
        }) : [];
        
        const bajaData = sprints ? sprints.map(sprint => {
          if (sprint.criticalBugsBaja !== undefined) return sprint.criticalBugsBaja;
          const sprintBugs = sprint.bugs || 0;
          return Math.round(sprintBugs * 0.08); // ~8% son Baja
        }) : [];
        
        const masBajaData = sprints ? sprints.map(sprint => {
          if (sprint.criticalBugsMasBaja !== undefined) return sprint.criticalBugsMasBaja;
          const sprintBugs = sprint.bugs || 0;
          return Math.round(sprintBugs * 0.02); // ~2% son Más baja
        }) : [];
        
        const datasets = [
          {
            label: 'Major',
            data: masAltaData,
            color: '#dc2626'
          },
          {
            label: 'High',
            data: altaData,
            color: '#f97316'
          },
          {
            label: 'Medium',
            data: mediaData,
            color: '#3b82f6'
          },
          {
            label: 'Low',
            data: bajaData,
            color: '#a3a3a3'
          },
          {
            label: 'Trivial',
            data: masBajaData,
            color: '#d4d4d4'
          }
        ];
        
        return (
          <TrendChartMultiple 
            datasets={datasets} 
            label="Evolution of Bugs by Priority by Sprint" 
            sprints={sprints} 
            yAxisLabel="Amount of Bugs" 
          />
        );
      })()}

      {/* Recomendaciones al final */}
      <div className="bg-danger-50 p-4 rounded-lg border border-danger-200">
        <h4 className="font-semibold text-danger-900 mb-2 flex items-center">
          <AlertCircle className="w-5 h-5 mr-2" />
           Urgent Actions
        </h4>
        <ul className="space-y-2 text-sm text-danger-800">
          {RecommendationEngine.getRecommendations('criticalBugs', data, recommendations).map((rec, idx) => (
            <li key={idx} dangerouslySetInnerHTML={{ __html: `${rec.icon} ${rec.text.includes(':') ? `<strong>${rec.text.split(':')[0]}:</strong>${rec.text.split(':').slice(1).join(':')}` : rec.text}` }} />
          ))}
        </ul>
      </div>
    </div>
  );

  const renderCriticalBugsStatusDetail = (data) => {
    const priorities = data.allPriorities || {};

    const normalize = (k) => (k || '').toString().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, '');

    const mapCanonical = (kNorm) => {
      if (!kNorm) return 'Other';
      if (kNorm.includes('major') || kNorm.includes('masalta') || kNorm.includes('mas') || kNorm.includes('highest') || kNorm.includes('mayor') || kNorm.includes('critical')) return 'Major';
      if (kNorm.includes('alta') || kNorm.includes('high')) return 'High';
      if (kNorm.includes('media') || kNorm.includes('medium')) return 'Medium';
      if (kNorm.includes('baja') || kNorm.includes('low')) return 'Low';
      if (kNorm.includes('trivial') || kNorm.includes('lowest') || kNorm.includes('masbaja')) return 'Trivial';
      return 'Other';
    };

    // Construir lista mapeada con pendientes/resueltos normalizados
    const mapped = Object.keys(priorities || {}).map(key => {
      const raw = priorities[key] || {};
      const pending = raw.pending ?? raw.pendingCount ?? raw.countPending ?? raw.pending_total ?? raw.count ?? raw.total ?? 0;
      const resolved = raw.resolved ?? raw.resolvedCount ?? raw.fixed ?? 0;
      const kNorm = normalize(key);
      const canonical = mapCanonical(kNorm);
      return { key, canonical, pending: Number(pending) || 0, resolved: Number(resolved) || 0 };
    });

    const masAltaPending = mapped.find(m => m.canonical === 'Major')?.pending || 0;
    const masAltaResolved = mapped.find(m => m.canonical === 'Major')?.resolved || 0;
    const altaPending = mapped.find(m => m.canonical === 'High')?.pending || 0;
    const altaResolved = mapped.find(m => m.canonical === 'High')?.resolved || 0;
    
    return (
    <div className="space-y-6">
      <div className="bg-orange-50 p-6 rounded-lg border border-orange-200">
        <h3 className="text-2xl font-bold text-warning-600 mb-2">
          {data.pending} pending Critical Bugs
        </h3>
        <p className="text-sm text-gray-600">Unresolved Critical Bugs</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Total Critical</div>
          <div className="text-2xl font-bold text-gray-900">{data.total}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Resolved</div>
          <div className="text-2xl font-bold text-success-600">{data.resolved}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Pending</div>
          <div className="text-2xl font-bold text-warning-600">{data.pending}</div>
        </div>
      </div>

      {/* Gráficos circulares de Pendientes y Resueltos por criticidad */}
      <div>
        <h4 className="font-semibold text-gray-800 mb-4">Distribution by Criticality</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Sección de Pendientes */}
          <div className="bg-warning-50 p-4 rounded-lg border border-warning-200">
            <h5 className="text-sm font-semibold text-warning-800 mb-3">Pending Bugs</h5>
            <div className="flex flex-col md:flex-row gap-6 items-center justify-center">
              {/* Gráfico circular */}
              <div className="flex-shrink-0">
              <svg width="180" height="180" viewBox="0 0 180 180" className="mx-auto">
                {(() => {
                  const totalPending = masAltaPending + altaPending || 1;
                  const masAltaPercent = (masAltaPending / totalPending) * 100;
                  const altaPercent = (altaPending / totalPending) * 100;
                  
                  const centerX = 90;
                  const centerY = 90;
                  const radius = 65;
                  
                  // Más alta
                  const masAltaAngle = (masAltaPercent / 100) * 360;
                  const masAltaStartRad = (-90 * Math.PI) / 180;
                  const masAltaEndRad = ((masAltaAngle - 90) * Math.PI) / 180;
                  
                  const masAltaX1 = centerX + radius * Math.cos(masAltaStartRad);
                  const masAltaY1 = centerY + radius * Math.sin(masAltaStartRad);
                  const masAltaX2 = centerX + radius * Math.cos(masAltaEndRad);
                  const masAltaY2 = centerY + radius * Math.sin(masAltaEndRad);
                  const masAltaLargeArc = masAltaAngle > 180 ? 1 : 0;
                  
                  // Alta
                  const altaAngle = (altaPercent / 100) * 360;
                  const altaStartRad = masAltaEndRad;
                  const altaEndRad = ((masAltaAngle + altaAngle - 90) * Math.PI) / 180;
                  
                  const altaX1 = masAltaX2;
                  const altaY1 = masAltaY2;
                  const altaX2 = centerX + radius * Math.cos(altaEndRad);
                  const altaY2 = centerY + radius * Math.sin(altaEndRad);
                  const altaLargeArc = altaAngle > 180 ? 1 : 0;
                  
                  return (
                    <g>
                      {/* Más alta */}
                      <path
                        d={`M ${centerX} ${centerY} L ${masAltaX1} ${masAltaY1} A ${radius} ${radius} 0 ${masAltaLargeArc} 1 ${masAltaX2} ${masAltaY2} Z`}
                        fill="#dc2626"
                        stroke="white"
                        strokeWidth="2"
                      />
                      {/* Alta */}
                      <path
                        d={`M ${centerX} ${centerY} L ${altaX1} ${altaY1} A ${radius} ${radius} 0 ${altaLargeArc} 1 ${altaX2} ${altaY2} Z`}
                        fill="#f97316"
                        stroke="white"
                        strokeWidth="2"
                      />
                    </g>
                  );
                })()}
              </svg>
              </div>

              {/* Leyenda */}
              <div className="flex-1">
                {(() => {
                  const totalPending = masAltaPending + altaPending || 1;
                  return (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between p-2 rounded bg-red-50">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#dc2626' }}></div>
                          <span className="text-sm font-medium text-red-700">Major</span>
                        </div>
                        <span className="text-sm font-semibold text-red-700">
                          {masAltaPending} ({totalPending > 0 ? Math.round((masAltaPending / totalPending) * 100) : 0}%)
                        </span>
                      </div>
                      <div className="flex items-center justify-between p-2 rounded bg-orange-50">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#f97316' }}></div>
                          <span className="text-sm font-medium text-orange-700">High</span>
                        </div>
                        <span className="text-sm font-semibold text-orange-700">
                          {altaPending} ({totalPending > 0 ? Math.round((altaPending / totalPending) * 100) : 0}%)
                        </span>
                      </div>
                    </div>
                  );
                })()}
              </div>
            </div>
          </div>

          {/* Sección de Resueltos */}
          <div className="bg-success-50 p-4 rounded-lg border border-success-200">
            <h5 className="text-sm font-semibold text-success-800 mb-3">Resolved Bugs</h5>
            <div className="flex flex-col md:flex-row gap-6 items-center justify-center">
              {/* Gráfico circular */}
              <div className="flex-shrink-0">
              <svg width="180" height="180" viewBox="0 0 180 180" className="mx-auto">
                {(() => {
                  const totalResolved = masAltaResolved + altaResolved || 1;
                  const masAltaPercent = (masAltaResolved / totalResolved) * 100;
                  const altaPercent = (altaResolved / totalResolved) * 100;
                  
                  const centerX = 90;
                  const centerY = 90;
                  const radius = 65;
                  
                  // Más alta
                  const masAltaAngle = (masAltaPercent / 100) * 360;
                  const masAltaStartRad = (-90 * Math.PI) / 180;
                  const masAltaEndRad = ((masAltaAngle - 90) * Math.PI) / 180;
                  
                  const masAltaX1 = centerX + radius * Math.cos(masAltaStartRad);
                  const masAltaY1 = centerY + radius * Math.sin(masAltaStartRad);
                  const masAltaX2 = centerX + radius * Math.cos(masAltaEndRad);
                  const masAltaY2 = centerY + radius * Math.sin(masAltaEndRad);
                  const masAltaLargeArc = masAltaAngle > 180 ? 1 : 0;
                  
                  // Alta
                  const altaAngle = (altaPercent / 100) * 360;
                  const altaStartRad = masAltaEndRad;
                  const altaEndRad = ((masAltaAngle + altaAngle - 90) * Math.PI) / 180;
                  
                  const altaX1 = masAltaX2;
                  const altaY1 = masAltaY2;
                  const altaX2 = centerX + radius * Math.cos(altaEndRad);
                  const altaY2 = centerY + radius * Math.sin(altaEndRad);
                  const altaLargeArc = altaAngle > 180 ? 1 : 0;
                  
                  return (
                    <g>
                      {/* Más alta */}
                      <path
                        d={`M ${centerX} ${centerY} L ${masAltaX1} ${masAltaY1} A ${radius} ${radius} 0 ${masAltaLargeArc} 1 ${masAltaX2} ${masAltaY2} Z`}
                        fill="#dc2626"
                        stroke="white"
                        strokeWidth="2"
                      />
                      {/* Alta */}
                      <path
                        d={`M ${centerX} ${centerY} L ${altaX1} ${altaY1} A ${radius} ${radius} 0 ${altaLargeArc} 1 ${altaX2} ${altaY2} Z`}
                        fill="#f97316"
                        stroke="white"
                        strokeWidth="2"
                      />
                    </g>
                  );
                })()}
              </svg>
              </div>

              {/* Leyenda */}
              <div className="flex-1">
                {(() => {
                  const totalResolved = masAltaResolved + altaResolved || 1;
                  return (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between p-2 rounded bg-red-50">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#dc2626' }}></div>
                          <span className="text-sm font-medium text-red-700">Major</span>
                        </div>
                        <span className="text-sm font-semibold text-red-700">
                          {masAltaResolved} ({totalResolved > 0 ? Math.round((masAltaResolved / totalResolved) * 100) : 0}%)
                        </span>
                      </div>
                      <div className="flex items-center justify-between p-2 rounded bg-orange-50">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#f97316' }}></div>
                          <span className="text-sm font-medium text-orange-700">High</span>
                        </div>
                        <span className="text-sm font-semibold text-orange-700">
                          {altaResolved} ({totalResolved > 0 ? Math.round((altaResolved / totalResolved) * 100) : 0}%)
                        </span>
                      </div>
                    </div>
                  );
                })()}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Gráfico de tendencia con líneas separadas por estado: Tareas por hacer, En progreso, Reabierto + Pendiente */}
      {(() => {
        const tareasPorHacerData = sprints ? sprints.map(sprint => sprint.criticalBugsByState?.tareasPorHacer || 0) : [];
        const enProgresoData = sprints ? sprints.map(sprint => sprint.criticalBugsByState?.enProgreso || 0) : [];
        const reabiertosData = sprints ? sprints.map(sprint => sprint.criticalBugsByState?.reabierto || 0) : [];
        
        // Calcular pendiente total (suma de los 3 estados)
        const pendienteData = sprints ? sprints.map((sprint, idx) => {
          return (tareasPorHacerData[idx] || 0) + (enProgresoData[idx] || 0) + (reabiertosData[idx] || 0);
        }) : [];
        
        const datasets = [
          {
            label: 'Pending (Total)',
            data: pendienteData,
            color: '#8b5cf6'
          },
          {
            label: 'To Do',
            data: tareasPorHacerData,
            color: '#dc2626'
          },
          {
            label: 'In Progress',
            data: enProgresoData,
            color: '#f97316'
          },
          {
            label: 'Reopened',
            data: reabiertosData,
            color: '#eab308'
          }
        ];
        
        return (
          <TrendChartMultiple 
            datasets={datasets} 
            label="Evolution of Pending Critical Findings by Sprint" 
            sprints={sprints} 
            yAxisLabel="Pending Critical Findings" 
          />
        );
      })()}

      {/* Recomendaciones al final */}
      <div className="bg-warning-50 p-4 rounded-lg border border-warning-200">
        <h4 className="font-semibold text-warning-900 mb-2 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" />
          Action Plan
        </h4>
        <ul className="space-y-2 text-sm text-warning-800">
          {RecommendationEngine.getRecommendations('criticalBugsStatus', data, recommendations).map((rec, idx) => (
            <li key={idx} dangerouslySetInnerHTML={{ __html: `${rec.icon} ${rec.text.includes(':') ? `<strong>${rec.text.split(':')[0]}:</strong>${rec.text.split(':').slice(1).join(':')}` : rec.text}` }} />
          ))}
        </ul>
      </div>
    </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-executive-600 text-white p-6 rounded-t-xl flex items-center justify-between">
          <h2 className="text-2xl font-bold">{modal.title}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
            aria-label="Cerrar modal"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {modal.type === 'cycleTime' && renderCycleTimeDetail(modal.data)}
          {(modal.type === 'automationCoverage' || modal.type === 'testAutomation' || modal.type === 'codeCoverage') && renderAutomationCoverageDetail(modal.data)}
          {modal.type === 'defectDensity' && renderDefectDensityDetail(modal.data)}
          {modal.type === 'testCases' && renderTestCasesDetail(modal.data)}
          {modal.type === 'resolutionEfficiency' && renderResolutionEfficiencyDetail(modal.data)}
          {modal.type === 'regressionRate' && renderRegressionRateDetail(modal.data)}
          {(modal.type === 'testExecutionRate' || modal.type === 'testEfficiency') && renderTestExecutionRateDetail(modal.data)}
          {modal.type === 'riskMatrix' && renderRiskMatrixDetail(modal.data)}
          {(modal.type === 'bugLeakageRate' || modal.type === 'bugLeakage') && renderBugLeakageRateDetail(modal.data)}
          {modal.type === 'module' && renderModuleDetail(modal.data)}
          {modal.type === 'criticalBugs' && renderCriticalBugsDetail(modal.data)}
          {modal.type === 'criticalBugsStatus' && renderCriticalBugsStatusDetail(modal.data)}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 px-6 py-4 rounded-b-xl border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-executive-600 text-white rounded-lg hover:bg-executive-700 transition-colors font-medium"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
