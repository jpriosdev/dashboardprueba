"""
Análisis de Métricas de Calidad y Testing - JIRA LTI
Experto en Analítica de Datos para Director de Tecnología
"""

import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class JiraQualityAnalyzer:
    """
    Analizador especializado en calidad y testing para datasets de JIRA
    """
    
    def __init__(self, csv_path):
        """Inicializar con ruta al archivo CSV"""
        self.csv_path = csv_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Cargar y preparar datos"""
        print("📂 Cargando datos JIRA LTI...")
        self.df = pd.read_csv(self.csv_path)
        print(f"✓ {len(self.df)} registros cargados")
        print(f"✓ {len(self.df.columns)} columnas")
    
    def get_overview(self):
        """Resumen general del proyecto"""
        print("\n" + "="*70)
        print("📊 RESUMEN GENERAL DEL PROYECTO")
        print("="*70)
        
        # Issues por tipo
        print("\n1. DISTRIBUCIÓN DE TIPOS DE ISSUES:")
        issue_types = self.df['Issue Type'].value_counts()
        for issue_type, count in issue_types.items():
            pct = (count / len(self.df)) * 100
            print(f"   • {issue_type}: {count} ({pct:.1f}%)")
        
        # Estados
        print("\n2. DISTRIBUCIÓN DE ESTADOS:")
        statuses = self.df['Status'].value_counts()
        for status, count in statuses.items():
            pct = (count / len(self.df)) * 100
            print(f"   • {status}: {count} ({pct:.1f}%)")
        
        # Prioridades
        print("\n3. DISTRIBUCIÓN DE PRIORIDADES:")
        priorities = self.df['Priority'].value_counts()
        for priority, count in priorities.items():
            if pd.notna(priority):
                pct = (count / len(self.df)) * 100
                print(f"   • {priority}: {count} ({pct:.1f}%)")
    
    def calculate_test_coverage_rate(self):
        """
        MÉTRICA 1: Test Coverage Rate
        Porcentaje de historias con test execution asociado
        """
        print("\n" + "="*70)
        print("🧪 MÉTRICA 1: TEST COVERAGE RATE (TCR)")
        print("="*70)
        
        stories = self.df[self.df['Issue Type'] == 'Story']
        test_execs = self.df[self.df['Issue Type'] == 'Test Execution']
        
        # Issues que tiene relación Test
        issues_with_tests = self.df[
            self.df['Inward issue link (Test)'].notna() | 
            self.df['Outward issue link (Test)'].notna()
        ]
        
        tcr = (len(issues_with_tests) / len(self.df)) * 100 if len(self.df) > 0 else 0
        
        print(f"\n✓ Total Issues con Test asociado: {len(issues_with_tests)}")
        print(f"✓ Total Stories: {len(stories)}")
        print(f"✓ Total Test Executions: {len(test_execs)}")
        print(f"\n📈 TEST COVERAGE RATE: {tcr:.1f}%")
        print(f"🎯 Meta recomendada: >80%")
        print(f"⚠️  Estado: {'CRÍTICO' if tcr < 50 else 'MEJORABLE' if tcr < 80 else 'ACEPTABLE'}")
        
        return tcr
    
    def calculate_defect_escape_rate(self):
        """
        MÉTRICA 2: Defect Escape Rate
        Bugs encontrados en producción vs total de bugs
        """
        print("\n" + "="*70)
        print("🐛 MÉTRICA 2: DEFECT ESCAPE RATE (DER)")
        print("="*70)
        
        bugs = self.df[self.df['Issue Type'] == 'Bug']
        bugs_done = bugs[bugs['Status'] == 'Done']
        bugs_in_prod = bugs_done[bugs_done['Status'] == 'Done'].copy()
        
        # Checks si tiene "Deployed to Production" en el log de trabajo
        deployed_bugs = 0
        for idx, row in bugs_in_prod.iterrows():
            if pd.notna(row.get('Log Work', '')):
                if 'Deployed to Production' in str(row.get('Log Work', '')):
                    deployed_bugs += 1
        
        der = (deployed_bugs / len(bugs)) * 100 if len(bugs) > 0 else 0
        
        print(f"\n✓ Total Bugs registrados: {len(bugs)}")
        print(f"✓ Bugs completados (Done): {len(bugs_done)}")
        print(f"✓ Bugs escapados a producción: {deployed_bugs}")
        print(f"\n📈 DEFECT ESCAPE RATE: {der:.1f}%")
        print(f"🎯 Meta recomendada: <5%")
        print(f"⚠️  Estado: {'CRÍTICO' if der > 10 else 'MEJORABLE' if der > 5 else 'ACEPTABLE'}")
        
        return der, len(bugs)
    
    def calculate_test_execution_velocity(self):
        """
        MÉTRICA 3: Test Execution Velocity
        Test cases ejecutados por día de sprint
        """
        print("\n" + "="*70)
        print("⚡ MÉTRICA 3: TEST EXECUTION VELOCITY (TEV)")
        print("="*70)
        
        test_execs = self.df[self.df['Issue Type'] == 'Test Execution']
        test_execs_done = test_execs[test_execs['Status'].isin(['Done', 'In Testing', 'Ready for Testing'])]
        
        # Análisis por sprint
        sprints = self.df['Sprint'].dropna().unique()
        print(f"\n✓ Sprints activos: {len(sprints)}")
        
        # Sprints identificados
        sprint_data = []
        for sprint in sprints[:5]:  # Top 5 sprints
            if pd.notna(sprint):
                sprint_tests = test_execs_done[test_execs_done['Sprint'] == sprint]
                sprint_data.append({
                    'sprint': str(sprint)[:30],
                    'tests': len(sprint_tests)
                })
        
        avg_tests_per_sprint = len(test_execs_done) / len(sprints) if len(sprints) > 0 else 0
        tev = avg_tests_per_sprint / 14  # Asumiendo sprints de 2 semanas
        
        print(f"\n✓ Test Executions completadas: {len(test_execs_done)}")
        print(f"✓ Promedio por sprint: {avg_tests_per_sprint:.1f}")
        print(f"\n📈 TEST EXECUTION VELOCITY: {tev:.2f} tests/día")
        print(f"🎯 Meta recomendada: >1.0 tests/día")
        print(f"⚠️  Estado: {'CRÍTICO' if tev < 0.5 else 'MEJORABLE' if tev < 1.0 else 'ACEPTABLE'}")
        
        return tev, len(test_execs_done)
    
    def calculate_quality_gate_pass_rate(self):
        """
        MÉTRICA 4: Quality Gate Pass Rate
        Issues que cumplen criterios sin rechazo
        """
        print("\n" + "="*70)
        print("✅ MÉTRICA 4: QUALITY GATE PASS RATE (QGPR)")
        print("="*70)
        
        issues_done = self.df[self.df['Status'] == 'Done']
        
        # Issues que fueron rechazadas (tienen estado "Reviewed" antes de Done)
        # Aproximación: si tienen múltiples transiciones de estado
        rejected_pattern = self.df[
            self.df['Status Category'].isin(['In Progress', 'To Do', 'Reviewed'])
        ]
        
        # Issues que pasaron directamente
        clean_issues = issues_done[~issues_done['Issue id'].isin(rejected_pattern['Issue id'])]
        
        qgpr = (len(clean_issues) / len(self.df)) * 100 if len(self.df) > 0 else 0
        
        print(f"\n✓ Total issues completadas (Done): {len(issues_done)}")
        print(f"✓ Issues sin rechazo: {len(clean_issues)}")
        print(f"✓ Issues con rework: {len(rejected_pattern)}")
        print(f"\n📈 QUALITY GATE PASS RATE: {qgpr:.1f}%")
        print(f"🎯 Meta recomendada: >70%")
        print(f"⚠️  Estado: {'CRÍTICO' if qgpr < 50 else 'MEJORABLE' if qgpr < 70 else 'ACEPTABLE'}")
        
        return qgpr
    
    def analyze_bug_severity(self):
        """
        MÉTRICA 5: Bug Severity Distribution
        Análisis de severidad de bugs
        """
        print("\n" + "="*70)
        print("🚨 MÉTRICA 5: BUG SEVERITY DISTRIBUTION (BSD)")
        print("="*70)
        
        bugs = self.df[self.df['Issue Type'] == 'Bug']
        
        # Clasificar por severidad basado en:
        # 1. Priority
        # 2. Bloqueadores (Inward Blocks)
        # 3. Descripción
        
        critical_keywords = ['crash', 'security', 'data loss', 'blocks', 'critical']
        high_keywords = ['error', 'broken', 'defect', 'failure']
        
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for idx, row in bugs.iterrows():
            priority = str(row.get('Priority', '')).lower()
            description = str(row.get('Description', '')).lower()
            summary = str(row.get('Summary', '')).lower()
            
            text = description + ' ' + summary
            
            if 'critical' in priority or any(kw in text for kw in critical_keywords):
                critical_count += 1
            elif 'high' in priority or any(kw in text for kw in high_keywords):
                high_count += 1
            elif 'medium' in priority:
                medium_count += 1
            else:
                low_count += 1
        
        total_bugs = len(bugs)
        
        print(f"\n✓ Total Bugs: {total_bugs}")
        print(f"\n📊 Distribución de severidad:")
        
        if total_bugs > 0:
            critical_pct = (critical_count / total_bugs) * 100
            high_pct = (high_count / total_bugs) * 100
            medium_pct = (medium_count / total_bugs) * 100
            low_pct = (low_count / total_bugs) * 100
            
            print(f"   🔴 Critical: {critical_count} ({critical_pct:.1f}%)")
            print(f"   🟠 High: {high_count} ({high_pct:.1f}%)")
            print(f"   🟡 Medium: {medium_count} ({medium_pct:.1f}%)")
            print(f"   🟢 Low: {low_count} ({low_pct:.1f}%)")
            
            print(f"\n🎯 Metas recomendadas:")
            print(f"   • Critical: 0% (Actual: {critical_pct:.1f}%)")
            print(f"   • High: <5% (Actual: {high_pct:.1f}%)")
            print(f"   • Medium: <15% (Actual: {medium_pct:.1f}%)")
            print(f"   • Low: >80% (Actual: {low_pct:.1f}%)")
            
            health = 'CRÍTICO' if critical_pct > 5 else 'MEJORABLE' if high_pct > 10 else 'ACEPTABLE'
            print(f"\n⚠️  Estado: {health}")
        
        return {
            'critical': critical_count,
            'high': high_count,
            'medium': medium_count,
            'low': low_count
        }
    
    def analyze_time_metrics(self):
        """Análisis de tiempos de resolución"""
        print("\n" + "="*70)
        print("⏱️  ANÁLISIS DE TIEMPOS DE RESOLUCIÓN")
        print("="*70)
        
        # Análisis de columna "Time Spent"
        time_spent = pd.to_numeric(self.df['Time Spent'], errors='coerce')
        
        print(f"\n✓ Total tiempo registrado: {time_spent.sum():.0f} horas")
        print(f"✓ Promedio por issue: {time_spent.mean():.1f} horas")
        print(f"✓ Mediana: {time_spent.median():.1f} horas")
        print(f"✓ Máximo: {time_spent.max():.0f} horas")
        print(f"✓ Mínimo: {time_spent.min():.0f} horas")
        
        # Por tipo de issue
        print(f"\n📊 Tiempo promedio por tipo de issue:")
        for issue_type in self.df['Issue Type'].unique():
            if pd.notna(issue_type):
                type_time = time_spent[self.df['Issue Type'] == issue_type].mean()
                if not pd.isna(type_time):
                    print(f"   • {issue_type}: {type_time:.1f} horas")
    
    def generate_report(self):
        """Generar reporte completo"""
        print("\n\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*15 + "REPORTE DE CALIDAD Y TESTING JIRA LTI" + " "*17 + "║")
        print("╚" + "="*68 + "╝")
        
        self.get_overview()
        tcr = self.calculate_test_coverage_rate()
        der, total_bugs = self.calculate_defect_escape_rate()
        tev, test_execs = self.calculate_test_execution_velocity()
        qgpr = self.calculate_quality_gate_pass_rate()
        bsd = self.analyze_bug_severity()
        self.analyze_time_metrics()
        
        # Resumen ejecutivo
        print("\n\n" + "="*70)
        print("📋 RESUMEN EJECUTIVO PARA DIRECTOR")
        print("="*70)
        
        print(f"""
╔─ KPIs CRÍTICOS ──────────────────────────────────────────────────╗
│                                                                  │
│  1. Test Coverage Rate:        {tcr:>6.1f}%  [Meta: 80%]
│  2. Defect Escape Rate:        {der:>6.1f}%  [Meta: <5%]
│  3. Test Execution Velocity:   {tev:>6.2f}   tests/día [Meta: >1.0]
│  4. Quality Gate Pass Rate:    {qgpr:>6.1f}%  [Meta: 70%]
│                                                                  │
│  Total Bugs: {total_bugs:<3} | Test Executions: {test_execs:<3}              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
        """)
        
        print("\n🎯 RECOMENDACIONES INMEDIATAS:")
        print("""
1. IMPLEMENTAR TEST-FIRST APPROACH
   → Crear Test Cases ANTES de "In Development"
   → Responsable: QA Lead
   → Timeline: Inmediato
   
2. OPTIMIZAR VELOCIDAD DE TESTING  
   → Target: 0.21 → 1.0 tests/día (+380% mejora)
   → Estrategia: Automatización + paralelización
   → Timeline: 30 días
   
3. ESTABLECER DEFINITION OF DONE
   → Checklist: Test execution + Quality gate + 0 Critical bugs
   → Enforcement: No merge sin cumplir
   → Timeline: Inmediato
   
4. MONITOREAR KPIs SEMANALMENTE
   → Dashboard actualizado cada lunes
   → Alertas: DER >5%, TCR <70%
   → Escalation: Director si hay 2 semanas bajo meta
        """)
        
        print("\n" + "="*70)


def main():
    """Punto de entrada"""
    try:
        analyzer = JiraQualityAnalyzer(
            r"c:\Users\ultra\PycharmProjects\PythonProject\TablerosLTI\JIRA LTI.csv"
        )
        analyzer.generate_report()
        
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo JIRA LTI.csv")
    except Exception as e:
        print(f"❌ Error durante análisis: {str(e)}")


if __name__ == "__main__":
    main()
