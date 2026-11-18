# Comprimir PDF

Aplicativo desktop para Windows que reduz o tamanho de arquivos PDF com processamento totalmente local e offline.

O sistema trabalha com um arquivo por vez, preserva textos pesquisáveis e aplica tratamentos diferentes para fotografias, logotipos e fontes incorporadas.

## Recursos

- Seleção de um único PDF por vez.
- Três níveis de compressão: Leve, Equilibrada e Forte.
- Redimensionamento de imagens conforme o tamanho real utilizado na página.
- Tratamento específico para fotografias e logotipos panorâmicos.
- Redução de fontes incorporadas aos caracteres realmente utilizados.
- Preservação de textos vetoriais e pesquisáveis.
- Suporte a documentos protegidos por senha.
- Exibição do tamanho original, tamanho final e percentual de redução.
- Processamento offline, sem envio de documentos para servidores externos.
- Executável único para Windows, sem necessidade de instalar Python.

## Como usar o executável

1. Abra `dist/Comprimir PDF.exe`.
2. Clique em **Selecionar PDF**.
3. Escolha o arquivo desejado.
4. Selecione o nível Leve, Equilibrada ou Forte.
5. Clique em **Comprimir**.
6. Escolha o nome e o local do arquivo de saída.

O arquivo original não é alterado.

## Níveis de compressão

| Nível | Imagens principais | Indicação |
| --- | --- | --- |
| Leve | Até 200 DPI | Prioriza nitidez e detalhes |
| Equilibrada | Aproximadamente 150 DPI | Equilíbrio entre qualidade e tamanho |
| Forte | Até 110 DPI | Prioriza o menor arquivo possível |

Logotipos e imagens panorâmicas recebem parâmetros próprios para permanecerem legíveis. Máscaras e transparências incompatíveis com a recompressão são preservadas.

## Tecnologias

- Python 3.12+
- Tkinter
- PyMuPDF
- Pillow
- PyInstaller

## Estrutura do projeto

```text
Comprimir PDF/
├── comprimir_pdf.py       # Aplicação e interface gráfica
├── comprimir_pdf.ico      # Ícone do programa
├── create_icon.py         # Gerador do ícone
├── requirements.txt       # Dependências de desenvolvimento
├── build.ps1              # Script de geração do executável
├── Comprimir PDF.spec     # Configuração do PyInstaller
└── dist/
    └── Comprimir PDF.exe  # Executável pronto para uso
```

## Executar pelo código-fonte

### Requisitos

- Windows 10 ou Windows 11.
- Python 3.12 ou superior com Tcl/Tk.

### Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python comprimir_pdf.py
```

## Gerar o executável

Com o ambiente ativado e as dependências instaladas:

```powershell
.\build.ps1
```

O executável será criado em:

```text
dist/Comprimir PDF.exe
```

O script também aceita a variável `COMPRIMIR_PDF_PYTHON` com o caminho de um interpretador Python específico.

```powershell
$env:COMPRIMIR_PDF_PYTHON = "C:\caminho\python.exe"
.\build.ps1
```

## Observações

- PDFs que já estejam otimizados podem apresentar pouca ou nenhuma redução.
- A opção Forte reduz mais detalhes das fotografias.
- Assinaturas digitais existentes podem deixar de ser válidas após qualquer modificação do PDF.
- O aplicativo nunca substitui o arquivo original pelo resultado.

## Privacidade

Todo o processamento acontece no computador do usuário. Nenhum PDF é enviado para a internet.
