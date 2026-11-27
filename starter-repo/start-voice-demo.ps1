$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:ZIPFORMER_BACKEND = 'onnx'
$env:ZIPFORMER_MODEL_DIR = Join-Path $PSScriptRoot 'runtime/zipformer'
$env:MODEL_PROVIDER = 'ollama'
$env:MODEL_NAME = 'qwen3:4b'
$env:PYTHONIOENCODING = 'utf-8'
& (Join-Path $PSScriptRoot '.venv/Scripts/python.exe') -m streamlit run voice_demo.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
exit $LASTEXITCODE
