/* global React, ReactDOM */
const { useState, useEffect, useMemo } = React;
const D = window.RFM_DATA;
const F = window.fmt;

// ============================================================
// Shared components
// ============================================================

function SecHead({ chapter, eyebrow, title, dek, takeaway }) {
  return (
    <header className="sec-head">
      <div className="eyebrow">{eyebrow}</div>
      <div className="title-block">
        <h1>{title}</h1>
        <div className="dek">{dek}</div>
        {takeaway && (
          <div className="takeaway">
            <div className="label">Conclusión del capítulo</div>
            <div className="body">{takeaway}</div>
          </div>
        )}
      </div>
    </header>
  );
}

function Figure({ num, title, source, caption, children }) {
  return (
    <figure className="figure">
      <div className="figure-head">
        <span className="fig-num">Fig. {num}</span>
        <span className="fig-title">{title}</span>
        <span className="fig-spacer"></span>
        {source && <span className="fig-meta">{source}</span>}
      </div>
      {children}
      {caption && <div className="fig-caption">{caption}</div>}
    </figure>
  );
}

function StatRow({ items }) {
  return (
    <div className="stat-row">
      {items.map((s, i) => (
        <div className="stat" key={i}>
          <div className="label">{s.label}</div>
          <div className="value">{s.value}{s.unit && <span className="unit">{s.unit}</span>}</div>
          {s.note && <div className="note">{s.note}</div>}
        </div>
      ))}
    </div>
  );
}

function SegDot({ seg }) {
  return <span className="seg-dot" style={{ background: `var(${seg.color})` }}/>;
}

// ============================================================
// Sidebar
// ============================================================

const SECTIONS = [
  { id: 'eda',        num: 'I',    name: 'Análisis exploratorio' },
  { id: 'pipeline',   num: 'II',   name: 'Pipeline' },
  { id: 'segments',   num: 'III',  name: 'Segmentación' },
  { id: 'evaluation', num: 'IV',   name: 'Evaluación' },
  { id: 'manual',     num: 'V',    name: 'Manual vs Pipeline' },
  { id: 'agents',     num: 'VI',   name: 'Arquitectura de agentes' },
  { id: 'reports',    num: 'VII',  name: 'Reports' },
];

function Sidebar({ active, setActive }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="mark">TFG · RFM</div>
        <div className="sub">Online Retail · 2010–2011</div>
      </div>
      <div>
        <div className="toc-label">Índice</div>
        <ul className="toc">
          {SECTIONS.map(s => (
            <li key={s.id} className={active === s.id ? 'active' : ''}>
              <button onClick={() => setActive(s.id)}>
                <span className="num">{s.num}</span>
                <span className="name">{s.name}</span>
                <span className="arrow">→</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div className="sidebar-meta">
        TFG · Grado en ADE<br/>
        Autor · A. Palma Escámez<br/>
        Revisión · abr 2026
      </div>
    </aside>
  );
}

// ============================================================
// Tweaks panel
// ============================================================

function TweaksPanel({ tweaks, setTweaks, visible }) {
  const set = (k, v) => setTweaks({ ...tweaks, [k]: v });
  return (
    <div id="tweaks-panel" className={visible ? 'visible' : ''}>
      <div className="tweak-head">
        Tweaks
        <span className="kicker">v1</span>
      </div>

      <div className="tweak-group">
        <div className="tweak-label">Segments viz</div>
        <div className="tweak-options">
          <button className={`tweak-opt ${tweaks.segViz==='A'?'active':''}`} onClick={()=>set('segViz','A')}>A · Matriz</button>
          <button className={`tweak-opt ${tweaks.segViz==='B'?'active':''}`} onClick={()=>set('segViz','B')}>B · Ficha</button>
        </div>
      </div>

      <div className="tweak-group">
        <div className="tweak-label">Densidad</div>
        <div className="tweak-options">
          <button className={`tweak-opt ${tweaks.density==='comfortable'?'active':''}`} onClick={()=>set('density','comfortable')}>Amplia</button>
          <button className={`tweak-opt ${tweaks.density==='compact'?'active':''}`} onClick={()=>set('density','compact')}>Compacta</button>
        </div>
      </div>

      <div className="tweak-group">
        <div className="tweak-label">Anotaciones al margen</div>
        <div className="tweak-options">
          <button className={`tweak-opt ${tweaks.annot?'active':''}`} onClick={()=>set('annot',true)}>Mostrar</button>
          <button className={`tweak-opt ${!tweaks.annot?'active':''}`} onClick={()=>set('annot',false)}>Ocultar</button>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// App root
// ============================================================

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "segViz": "A",
  "density": "comfortable",
  "annot": true
}/*EDITMODE-END*/;

function App() {
  const [active, setActive] = useState(() => localStorage.getItem('rfm_section') || 'eda');
  const [tweaks, setTweaks] = useState(TWEAK_DEFAULTS);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => { localStorage.setItem('rfm_section', active); window.scrollTo(0,0); }, [active]);

  useEffect(() => {
    document.body.classList.toggle('density-compact', tweaks.density === 'compact');
    document.body.classList.toggle('hide-annot', !tweaks.annot);
    // persist to host
    try {
      window.parent.postMessage({ type: '__edit_mode_set_keys', edits: tweaks }, '*');
    } catch(e) {}
  }, [tweaks]);

  useEffect(() => {
    const handler = (e) => {
      if (e.data?.type === '__activate_edit_mode') setEditMode(true);
      if (e.data?.type === '__deactivate_edit_mode') setEditMode(false);
    };
    window.addEventListener('message', handler);
    window.parent.postMessage({ type: '__edit_mode_available' }, '*');
    return () => window.removeEventListener('message', handler);
  }, []);

  return (
    <div className="app">
      <Sidebar active={active} setActive={setActive} />
      <main className="main">
        <div className={`section ${active==='eda'?'active':''}`} data-screen-label="I EDA">
          {active==='eda' && <EDA/>}
        </div>
        <div className={`section ${active==='pipeline'?'active':''}`} data-screen-label="II Pipeline">
          {active==='pipeline' && <Pipeline/>}
        </div>
        <div className={`section ${active==='segments'?'active':''}`} data-screen-label="III Segments">
          {active==='segments' && <Segments variant={tweaks.segViz}/>}
        </div>
        <div className={`section ${active==='evaluation'?'active':''}`} data-screen-label="IV Evaluation">
          {active==='evaluation' && <Evaluation/>}
        </div>
        <div className={`section ${active==='manual'?'active':''}`} data-screen-label="V Manual vs Pipeline">
          {active==='manual' && <ManualVsPipeline/>}
        </div>
        <div className={`section ${active==='agents'?'active':''}`} data-screen-label="VI Agents">
          {active==='agents' && <Agents/>}
        </div>
        <div className={`section ${active==='reports'?'active':''}`} data-screen-label="VII Reports">
          {active==='reports' && <Reports/>}
        </div>
      </main>
      <TweaksPanel tweaks={tweaks} setTweaks={setTweaks} visible={editMode}/>
    </div>
  );
}

// Export shared helpers for other files
Object.assign(window, { SecHead, Figure, StatRow, SegDot, D, F, App });
