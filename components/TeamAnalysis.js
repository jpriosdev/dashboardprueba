// TeamAnalysis.js - Scaffold for Team Analysis tab
import React, { useMemo, useState, useEffect } from 'react';
import ActionableRecommendations from './ActionableRecommendations';
import DetailModal from './DetailModal';
import { User, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';

function TeamKpiCard({ title, value, sub, children }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      {sub && <div className="text-xs text-gray-400">{sub}</div>}
      {children}
    </div>
  );
}

function DataSummaryPanel({ data, filteredSprintData }) {
  const totalBugs = (data && (data.summary?.totalBugs || data.summary?.total_bugs)) || 0;
  const developerData = Array.isArray(data?.developerData) ? data.developerData : (Array.isArray(data?.developers) ? data.developers : []);
  // compute assigned sum from developerData (processor normalizes several names)
  const assignedSum = developerData.reduce((s, d) => s + (d.assigned || d.total_bugs || d.assigned_bugs || 0), 0);
  const unassigned = Math.max(0, totalBugs - assignedSum);

  // top 5 developers
  const topDevs = developerData.slice().sort((a, b) => (b.assigned || b.total_bugs || 0) - (a.assigned || a.total_bugs || 0)).slice(0, 5);

  // distinct statuses and issue types from available bugs if present
  const bugs = Array.isArray(data?.bugs) ? data.bugs : [];
  const statusSet = new Set(bugs.map(b => (b.estado || b.status || b.state || '').toString()).filter(Boolean));
  const issueTypeSet = new Set(bugs.map(b => (b.tipo_incidencia || b.issueType || b.type || '').toString()).filter(Boolean));

  return (
    <div className="text-sm text-gray-700 space-y-3">
      <div className="font-semibold">Quick Data</div>
      <div>Total bugs: <span className="font-medium">{totalBugs}</span></div>
      <div>Assigned: <span className="font-medium">{assignedSum}</span> • Unassigned: <span className="font-medium">{unassigned}</span></div>

      <div className="pt-2">
        <div className="font-semibold">Top 5 Developers</div>
        {topDevs.length > 0 ? (
          <ul className="list-disc list-inside text-xs text-gray-600">
            {topDevs.map((d, i) => (
              <li key={i}>{d.name || d.developer_name || d.developer || 'Sin asignar'} — {d.assigned || d.total_bugs || 0} bugs</li>
            ))}
          </ul>
        ) : (
          <div className="text-xs text-gray-500">No developer summary available</div>
        )}
      </div>

      <div className="pt-2">
        <div className="font-semibold">Statuses</div>
        {statusSet.size > 0 ? (
          <div className="text-xs text-gray-600">{Array.from(statusSet).join(', ')}</div>
        ) : (
          <div className="text-xs text-gray-500">No status values available</div>
        )}
      </div>

      <div className="pt-2">
        <div className="font-semibold">Issue Types</div>
        {issueTypeSet.size > 0 ? (
          <div className="text-xs text-gray-600">{Array.from(issueTypeSet).join(', ')}</div>
        ) : (
          <div className="text-xs text-gray-500">No issue types available</div>
        )}
      </div>
    </div>
  );
}

function SprintModulesList({ data }) {
  // show modules breakdown if available (bugsByModule or data.bugs grouped)
  const modules = data?.bugsByModule || [];
  if (modules && modules.length > 0) {
    return (
      <ul className="text-xs space-y-1">
        {modules.slice(0, 8).map((m, i) => (
          <li key={i} className="flex justify-between">
            <span>{m.module || m.name || m[0]}</span>
            <span className="font-medium">{m.count || m.total || 0}</span>
          </li>
        ))}
      </ul>
    );
  }

  // fallback: derive from bugs array
  const bugs = Array.isArray(data?.bugs) ? data.bugs : [];
  if (bugs.length === 0) return <div className="text-xs text-gray-500">No module data available</div>;
  const byModule = {};
  bugs.forEach(b => {
    const mod = (b.module || b.modulo || 'Other').toString();
    byModule[mod] = (byModule[mod] || 0) + 1;
  });
  const rows = Object.entries(byModule).sort((a, b) => b[1] - a[1]).slice(0, 8);
  return (
    <ul className="text-xs space-y-1">
      {rows.map(([mod, count], i) => (
        <li key={i} className="flex justify-between"><span>{mod}</span><span className="font-medium">{count}</span></li>
      ))}
    </ul>
  );
}

function SprintListPanel({ data, loading }) {
  if (loading) return <div className="text-xs text-gray-500">Loading...</div>;
  const sprints = Array.isArray(data?.sprintData) ? data.sprintData : [];
  if (!sprints || sprints.length === 0) return <div className="text-xs text-gray-500">No sprint data available</div>;
  return (
    <div className="space-y-2">
      {sprints.slice().sort((a,b)=> (a.sprint_num||0)-(b.sprint_num||0)).map((s, idx) => (
        <div key={idx} className="flex justify-between items-center border-b pb-2">
          <div className="text-xs">
            <div className="font-medium">{s.sprint || s.sprint_name || s.sprint}</div>
            <div className="text-gray-500 text-xs">Start: {s.startDate || s.start_date || 'n/a'}</div>
          </div>
          <div className="text-sm text-gray-700">Bugs: <span className="font-semibold">{s.bugs || s.total || 0}</span> • Tests: <span className="font-semibold">{s.testCases || s.testCasesExecuted || s.testCases || 0}</span></div>
        </div>
      ))}
    </div>
  );
}

export default function TeamAnalysis({ data, filteredSprintData }) {
  // Prefer developer summary arrays from incoming data
  const incomingDevelopers = Array.isArray(data?.developerData) ? data.developerData : (Array.isArray(data?.developers) ? data.developers : []);
  const [fetchedDevelopers, setFetchedDevelopers] = useState(null);
  const developers = incomingDevelopers.length > 0 ? incomingDevelopers : (Array.isArray(fetchedDevelopers) ? fetchedDevelopers : []);
  // If incoming developer data is not present, fetch summaries from server-side API.
  useEffect(() => {
    if (incomingDevelopers && incomingDevelopers.length > 0) return;
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch('/api/team-analysis');
        if (!res.ok) return;
        const payload = await res.json();
        if (cancelled) return;
        if (Array.isArray(payload.developerSummaries) && payload.developerSummaries.length > 0) {
          const normalized = payload.developerSummaries.map(d => ({
            name: d.developer || 'Sin asignar',
            totalBugs: d.total || 0,
            resolved: d.resolved || 0,
            pending: d.pending || 0,
            workload: ''
          }));
          setFetchedDevelopers(normalized);
        }
      } catch (e) {
        // ignore
      }
    })();
    return () => { cancelled = true; };
  }, [incomingDevelopers]);

  if (!developers || developers.length === 0) {
    return (
      <div className="executive-card text-center p-8">
        <AlertCircle className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-600">Cargando datos de desarrolladores...</p>
      </div>
    );
  }

  const sortedDevelopers = [...developers].sort((a, b) => (b.pending || b.pending_bugs || 0) - (a.pending || a.pending_bugs || 0));
  const totalBugs = developers.reduce((sum, dev) => sum + (dev.totalBugs || dev.total_bugs || 0), 0);
  const totalPending = developers.reduce((sum, dev) => sum + (dev.pending || dev.pending_bugs || 0), 0);

  const getWorkloadColor = (workload) => {
    switch ((workload || '').toString()) {
      case 'Alto':
      case 'High':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'Medio':
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Bajo':
      case 'Low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getEfficiencyColor = (efficiency) => {
    if (efficiency >= 80) return 'text-green-600';
    if (efficiency >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="executive-card text-center">
          <User className="w-8 h-8 text-executive-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">{developers.length}</div>
          <div className="text-sm text-gray-600">Desarrolladores Activos</div>
        </div>

        <div className="executive-card text-center">
          <AlertCircle className="w-8 h-8 text-warning-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">{totalPending}</div>
          <div className="text-sm text-gray-600">Bugs Pendientes Total</div>
        </div>

        <div className="executive-card text-center">
          <TrendingUp className="w-8 h-8 text-success-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {totalBugs > 0 ? `${Math.round(((totalBugs - totalPending) / totalBugs) * 100)}%` : '—'}
          </div>
          <div className="text-sm text-gray-600">Eficiencia General</div>
        </div>
      </div>

      <div className="executive-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Análisis Detallado por Desarrollador</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Desarrollador</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Bugs</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pendientes</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resueltos</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Eficiencia</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Carga</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">% del Total</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedDevelopers.map((developer, index) => {
                const total = developer.totalBugs || developer.total_bugs || 0;
                const resolved = developer.resolved || developer.resueltos || 0;
                const pending = developer.pending || developer.pending_bugs || 0;
                const efficiency = total > 0 ? Math.round((resolved / total) * 100) : 0;
                const percentageOfTotal = totalBugs > 0 ? Math.round((total / totalBugs) * 100) : 0;

                return (
                  <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8">
                          <div className="h-8 w-8 rounded-full bg-executive-100 flex items-center justify-center">
                            <span className="text-sm font-medium text-executive-600">
                              {(developer.name || developer.developer || 'NA').toString().split(' ').map(n => n[0]).join('').substring(0,2)}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{developer.name || developer.developer || 'Sin nombre'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"><span className="font-semibold">{total}</span></td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`font-semibold ${pending > 15 ? 'text-red-600' : pending > 10 ? 'text-yellow-600' : 'text-green-600'}`}>{pending}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-semibold">{resolved}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div className={`${efficiency >= 80 ? 'bg-green-500' : efficiency >= 60 ? 'bg-yellow-500' : 'bg-red-500'} h-2 rounded-full`} style={{ width: `${efficiency}%` }} />
                        </div>
                        <span className={`font-semibold ${getEfficiencyColor(efficiency)}`}>{efficiency}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getWorkloadColor(developer.workload || developer.carga || '')}`}>{developer.workload || developer.carga || 'N/A'}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <div className="w-12 bg-gray-200 rounded-full h-2 mr-2">
                          <div className="bg-executive-500 h-2 rounded-full" style={{ width: `${percentageOfTotal}%` }} />
                        </div>
                        <span className="font-medium">{percentageOfTotal}%</span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="executive-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recomendaciones para el Equipo</h3>
        <div className="space-y-3">
          {sortedDevelopers[0] && (sortedDevelopers[0].pending || sortedDevelopers[0].pending_bugs) > 15 && (
            <div className="flex items-start p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-500 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800">Sobrecarga Crítica Detectada</p>
                <p className="text-sm text-red-700">{sortedDevelopers[0].name || sortedDevelopers[0].developer} tiene {sortedDevelopers[0].pending || sortedDevelopers[0].pending_bugs} bugs pendientes. Considerar redistribuir carga de trabajo inmediatamente.</p>
              </div>
            </div>
          )}

          {developers.filter(dev => (dev.workload || dev.carga || '').toString().toLowerCase().includes('bajo')).length > 0 && (
            <div className="flex items-start p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <TrendingUp className="w-5 h-5 text-blue-500 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-blue-800">Oportunidad de Balanceo</p>
                <p className="text-sm text-blue-700">{developers.filter(dev => (dev.workload || dev.carga || '').toString().toLowerCase().includes('bajo')).length} desarrolladores con carga baja pueden asumir más responsabilidades.</p>
              </div>
            </div>
          )}

          <div className="flex items-start p-3 bg-green-50 border border-green-200 rounded-lg">
            <TrendingUp className="w-5 h-5 text-green-500 mr-3 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-green-800">Eficiencia General del Equipo</p>
              <p className="text-sm text-green-700">El equipo mantiene una eficiencia del {totalBugs > 0 ? Math.round(((totalBugs - totalPending) / totalBugs) * 100) : 0}% en resolución de bugs.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
