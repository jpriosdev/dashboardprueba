import Link from 'next/link';

export default function Home() {
  return (
    <main style={{fontFamily:'Inter, system-ui, -apple-system, Roboto, "Helvetica Neue", Arial',display:'flex',alignItems:'center',justifyContent:'center',minHeight:'100vh',background:'#0f172a',color:'#e6eef8',padding:'24px'}}>
      <div style={{maxWidth:900,width:'100%',textAlign:'center'}}>
        <header style={{display:'flex',alignItems:'center',gap:16,justifyContent:'center',marginBottom:24}}>
          <svg width="64" height="64" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Abstracta logo" style={{flex:'0 0 auto'}}>
            <defs>
              <linearGradient id="g" x1="0" x2="1">
                <stop offset="0%" stopColor="#6D28D9"/>
                <stop offset="100%" stopColor="#0EA5E9"/>
              </linearGradient>
            </defs>
            <rect width="48" height="48" rx="8" fill="url(#g)" />
            <g transform="translate(8,8)" fill="#fff">
              <circle cx="8" cy="8" r="5" opacity="0.95" />
              <rect x="18" y="4" width="8" height="8" rx="2" opacity="0.95" />
            </g>
          </svg>
          <div style={{textAlign:'left'}}>
            <h1 style={{margin:0,fontSize:28}}>Abstracta QA Dashboard</h1>
            <p style={{margin:0,opacity:0.9,fontSize:13}}>Visor de métricas QA — despliegue estático listo para Vercel</p>
          </div>
        </header>

        <section style={{background:'#071033',borderRadius:12,padding:24,boxShadow:'0 6px 20px rgba(2,6,23,0.6)'}}>
          <p style={{marginTop:0,marginBottom:16}}>Bienvenido. Usa los enlaces para navegar a los módulos disponibles:</p>
          <nav style={{display:'flex',gap:12,flexWrap:'wrap',justifyContent:'center'}}>
            <Link href="/qa-dashboard"><a style={linkStyle}>QA Dashboard</a></Link>
            <Link href="/config-dashboard"><a style={linkStyle}>Config Dashboard</a></Link>
            <Link href="/qa-dashboard"><a style={linkStyle}>Executive Dashboard</a></Link>
          </nav>
          <p style={{marginTop:18,opacity:0.8,fontSize:13}}>Si alguno de los enlaces falla, revisa el despliegue o abre el menú API en <code style={{background:'#07162b',padding:'2px 6px',borderRadius:4}}> /api/* </code>.</p>
        </section>

        <footer style={{marginTop:18,opacity:0.7,fontSize:12}}>© Abstracta — generador JSON integrado • {new Date().getFullYear()}</footer>
      </div>
    </main>
  );
}

const linkStyle = {
  display:'inline-block',padding:'10px 16px',background:'linear-gradient(90deg,#1e293b,#0b1220)',color:'#e6eef8',borderRadius:8,textDecoration:'none',boxShadow:'0 4px 12px rgba(2,6,23,0.5)'
};
/**
 * Home/Redirect Page
 * Redirects all traffic to the QA dashboard.
 */
import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Auto-redirect to dashboard (non-blocking if already there)
    router.push('/qa-dashboard');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <p className="text-gray-600">Redirecting to dashboard...</p>
    </div>
  );
}
