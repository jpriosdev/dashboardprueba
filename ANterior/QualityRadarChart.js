import React, { useState, useEffect } from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { ChevronDown, AlertCircle, TrendingUp, Shield, Zap, Eye, X, Filter } from 'lucide-react';

// Componente de Sección de Filtro
function FilterSection({ title, icon, color, options, selected, onChange }) {
  const [collapsed, setCollapsed] = useState(false);
  
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    indigo: 'bg-indigo-50 border-indigo-200 text-indigo-700',
    orange: 'bg-orange-50 border-orange-200 text-orange-700',
    cyan: 'bg-cyan-50 border-cyan-200 text-cyan-700',
    teal: 'bg-teal-50 border-teal-200 text-teal-700',
    pink: 'bg-pink-50 border-pink-200 text-pink-700',
    violet: 'bg-violet-50 border-violet-200 text-violet-700',
  };

  const buttonClasses = {
    blue: 'bg-blue-500 hover:bg-blue-600',
    red: 'bg-red-500 hover:bg-red-600',
    green: 'bg-green-500 hover:bg-green-600',
    indigo: 'bg-indigo-500 hover:bg-indigo-600',
    orange: 'bg-orange-500 hover:bg-orange-600',
    cyan: 'bg-cyan-500 hover:bg-cyan-600',
    teal: 'bg-teal-500 hover:bg-teal-600',
    pink: 'bg-pink-500 hover:bg-pink-600',
    violet: 'bg-violet-500 hover:bg-violet-600',
  };

  return (
    <div className={`border rounded-lg p-3 ${colorClasses[color]}`}>
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="w-full flex items-center justify-between mb-2"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{icon}</span>
          <p className="text-xs font-bold uppercase">{title}</p>
          {selected.length > 0 && (
            <span className="ml-1 px-2 py-.5 bg-white bg-opacity-50 text-xs font-bold rounded">
              {selected.length}
            </span>
          )}
        </div>
        <ChevronDown size={14} className={`transition-transform ${collapsed ? '' : 'rotate-180'}`} />
      </button>

      {!collapsed && (
        <div className="flex flex-wrap gap-1.5">
          {options.slice(0, 6).map(option => (
            <button
              key={option}
              onClick={() => onChange(option)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-full transition-all whitespace-nowrap ${
                selected.includes(option)
                  ? `${buttonClasses[color]} text-white shadow-md`
                  : 'bg-white bg-opacity-70 hover:bg-opacity-100'
              }`}
            >
              {option}
            </button>
          ))}
          {options.length > 6 && (
            <button
              onClick={() => setCollapsed(false)}
              className="px-2.5 py-1 text-xs font-semibold text-gray-600 bg-white bg-opacity-70 rounded-full hover:bg-opacity-100"
            >
              +{options.length - 6}
            </button>
          )}
        </div>
      )}

      {collapsed && (
        <div className="space-y-1">
          {options.map(option => (
            <label key={option} className="flex items-center gap-2 cursor-pointer hover:bg-white hover:bg-opacity-30 p-1.5 rounded transition-all">
              <input
                type="checkbox"
                checked={selected.includes(option)}
                onChange={() => onChange(option)}
                className="w-4 h-4 rounded cursor-pointer"
              />
              <span className="text-sm font-medium">{option}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  );
}

const MATURITY_LEVELS = {
  0: {
    name: 'Sin Madurez (Baseline)',
    maturityGap: 'Estado actual',
    executiveSummary: 'Procesos manuales y desorganizados. Testing reactivo detecta defectos en producción. Alto riesgo y costos.',
    benefits: [
      'Sin inversión inicial en herramientas',
      'Máxima flexibilidad operativa',
    ],
    riskMitigation: [
      '⚠ 60-80% defectos escapan a producción',
      '⚠ Ciclos de release lentos (1-2 meses)',
      '⚠ Cero visibilidad de calidad en tiempo real',
      '⚠ Zero shift-left: Testing comienza en QA',
    ],
    processEfficiency: [
      '❌ Testing manual 100%',
      '❌ ~4 horas QA por feature',
      '❌ Sin métricas de cobertura',
      '❌ Debugging manual de fallos',
    ],
    observability: [
      '❌ No hay visibilidad en desarrollo',
      '❌ Logs manuales sin agregación',
      '❌ Fallos descubiertos por usuarios',
      '❌ Causa raíz toma 2-3 días',
    ],
    shiftStrategy: [
      '📍 0% Shift-Left: Testing al final',
      '📍 0% Shift-Right: Sin monitoreo producción',
    ],
    attributes: {
      'Metodología': 5,
      'Funcionales': 5,
      'Desempeño': 2,
      'Seguridad': 0,
      'Automatización': 0,
      'Datos': 0,
      'Adopción de AI': 0,
      'Observabilidad': 1,
    },
    impact: [
      '💰 Costo de defectos en prod: $10K-50K por incidente',
      '📉 Velocidad release: 6-8 semanas',
      '😞 Satisfacción cliente: 60-70%',
      '⏰ MTTR (Mean Time To Resolve): 2-3 días',
    ],
  },
  1: {
    name: 'Inicial',
    maturityGap: 'Primeros pasos organizados',
    executiveSummary: 'Testing documentado pero aún manual. QA integrado en sprints. Primeras métricas. Detecta 40-50% defectos.',
    benefits: [
      'Casos de prueba documentados y reproducibles',
      'Mejora visible en defectos detectados (vs Level 0)',
      'Traceabilidad inicial de pruebas',
      'Participación de QA en planning',
    ],
    riskMitigation: [
      '⚠ 40-50% defectos aún escapan',
      '⚠ Ciclos release reducidos a 3-4 semanas',
      '⚠ Observabilidad manual sin automatización',
      '⚠ 10% Shift-Left: Solo en planificación',
    ],
    processEfficiency: [
      '✓ Testing manual 95%, automatización 5%',
      '✓ ~2.5 horas QA por feature',
      '✓ Métricas básicas (pass/fail)',
      '✓ Tracking manual de defectos',
    ],
    observability: [
      '⚠ Visibilidad limitada a reports manuales',
      '⚠ Sin alertas automáticas',
      '⚠ Logs no agregados centralmente',
      '⚠ Causa raíz toma 1-2 días',
    ],
    shiftStrategy: [
      '📍 10% Shift-Left: QA en Daily Standups',
      '📍 5% Shift-Right: Feedback manual de usuarios',
    ],
    attributes: {
      'Metodología': 40,
      'Funcionales': 40,
      'Desempeño': 10,
      'Seguridad': 0,
      'Automatización': 20,
      'Datos': 10,
      'Adopción de AI': 10,
      'Observabilidad': 0,
    },
    impact: [
      '💰 Costo de defectos en prod: $5K-25K por incidente',
      '📈 Mejora: -40% defectos vs Level 0',
      '📉 Velocidad release: 3-4 semanas',
      '😊 Satisfacción cliente: 70-75%',
      '⏰ MTTR: 1-2 días',
    ],
  },
  2: {
    name: 'Repetible',
    maturityGap: 'Automatización comienza',
    executiveSummary: 'Primeras pruebas automatizadas (10-30%). CI básico. Riesgos funcionales controlados. Menos sorpresas.',
    benefits: [
      'Automatización de regresión funcional (10-30%)',
      'CI Pipeline básico: menos defectos en stage',
      'Ejecución de pruebas más rápida',
      'Trazabilidad de casos de prueba',
    ],
    riskMitigation: [
      '✓ 20-30% defectos escapan (mejora significativa)',
      '✓ Ciclos release 2-3 semanas',
      '✓ Algunos riesgos funcionales prevenidos',
      '✓ 20% Shift-Left: Automatización de regresión',
    ],
    processEfficiency: [
      '✓ Testing manual 70%, automatización 30%',
      '✓ ~1.5 horas QA por feature',
      '✓ Métricas de cobertura básicas (line coverage)',
      '✓ Ejecución automática de suites regresión',
    ],
    observability: [
      '✓ CI/CD reportes de builds',
      '✓ Test results en dashboards básicos',
      '⚠ Sin observabilidad en producción aún',
      '⚠ Causa raíz toma ~24 horas',
    ],
    shiftStrategy: [
      '📍 20% Shift-Left: Automatización de regresión',
      '📍 10% Shift-Right: Alertas básicas de fallos',
    ],
    attributes: {
      'Metodología': 60,
      'Funcionales': 70,
      'Desempeño': 25,
      'Seguridad': 15,
      'Automatización': 40,
      'Datos': 30,
      'Adopción de AI': 25,
      'Observabilidad': 40,
    },
    impact: [
      '💰 Costo de defectos en prod: $2K-10K por incidente',
      '📈 Mejora: -70% defectos vs Level 0',
      '⚡ Velocidad release: 2-3 semanas',
      '😊 Satisfacción cliente: 75-80%',
      '⏰ MTTR: 12-18 horas',
    ],
  },
  3: {
    name: 'Definido',
    maturityGap: 'Testing totalmente integrado en DevOps',
    executiveSummary: 'Shift-Left proactivo. Testing en cada stage del pipeline. Seguridad y performance integrados. 5-10% fallos escapan.',
    benefits: [
      'Defectos detectados en desarrollo (Shift-Left)',
      'CI/CD con gates automáticos de calidad',
      'Pruebas de seguridad y rendimiento integradas',
      'Mejora continua basada en métricas',
    ],
    riskMitigation: [
      '✓ 5-10% defectos escapan (control alto)',
      '✓ Ciclos release 1-2 semanas',
      '✓ Riesgos de seguridad y performance prevenidos',
      '✓ 40% Shift-Left: Testing desde planificación',
    ],
    processEfficiency: [
      '✓ Testing manual 40%, automatización 60%',
      '✓ ~45 minutos QA por feature',
      '✓ Cobertura >70%, riesgos mapeados',
      '✓ Execución automática en cada commit',
    ],
    observability: [
      '✓ Dashboards de calidad en tiempo real',
      '✓ Alertas automáticas de regresiones',
      '✓ Logs centralizados (ELK, Datadog)',
      '✓ Causa raíz identificada en <2 horas',
    ],
    shiftStrategy: [
      '📍 40% Shift-Left: Security & performance desde design',
      '📍 20% Shift-Right: Monitoreo producción + alertas',
    ],
    attributes: {
      'Metodología': 80,
      'Funcionales': 80,
      'Desempeño': 50,
      'Seguridad': 40,
      'Automatización': 60,
      'Datos': 50,
      'Adopción de AI': 40,
      'Observabilidad': 50,
    },
    impact: [
      '💰 Costo de defectos en prod: $500-2K por incidente',
      '📈 Mejora: -95% defectos vs Level 0',
      '⚡ Velocidad release: 1-2 semanas',
      '😍 Satisfacción cliente: 85-90%',
      '⏰ MTTR: 2-4 horas',
    ],
  },
  4: {
    name: 'Gestionado',
    maturityGap: 'Testing inteligente con data-driven insights',
    executiveSummary: 'Automatización completa de funcionales. ML para análisis predictivo. Seguridad contínua. <1% fallos escapan.',
    benefits: [
      'Automatización completa de funcionales (70-85%)',
      'Análisis predictivo de defectos con ML',
      'Pruebas de seguridad avanzadas en cada release',
      'Optimización automática de suite de pruebas',
    ],
    riskMitigation: [
      '✓ <1% defectos escapan (control crítico)',
      '✓ Hotfix releases en horas',
      '✓ Seguridad y compliance validado continuamente',
      '✓ 60% Shift-Left: Análisis de código + tests automáticos',
    ],
    processEfficiency: [
      '✓ Testing manual 15%, automatización 85%',
      '✓ ~15 minutos QA por feature',
      '✓ Cobertura >85%, análisis de riesgos automático',
      '✓ Ejecución paralela en minutos',
    ],
    observability: [
      '✓ Observabilidad IA-driven en prod',
      '✓ Predicción de fallos antes que ocurran',
      '✓ Distributed tracing completo',
      '✓ Causa raíz identificada en <30 minutos',
    ],
    shiftStrategy: [
      '📍 60% Shift-Left: SAST, análisis dinámico, threat modeling',
      '📍 40% Shift-Right: Monitoreo IA, alertas inteligentes, canary deployments',
    ],
    attributes: {
      'Metodología': 90,
      'Funcionales': 80,
      'Desempeño': 70,
      'Seguridad': 60,
      'Automatización': 80,
      'Datos': 70,
      'Adopción de AI': 60,
      'Observabilidad': 60,
    },
    impact: [
      '💰 Costo de defectos en prod: <$500 por incidente',
      '📈 Mejora: -99% defectos vs Level 0',
      '⚡ Velocidad release: On-demand (horas)',
      '😍 Satisfacción cliente: 90-95%',
      '⏰ MTTR: 15-30 minutos',
    ],
  },
  5: {
    name: 'Optimizado',
    maturityGap: 'Excelencia operativa con IA/ML',
    executiveSummary: 'Testing casi invisible para developers. Generación automática de casos. Observabilidad predictiva. Mejora continua autónoma.',
    benefits: [
      'Generación automática de casos de prueba (IA)',
      'Testeo predictivo antes de producción',
      'Observabilidad con IA predice incidentes',
      'Mejora continua completamente autónoma',
    ],
    riskMitigation: [
      '✓ Defectos cercanos a CERO',
      '✓ Incidentes preventivos (predichos antes)',
      '✓ Seguridad y compliance automático',
      '✓ 80% Shift-Left: IA genera tests automáticamente',
    ],
    processEfficiency: [
      '✓ Testing manual 5%, automatización 95%',
      '✓ Developers sin overhead de testing',
      '✓ Cobertura >95%, adaptada automáticamente',
      '✓ Test execution seconds',
    ],
    observability: [
      '✓ Observabilidad total con IA/ML',
      '✓ Predicción de degradación 12-48h anticipado',
      '✓ Análisis causal automático',
      '✓ Causa raíz identificada automáticamente',
    ],
    shiftStrategy: [
      '📍 80% Shift-Left: IA genera tests, SAST autónomo, fuzzing contínuo',
      '📍 60% Shift-Right: Monitoreo autónomo 24/7, alertas predictivas, self-healing tests',
    ],
    attributes: {
      'Metodología': 90,
      'Funcionales': 100,
      'Desempeño': 80,
      'Seguridad': 70,
      'Automatización': 90,
      'Datos': 90,
      'Adopción de AI': 80,
      'Observabilidad': 80,
    },
    impact: [
      '💰 Costo de defectos: $0 (prevenidos)',
      '📈 Mejora: -99.5% defectos vs Level 0',
      '⚡ Velocidad release: Continuous deployment',
      '😍 Satisfacción cliente: 95%+',
      '⏰ MTTR: <5 minutos (automático)',
    ],
  },
  6: {
    name: 'Inteligente',
    maturityGap: 'Futuro: Testing invisible y autónomo',
    executiveSummary: 'IA generativa crea y repara tests. Cero intervención manual. Observabilidad cognitiva. Negocio en tempo máximo.',
    benefits: [
      'Pruebas autorreparables con IA (self-healing)',
      'IA generativa crea nuevos test cases automáticamente',
      'Zero-touch testing: desarrolladores escriben código',
      'Negocios itera a velocidad máxima',
    ],
    riskMitigation: [
      '✓ Defectos prácticamente eliminados',
      '✓ Incidentes prevenidos automáticamente',
      '✓ Compliance y seguridad automático 24/7',
      '✓ 100% Shift-Left: IA omnipresente en desarrollo',
    ],
    processEfficiency: [
      '✓ Testing manual 0%, IA 100%',
      '✓ Code to production: minutos',
      '✓ Cobertura dinámica y adaptable',
      '✓ Zero QA overhead',
    ],
    observability: [
      '✓ Cognición total: IA entiende intención del código',
      '✓ Anticipación: problemas detectados antes de ocurrir',
      '✓ Auto-remediación: IA repara automáticamente',
      '✓ Root cause: explicación cognitiva automática',
    ],
    shiftStrategy: [
      '📍 100% Shift-Left: IA cognitiva en IDE, auto-test generation',
      '📍 100% Shift-Right: Observabilidad total, auto-remediation, predictive infrastructure',
    ],
    attributes: {
      'Metodología': 100,
      'Funcionales': 100,
      'Desempeño': 100,
      'Seguridad': 100,
      'Automatización': 100,
      'Datos': 100,
      'Adopción de AI': 100,
      'Observabilidad': 100,
    },
    impact: [
      '💰 Costo de defectos: $0',
      '📈 Mejora: -100% defectos vs Level 0',
      '⚡ Time-to-market: Horas/minutos',
      '😍 Satisfacción cliente: 99%+',
      '⏰ MTTR: Automático',
    ],
  },
};

export default function QualityRadarChart({ data = {} }) {
  const [selectedLevel, setSelectedLevel] = useState(3);
  const [expandedLevel, setExpandedLevel] = useState(null);

  const currentLevel = MATURITY_LEVELS[0];
  const targetLevel = MATURITY_LEVELS[selectedLevel];

  const radarData = Object.entries(targetLevel.attributes).map(([category, value]) => ({
    category,
    value,
    fullMark: 100,
  }));

  return (
    <div className="space-y-3">
      {/* Compact selector in header/modal */}
      <div className="flex items-center justify-between px-1">
        <div>
          <h3 className="text-lg font-bold text-gray-900">Maturity Roadmap</h3>
        </div>
        <select
          value={selectedLevel}
          onChange={(e) => setSelectedLevel(parseInt(e.target.value))}
          className="px-3 py-1 text-sm border border-gray-300 rounded-lg bg-white text-gray-900 font-semibold focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          {Object.entries(MATURITY_LEVELS).map(([level, info]) => (
            <option key={level} value={level}>
              Level {level}: {info.name}
            </option>
          ))}
        </select>
      </div>

      {/* Radar Chart - Main */}
      <div className="bg-white p-3 rounded-lg shadow-sm border border-gray-200">
        <div className="w-full h-96">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData} margin={{ top: 20, right: 100, left: 100, bottom: 20 }}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="category" tick={{ fill: '#6b7280', fontSize: 11 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar name={`Level ${selectedLevel}`} dataKey="value" stroke="#8b5cf6" fill="#a78bfa" fillOpacity={.6} />
              <Tooltip formatter={(value) => `${Math.round(value)}%`} />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Side-by-side comparison - compact */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-2">
        {/* Current Level (Baseline) */}
        <div className="border border-gray-300 rounded-lg p-3 bg-gray-50">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-full bg-gray-400 flex items-center justify-center text-white font-bold text-xs">0</div>
              <div>
                <p className="text-xs text-gray-600 uppercase font-semibold">Current</p>
                <p className="text-sm font-bold text-gray-900">{currentLevel.name}</p>
              </div>
          </div>
          <p className="text-xs text-gray-700 leading-tight italic">{currentLevel.executiveSummary}</p>
        </div>

        {/* Target Level */}
        <div className="border border-purple-500 rounded-lg p-3 bg-purple-50">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold text-xs">{selectedLevel}</div>
            <div>
              <p className="text-xs text-gray-600 uppercase font-semibold">Target</p>
              <p className="text-sm font-bold text-purple-900">{targetLevel.name}</p>
            </div>
          </div>
          <p className="text-xs text-gray-700 leading-tight italic">{targetLevel.executiveSummary}</p>
        </div>
      </div>

      {/* Benefits, Risks and Efficiency - improved readability */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-gradient-to-br from-green-50 to-white p-4 rounded-lg shadow-sm border border-green-300 border-l-4 border-l-green-500">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp size={18} className="text-green-600" />
            <h4 className="text-sm font-bold text-gray-900">Benefits</h4>
          </div>
          <ul className="space-y-2">
            {targetLevel.benefits.map((benefit, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-700 leading-snug">
                <span className="text-green-600 font-bold text-lg flex-shrink-0 mt-.5">✓</span>
                <span>{benefit}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-white p-4 rounded-lg shadow-sm border border-red-300 border-l-4 border-l-red-500">
          <div className="flex items-center gap-2 mb-3">
            <Shield size={18} className="text-red-600" />
            <h4 className="text-sm font-bold text-gray-900">Risks</h4>
          </div>
          <ul className="space-y-2">
            {targetLevel.riskMitigation.map((risk, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-700 leading-snug">
                <span className="flex-shrink-0 font-bold text-red-600">{risk.split(' ')[0]}</span>
                <span>{risk.substring(2)}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-white p-4 rounded-lg shadow-sm border border-blue-300 border-l-4 border-l-blue-500">
          <div className="flex items-center gap-2 mb-3">
            <Zap size={18} className="text-blue-600" />
            <h4 className="text-sm font-bold text-gray-900">Efficiency</h4>
          </div>
          <ul className="space-y-2">
            {targetLevel.processEfficiency.map((eff, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-700 leading-snug">
                <span className="flex-shrink-0 font-bold text-blue-600">{eff.split(' ')[0]}</span>
                <span>{eff.substring(2)}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Observability and Shift Strategy - improved readability */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="bg-gradient-to-br from-yellow-50 to-white p-4 rounded-lg shadow-sm border border-yellow-300 border-l-4 border-l-yellow-500">
          <div className="flex items-center gap-2 mb-3">
            <Eye size={18} className="text-yellow-600" />
            <h4 className="text-sm font-bold text-gray-900">Observability</h4>
          </div>
          <ul className="space-y-2">
            {targetLevel.observability.map((obs, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-700 leading-snug">
                <span className="flex-shrink-0 font-bold text-yellow-600">{obs.split(' ')[0]}</span>
                <span>{obs.substring(2)}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-gradient-to-br from-indigo-50 to-white p-4 rounded-lg shadow-sm border border-indigo-300 border-l-4 border-l-indigo-500">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle size={18} className="text-indigo-600" />
            <h4 className="text-sm font-bold text-gray-900">Shift-Left/Right</h4>
          </div>
          <ul className="space-y-2">
            {targetLevel.shiftStrategy.map((shift, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-700 leading-snug">
                <span className="flex-shrink-0 font-bold text-indigo-600">{shift.split(' ')[0]}</span>
                <span>{shift.substring(2)}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Business Impact - compact */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border border-purple-200">
        <h4 className="text-xs font-bold text-gray-900 mb-2">Impact - Level {selectedLevel}</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {targetLevel.impact.map((item, idx) => (
            <div key={idx} className="flex items-start gap-1 p-1 bg-white rounded">
              <span className="text-sm flex-shrink-0">{item.split(' ')[0]}</span>
              <p className="text-xs text-gray-900">{item.substring(2)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Attribute Comparison - compact */}
      <div className="bg-white p-3 rounded-lg shadow-sm border border-gray-200">
        <h4 className="text-xs font-bold text-gray-900 mb-2">Attributes</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {Object.keys(MATURITY_LEVELS[0].attributes).map((attr) => (
            <div key={attr} className="p-2 bg-gradient-to-br from-gray-50 to-white rounded border border-gray-200">
              <p className="text-xs font-semibold text-gray-600 uppercase mb-1">{attr}</p>
              <div className="flex items-center justify-between mb-1 text-xs">
                <div className="text-center">
                  <p className="font-bold text-gray-400">{currentLevel.attributes[attr]}%</p>
                </div>
                <div>→</div>
                <div className="text-center">
                  <p className="font-bold text-purple-600">{targetLevel.attributes[attr]}%</p>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1">
                <div className="bg-purple-600 h-1 rounded-full" style={{ width: `${targetLevel.attributes[attr]}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Estimated ROI by maturity level */}
      {(() => {
        const roiMultipliers = {0:0.05,1:0.1,2:0.25,3:0.45,4:0.7,5:0.9,6:0.98};
        const baseAnnualCost = 300000; // base de referencia (costos por defectos/uops)
        const estimatedSavings = Math.round(baseAnnualCost * (roiMultipliers[selectedLevel] || 0));
        const ttmImprovements = ['0%','5%','10%','20%','35%','50%','65%'];
        const mttrImprovements = ['0%','10%','15%','30%','45%','60%','80%'];

        return (
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h4 className="text-lg font-bold text-gray-900">Estimated ROI by Maturity</h4>
            <p className="text-sm text-gray-600">Simplified estimate of annual savings from defect reduction and operational improvements for the selected target level.</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
              <div className="p-3 bg-green-50 rounded-lg">
                <div className="text-xs text-gray-600">Estimated annual savings</div>
                  <div className="text-2xl font-bold text-green-700">${estimatedSavings.toLocaleString()}</div>
                  <div className="text-xs text-gray-500">Based on ${baseAnnualCost.toLocaleString()}</div>
              </div>

              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="text-xs text-gray-600">Time-to-market improvement</div>
                <div className="text-2xl font-bold text-blue-700">{ttmImprovements[selectedLevel] || 'N/A'}</div>
                <div className="text-xs text-gray-500">Estimated % acceleration</div>
              </div>

              <div className="p-3 bg-yellow-50 rounded-lg">
                <div className="text-xs text-gray-600">MTTR reduction</div>
                <div className="text-2xl font-bold text-yellow-700">{mttrImprovements[selectedLevel] || 'N/A'}</div>
                <div className="text-xs text-gray-500">Estimated % reduction</div>
              </div>
            </div>
          </div>
        );
      })()}


    </div>
  );
}


