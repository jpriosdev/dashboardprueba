/**
 * QA Dashboard Page
 * Main page for the QA executive dashboard.
 * Renders the ExecutiveDashboard with API sources and refresh interval.
 */
import ExecutiveDashboard from '../components/ExecutiveDashboard';

export default function QADashboardPage() {
  return (
    <ExecutiveDashboard 
      dataSource="/api/qa-data"
      configSource="/api/config"
      refreshInterval={300000} // 5 minutes
    />
  );
}

// Force SSG: fetch QA data at build time so Next generates a static HTML for this page
export async function getStaticProps() {
  try {
    const loader = await import('../lib/qaDataLoader.js');
    const data = await loader.getQAData({ forceReload: false });
    return { props: { initialQAData: data || null } };
  } catch (e) {
    return { props: { initialQAData: null } };
  }
}

