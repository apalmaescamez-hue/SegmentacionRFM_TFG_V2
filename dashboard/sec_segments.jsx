/* global React */

// ============================================================
// III. Segments  (Variant A: Matriz · Variant B: Ficha)
// ============================================================

function Segments({ variant }) {
  const segs = D.segments;

  return (
    <>
      <SecHead
        chapter="III" eyebrow="§ III · Resultado"
        title="Ocho segmentos de comportamiento"
        dek="El modelo asigna a cada uno de los 4 372 clientes una de ocho etiquetas, a partir de reglas determinísticas sobre los scores R, F y M en escala 1–5."
        takeaway="Champions (19% de clientes) concentra el 39,7% de los ingresos. Hibernating y At Risk juntos suman el 28% de clientes pero solo el 8,6% del revenue — candidatos a políticas de eficiencia, no de adquisición."
      />

      {/* Methodology bar — quintile logic visible */}
      <Figure num="3.1" title="Lógica de scoring · quintiles sobre R, F, M" source="src/tfg_rfm/segmentation/scoring.py">
        <div className="split-3" style={{ gap: 32 }}>
          {[
            { letter: 'R', name: 'Recency', desc: 'Días desde la última compra', dir: 'invertido', hi: 'Reciente', lo: 'Lejano' },
            { letter: 'F', name: 'Frequency', desc: 'Número de facturas únicas', dir: 'directo', hi: 'Frecuente', lo: 'Esporádico' },
            { letter: 'M', name: 'Monetary', desc: 'Suma neta gastada', dir: 'directo', hi: 'Alto gasto', lo: 'Bajo gasto' },
          ].map((v, i) => (
            <div key={i} className="panel filled">
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 14, marginBottom: 12 }}>
                <div style={{ fontFamily: 'var(--ff-serif)', fontSize: 56, lineHeight: 1, color: 'var(--accent-ink)' }}>{v.letter}</div>
                <div>
                  <div style={{ fontFamily: 'var(--ff-serif)', fontSize: 20 }}>{v.name}</div>
                  <div className="kicker">Dirección: {v.dir}</div>
                </div>
              </div>
              <div style={{ fontSize: 13, color: 'var(--ink-2)', marginBottom: 14 }}>{v.desc}</div>
              <div style={{ display: 'flex', gap: 4, marginBottom: 10 }}>
                {[1,2,3,4,5].map(n => (
                  <div key={n} style={{
                    flex: 1, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: 'var(--ff-mono)', fontSize: 12, color: n===5?'var(--paper)':'var(--ink)',
                    background: `oklch(${98 - n*10}% 0.05 40)`,
                  }}>{n}</div>
                ))}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--ff-mono)', fontSize: 10, color: 'var(--ink-3)', letterSpacing: '0.08em' }}>
                <span>{v.lo}</span><span>{v.hi}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="fig-caption">
          Cada variable se divide en quintiles por rango (pd.qcut con method='first'). R se invierte
          para que 5 siempre signifique «mejor». La suma R+F+M produce RFM_Total ∈ [3, 15].
        </div>
      </Figure>

      {/* Revenue concentration — always shown */}
      <Figure num="3.2" title="Concentración de ingresos · % clientes vs % revenue por segmento">
        <svg className="chart" viewBox="0 0 900 260" style={{ width: '100%', height: 'auto' }}>
          <line className="axis-strong" x1="20" y1="120" x2="880" y2="120"/>
          {segs.map((s, i) => {
            const x = 30 + i * 107;
            const cH = s.pct * 4;
            const rH = s.revpct * 4;
            return (
              <g key={s.key}>
                <rect x={x} y={120 - cH} width="40" height={cH} fill="var(--ink-3)" opacity="0.45"/>
                <rect x={x+46} y={120} width="40" height={rH} fill={`var(${s.color})`}/>
                <text x={x+43} y={240} textAnchor="middle" className="label-serif" style={{ fontSize: 11 }}>{s.name}</text>
                <text x={x+20} y={115 - cH} textAnchor="middle" style={{ fontSize: 10, fill: 'var(--ink-3)' }}>{s.pct}%</text>
                <text x={x+66} y={125 + rH + 11} textAnchor="middle" style={{ fontSize: 10, fill: 'var(--ink-2)' }}>{s.revpct}%</text>
              </g>
            );
          })}
          {/* center labels */}
          <text x="890" y="40" textAnchor="end" style={{ fontSize: 11, fill: 'var(--ink-3)' }}>% clientes</text>
          <text x="890" y="220" textAnchor="end" style={{ fontSize: 11, fill: 'var(--ink-3)' }}>% revenue</text>
        </svg>
        <div className="fig-caption">
          Barras espejadas. Champions muestra el desbalance característico de Pareto: menos clientes por encima,
          mucho más revenue por debajo. Hibernating presenta lo opuesto.
        </div>
      </Figure>

      {/* VARIANT A — matrix table */}
      {variant === 'A' && <SegmentsMatrix segs={segs}/>}

      {/* VARIANT B — card per segment */}
      {variant === 'B' && <SegmentsCards segs={segs}/>}
    </>
  );
}

// ---------- Variant A: matrix / editorial table ----------

function SegmentsMatrix({ segs }) {
  return (
    <>
      <h3 style={{ marginTop: 72, marginBottom: 4 }}>Tabla maestra de segmentos</h3>
      <p style={{ color: 'var(--ink-3)', fontSize: 13, marginBottom: 24 }}>Ordenada por revenue total. Haz clic sobre una fila para detalle.</p>

      <Figure num="3.3" title="Perfil cuantitativo de cada segmento" source="rfm_segments.csv">
        <table className="ed-table">
          <thead>
            <tr>
              <th>Segmento</th>
              <th className="num">Clientes</th>
              <th className="num">% clientes</th>
              <th className="num">Revenue</th>
              <th className="num">% revenue</th>
              <th className="num">R̄ (días)</th>
              <th className="num">F̄</th>
              <th className="num">M̄ (£)</th>
            </tr>
          </thead>
          <tbody>
            {segs.map(s => (
              <tr key={s.key}>
                <td><SegDot seg={s}/><span style={{ fontFamily: 'var(--ff-serif)', fontSize: 16 }}>{s.name}</span></td>
                <td className="num">{F.int(s.n)}</td>
                <td className="num muted">{s.pct}%</td>
                <td className="num">{F.moneyK(s.rev)}</td>
                <td className="num" style={{ color: s.revpct > 15 ? 'var(--accent-ink)' : 'var(--ink)' }}>{s.revpct}%</td>
                <td className="num muted">{Math.round(s.r)}</td>
                <td className="num muted">{s.f.toFixed(1)}</td>
                <td className="num muted">{F.int(s.m)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td>Total</td>
              <td className="num">{F.int(segs.reduce((a,s)=>a+s.n,0))}</td>
              <td className="num">100%</td>
              <td className="num">{F.moneyK(segs.reduce((a,s)=>a+s.rev,0))}</td>
              <td className="num">100%</td>
              <td className="num" colSpan="3">— promedio ponderado —</td>
            </tr>
          </tfoot>
        </table>
      </Figure>

      {/* Actionable recommendations */}
      <Figure num="3.4" title="Recomendaciones accionables por segmento">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0 }}>
          {segs.map((s, i) => (
            <div key={s.key} style={{
              padding: '20px 24px 20px 20px',
              borderTop: '1px solid var(--rule)',
              borderLeft: i%2===1 ? '1px solid var(--rule)' : 'none',
              borderBottom: i>=segs.length-2 ? '1px solid var(--rule)' : 'none',
              position: 'relative',
            }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 8 }}>
                <SegDot seg={s}/>
                <div style={{ fontFamily: 'var(--ff-serif)', fontSize: 19 }}>{s.name}</div>
                <div style={{ marginLeft: 'auto', fontFamily: 'var(--ff-mono)', fontSize: 11, color: 'var(--ink-3)' }}>{F.int(s.n)} · {F.moneyK(s.rev)}</div>
              </div>
              <div style={{ fontFamily: 'var(--ff-serif)', fontSize: 14, fontStyle: 'italic', color: 'var(--ink-2)', lineHeight: 1.5, marginBottom: 10 }}>
                {s.story}
              </div>
              <div style={{
                fontFamily: 'var(--ff-sans)', fontSize: 13, color: 'var(--ink)',
                padding: '10px 14px', background: 'var(--paper-2)', borderLeft: `3px solid var(${s.color})`,
              }}>
                <span className="kicker" style={{ display: 'block', marginBottom: 4, color: 'var(--ink-3)' }}>Acción sugerida</span>
                {s.action}
              </div>
            </div>
          ))}
        </div>
      </Figure>
    </>
  );
}

// ---------- Variant B: card per segment ----------

function SegmentsCards({ segs }) {
  return (
    <>
      <h3 style={{ marginTop: 72, marginBottom: 4 }}>Ficha detallada por segmento</h3>
      <p style={{ color: 'var(--ink-3)', fontSize: 13, marginBottom: 24 }}>
        Cada ficha muestra tamaño, peso económico, perfil RFM y recomendación accionable.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {segs.map(s => {
          const rMax = 300, fMax = 15, mMax = 4500;
          return (
            <div key={s.key} className="panel" style={{ padding: 0, overflow: 'hidden' }}>
              {/* colored top stripe */}
              <div style={{ height: 6, background: `var(${s.color})` }}/>
              <div style={{ padding: '24px 26px' }}>
                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div style={{ fontFamily: 'var(--ff-serif)', fontSize: 26, letterSpacing: '-0.01em' }}>{s.name}</div>
                  <div style={{ fontFamily: 'var(--ff-mono)', fontSize: 10, color: 'var(--ink-3)', letterSpacing: '0.08em' }}>SEG · {s.key.toUpperCase().slice(0,3)}</div>
                </div>
                <div style={{ fontFamily: 'var(--ff-serif)', fontStyle: 'italic', color: 'var(--ink-2)', fontSize: 14, lineHeight: 1.5, marginBottom: 18 }}>
                  {s.story}
                </div>

                {/* twin stats */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, borderTop: '1px solid var(--ink)', borderBottom: '1px solid var(--rule)' }}>
                  <div style={{ padding: '12px 12px 12px 0', borderRight: '1px solid var(--rule-soft)' }}>
                    <div className="kicker">Clientes</div>
                    <div style={{ fontFamily: 'var(--ff-serif)', fontSize: 28, lineHeight: 1, marginTop: 4 }}>
                      {F.int(s.n)} <span style={{ fontSize: 13, color: 'var(--ink-3)' }}>· {s.pct}%</span>
                    </div>
                  </div>
                  <div style={{ padding: '12px 0 12px 16px' }}>
                    <div className="kicker">Revenue</div>
                    <div style={{ fontFamily: 'var(--ff-serif)', fontSize: 28, lineHeight: 1, marginTop: 4 }}>
                      {F.moneyK(s.rev)} <span style={{ fontSize: 13, color: 'var(--ink-3)' }}>· {s.revpct}%</span>
                    </div>
                  </div>
                </div>

                {/* RFM signature bars */}
                <div style={{ marginTop: 18 }}>
                  <div className="kicker" style={{ marginBottom: 10 }}>Firma RFM promedio</div>
                  {[
                    { k: 'R', v: s.r, max: rMax, unit: 'días', rev: true },
                    { k: 'F', v: s.f, max: fMax, unit: 'facturas' },
                    { k: 'M', v: s.m, max: mMax, unit: '£' },
                  ].map(row => {
                    const pct = Math.min(row.v / row.max, 1) * 100;
                    return (
                      <div key={row.k} style={{ display: 'grid', gridTemplateColumns: '18px 1fr 90px', gap: 10, alignItems: 'center', marginBottom: 6 }}>
                        <div style={{ fontFamily: 'var(--ff-serif)', fontSize: 14, color: 'var(--accent-ink)' }}>{row.k}</div>
                        <div style={{ position: 'relative', height: 5, background: 'var(--paper-3)' }}>
                          <div style={{ position: 'absolute', inset: 0, width: `${pct}%`, background: `var(${s.color})`, opacity: 0.85 }}/>
                        </div>
                        <div style={{ fontFamily: 'var(--ff-mono)', fontSize: 11, color: 'var(--ink-2)', textAlign: 'right' }}>
                          {row.k==='M' ? F.int(row.v) : row.v.toFixed(row.k==='F'?1:0)} {row.unit}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* action */}
                <div style={{ marginTop: 20, padding: '12px 14px', background: 'var(--paper-2)', borderLeft: `3px solid var(${s.color})` }}>
                  <div className="kicker" style={{ color: 'var(--ink-3)', marginBottom: 4 }}>Acción sugerida</div>
                  <div style={{ fontSize: 13, color: 'var(--ink)' }}>{s.action}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}

window.Segments = Segments;
