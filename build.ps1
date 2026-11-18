$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = $env:COMPRIMIR_PDF_PYTHON
if (-not $Python) {
    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($PythonCommand) {
        $Python = $PythonCommand.Source
    }
}
if (-not $Python -or -not (Test-Path -LiteralPath $Python)) {
    throw "Python não encontrado. Instale o Python 3.12 ou superior antes de gerar o executável."
}

& $Python (Join-Path $ProjectDir "create_icon.py")
& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "Comprimir PDF" `
    --icon (Join-Path $ProjectDir "comprimir_pdf.ico") `
    --add-data "$(Join-Path $ProjectDir 'comprimir_pdf.ico');." `
    --exclude-module pymupdf_layout `
    --exclude-module pymupdf4llm `
    --exclude-module onnxruntime `
    --exclude-module networkx `
    --exclude-module yaml `
    --exclude-module numpy `
    --distpath (Join-Path $ProjectDir "dist") `
    --workpath (Join-Path $ProjectDir "build") `
    --specpath $ProjectDir `
    (Join-Path $ProjectDir "comprimir_pdf.py")
