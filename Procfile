release: pip install -e .
web: python3 -m streamlit run frontend/app.py --server.port=$STREAMLIT_SERVER_PORT --server.address=0.0.0.0 --server.headless=true
worker: python3 -m uvicorn backend.main:app --host 0.0.0.0 --port ${API_PORT:-8000}
