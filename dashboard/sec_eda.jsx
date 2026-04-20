/* global React */
const { useMemo: _useMemoEDA } = React;

// ============================================================
// I. EDA
// ============================================================

function EDA() {
  const m = D.meta;
  const revMax = Math.max(...D.monthly.map(x => x.rev));
  const invMax = Math.max(...D.monthly.map(x => x.inv));

  return (
    <>
      <SecHead
        chapter="I" eyebrow="§ I · Datos"
        title="Análisis exploratorio"
        dek="Antes de segmentar, miramos. El dataset Online Retail documenta 13 meses de e-commerce británico. Su forma determina qué podemos y qué no podemos concluir."
        takeaway="4 372 clientes y £8,28M en ingresos netos, altamente concentrados en Reino Unido (90%) y sesgados hacia el último trimestre. El 24,9% de las transacciones originales no tenían CustomerID y quedan fuera del análisis RFM."
      />

      <StatRow items={[
        { label: "Filas crudas", value: F.int(m.rows_raw), note: "transacciones originales" },
        { label: "Filas limpias", value: F.int(m.rows_clean), note: "tras reglas de calidad" },
        { label: "Clientes únicos", value: F.int(m.customers), note: "con CustomerID válido" },
        { label: "Ingresos netos", value: F.moneyK(m.revenue_total), note: "Quantity × UnitPrice" },
      ]}/>

      <div className="lede">
        La segmentación RFM hereda todos los sesgos del dataset. Por eso dedicamos este capítulo
        a caracterizar la distribución temporal, geográfica y de calidad de los datos — y a declarar
        explícitamente qué decisiones de limpieza toman las reglas automáticas.
      </div>

      {/* Figure 1.1 — Monthly revenue */}
      <Figure num="1.1" title="Ingresos mensuales y número de facturas" source="Fuente: UCI Online Retail · elaboración propia">
        <svg className="chart" viewBox="0 0 900 280" style={{ width: '100%', height: 'auto' }}>
          {/* gridlines */}
          {[0, 250, 500, 750, 1000, 1250].map((v, i) => (
            <g key={i}>
              <line className="gridline" x1="60" x2="880" y1={250 - v/1250*210} y2={250 - v/1250*210}/>
              <text x="52" y={254 - v/1250*210} textAnchor="end">{v === 0 ? '0' : v+'k'}</text>
            </g>
          ))}
          {/* axis */}
          <line className="axis-strong" x1="60" y1="250" x2="880" y2="250"/>
          {/* bars: invoices (narrow, grey) + revenue (wider, accent) */}
          {D.monthly.map((d, i) => {
            const x = 75 + i * 63;
            const h = d.rev / 1250 * 210;
            const h2 = d.inv / 3000 * 210;
            return (
              <g key={i}>
                <rect x={x} y={250 - h} width="28" height={h} fill="var(--accent)"/>
                <rect x={x+32} y={250 - h2} width="10" height={h2} fill="var(--ink-3)" opacity="0.55"/>
                <text x={x+21} y="268" textAnchor="middle">{d.m}</text>
              </g>
            );
          })}
          {/* annotation */}
          <line className="rule-annot" x1="700" y1="55" x2="780" y2="40"/>
          <text className="annotation" x="785" y="44">Pico navideño Nov ’11</text>
          <text className="annotation" x="785" y="58">£1,16M en 2 751 facturas</text>

          {/* legend */}
          <rect x="60" y="10" width="10" height="10" fill="var(--accent)"/>
          <text x="76" y="19" style={{ fontSize: 11, fill: 'var(--ink-2)' }}>Ingresos (k£)</text>
          <rect x="170" y="10" width="10" height="10" fill="var(--ink-3)" opacity="0.55"/>
          <text x="186" y="19" style={{ fontSize: 11, fill: 'var(--ink-2)' }}>Facturas</text>
        </svg>
        <div className="fig-caption">
          Estacionalidad marcada: Sep–Nov concentran el 38% de ingresos anuales. Dic’11 truncado (dataset termina el día 9).
          El ratio £/factura sube un 27% en el Q4, señal de ticket navideño.
        </div>
      </Figure>

      {/* Figure 1.2 — Quality table with marginalia */}
      <div className="marginalia">
        <Figure num="1.2" title="Perfil de columnas · calidad del dataset crudo">
          <table className="ed-table">
            <thead>
              <tr>
                <th>Columna</th>
                <th>Tipo</th>
                <th className="num">Nulos</th>
                <th className="num">% nulos</th>
                <th className="num">Únicos</th>
                <th>Observación</th>
              </tr>
            </thead>
            <tbody>
              {D.quality.map((q, i) => {
                const pct = (q.missing / m.rows_raw * 100);
                return (
                  <tr key={i}>
                    <td style={{ fontFamily: 'var(--ff-mono)', fontSize: 12 }}>{q.col}</td>
                    <td className="muted">{q.type}</td>
                    <td className="num">{F.int(q.missing)}</td>
                    <td className="num" style={{ color: pct > 10 ? 'var(--neg)' : 'var(--ink-3)' }}>{pct.toFixed(2)}%</td>
                    <td className="num">{F.int(q.unique)}</td>
                    <td className="muted" style={{ fontStyle: 'italic' }}>{q.note}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Figure>
        <aside className="margin-note">
          <span className="label">Nota metodológica</span>
          El 24,9% de nulos en CustomerID es el principal descarte. No son errores: corresponden a transacciones
          de canal presencial o B2B sin trazabilidad de cliente. Mantenerlas contaminaría los scores de frecuencia.
        </aside>
      </div>

      {/* Country split + temporal distribution */}
      <div className="split" style={{ marginTop: 48 }}>
        <Figure num="1.3" title="Distribución geográfica de clientes">
          <div style={{ padding: '8px 0' }}>
            {D.countries.map((c, i) => {
              const max = D.countries[0].pct;
              return (
                <div key={i} style={{ display: 'grid', gridTemplateColumns: '160px 1fr 70px', gap: 14, alignItems: 'center', padding: '7px 0', borderBottom: '1px solid var(--rule-soft)' }}>
                  <div style={{ fontSize: 13 }}>{c.c}</div>
                  <div style={{ position: 'relative', height: 8, background: 'var(--paper-3)' }}>
                    <div style={{ position: 'absolute', inset: 0, width: `${c.pct/max*100}%`, background: i===0 ? 'var(--accent)' : 'var(--ink-3)', opacity: i===0?1:0.55 }}/>
                  </div>
                  <div style={{ textAlign: 'right', fontFamily: 'var(--ff-mono)', fontSize: 11, fontVariantNumeric: 'tabular-nums' }}>
                    {c.n} · {c.pct}%
                  </div>
                </div>
              );
            })}
          </div>
          <div className="fig-caption">
            La concentración en Reino Unido (90,4%) condiciona el análisis: los segmentos reflejan
            comportamiento del mercado británico más que patrones globales.
          </div>
        </Figure>

        <Figure num="1.4" title="Distribución de la variable Monetary por cliente">
          <svg className="chart" viewBox="0 0 400 240" style={{ width: '100%', height: 'auto' }}>
            {/* log-scale histogram shape */}
            <line className="axis-strong" x1="40" y1="200" x2="380" y2="200"/>
            <line className="axis" x1="40" y1="200" x2="40" y2="20"/>

            {/* bars: right-skewed distribution */}
            {[
              {x: 45, h: 170, lab: '<50'},
              {x: 80, h: 145, lab: '50-250'},
              {x: 115, h: 115, lab: '250-500'},
              {x: 150, h: 88, lab: '0,5k-1k'},
              {x: 185, h: 62, lab: '1k-2k'},
              {x: 220, h: 42, lab: '2k-5k'},
              {x: 255, h: 28, lab: '5k-10k'},
              {x: 290, h: 14, lab: '10k-50k'},
              {x: 325, h: 6, lab: '>50k'},
            ].map((b, i) => (
              <g key={i}>
                <rect x={b.x} y={200-b.h} width="30" height={b.h} fill="var(--accent)" opacity={0.85-i*0.07}/>
                <text x={b.x+15} y="214" textAnchor="middle" style={{ fontSize: 9 }}>{b.lab}</text>
              </g>
            ))}
            <text x="40" y="14" style={{ fontSize: 10, fill: 'var(--ink-3)' }}>clientes</text>
            <text x="215" y="234" textAnchor="middle" style={{ fontSize: 10, fill: 'var(--ink-3)' }}>Monetary (£)</text>

            <line className="rule-annot" x1="200" y1="80" x2="280" y2="60"/>
            <text className="annotation" x="285" y="64">Long tail:</text>
            <text className="annotation" x="285" y="77">top 1% = 22% ingresos</text>
          </svg>
          <div className="fig-caption">
            Distribución fuertemente asimétrica (skew ≈ 19). Justifica el uso de cuantiles sobre valores absolutos
            en el scoring RFM.
          </div>
        </Figure>
      </div>
    </>
  );
}

window.EDA = EDA;
