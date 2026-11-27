$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:ZIPFORMER_BACKEND = 'onnx'
$env:ZIPFORMER_MODEL_DIR = Join-Path $PSScriptRoot 'runtime/zipformer'
$env:MODEL_PROVIDER = if ($env:MODEL_PROVIDER) { $env:MODEL_PROVIDER } else { 'ollama' }
$env:MODEL_NAME = if ($env:MODEL_NAME) { $env:MODEL_NAME } else { 'qwen3:4b' }
$env:PYTHONIOENCODING = 'utf-8'
if ($env:MODEL_PROVIDER -eq 'ollama') {
    Write-Host "Đang dùng Ollama model $env:MODEL_NAME. Khởi động Ollama và tải model trước khi hỏi AI."
} elseif ($env:MODEL_PROVIDER -eq 'openai_compatible') {
    Write-Host 'Đang dùng API tương thích OpenAI. Cấu hình API_KEY và LLM_API_BASE trong .env.'
}
Write-Host 'Sau khi Streamlit khởi động, mở http://127.0.0.1:8501'
& (Join-Path $PSScriptRoot '.venv/Scripts/python.exe') -m streamlit run voice_demo.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
exit $LASTEXITCODE
