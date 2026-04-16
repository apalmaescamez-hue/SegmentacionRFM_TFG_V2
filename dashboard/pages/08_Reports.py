from __future__ import annotations

import json

import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import ROOT, list_report_files

st.set_page_config(page_title="Reports", page_icon="📄", layout="wide")
st.title("📄 Reports")

files = list_report_files()
if not files:
    st.warning("No hay reportes disponibles.")
    st.stop()

labels = [str(path.relative_to(ROOT)) for path in files]
choice = st.selectbox("Selecciona un reporte", labels)
path = ROOT / choice

st.download_button("Descargar", path.read_bytes(), file_name=path.name)

if path.suffix.lower() == ".md":
    st.markdown(path.read_text(encoding="utf-8"))
elif path.suffix.lower() == ".json":
    st.json(json.loads(path.read_text(encoding="utf-8")))
else:
    st.write(path.read_text(encoding="utf-8"))
