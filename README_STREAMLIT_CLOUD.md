# Deploy en Streamlit Community Cloud

## App principal

Usa este archivo como entrypoint:

```text
dashboard/app.py
```

## Requisitos

Streamlit Cloud instalará dependencias desde:

```text
requirements.txt
```

## Datos y artefactos

La app visualiza artefactos ya generados por el pipeline:

```text
reports/*.json
reports/*.md
data/processed/customer_segments.parquet
data/processed/customer_rfm.parquet
```

El CSV raw copiado en `data/raw/Online_Retail.csv` pesa aproximadamente 48 MB, por debajo del límite típico de archivo de GitHub de 100 MB. Si prefieres un repo más ligero, puedes desplegar solo los artefactos procesados y reportes.

## Pasos en Streamlit Community Cloud

1. Sube este proyecto a GitHub.
2. Entra en Streamlit Community Cloud.
3. Selecciona **New app**.
4. Elige tu repositorio y rama.
5. En **Main file path**, escribe:

```text
dashboard/app.py
```

6. Deploy.

## Ejecución local equivalente

En PowerShell:

```powershell
cd "C:\Users\User\Documents\Data science"
$env:PYTHONPATH='src;dashboard'
C:\Users\User\anaconda3\python.exe -m streamlit run dashboard/app.py
```

## Nota

El dashboard no ejecuta el pipeline en cada carga. Lee los artefactos ya generados para mantener reproducibilidad y evitar tiempos de ejecución innecesarios en Streamlit Cloud.
