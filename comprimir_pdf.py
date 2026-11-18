import io
import os
import shutil
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

import pymupdf
from PIL import Image


APP_NAME = "Comprimir PDF"

PRESETS = {
    "Leve": {
        "dpi_target": 200,
        "quality": 82,
        "subsampling": 1,
        "graphic_dpi": 220,
        "graphic_quality": 88,
        "graphic_subsampling": 0,
    },
    "Equilibrada": {
        "dpi_target": 150,
        "quality": 68,
        "subsampling": 2,
        "graphic_dpi": 150,
        "graphic_quality": 78,
        "graphic_subsampling": 1,
    },
    "Forte": {
        "dpi_target": 110,
        "quality": 55,
        "subsampling": 2,
        "graphic_dpi": 120,
        "graphic_quality": 70,
        "graphic_subsampling": 2,
    },
}


def human_size(size):
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024


class PDFCompressorApp:
    def __init__(self, root):
        self.root = root
        self.input_path = None
        self.busy = False

        root.title(APP_NAME)
        root.geometry("680x540")
        root.minsize(620, 510)
        root.configure(bg="#f3f6fa")

        try:
            root.iconbitmap(self.resource_path("comprimir_pdf.ico"))
        except (tk.TclError, OSError):
            pass

        self._configure_style()
        self._build_ui()

    @staticmethod
    def resource_path(name):
        base = Path(getattr(__import__("sys"), "_MEIPASS", Path(__file__).parent))
        return str(base / name)

    def _configure_style(self):
        style = ttk.Style()
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#f3f6fa")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("Title.TLabel", background="#f3f6fa", foreground="#15324b", font=("Segoe UI", 21, "bold"))
        style.configure("Subtitle.TLabel", background="#f3f6fa", foreground="#5e6f7f", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#ffffff", foreground="#263746", font=("Segoe UI", 10))
        style.configure("File.TLabel", background="#ffffff", foreground="#15324b", font=("Segoe UI", 10, "bold"))
        style.configure("Hint.TLabel", background="#ffffff", foreground="#657786", font=("Segoe UI", 9))
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), padding=(24, 14))
        style.configure("TButton", font=("Segoe UI", 10), padding=(14, 8))
        style.configure("TRadiobutton", background="#ffffff", foreground="#263746", font=("Segoe UI", 10))
        style.configure("Horizontal.TProgressbar", troughcolor="#dfe7ee", background="#1976d2")

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=(28, 22))
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text=APP_NAME, style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="Reduza o tamanho de um arquivo PDF por vez, com processamento totalmente offline.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 18))

        card = ttk.Frame(outer, style="Card.TFrame", padding=22)
        card.pack(fill="both", expand=True)

        select_row = ttk.Frame(card, style="Card.TFrame")
        select_row.pack(fill="x")
        self.select_button = ttk.Button(select_row, text="Selecionar PDF", command=self.select_pdf)
        self.select_button.pack(side="left")
        self.clear_button = ttk.Button(select_row, text="Limpar", command=self.clear_selection, state="disabled")
        self.clear_button.pack(side="left", padx=(8, 0))

        self.file_label = ttk.Label(card, text="Nenhum arquivo selecionado", style="File.TLabel", wraplength=570)
        self.file_label.pack(anchor="w", pady=(16, 2))
        self.file_info = ttk.Label(card, text="Selecione somente um arquivo PDF.", style="Hint.TLabel")
        self.file_info.pack(anchor="w")

        ttk.Separator(card).pack(fill="x", pady=18)
        ttk.Label(card, text="Nível de compressão", style="Card.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.preset = tk.StringVar(value="Equilibrada")
        radio_row = ttk.Frame(card, style="Card.TFrame")
        radio_row.pack(fill="x", pady=(8, 2))
        for name in PRESETS:
            ttk.Radiobutton(
                radio_row,
                text=name,
                value=name,
                variable=self.preset,
            ).pack(side="left", padx=(0, 24))

        self.progress = ttk.Progressbar(card, mode="indeterminate")
        self.progress.pack(fill="x", pady=(4, 8))
        self.status_label = ttk.Label(card, text="Pronto para selecionar um PDF.", style="Hint.TLabel")
        self.status_label.pack(anchor="w")

        self.compress_button = ttk.Button(
            card,
            text="Comprimir",
            command=self.start_compression,
            state="disabled",
            style="Accent.TButton",
            width=18,
        )
        self.compress_button.pack(anchor="e", pady=(16, 0))

    def select_pdf(self):
        filename = filedialog.askopenfilename(
            title="Selecione um arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
        )
        if not filename:
            return
        if Path(filename).suffix.lower() != ".pdf":
            messagebox.showwarning(APP_NAME, "Selecione um arquivo com extensão .pdf.")
            return
        try:
            size = os.path.getsize(filename)
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Não foi possível acessar o arquivo:\n{exc}")
            return
        self.input_path = filename
        self.file_label.config(text=os.path.basename(filename))
        self.file_info.config(text=f"Tamanho original: {human_size(size)}")
        self.status_label.config(text="Arquivo pronto para compressão.")
        self.clear_button.config(state="normal")
        self.compress_button.config(state="normal")

    def clear_selection(self):
        if self.busy:
            return
        self.input_path = None
        self.file_label.config(text="Nenhum arquivo selecionado")
        self.file_info.config(text="Selecione somente um arquivo PDF.")
        self.status_label.config(text="Pronto para selecionar um PDF.")
        self.clear_button.config(state="disabled")
        self.compress_button.config(state="disabled")

    def start_compression(self):
        if not self.input_path or self.busy:
            return

        input_path = self.input_path
        source = Path(input_path)
        suggested = f"{source.stem}_comprimido.pdf"
        output_path = filedialog.asksaveasfilename(
            title="Salvar PDF comprimido como",
            initialdir=str(source.parent),
            initialfile=suggested,
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
        )
        if not output_path:
            return
        if os.path.abspath(input_path).lower() == os.path.abspath(output_path).lower():
            messagebox.showwarning(APP_NAME, "Escolha um nome diferente do arquivo original.")
            return

        password = None
        try:
            document = pymupdf.open(input_path)
            needs_password = document.needs_pass
            document.close()
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Não foi possível abrir o PDF:\n{exc}")
            return
        if needs_password:
            password = simpledialog.askstring(APP_NAME, "Digite a senha do PDF:", show="*")
            if password is None:
                return

        self._set_busy(True)
        settings = PRESETS[self.preset.get()].copy()
        worker = threading.Thread(
            target=self._compress_worker,
            args=(input_path, output_path, password, settings),
            daemon=True,
        )
        worker.start()

    def _set_busy(self, busy):
        self.busy = busy
        state = "disabled" if busy else "normal"
        self.select_button.config(state=state)
        self.clear_button.config(state=state if self.input_path else "disabled")
        self.compress_button.config(state=state if self.input_path else "disabled")
        if busy:
            self.status_label.config(text="Comprimindo o PDF... aguarde.")
            self.progress.start(12)
        else:
            self.progress.stop()

    def _compress_worker(self, input_path, output_path, password, settings):
        temp_path = None
        try:
            destination = Path(output_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            fd, temp_path = tempfile.mkstemp(prefix="comprimir_pdf_", suffix=".pdf", dir=str(destination.parent))
            os.close(fd)

            document = pymupdf.open(input_path)
            if document.needs_pass and not document.authenticate(password or ""):
                document.close()
                raise ValueError("Senha incorreta para este PDF.")

            self._compress_photos_safely(document, settings)
            # PDFs gerados por impressão frequentemente incorporam dezenas de
            # cópias completas das mesmas fontes. Mantemos somente os glifos
            # realmente usados, sem rasterizar ou alterar o texto das páginas.
            try:
                document.subset_fonts()
            except Exception:
                # Alguns PDFs possuem fontes incomuns; a compressão de imagens
                # ainda deve ser concluída nesses casos.
                pass
            document.save(
                temp_path,
                garbage=4,
                clean=False,
                deflate=True,
                deflate_images=True,
                deflate_fonts=True,
                use_objstms=1,
                compression_effort=100,
                preserve_metadata=True,
            )
            document.close()

            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(temp_path)
            if compressed_size < original_size:
                os.replace(temp_path, output_path)
                temp_path = None
            else:
                os.remove(temp_path)
                temp_path = None
                shutil.copy2(input_path, output_path)
                compressed_size = original_size
            self.root.after(0, self._compression_done, output_path, original_size, compressed_size)
        except Exception as exc:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            self.root.after(0, self._compression_failed, str(exc))

    @staticmethod
    def _compress_photos_safely(document, settings):
        """Recomprime somente fotografias JPEG com geometria segura.

        Máscaras e transparências são preservadas. Fotografias e artes
        panorâmicas usam perfis separados e a dimensão real de exibição,
        evitando o erro que reduzia logotipos a poucos pixels.
        """
        usages = {}
        pages_by_xref = {}
        image_info = {}

        for page_number in range(document.page_count):
            page = document[page_number]
            for item in page.get_images(full=True):
                xref, smask, width, height, bpc = item[:5]
                if xref <= 0:
                    continue
                image_info.setdefault(xref, (smask, width, height, bpc))
                pages_by_xref.setdefault(xref, page_number)
                try:
                    rects = page.get_image_rects(xref)
                except Exception:
                    rects = []
                for rect in rects:
                    if rect.width > 0 and rect.height > 0:
                        usages.setdefault(xref, []).append((rect.width, rect.height))

        for xref, (smask, width, height, bpc) in image_info.items():
            if smask > 0 or bpc <= 1 or width < 128 or height < 64:
                continue
            aspect = width / height
            is_graphic = aspect > 4.0 or aspect < 0.25

            try:
                extracted = document.extract_image(xref)
            except Exception:
                continue
            extension = str(extracted.get("ext", "")).lower()
            if extension not in {"jpg", "jpeg"}:
                continue

            placements = usages.get(xref, [])
            if not placements:
                continue
            target_dpi = settings["graphic_dpi"] if is_graphic else settings["dpi_target"]
            quality = settings["graphic_quality"] if is_graphic else settings["quality"]
            subsampling = settings["graphic_subsampling"] if is_graphic else settings["subsampling"]
            required_width = max(display_width / 72 * target_dpi for display_width, _ in placements)
            required_height = max(display_height / 72 * target_dpi for _, display_height in placements)
            scale = min(1.0, max(required_width / width, required_height / height))

            # Evita pequenas reamostragens desnecessárias; ainda permite
            # otimizar a codificação JPEG mantendo as dimensões originais.
            if scale > 0.90:
                scale = 1.0
            new_width = max(1, round(width * scale))
            new_height = max(1, round(height * scale))

            try:
                with Image.open(io.BytesIO(extracted["image"])) as image:
                    image.load()
                    if image.mode not in {"RGB", "L"}:
                        image = image.convert("RGB")
                    if image.size != (new_width, new_height):
                        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    output = io.BytesIO()
                    image.save(
                        output,
                        format="JPEG",
                        quality=quality,
                        optimize=True,
                        progressive=False,
                        subsampling=subsampling,
                    )
                # Atualiza o próprio objeto de imagem. page.replace_image()
                # cria uma segunda referência em alguns PDFs e aumenta o arquivo.
                document.update_stream(xref, output.getvalue(), new=False, compress=False)
                document.xref_set_key(xref, "Type", "/XObject")
                document.xref_set_key(xref, "Subtype", "/Image")
                document.xref_set_key(xref, "Width", str(new_width))
                document.xref_set_key(xref, "Height", str(new_height))
                document.xref_set_key(xref, "BitsPerComponent", "8")
                document.xref_set_key(xref, "ColorSpace", "/DeviceGray" if image.mode == "L" else "/DeviceRGB")
                document.xref_set_key(xref, "Filter", "/DCTDecode")
                document.xref_set_key(xref, "DecodeParms", "null")
            except Exception:
                # Um formato incomum não deve impedir a compressão do PDF.
                continue

    def _compression_done(self, output_path, original_size, compressed_size):
        self._set_busy(False)
        difference = original_size - compressed_size
        if original_size:
            percent = difference / original_size * 100
        else:
            percent = 0

        if difference > 0:
            summary = f"Redução de {percent:.1f}% ({human_size(original_size)} → {human_size(compressed_size)})."
        elif difference == 0:
            summary = "O PDF já estava otimizado e manteve o mesmo tamanho."
        else:
            summary = "O PDF já estava otimizado; foi mantido sem aumentar o tamanho."

        self.status_label.config(text=summary)
        messagebox.showinfo(APP_NAME, f"PDF processado com sucesso!\n\n{summary}\n\nSalvo em:\n{output_path}")

    def _compression_failed(self, error):
        self._set_busy(False)
        self.status_label.config(text="Não foi possível comprimir o arquivo.")
        messagebox.showerror(APP_NAME, f"Falha ao comprimir o PDF:\n{error}")


def main():
    root = tk.Tk()
    PDFCompressorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
