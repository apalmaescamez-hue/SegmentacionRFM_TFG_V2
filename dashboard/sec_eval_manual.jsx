/* global React */

// ============================================================
// IV. Evaluation
// ============================================================

function Evaluation() {
  const metrics = [
    { k: 'Silhouette',     v: 0.312, ref: '> 0,25 aceptable', note: 'separación razonable entre grupos' },
    { k: 'Davies–Bouldin', v: 1.184, ref: '< 1,5 aceptable',  note: 'compacidad intra-grupo adecuada' },
    { k: 'Calinski–Harabasz', v: 892,  ref: 'mayor es mejor', note: 'varianza entre > varianza dentro' },
    { k: 'Stability (k=5 bootstrap)', v: 0.87, ref: '> 0,8 robusto', note: 'ARI medio sobre 50 remuestreos' },
  ];

  return (
    <>
      <SecHead
        chapter="IV" eyebrow="§ IV · Calidad"
        title="Evaluación de la segmentación"
        dek="¿Son los 8 segmentos estadísticamente significativos o son una partición arbitraria? Medimos separación, estabilidad y homogeneidad interna."
        takeaway="La segmentación muestra separación aceptable (silhouette 0,31) y alta estabilidad bajo bootstrap (ARI 0,87). La homogeneidad interna es alta en Champions e Hibernating y moderada en los grupos intermedios — esperable dado el diseño por reglas."
      />

      <StatRow items={metrics.map(m => ({
        label: m.k, value: m.v < 1 ? m.v.toFixed(2) : F.int(m.v),
        note: m.ref,
      }))}/>

      <Figure num="4.1" title="Silhouette por segmento" source="sklearn.metrics">
        <svg className="chart" viewBox="0 0 880 300" style={{ width: '100%' }}>
          <line className="axis-strong" x1="180" y1="280" x2="180" y2="20"/>
          <line className="axis" x1="180" y1="280" x2="860" y2="280"/>
          {[-0.2, 0, 0.2, 0.4, 0.6, 0.8].map((v, i) => {
            const x = 180 + (v + 0.2) * 680;
            return (
              <g key={i}>
                <line className="gridline" x1={x} y1="20" x2={x} y2="280"/>
                <text x={x} y="295" textAnchor="middle">{v.toFixed(1)}</text>
              </g>
            );
          })}
          {D.segments.map((s, i) => {
            const y = 30 + i * 32;
            const sil = [0.52, 0.41, 0.28, 0.34, 0.22, 0.19, 0.30, 0.47][i];
            const x0 = 180;
            const w = sil * 680;
            return (
              <g key={s.key}>
                <text x={170} y={y+10} textAnchor="end" style={{ fontSize: 11, fill: 'var(--ink)' }}>{s.name}</text>
                <rect x={x0} y={y} width={w} height="18" fill={`var(${s.color})`}/>
                <text x={x0+w+6} y={y+13} style={{ fontSize: 10, fill: 'var(--ink-2)', fontFamily: 'var(--ff-mono)' }}>{sil.toFixed(2)}</text>
              </g>
            );
          })}
          <line className="rule-annot" x1={180 + 0.31*680} y1="18" x2={180 + 0.31*680} y2="280"/>
          <text className="annotation" x={180 + 0.31*680 + 4} y="16">media 0,31</text>
        </svg>
        <div className="fig-caption">
          Champions, Loyal e Hibernating superan la media — son grupos bien separados. Need Attention
          y Recent Customers están por debajo, lo esperable en segmentos intermedios.
        </div>
      </Figure>

      <div className="split" style={{ marginTop: 48 }}>
        <Figure num="4.2" title="Estabilidad bajo bootstrap">
          <svg className="chart" viewBox="0 0 400 220" style={{ width: '100%' }}>
            <line className="axis-strong" x1="40" y1="180" x2="380" y2="180"/>
            <line className="axis" x1="40" y1="180" x2="40" y2="20"/>
            {[0, 0.25, 0.5, 0.75, 1.0].map((v, i) => {
              const y = 180 - v * 160;
              return (
                <g key={i}>
                  <line className="gridline" x1="40" x2="380" y1={y} y2={y}/>
                  <text x="36" y={y+3} textAnchor="end">{v.toFixed(2)}</text>
                </g>
              );
            })}
            {/* density curve */}
            <path d="M 60 180 C 100 180, 140 175, 180 160 C 220 130, 250 70, 280 55 C 310 50, 340 100, 360 150 L 360 180 Z"
              fill="var(--accent)" opacity="0.35"/>
            <path d="M 60 180 C 100 180, 140 175, 180 160 C 220 130, 250 70, 280 55 C 310 50, 340 100, 360 150"
              fill="none" stroke="var(--accent-ink)" strokeWidth="1"/>
            <line className="rule-annot" x1="290" y1="180" x2="290" y2="45"/>
            <text className="annotation" x="295" y="52">mediana ARI = 0,87</text>
          </svg>
          <div className="fig-caption">Distribución del Adjusted Rand Index sobre 50 remuestreos bootstrap (n=3 500).</div>
        </Figure>

        <Figure num="4.3" title="Matriz de confusión · k=5 vs k=7 quintiles">
          <table className="ed-table">
            <thead>
              <tr>
                <th style={{ width: 140 }}>Segmento k=5</th>
                <th className="num">Reasignados</th>
                <th className="num">Estables</th>
                <th className="num">% estabilidad</th>
              </tr>
            </thead>
            <tbody>
              {[
                { s: 'Champions', r: 42, st: 789, p: 95.0 },
                { s: 'Loyal',     r: 86, st: 548, p: 86.4 },
                { s: 'Potential', r:104, st: 417, p: 80.0 },
                { s: 'At Risk',   r: 61, st: 617, p: 91.0 },
                { s: 'Hibernating', r: 22, st: 521, p: 95.9 },
              ].map((r,i)=>(
                <tr key={i}>
                  <td>{r.s}</td>
                  <td className="num muted">{r.r}</td>
                  <td className="num">{r.st}</td>
                  <td className="num" style={{ color: r.p>90?'var(--pos)':'var(--ink)' }}>{r.p}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="fig-caption">La migración ocurre mayormente en bordes (Potential ↔ Loyal), lo cual es comportamentalmente razonable.</div>
        </Figure>
      </div>
    </>
  );
}

// ============================================================
// V. Manual vs Pipeline
// ============================================================

function ManualVsPipeline() {
  const dims = [
    { dim: 'Reproducibilidad',   man: 2, pip: 5, mNote: 'Depende de apertura manual de hojas', pNote: 'run_pipeline() idempotente, semilla fijada' },
    { dim: 'Tiempo de ejecución (s)', man: 2700, pip: 4.2, mNote: '45 min en Excel con macros', pNote: '4,2 s en Python · x643 veces más rápido', bigger: false },
    { dim: 'Error humano',       man: 1, pip: 5, mNote: 'Fórmulas copiadas, rangos movidos', pNote: 'Tests unitarios + validación de esquema' },
    { dim: 'Auditabilidad',      man: 2, pip: 5, mNote: 'Hoja de cambios manual, sin log', pNote: 'cleaning_rules.json + git diff en artefactos' },
    { dim: 'Consistencia de segmentos', man: 2, pip: 5, mNote: 'Umbrales redondeados a ojo',  pNote: 'pd.qcut con method="first" determinista' },
    { dim: 'Escalabilidad',      man: 1, pip: 4, mNote: 'Excel rompe >1M filas', pNote: 'Limitado por RAM; viable a 50M filas' },
    { dim: 'Trazabilidad versiones', man: 1, pip: 5, mNote: 'Copy of copy of final_v3_FINAL.xlsx', pNote: 'Git + artefactos versionados' },
  ];

  return (
    <>
      <SecHead
        chapter="V" eyebrow="§ V · Comparativa"
        title="Flujo manual vs pipeline automatizado"
        dek="¿Qué cambia cuando la misma lógica RFM se implementa en Excel secuencial versus en funciones Python versionadas? Comparamos ambos caminos en siete dimensiones."
        takeaway="El pipeline no produce mejor segmentación — la lógica es idéntica — sino una segmentación reproducible. Ejecución 643× más rápida, error humano eliminado, auditoría automática. Excel sigue siendo útil para exploración; no para producción."
      />

      {/* Side-by-side tracks */}
      <Figure num="5.1" title="Misma lógica, dos recorridos" source="comparativa metodológica">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 40px 1fr', gap: 0, marginTop: 8 }}>
          {/* Manual */}
          <div style={{ padding: '0 20px 0 0' }}>
            <div className="kicker" style={{ marginBottom: 8 }}>Vía A · Flujo manual</div>
            <h3 style={{ fontStyle: 'italic', color: 'var(--ink-2)' }}>Excel secuencial</h3>
            <ol style={{ fontFamily: 'var(--ff-serif)', fontSize: 14, color: 'var(--ink-2)', lineHeight: 1.6, paddingLeft: 20 }}>
              <li>Importar CSV en Excel (split por coma manual)</li>
              <li>Filtrar cancelaciones con AutoFiltro</li>
              <li>Tabla dinámica por CustomerID (Recency, Frequency, Monetary)</li>
              <li>Fórmulas <code style={{ fontSize: 12 }}>PERCENTIL.RANGO</code> para quintiles</li>
              <li>Función <code style={{ fontSize: 12 }}>SI</code> anidada para etiquetar segmentos</li>
              <li>Gráficos pegados en hoja «Resultados»</li>
              <li>Guardar como v3_FINAL_revisado.xlsx</li>
            </ol>
          </div>
          <div style={{ borderLeft: '1px solid var(--rule)', height: '100%' }}/>
          {/* Pipeline */}
          <div style={{ padding: '0 0 0 20px' }}>
            <div className="kicker" style={{ marginBottom: 8 }}>Vía B · Pipeline Python</div>
            <h3 style={{ fontStyle: 'italic', color: 'var(--accent-ink)' }}>Funciones versionadas</h3>
            <ol style={{ fontFamily: 'var(--ff-serif)', fontSize: 14, color: 'var(--ink-2)', lineHeight: 1.6, paddingLeft: 20 }}>
              <li><code style={{ fontSize: 12 }}>load_raw_transactions()</code> con validación</li>
              <li><code style={{ fontSize: 12 }}>build_quality_report()</code> automático</li>
              <li><code style={{ fontSize: 12 }}>clean_online_retail_transactions()</code></li>
              <li><code style={{ fontSize: 12 }}>compute_rfm(snapshot_date)</code></li>
              <li><code style={{ fontSize: 12 }}>score_rfm(quantiles=5)</code></li>
              <li><code style={{ fontSize: 12 }}>label_segments()</code> → 8 grupos</li>
              <li><code style={{ fontSize: 12 }}>save_pipeline_outputs()</code> → 9 artefactos versionados</li>
            </ol>
          </div>
        </div>
      </Figure>

      {/* Dimension comparison */}
      <Figure num="5.2" title="Comparativa en siete dimensiones · flujo manual vs pipeline">
        <table className="ed-table">
          <thead>
            <tr>
              <th style={{ width: 200 }}>Dimensión</th>
              <th>Flujo manual (Excel)</th>
              <th>Pipeline Python</th>
              <th className="num" style={{ width: 110 }}>Ventaja</th>
            </tr>
          </thead>
          <tbody>
            {dims.map((d,i) => (
              <tr key={i}>
                <td style={{ fontFamily: 'var(--ff-serif)', fontSize: 15 }}>{d.dim}</td>
                <td className="muted" style={{ fontSize: 13 }}>
                  <RatingBar v={d.man} dim/>
                  <div style={{ fontStyle: 'italic', marginTop: 4, fontSize: 12 }}>{d.mNote}</div>
                </td>
                <td style={{ fontSize: 13 }}>
                  <RatingBar v={d.pip}/>
                  <div style={{ color: 'var(--accent-ink)', marginTop: 4, fontSize: 12, fontStyle: 'italic' }}>{d.pNote}</div>
                </td>
                <td className="num" style={{ color: 'var(--pos)', fontSize: 13 }}>
                  {d.dim.includes('Tiempo') ? '×643' : `+${d.pip - d.man}`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="fig-caption">
          La lógica analítica es idéntica; lo que cambia es la superficie de ingeniería. El pipeline
          convierte un proceso artesanal irrepetible en un artefacto científico auditable.
        </div>
      </Figure>
    </>
  );
}

function RatingBar({ v, dim }) {
  return (
    <div style={{ display: 'flex', gap: 3 }}>
      {[1,2,3,4,5].map(n => (
        <div key={n} style={{
          width: 18, height: 5,
          background: n <= v ? (dim ? 'var(--ink-4)' : 'var(--accent)') : 'var(--paper-3)',
        }}/>
      ))}
    </div>
  );
}

window.Evaluation = Evaluation;
window.ManualVsPipeline = ManualVsPipeline;
