/* global React */

// ============================================================
// VI. Agents — LangGraph architecture
// ============================================================

function Agents() {
  const agents = [
    { n: '01', name: 'Data Collector',     kind: 'det',  mod: 'io.load_raw_data',              role: 'Carga y normaliza el archivo fuente a DataFrame.' },
    { n: '02', name: 'Data Validator',     kind: 'det',  mod: 'quality.validation',             role: 'Verifica columnas requeridas y coerción de tipos.' },
    { n: '03', name: 'Data Profiler',      kind: 'det',  mod: 'quality.profiling',              role: 'Produce quality_report y column_profile.' },
    { n: '04', name: 'Data Cleaner',       kind: 'det',  mod: 'cleaning.clean_transactions',    role: 'Aplica reglas de limpieza documentadas.' },
    { n: '05', name: 'Feature Engineer',   kind: 'det',  mod: 'features.customer_features',     role: 'Construye variables a nivel factura y cliente.' },
    { n: '06', name: 'RFM Segmentation',   kind: 'det',  mod: 'segmentation.scoring + segments', role: 'Scoring cuantílico y asignación de etiquetas.' },
    { n: '07', name: 'Benchmark Agent',    kind: 'det',  mod: 'segmentation.kmeans_bench',      role: 'Compara resultados con un baseline KMeans(k=8).' },
    { n: '08', name: 'Insight Generator',  kind: 'llm',  mod: 'reporting.insights + LLM',       role: 'Redacta explicaciones naturales por segmento. No modifica datos.' },
    { n: '09', name: 'Report Builder',     kind: 'llm',  mod: 'reporting.report_builder',       role: 'Ensambla el informe ejecutivo final en Markdown/HTML.' },
  ];

  return (
    <>
      <SecHead
        chapter="VI" eyebrow="§ VI · Arquitectura"
        title="Arquitectura multi-agente"
        dek="Cada etapa del pipeline se encapsula en un agente especializado con contrato explícito. Siete son deterministas; dos son asistidos por LLM y están confinados a explicación y redacción."
        takeaway="Los LLM nunca tocan umbrales, reglas ni asignación de segmentos. Solo explican y redactan a partir de artefactos inmutables. Esto preserva la reproducibilidad estadística y habilita la narrativa automatizada."
      />

      {/* Graph diagram */}
      <Figure num="6.1" title="Grafo orquestador · LangGraph" source="src/tfg_rfm/agents/graph.py">
        <svg className="chart" viewBox="0 0 960 460" style={{ width: '100%', height: 'auto' }}>
          <defs>
            <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M0,0 L10,5 L0,10 z" fill="var(--ink-3)"/>
            </marker>
          </defs>

          {/* START */}
          <circle cx="70" cy="60" r="18" fill="var(--ink)"/>
          <text x="70" y="63" textAnchor="middle" style={{ fontSize: 9, fill: 'var(--paper)', fontFamily: 'var(--ff-mono)' }}>START</text>

          {/* Deterministic row */}
          {agents.slice(0,7).map((a, i) => {
            const x = 130 + (i % 4) * 200;
            const y = 60 + Math.floor(i/4) * 140;
            return (
              <g key={a.n}>
                <rect x={x} y={y-30} width="170" height="60" fill="var(--paper)" stroke="var(--ink)" strokeWidth="0.8"/>
                <text x={x+12} y={y-14} style={{ fontFamily: 'var(--ff-mono)', fontSize: 9, fill: 'var(--ink-3)', letterSpacing: '0.1em' }}>{a.n} · DETERMINISTA</text>
                <text x={x+12} y={y+4} className="label-serif" style={{ fontSize: 14 }}>{a.name}</text>
                <text x={x+12} y={y+20} style={{ fontFamily: 'var(--ff-mono)', fontSize: 9, fill: 'var(--accent-ink)' }}>{a.mod}</text>
              </g>
            );
          })}

          {/* LLM row */}
          {agents.slice(7).map((a, i) => {
            const x = 330 + i * 220;
            const y = 340;
            return (
              <g key={a.n}>
                <rect x={x} y={y-30} width="190" height="60" fill="var(--accent-soft)" stroke="var(--accent-ink)" strokeWidth="0.8" strokeDasharray="4 2"/>
                <text x={x+12} y={y-14} style={{ fontFamily: 'var(--ff-mono)', fontSize: 9, fill: 'var(--accent-ink)', letterSpacing: '0.1em' }}>{a.n} · LLM · OPCIONAL</text>
                <text x={x+12} y={y+4} className="label-serif" style={{ fontSize: 14 }}>{a.name}</text>
                <text x={x+12} y={y+20} style={{ fontFamily: 'var(--ff-mono)', fontSize: 9, fill: 'var(--ink-2)' }}>{a.mod}</text>
              </g>
            );
          })}

          {/* Flow arrows (sequential) */}
          <line x1="88" y1="60" x2="130" y2="60" stroke="var(--ink-3)" strokeWidth="0.6" markerEnd="url(#arr)"/>
          <line x1="300" y1="60" x2="330" y2="60" stroke="var(--ink-3)" strokeWidth="0.6" markerEnd="url(#arr)"/>
          <line x1="500" y1="60" x2="530" y2="60" stroke="var(--ink-3)" strokeWidth="0.6" markerEnd="url(#arr)"/>
          <line x1="700" y1="60" x2="730" y2="60" stroke="var(--ink-3)" strokeWidth="0.6" markerEnd="url(#arr)"/>
          {/* down */}
          <path d="M 900 90 L 900 115 L 215 115 L 215 170" fill="none" stroke="var(--ink-3)" strokeWidth="0.6" markerEnd="url(#arr)"/>
          <line x1="300" y1="200" x2="330" y2="200" stroke="var(--ink-3)" strokeWidth="0.6" markerEnd="url(#arr)"/>
          <line x1="500" y1="200" x2="530" y2="200" stroke="var(--ink-3)" strokeWidth="0.6" markerEnd="url(#arr)"/>
          <line x1="700" y1="200" x2="730" y2="200" stroke="var(--ink-3)" strokeWidth="0.6" markerEnd="url(#arr)"/>
          {/* down to LLM layer (through insights) */}
          <path d="M 815 230 L 815 275 L 425 275 L 425 310" fill="none" stroke="var(--accent-ink)" strokeWidth="0.6" strokeDasharray="3 2" markerEnd="url(#arr)"/>
          <line x1="520" y1="340" x2="550" y2="340" stroke="var(--accent-ink)" strokeWidth="0.6" strokeDasharray="3 2" markerEnd="url(#arr)"/>

          {/* END */}
          <circle cx="810" cy="340" r="18" fill="var(--paper)" stroke="var(--ink)" strokeWidth="1.2"/>
          <circle cx="810" cy="340" r="11" fill="var(--ink)"/>
          <line x1="740" y1="340" x2="792" y2="340" stroke="var(--ink-3)" strokeWidth="0.6" markerEnd="url(#arr)"/>

          {/* Legend */}
          <g transform="translate(60, 410)">
            <rect x="0" y="0" width="14" height="10" fill="var(--paper)" stroke="var(--ink)" strokeWidth="0.8"/>
            <text x="20" y="9" style={{ fontSize: 10, fill: 'var(--ink-2)' }}>Agente determinista · función Python pura</text>
            <rect x="320" y="0" width="14" height="10" fill="var(--accent-soft)" stroke="var(--accent-ink)" strokeWidth="0.8" strokeDasharray="3 1"/>
            <text x="340" y="9" style={{ fontSize: 10, fill: 'var(--ink-2)' }}>Agente LLM · explicación/redacción, sin escritura sobre datos</text>
          </g>
        </svg>
        <div className="fig-caption">
          El estado (AgentState) fluye entre nodos; cada agente lee claves específicas y escribe otras nuevas.
          La separación entre capa determinista y capa LLM es una frontera de confianza, no solo organizativa.
        </div>
      </Figure>

      {/* Agents table */}
      <Figure num="6.2" title="Responsabilidades por agente">
        <table className="ed-table">
          <thead>
            <tr>
              <th style={{ width: 40 }}>#</th>
              <th>Agente</th>
              <th>Módulo</th>
              <th>Responsabilidad</th>
              <th style={{ width: 130 }}>Tipo</th>
            </tr>
          </thead>
          <tbody>
            {agents.map(a => (
              <tr key={a.n}>
                <td className="muted" style={{ fontFamily: 'var(--ff-mono)', fontSize: 11 }}>{a.n}</td>
                <td style={{ fontFamily: 'var(--ff-serif)', fontSize: 15 }}>{a.name}</td>
                <td className="muted" style={{ fontFamily: 'var(--ff-mono)', fontSize: 11 }}>{a.mod}</td>
                <td style={{ fontSize: 13, color: 'var(--ink-2)' }}>{a.role}</td>
                <td>
                  <span className={`tag ${a.kind==='det'?'':'accent'}`}>
                    {a.kind==='det' ? 'Determinista' : 'LLM · opcional'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Figure>

      {/* Guardrails */}
      <Figure num="6.3" title="Frontera LLM · restricciones de diseño">
        <div className="split">
          <div className="panel" style={{ borderColor: 'var(--pos)', borderLeft: '4px solid var(--pos)' }}>
            <div className="kicker" style={{ color: 'var(--pos)', marginBottom: 10 }}>Los LLM SÍ pueden</div>
            <ul style={{ fontFamily: 'var(--ff-serif)', color: 'var(--ink-2)', fontSize: 14, lineHeight: 1.7, paddingLeft: 18 }}>
              <li>Redactar resúmenes en lenguaje natural a partir de insights.json</li>
              <li>Sugerir acciones de marketing por segmento (catálogo documentado)</li>
              <li>Ensamblar el informe final en Markdown o HTML</li>
              <li>Traducir tablas a narrativa ejecutiva</li>
            </ul>
          </div>
          <div className="panel" style={{ borderColor: 'var(--neg)', borderLeft: '4px solid var(--neg)' }}>
            <div className="kicker" style={{ color: 'var(--neg)', marginBottom: 10 }}>Los LLM NO pueden</div>
            <ul style={{ fontFamily: 'var(--ff-serif)', color: 'var(--ink-2)', fontSize: 14, lineHeight: 1.7, paddingLeft: 18 }}>
              <li>Modificar umbrales de quintiles ni reglas de limpieza</li>
              <li>Reasignar segmentos de ningún cliente</li>
              <li>Escribir sobre rfm_segments.csv o customer_features.csv</li>
              <li>Alterar configuración (snapshot_date, quantiles, filtros)</li>
            </ul>
          </div>
        </div>
        <div className="fig-caption">
          La línea entre capa analítica y capa narrativa es inamovible por diseño. Un LLM que alucina
          en prosa es aceptable; uno que altera un score RFM es inaceptable.
        </div>
      </Figure>
    </>
  );
}

// ============================================================
// VII. Reports
// ============================================================

function Reports() {
  const reports = [
    { id: 'eda',    name: 'Informe EDA',                    file: 'eda_report.md',             size: '24 KB', date: '2026-04-18 11:42', rules: 'quantiles=5, snapshot=2011-12-09' },
    { id: 'qual',   name: 'Reporte de calidad',             file: 'quality_report.json',       size: '6 KB',  date: '2026-04-18 11:42', rules: 'schema v1.2' },
    { id: 'clean',  name: 'Reglas de limpieza',             file: 'cleaning_rules.json',       size: '2 KB',  date: '2026-04-18 11:42', rules: '4 reglas activas' },
    { id: 'rfm',    name: 'Segmentación RFM',               file: 'rfm_segments.csv',          size: '412 KB',date: '2026-04-18 11:42', rules: 'quantiles=5' },
    { id: 'bench',  name: 'Benchmark KMeans',               file: 'kmeans_benchmark.json',     size: '18 KB', date: '2026-04-18 11:43', rules: 'k=8, random_state=42' },
    { id: 'cmp',    name: 'Comparativa manual vs pipeline', file: 'manual_vs_pipeline.md',     size: '31 KB', date: '2026-04-18 11:43', rules: 'dataset idéntico' },
    { id: 'eff',    name: 'Eficiencia y tiempos',           file: 'efficiency_report.json',    size: '4 KB',  date: '2026-04-18 11:43', rules: '—' },
    { id: 'repro',  name: 'Reproducibilidad',               file: 'reproducibility.json',      size: '5 KB',  date: '2026-04-18 11:43', rules: 'hash MD5 por artefacto' },
    { id: 'trace',  name: 'Trazabilidad',                   file: 'traceability.json',         size: '12 KB', date: '2026-04-18 11:43', rules: 'grafo de dependencias' },
  ];

  return (
    <>
      <SecHead
        chapter="VII" eyebrow="§ VII · Entregables"
        title="Reports"
        dek="Cada ejecución del pipeline deja un rastro de nueve artefactos auditables. Previsualización en línea, descarga en JSON o Markdown, con la configuración exacta que los produjo."
        takeaway="La auditoría responde a cuatro preguntas por artefacto: qué se generó, cuándo, desde qué entrada y bajo qué reglas. El PDF ejecutivo queda como enhancement futuro; la prioridad actual es trazabilidad completa."
      />

      {/* Report catalogue */}
      <Figure num="7.1" title="Catálogo de informes · última ejecución">
        <table className="ed-table">
          <thead>
            <tr>
              <th>Informe</th>
              <th>Artefacto</th>
              <th className="num">Tamaño</th>
              <th>Generado</th>
              <th>Configuración</th>
              <th style={{ width: 100 }}>Formato</th>
            </tr>
          </thead>
          <tbody>
            {reports.map(r => (
              <tr key={r.id}>
                <td style={{ fontFamily: 'var(--ff-serif)', fontSize: 15 }}>{r.name}</td>
                <td className="muted" style={{ fontFamily: 'var(--ff-mono)', fontSize: 11 }}>{r.file}</td>
                <td className="num muted">{r.size}</td>
                <td className="muted" style={{ fontFamily: 'var(--ff-mono)', fontSize: 11 }}>{r.date}</td>
                <td className="muted" style={{ fontSize: 12, fontStyle: 'italic' }}>{r.rules}</td>
                <td>
                  <span className="tag">{r.file.endsWith('.md') ? 'Markdown' : r.file.endsWith('.csv') ? 'CSV' : 'JSON'}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Figure>

      {/* Executive summary preview */}
      <div className="marginalia" style={{ marginTop: 64 }}>
        <Figure num="7.2" title="Resumen ejecutivo · vista previa">
          <div className="panel filled" style={{ padding: '32px 36px' }}>
            <div className="kicker" style={{ marginBottom: 8 }}>TFG · RFM · Online Retail</div>
            <h2 style={{ marginBottom: 16, fontSize: 28 }}>Segmentación de clientes — Informe ejecutivo</h2>
            <div style={{ fontFamily: 'var(--ff-mono)', fontSize: 11, color: 'var(--ink-3)', marginBottom: 24 }}>
              Generado 18 abr 2026 · dataset 2010–2011 · snapshot 2011-12-09 · quantiles=5
            </div>

            <div className="body-text">
              <p><strong>Contexto.</strong> Se analizan 397 885 transacciones de 4 372 clientes distintos en un período de 13 meses,
              con un volumen neto de £8,28M. El 90,4% de los clientes son del Reino Unido.</p>

              <p><strong>Resultado.</strong> La segmentación RFM asigna cada cliente a uno de 8 grupos interpretables.
              Los Champions (19,0%) concentran el 39,7% de los ingresos; junto con Loyal Customers (14,5% · 22,8%)
              suman 62,5% del revenue con solo el 33,5% de los clientes — un patrón de Pareto pronunciado.</p>

              <p><strong>Riesgo.</strong> At Risk e Hibernating agrupan al 27,9% de los clientes y aportan 8,6% del revenue.
              Son candidatos para campañas de win-back selectivo o para depuración del CRM activo.</p>

              <p><strong>Calidad.</strong> La segmentación muestra separación aceptable (silhouette 0,31) y
              alta estabilidad bajo bootstrap (ARI 0,87). La mayor incertidumbre se concentra en segmentos
              intermedios (Need Attention, Recent Customers), lo esperado para grupos de frontera.</p>

              <p><strong>Reproducibilidad.</strong> Toda la cadena se ejecuta en 4,2 s mediante <code>run_pipeline()</code>.
              Los 9 artefactos quedan versionados bajo hash y cubren auditoría de entrada, configuración,
              limpieza y resultado.</p>
            </div>
          </div>
        </Figure>
        <aside className="margin-note">
          <span className="label">Descargas</span>
          Este resumen se genera a partir de insights.json mediante el agente Report Builder.
          Disponible también en Markdown y —como enhancement futuro— PDF maquetado.
        </aside>
      </div>

      {/* Audit footer */}
      <Figure num="7.3" title="Auditoría · qué, cuándo, desde dónde, bajo qué reglas">
        <div className="split">
          <div>
            <div className="kicker" style={{ marginBottom: 10 }}>Manifiesto de ejecución</div>
            <div className="code" style={{ fontSize: 11 }}>
<span className="cm"># manifest.json</span>{'\n'}
{'{'}{'\n'}
{'  '}<span className="str">"run_id"</span>: <span className="str">"2026-04-18T11-42-08"</span>,{'\n'}
{'  '}<span className="str">"source"</span>: <span className="str">"data/raw/online_retail.xlsx"</span>,{'\n'}
{'  '}<span className="str">"source_md5"</span>: <span className="str">"a3f81c...9e2d"</span>,{'\n'}
{'  '}<span className="str">"params"</span>: {'{'}{'\n'}
{'    '}<span className="str">"snapshot_date"</span>: <span className="str">"2011-12-09"</span>,{'\n'}
{'    '}<span className="str">"quantiles"</span>: <span className="kw">5</span>{'\n'}
{'  '}{'}'},{'\n'}
{'  '}<span className="str">"artefacts"</span>: <span className="kw">9</span>,{'\n'}
{'  '}<span className="str">"duration_s"</span>: <span className="kw">4.2</span>,{'\n'}
{'  '}<span className="str">"python"</span>: <span className="str">"3.11.7"</span>,{'\n'}
{'  '}<span className="str">"pandas"</span>: <span className="str">"2.1.4"</span>{'\n'}
{'}'}
            </div>
          </div>
          <div>
            <div className="kicker" style={{ marginBottom: 10 }}>Principios de auditabilidad</div>
            <ol style={{ fontFamily: 'var(--ff-serif)', fontSize: 14, lineHeight: 1.6, paddingLeft: 20, color: 'var(--ink-2)' }}>
              <li><strong>Qué.</strong> Cada artefacto lleva nombre canónico y esquema versionado.</li>
              <li><strong>Cuándo.</strong> Timestamp ISO-8601 en el run_id; inmutable tras ejecución.</li>
              <li><strong>Desde dónde.</strong> Hash MD5 de la fuente original garantiza trazabilidad.</li>
              <li><strong>Bajo qué reglas.</strong> Parámetros completos persistidos en manifest.json.</li>
              <li><strong>Bajo qué entorno.</strong> Versiones de Python y dependencias clave.</li>
            </ol>
          </div>
        </div>
        <div className="fig-caption">
          Cualquier tercero debe poder reconstruir la segmentación exacta a partir de estos metadatos.
          Es el mínimo común de un análisis científico.
        </div>
      </Figure>
    </>
  );
}

window.Agents = Agents;
window.Reports = Reports;
