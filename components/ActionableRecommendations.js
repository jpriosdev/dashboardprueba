// ActionableRecommendations.js
// Component to generate actionable recommendations based on QA metrics
import React from 'react';
import { Lightbulb, AlertTriangle, TrendingUp, CheckCircle, Target, Users, Code, Clock } from 'lucide-react';

/**
 * Component that generates actionable recommendations based on sprint and KPI data.
 * All calculations and names are aligned with the new SQL/CSV data structure.
 * Applies coding, security and performance best practices.
 * @param {Object} props
 * @param {Object} props.data - Datos globales del dashboard
 * @param {Array} props.filteredSprintData - Array de datos de sprints filtrados
 */
export default function ActionableRecommendations({ data, filteredSprintData }) {
  // Normalize filteredSprintData to accept array or object shapes
  const sprintsArray = Array.isArray(filteredSprintData)
    ? filteredSprintData
    : (filteredSprintData && Array.isArray(filteredSprintData.sprintData))
      ? filteredSprintData.sprintData
      : (filteredSprintData && Array.isArray(filteredSprintData.sprints))
        ? filteredSprintData.sprints
        : [];

  if (!data || sprintsArray.length === 0) return null;

  // Robust calculation of main metrics
  const totalBugs = sprintsArray.reduce((acc, sprint) => acc + (sprint.bugs || sprint.bugs_encontrados || 0), 0);
  const bugsClosed = sprintsArray.reduce((acc, sprint) => acc + (sprint.bugsResolved || sprint.bugs_resueltos || 0), 0);
  const totalTestCases = sprintsArray.reduce((acc, sprint) => acc + (sprint.testCases || sprint.casosEjecutados || sprint.test_cases || 0), 0);

  // Resolution efficiency
  const resolutionEfficiency = totalBugs > 0 ? Math.round((bugsClosed / totalBugs) * 100) : 0;
  // Average test cases executed per sprint
  const avgTestCasesPerSprint = sprintsArray.length > 0 ? Math.round(totalTestCases / sprintsArray.length) : 0;

  // Calculation of critical bugs
  const criticalBugsTotal = sprintsArray.reduce((acc, sprint) => {
    const priorities = sprint.bugsByPriority || {};
    return acc + (priorities['Más alta'] || priorities['Alta'] || 0);
  }, 0);
  const criticalBugsPercent = totalBugs > 0 ? (criticalBugsTotal / totalBugs) * 100 : 0;

  // Estimated cycle time calculation
  const sprintDays = 14;
  const avgEfficiency = sprintsArray.reduce((acc, sprint) => {
    const total = sprint.bugs || sprint.bugs_encontrados || 0;
    const resolved = sprint.bugsResolved || sprint.bugs_resueltos || 0;
    return acc + (total > 0 ? resolved / total : 0);
  }, 0) / (sprintsArray.length || 1);
  const cycleTime = Math.round(sprintDays * (1 - avgEfficiency * 0.5));

  // Defect density
  const estimatedHUsPerSprint = 6;
  const totalHUs = sprintsArray.length * estimatedHUsPerSprint;
  const defectDensity = totalBugs / (totalHUs || 1);

  // Generate recommendations based on thresholds and best practices
  const recommendations = [];

  // Cycle Time recommendations
  if (cycleTime > 10) {
    recommendations.push({
      category: 'velocity',
      priority: 'high',
      icon: <Clock className="w-5 h-5" />,
      title: 'Reduce Critical Cycle Time',
      description: `Average resolution time is ${cycleTime} days, exceeding the 10-day threshold.`,
      actions: [
        'Implement daily 15min meetings to resolve blockers',
        'Assign critical bugs to dedicated senior developers',
        'Set a 48h SLA for critical-priority bugs',
        'Review deployment process to speed up fix releases'
      ],
      impact: 'High',
      effort: 'Medium'
    });
  } else if (cycleTime > 7) {
    recommendations.push({
      category: 'velocity',
      priority: 'medium',
      icon: <Clock className="w-5 h-5" />,
      title: 'Optimize Resolution Velocity',
      description: `The cycle time of ${cycleTime} days is acceptable but can be improved.`,
      actions: [
        'Document bugs with more detail to speed up diagnosis',
        'Implement a hotfix pipeline for urgent bugs',
        'Train the team on efficient debugging techniques'
      ],
      impact: 'Medium',
      effort: 'Low'
    });
  }

  // Defect Density recommendations
  if (defectDensity > 2.0) {
    recommendations.push({
      category: 'quality',
      priority: 'high',
      icon: <Code className="w-5 h-5" />,
      title: 'Urgent Code Quality Improvement',
      description: `A defect density of ${defectDensity.toFixed(2)} bugs/HU indicates serious quality issues.`,
      actions: [
        'Enforce code reviews with at least 2 approvers',
        'Increase unit test coverage to at least 80%',
        'Implement static code analysis (SonarQube/ESLint)',
        'Require pair programming for complex HUs',
        'Refactor modules with high bug concentration'
      ],
      impact: 'Very High',
      effort: 'High'
    });
  } else if (defectDensity > 1.0) {
    recommendations.push({
      category: 'quality',
      priority: 'medium',
      icon: <Code className="w-5 h-5" />,
      title: 'Strengthen Quality Practices',
      description: `A defect density of ${defectDensity.toFixed(2)} bugs/HU suggests room for improvement.`,
      actions: [
        'Establish a Definition of Done with quality criteria',
        'Increase integration test coverage',
        'Conduct weekly mob programming sessions',
        'Implement a pre-commit quality checklist'
      ],
      impact: 'Medium',
      effort: 'Medium'
    });
  }

  // Resolution Efficiency recommendations
  if (resolutionEfficiency < 50) {
    recommendations.push({
      category: 'efficiency',
      priority: 'high',
      icon: <Target className="w-5 h-5" />,
      title: 'Improve Critical Resolution Efficiency',
      description: `Only ${resolutionEfficiency}% of bugs are resolved - well below the 70% target.`,
      actions: [
        'Analyze root causes of unresolved bugs (resource constraints, complexity, prioritization)',
        'Increase team capacity or redistribute workload',
        'Hold bi-weekly triage meetings',
        'Implement an escalation system for stalled bugs',
        'Consider bringing external consultants for complex bugs'
      ],
      impact: 'Critical',
      effort: 'High'
    });
  } else if (resolutionEfficiency < 70) {
    recommendations.push({
      category: 'efficiency',
      priority: 'medium',
      icon: <Target className="w-5 h-5" />,
      title: 'Increase Resolution Rate',
      description: `An efficiency of ${resolutionEfficiency}% is below the 70% target.`,
      actions: [
        'Review bug backlog prioritization',
        'Allocate dedicated sprint time for bug resolution',
        'Implement a weekly "bug master" rotation',
        'Automate repetitive bugs where possible'
      ],
      impact: 'High',
      effort: 'Medium'
    });
  }

  // Critical Bugs recommendations
  if (criticalBugsPercent > 30) {
    recommendations.push({
      category: 'critical',
      priority: 'high',
      icon: <AlertTriangle className="w-5 h-5" />,
      title: 'High Volume of Critical Bugs',
      description: `${criticalBugsPercent.toFixed(1)}% of bugs are critical - requires immediate attention.`,
      actions: [
        'Review architecture of most affected components',
        'Implement automated smoke tests pre-deployment',
        'Improve acceptance criteria in user stories',
        'Perform root cause analysis of recurring critical bugs',
        'Hold a quality-focused retrospective session'
      ],
      impact: 'Very High',
      effort: 'High'
    });
  } else if (criticalBugsPercent > 20) {
    recommendations.push({
      category: 'critical',
      priority: 'medium',
      icon: <AlertTriangle className="w-5 h-5" />,
      title: 'Reduce Proportion of Critical Bugs',
      description: `${criticalBugsPercent.toFixed(1)}% critical bugs exceeds the 20% target.`,
      actions: [
        'Improve pre-production testing process',
        'Implement QA checklist for core features',
        'Increase regression test coverage'
      ],
      impact: 'High',
      effort: 'Medium'
    });
  }

  // Testing Coverage recommendations
  if (avgTestCasesPerSprint < 150) {
    recommendations.push({
      category: 'testing',
      priority: 'medium',
      icon: <CheckCircle className="w-5 h-5" />,
      title: 'Increase Test Coverage',
      description: `Only ${avgTestCasesPerSprint} test cases executed per sprint - below the target of 200.`,
      actions: [
        'Automatizar casos de prueba manuales repetitivos',
        'Automate repetitive manual test cases',
        'Increase QA team or train developers in testing',
        'Implement CI/CD with automatic tests on every PR',
        'Create automated regression test suite'
      ],
      impact: 'High',
      effort: 'High'
    });
  }

  // ...renderizado y lógica UI sin cambios...
  // ...existing code...

  // Positive recommendations when metrics are strong
  if (resolutionEfficiency >= 80 && defectDensity <= 1.0 && cycleTime <= 7) {
    recommendations.push({
      category: 'excellence',
      priority: 'low',
      icon: <TrendingUp className="w-5 h-5" />,
      title: 'Excellent Performance - Maintain Practices',
      description: 'The team demonstrates outstanding metrics in quality and velocity.',
      actions: [
        'Document successful practices for other teams',
        'Share learnings in knowledge-sharing sessions',
        'Consider increasing feature complexity based on this solid foundation',
        'Explore opportunities for technical innovation'
      ],
      impact: 'Medium',
      effort: 'Low'
    });
  }

  // Ordenar por prioridad
  const priorityOrder = { high: 0, medium: 1, low: 2 };
  recommendations.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'border-danger-500 bg-danger-50';
      case 'medium': return 'border-warning-500 bg-warning-50';
      case 'low': return 'border-success-500 bg-success-50';
      default: return 'border-gray-300 bg-gray-50';
    }
  };

  const getPriorityTextColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-danger-700';
      case 'medium': return 'text-warning-700';
      case 'low': return 'text-success-700';
      default: return 'text-gray-700';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'velocity': return <Clock className="w-5 h-5" />;
      case 'quality': return <Code className="w-5 h-5" />;
      case 'efficiency': return <Target className="w-5 h-5" />;
      case 'critical': return <AlertTriangle className="w-5 h-5" />;
      case 'testing': return <CheckCircle className="w-5 h-5" />;
      case 'excellence': return <TrendingUp className="w-5 h-5" />;
      default: return <Lightbulb className="w-5 h-5" />;
    }
  };

  return (
    <div className="executive-card">
      <div className="mb-6 flex items-center">
        <Lightbulb className="w-6 h-6 text-executive-600 mr-3" />
        <div>
          <h3 className="text-xl font-bold text-gray-900">Actionable Recommendations</h3>
          <p className="text-sm text-gray-600">Based on automated analysis of metrics and quality thresholds</p>
        </div>
      </div>

      {recommendations.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CheckCircle className="w-12 h-12 mx-auto mb-3 text-success-500" />
          <p>No critical recommendations at this time. Good job!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec, index) => (
            <div
              key={index}
              className={`border-l-4 ${getPriorityColor(rec.priority)} rounded-lg p-5 shadow-sm`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center">
                  <div className={`${getPriorityTextColor(rec.priority)} mr-3`}>{getCategoryIcon(rec.category)}</div>
                  <div>
                    <h4 className="font-bold text-gray-900 text-lg">{rec.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                  </div>
                </div>
                <div className="flex gap-2 text-xs">
                  <span className={`px-3 py-1 rounded-full font-semibold ${
                    rec.priority === 'high' ? 'bg-danger-100 text-danger-700' :
                    rec.priority === 'medium' ? 'bg-warning-100 text-warning-700' :
                    'bg-success-100 text-success-700'
                  }`}>
                    {rec.priority === 'high' ? 'High' : rec.priority === 'medium' ? 'Medium' : 'Low'}
                  </span>
                </div>
              </div>

              <div className="mt-4">
                <div className="font-semibold text-sm text-gray-700 mb-2">Suggested Actions:</div>
                <ul className="space-y-2">
                  {rec.actions.map((action, idx) => (
                    <li key={idx} className="flex items-start text-sm text-gray-700">
                      <span className="text-executive-600 mr-2 mt-0.5">▸</span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 flex gap-4 text-xs">
                <div>
                  <span className="font-semibold text-gray-600">Impact:</span>
                  <span className="ml-2 text-gray-900">{rec.impact}</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-600">Effort:</span>
                  <span className="ml-2 text-gray-900">{rec.effort}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
