import sqlite3 from 'sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dbPath = path.resolve(__dirname, '../public/data/qa-dashboard.db');

async function checkDensity() {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('Error abriendo BD:', err);
        reject(err);
        return;
      }

      console.log('=== VERIFICACIÓN DE DENSIDAD DE HALLAZGOS ===\n');

      // Query para verificar si el WHERE se está aplicando
      db.all(`
        SELECT sprint, COUNT(*) as total_con_sugerencias
        FROM bugs_detail
        GROUP BY sprint
        ORDER BY CAST(SUBSTR(sprint, -2) AS INTEGER)
      `, (err, rows1) => {
        if (err) {
          console.error('Error query 1:', err);
          reject(err);
          return;
        }

        console.log('TOTALES CON SUGERENCIAS INCLUIDAS:');
        rows1.forEach(r => {
          console.log(`${r.sprint}: ${r.total_con_sugerencias}`);
        });
        console.log();

        // Query con el WHERE de la vista
        db.all(`
          SELECT sprint, COUNT(*) as total_sin_sugerencias
          FROM bugs_detail
          WHERE tipo_incidencia != 'Sugerencia'
          GROUP BY sprint
          ORDER BY CAST(SUBSTR(sprint, -2) AS INTEGER)
        `, (err, rows2) => {
          if (err) {
            console.error('Error query 2:', err);
            reject(err);
            return;
          }

          console.log('TOTALES SIN SUGERENCIAS (aplicando WHERE):');
          rows2.forEach(r => {
            console.log(`${r.sprint}: ${r.total_sin_sugerencias}`);
          });
          console.log();

          // Calcular promedios
          const promedio1 = rows1.reduce((acc, r) => acc + r.total_con_sugerencias, 0) / rows1.length;
          const promedio2 = rows2.reduce((acc, r) => acc + r.total_sin_sugerencias, 0) / rows2.length;

          console.log(`DENSIDAD CON SUGERENCIAS: ${promedio1.toFixed(1)}`);
          console.log(`DENSIDAD SIN SUGERENCIAS: ${promedio2.toFixed(1)}`);

          // Verificar qué hay en tipo_incidencia
          db.all(`
            SELECT DISTINCT tipo_incidencia, COUNT(*) as count
            FROM bugs_detail
            GROUP BY tipo_incidencia
          `, (err, rows3) => {
            if (err) {
              console.error('Error query 3:', err);
              reject(err);
              return;
            }

            console.log('\nDISTRIBUCIÓN DE TIPOS DE INCIDENCIA:');
            rows3.forEach(r => {
              console.log(`${r.tipo_incidencia || 'NULL'}: ${r.count}`);
            });

            db.close();
            resolve();
          });
        });
      });
    });
  });
}

checkDensity().catch(console.error);
