#!/usr/bin/env node
/**
 * generateQAJson.mjs
 * 
 * Script para generar JSON de QA a partir de SQLite.
 * Se ejecuta automáticamente en el build de Vercel.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import http from 'http';
import https from 'https';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Import DAL después de definir __dirname
async function main() {
  try {
    const JSON_OUTPUT_PATH = path.join(__dirname, '..', '..', 'public', 'data', 'qa-data.json');
    const DATA_DIR = path.dirname(JSON_OUTPUT_PATH);

    // Permitir personalizar la fuente de datos mediante la variable de entorno DATA_SOURCE
    // Si DATA_SOURCE está definida y apunta a un archivo, se usa como DB_PATH.
    // Si DATA_SOURCE == 'none', se omite la generación desde SQLite.
    const envDataSource = process.env.DATA_SOURCE;
    let DB_PATH = path.join(__dirname, '..', '..', 'public', 'data', 'qa-dashboard.db');
    if (envDataSource) {
      if (envDataSource === 'none') {
        DB_PATH = null;
      } else {
        // Si es URL (http/https) la descargamos; si es ruta relativa, resolverla respecto al cwd
        if (/^https?:\/\//i.test(envDataSource)) {
          // destino local para la descarga
          if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
          DB_PATH = path.join(DATA_DIR, 'qa-dashboard.db');

          // Descargar si no existe localmente
          if (!fs.existsSync(DB_PATH)) {
            console.log(`⬇️ Descargando DB desde URL: ${envDataSource} -> ${DB_PATH}`);
            await downloadFile(envDataSource, DB_PATH);
            console.log(`✅ Descarga completada: ${DB_PATH}`);
          } else {
            console.log(`ℹ️ DB ya existe localmente, no se descargará: ${DB_PATH}`);
          }
        } else {
          DB_PATH = path.isAbsolute(envDataSource) ? envDataSource : path.join(process.cwd(), envDataSource);
        }
      }
    }


    // Si DATA_SOURCE == 'none' (DB_PATH === null) omitimos la carga de DAL y generamos/retomamos JSON mínimo
    if (!DB_PATH) {
      console.log(`ℹ️ DATA_SOURCE='none' configurado, se omitirá la generación desde SQLite.`);
      if (fs.existsSync(JSON_OUTPUT_PATH)) {
        console.log(`ℹ️ JSON existente encontrado en ${JSON_OUTPUT_PATH}, se mantiene.`);
        process.exit(0);
      }
      if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
      const outputDataFallback = {
        metadata: {
          version: '1.0',
          source: 'none',
          generatedAt: new Date().toISOString(),
          sprintsCount: 0,
        },
        sprintData: [],
      };
      fs.writeFileSync(JSON_OUTPUT_PATH, JSON.stringify(outputDataFallback, null, 2));
      console.log(`✅ JSON mínimo generado: ${path.relative(process.cwd(), JSON_OUTPUT_PATH)}`);
      process.exit(0);
    }

    // Si se ha descargado o señalado una DB local, exponerla a DAL mediante la variable de entorno
    process.env.DATA_SOURCE = DB_PATH;

    // Importar DAL después de preparar DATA_SOURCE para que DAL lea la variable al cargarse
    const DAL = (await import('../../lib/database/dal.js')).default;

    // helper: descarga un archivo HTTP/HTTPS a destino
    function downloadFile(url, dest) {
      return new Promise((resolve, reject) => {
        const client = url.startsWith('https://') ? https : http;
        const req = client.get(url, (res) => {
          if (res.statusCode >= 400) return reject(new Error(`HTTP ${res.statusCode} - ${res.statusMessage}`));
          const file = fs.createWriteStream(dest);
          res.pipe(file);
          file.on('finish', () => file.close(resolve));
          file.on('error', (err) => reject(err));
        });
        req.on('error', (err) => reject(err));
      });
    }

    console.log(`📁 Workspace: ${process.cwd()}`);
    console.log(`📁 Output: ${JSON_OUTPUT_PATH}`);
    console.log(`📁 Database: ${DB_PATH}`);

    // Verificar que la DB existe (si se escogió usar SQLite)
    if (!DB_PATH) {
      console.log(`ℹ️ DATA_SOURCE='none' configurado, se omitirá la generación desde SQLite.`);
    } else if (!fs.existsSync(DB_PATH)) {
      console.warn(`⚠️ Base de datos no encontrada: ${DB_PATH}`);
      // Si ya existe un JSON en `public/data/qa-data.json`, lo conservamos y salimos exitosamente.
      if (fs.existsSync(JSON_OUTPUT_PATH)) {
        console.log(`ℹ️ JSON existente encontrado en ${JSON_OUTPUT_PATH}, se mantiene.`);
        process.exit(0);
      }
      // Si no hay JSON previo, generamos un JSON mínimo para evitar fallos en el build.
      console.log(`ℹ️ Generando JSON mínimo vacío en: ${JSON_OUTPUT_PATH}`);
      const outputDataFallback = {
        metadata: {
          version: '1.0',
          source: 'none',
          generatedAt: new Date().toISOString(),
          sprintsCount: 0,
        },
        sprintData: [],
      };
      if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
      fs.writeFileSync(JSON_OUTPUT_PATH, JSON.stringify(outputDataFallback, null, 2));
      console.log(`✅ JSON mínimo generado: ${path.relative(process.cwd(), JSON_OUTPUT_PATH)}`);
      process.exit(0);
    } else {
      console.log(`✅ Base de datos encontrada: ${DB_PATH}`);
    }

    // Verificar que el directorio de salida existe
    if (!fs.existsSync(DATA_DIR)) {
      console.log(`📁 Creando directorio: ${DATA_DIR}`);
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }

    console.log(`📊 Generando JSON desde SQLite...`);

    // Obtener datos desde DAL
    const qaData = await DAL.getFullQAData(DB_PATH);
    
    if (!qaData || !qaData.sprintData) {
      console.error(`❌ DAL retornó datos inválidos`, qaData);
      process.exit(1);
    }

    console.log(`✅ Datos obtenidos: ${qaData.sprintData.length} sprints`);

    // Agregar metadata
    const outputData = {
      metadata: {
        version: '1.0',
        source: 'sqlite',
        generatedAt: new Date().toISOString(),
        sprintsCount: qaData.sprintData.length,
      },
      ...qaData,
    };

    // Guardar JSON
    fs.writeFileSync(JSON_OUTPUT_PATH, JSON.stringify(outputData, null, 2));
    const sizeKB = (fs.statSync(JSON_OUTPUT_PATH).size / 1024).toFixed(2);
    console.log(`✅ JSON generado exitosamente: ${path.relative(process.cwd(), JSON_OUTPUT_PATH)}`);
    console.log(`   Tamaño: ${sizeKB} KB`);
    console.log(`   Sprints: ${outputData.metadata.sprintsCount}`);

    process.exit(0);
  } catch (error) {
    console.error(`❌ Error generando JSON:`);
    console.error(`   Mensaje: ${error.message}`);
    console.error(`   Stack:`, error.stack);
    process.exit(1);
  }
}

main();
