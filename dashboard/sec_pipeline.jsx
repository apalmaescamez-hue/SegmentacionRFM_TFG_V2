/* global React */

// ============================================================
// II. Pipeline
// ============================================================

function Pipeline() {
  const stages = [
    { n: '01', key: 'load',     name: 'Ingesta',          fn: 'load_raw_transactions()',  rows: 541909, out: 'raw_df',          desc: 'Carga CSV/Excel/Parquet con validación de esquema mínimo.' },
    { n: '02', key: 'profile',  name: 'Perfilado',        fn: 'build_quality_report()',    rows: 541909, out: 'quality_report', desc: 'Detecta tipos, nulos, únicos, valores extremos por columna.' },
    { n: '03', key: 'validate', name: 'Validación',       fn: 'validate_schema()',         rows: 541909, out: '—',               desc: 'Comprueba columnas requeridas y coerciona tipos.' },
    { n: '04', key: 'clean',    name: 'Limpieza',         fn: 'clean_online_retail_transactions()', rows: 397885, out: 'clean_df', desc: 'Aplica 4 reglas documentadas; registra cleaning_rules.json.' },
    { n: '05', key: 'feat',     name: 'Feature engineering', fn: 'build_customer_features()', rows: 4372, out: 'customer_features', desc: 'Agrega a nivel factura y cliente: ticket, SKUs, periodos.' },
    { n: '06', key: 'rfm',      name: 'Cálculo RFM',      fn: 'compute_rfm()',             rows: 4372,  out: 'rfm_table',      desc: 'Recency = días desde snapshot. Frequency = facturas. Monetary = suma neta.' },
    { n: '07', key: 'score',    name: 'Scoring',          fn: 'score_rfm(quantiles=5)',    rows: 4372,  out: 'scored',         desc: 'Quintiles por qcut(method="first"), R invertido.' },
    { n: '08', key: 'seg',      name: 'Segmentación',     fn: 'label_segments()',          rows: 4372,  out: 'segment_table',  desc: 'Asigna 8 etiquetas vía reglas sobre (R,F,M).' },
    { n: '09', key: 'insights', name: 'Insights',         fn: 'summarize_segments()',      rows: 8,     out: 'insights.json',  desc: 'Agrega por segmento: n, revenue, share, R/F/M medios.' },
  ];

  return (
    <>
      <SecHead
        chapter="II" eyebrow="§ II · Flujo"
        title="Pipeline reproducible"
        dek="Nueve etapas deterministas encadenadas en src/tfg_rfm/pipeline.py. Cada una lee un artefacto, lo transforma y lo deja versionado en disco."
        takeaway="Ejecutar run_pipeline(source) produce 9 artefactos reproducibles en 4,2 s. Cualquier cambio en una etapa se traza por diff de los CSV/JSON de salida — auditabilidad sin esfuerzo."
      />

      <div className="lede">
        El pipeline no es un script monolítico. Cada etapa es una función pura importable desde
        <span style={{ fontFamily: 'var(--ff-mono)', fontSize: 14 }}> src/tfg_rfm/</span>, con un
        contrato claro de entrada y salida. Esto permite testear por separado, paralelizar y —el punto
        crítico del TFG— envolver cada una en un nodo LangGraph sin reescribir lógica.
      </div>

      {/* Flow diagram */}
      <Figure num="2.1" title="Diagrama de etapas · pipeline determinista" source="src/tfg_rfm/pipeline.py">
        <svg className="chart" viewBox="0 0 920 420" style={{ width: '100%', height: 'auto' }}>
          {stages.map((s, i) => {
            const col = i % 3;
            const row = Math.floor(i / 3);
            const x = 30 + col * 300;
            const y = 20 + row * 130;
            return (
              <g key={s.key}>
                <rect x={x} y={y} width="270" height="100" fill="var(--paper)" stroke="var(--ink)" strokeWidth="0.5"/>
                <text x={x+14} y={y+22} style={{ fontFamily: 'var(--ff-mono)', fontSize: 10, fill: 'var(--ink-3)', letterSpacing: '0.1em' }}>{s.n}</text>
                <text x={x+14} y={y+44} className="label-serif" style={{ fontSize: 16 }}>{s.name}</text>
                <text x={x+14} y={y+62} style={{ fontFamily: 'var(--ff-mono)', fontSize: 10, fill: 'var(--accent-ink)' }}>{s.fn}</text>
                <text x={x+14} y={y+82} style={{ fontSize: 10, fill: 'var(--ink-3)' }}>→ {F.int(s.rows)} filas · {s.out}</text>

                {/* arrow to next */}
                {i < stages.length-1 && (
                  col < 2 ? (
                    <g>
                      <line x1={x+270} y1={y+50} x2={x+300} y2={y+50} stroke="var(--ink-3)" strokeWidth="0.5"/>
                      <polygon points={`${x+300},${y+50} ${x+295},${y+47} ${x+295},${y+53}`} fill="var(--ink-3)"/>
                    </g>
                  ) : (
                    <g>
                      <path d={`M ${x+135} ${y+100} L ${x+135} ${y+115} L ${165} ${y+115} L ${165} ${y+130}`}
                        fill="none" stroke="var(--ink-3)" strokeWidth="0.5"/>
                      <polygon points={`165,${y+130} 162,${y+125} 168,${y+125}`} fill="var(--ink-3)"/>
                    </g>
                  )
                )}
              </g>
            );
          })}
        </svg>
        <div className="fig-caption">
          Nueve etapas, una dirección. Los artefactos intermedios (clean_df, rfm_table) se persisten
          como CSV en data/processed/, permitiendo continuar desde cualquier punto.
        </div>
      </Figure>

      {/* Stage-by-stage table + code */}
      <div className="split" style={{ marginTop: 64, alignItems: 'start' }}>
        <div>
          <h3 style={{ marginBottom: 20 }}>Contrato de cada etapa</h3>
          <table className="ed-table">
            <thead>
              <tr>
                <th>Etapa</th>
                <th>Entrada → Salida</th>
                <th className="num">Filas</th>
              </tr>
            </thead>
            <tbody>
              {stages.map(s => (
                <tr key={s.key}>
                  <td>
                    <div style={{ fontFamily: 'var(--ff-serif)', fontSize: 15 }}>{s.n} · {s.name}</div>
                    <div style={{ fontFamily: 'var(--ff-mono)', fontSize: 11, color: 'var(--ink-3)', marginTop: 2 }}>{s.desc}</div>
                  </td>
                  <td className="muted" style={{ fontFamily: 'var(--ff-mono)', fontSize: 11 }}>{s.out}</td>
                  <td className="num">{F.int(s.rows)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <h3 style={{ marginBottom: 20 }}>Ejecución</h3>
          <div className="code">
<span className="cm"># Ejecución completa del pipeline</span>{'\n'}
<span className="kw">from</span> tfg_rfm.pipeline <span className="kw">import</span> run_pipeline{'\n'}
{'\n'}
results = <span className="fn">run_pipeline</span>({'\n'}
{'    '}source_path=<span className="str">"data/raw/online_retail.xlsx"</span>,{'\n'}
{'    '}snapshot_date=<span className="str">"2011-12-09"</span>,{'\n'}
{'    '}quantiles=<span className="kw">5</span>,{'\n'}
){'\n'}
{'\n'}
<span className="cm"># results contiene 11 claves:</span>{'\n'}
<span className="cm"># raw_df, quality_report, column_profile,</span>{'\n'}
<span className="cm"># clean_df, cleaning_rules, invoice_features,</span>{'\n'}
<span className="cm"># customer_features, rfm_table, segment_table,</span>{'\n'}
<span className="cm"># insights, insight_text</span>{'\n'}
{'\n'}
<span className="fn">save_pipeline_outputs</span>(results, <span className="str">"data/processed/"</span>)
          </div>
          <div style={{ marginTop: 24 }}>
            <StatRow items={[
              { label: "Tiempo", value: "4.2", unit: "s", note: "MacBook Air M2" },
              { label: "Artefactos", value: "9", note: "5 CSV + 4 JSON" },
            ]}/>
          </div>
        </div>
      </div>

      {/* Cleaning rules detail */}
      <Figure num="2.2" title="Reglas de limpieza aplicadas · cascada de filtrado" source="cleaning_rules.json">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 0 }}>
          {D.cleaning.map((r, i) => {
            const pctBar = r.pct;
            return (
              <div key={i} style={{
                display: 'grid',
                gridTemplateColumns: '40px 1fr 120px 120px 90px',
                gap: 16,
                alignItems: 'center',
                padding: '16px 0',
                borderBottom: '1px solid var(--rule)',
              }}>
                <div style={{ fontFamily: 'var(--ff-mono)', fontSize: 10, color: 'var(--ink-3)' }}>0{i+1}</div>
                <div>
                  <div style={{ fontFamily: 'var(--ff-mono)', fontSize: 13, color: 'var(--ink)' }}>{r.rule}</div>
                  <div style={{ position: 'relative', height: 4, background: 'var(--paper-3)', marginTop: 8 }}>
                    <div style={{ position: 'absolute', inset: 0, width: `${pctBar*2}%`, maxWidth: '100%', background: 'var(--accent)' }}/>
                  </div>
                </div>
                <div style={{ fontFamily: 'var(--ff-mono)', fontSize: 11, color: 'var(--ink-3)', textAlign: 'right' }}>
                  antes<br/><span style={{ color: 'var(--ink)', fontSize: 13 }}>{F.int(r.before)}</span>
                </div>
                <div style={{ fontFamily: 'var(--ff-mono)', fontSize: 11, color: 'var(--ink-3)', textAlign: 'right' }}>
                  después<br/><span style={{ color: 'var(--ink)', fontSize: 13 }}>{F.int(r.after)}</span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontFamily: 'var(--ff-mono)', fontSize: 11, color: r.dropped>0 ? 'var(--neg)' : 'var(--ink-4)' }}>
                    {r.dropped > 0 ? `−${F.int(r.dropped)}` : 'sin efecto'}
                  </div>
                  <div style={{ fontFamily: 'var(--ff-mono)', fontSize: 11, color: 'var(--ink-3)' }}>{r.pct}%</div>
                </div>
              </div>
            );
          })}
        </div>
        <div className="fig-caption">
          Cascada documentada: de 541 909 a 397 885 filas (−26,6%). Cada regla queda registrada en
          cleaning_rules.json con nombre, configuración y filas afectadas para auditoría.
        </div>
      </Figure>
    </>
  );
}

window.Pipeline = Pipeline;
