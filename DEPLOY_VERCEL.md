Pasos para desplegar en Vercel

1) Conectar el repositorio a Vercel
   - En Vercel, elige "Import Project" y conecta el repositorio.

2) Comportamiento de build
   - Vercel ejecutará `npm run vercel-build` (proporcionado) que ejecuta `npm run build`.
   - El script `build` ya ejecuta `node scripts/generate/generateQAJson.mjs && next build`.

3) Variables de entorno
   - Si usas variables (p. ej. para bases de datos), añádelas en Settings → Environment Variables.

4) Node.js
   - El archivo `package.json` fija `engines.node` a `18.x` para asegurar compatibilidad.

5) Archivos añadidos
   - `vercel.json`: instruye a Vercel a usar el builder de Next.js.
   - `DEPLOY_VERCEL.md`: este archivo con pasos.

6) Comprobación local (opcional)
   - Instala dependencias y prueba el build:

```powershell
npm install
npm run build
npm run start
```

7) Push y despliegue
   - Haz push a la rama que Vercel vaya a desplegar (p. ej. `main`), y Vercel lanzará el build automático.

---

Configuración de `DATA_SOURCE` y consideraciones sobre SQLite en Vercel

- `DATA_SOURCE` puede usarse para controlar cómo `generate-json` obtiene los datos durante el `build`:
   - `DATA_SOURCE='none'` → omite la lectura de SQLite y el script generará (o mantendrá) un `qa-data.json` mínimo.
   - `DATA_SOURCE` como ruta relativa (p. ej. `public/data/qa-dashboard.db`) → se resolverá respecto al `cwd` durante el build en Vercel.
   - `DATA_SOURCE` como ruta absoluta → se usa tal cual.

- Recomendaciones para Vercel:
   - Preferible: usar un servicio de datos externo (Postgres, MySQL, etc.) y exponerlo mediante `DATABASE_URL` o similar. Configura esa variable en Vercel (Settings → Environment Variables) y adapta tus APIs para conectar a ella.
   - Si quieres seguir generando JSON en el build y `qa-dashboard.db` ya está en el repo, Vercel ejecutará `generate-json` y el JSON aparecerá en la build, pero los cambios en disco NO se persisten entre despliegues.
   - Si la `.db` no está presente en el repositorio, establece `DATA_SOURCE='none'` para evitar fallos en el build.

- Ejemplos de variables en Vercel (Environment Variables):

   - Opción A (omitimos SQLite y usamos JSON mínimo):

      DATA_SOURCE=none

   - Opción B (usar `.db` incluida en el repo — no recomendado si cambia frecuentemente):

      DATA_SOURCE=public/data/qa-dashboard.db

   - Opción C (usar DB externa — recomendado para producción):

      DATABASE_URL=postgres://user:pass@host:5432/dbname

Después de ajustar variables, despliega desde Vercel y revisa los logs de build si necesitas depurar la generación de `qa-data.json`.
