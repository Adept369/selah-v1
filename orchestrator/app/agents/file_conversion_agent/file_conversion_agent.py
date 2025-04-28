import logging
import os
from pathlib import Path
from typing import Any, Tuple

import pypandoc

from speech_recognition import UnknownValueError  # ← catch this

logger = logging.getLogger(__name__)

# Optional PDF→DOCX via pdf2docx
try:
    from pdf2docx import Converter
    PDF2DOCX_AVAILABLE = True
except ImportError:
    PDF2DOCX_AVAILABLE = False

class FileConversionAgent:
    """
    Agent for common file conversions:
      - CSV ↔ XLSX
      - DOCX → PDF
      - PDF → DOCX
      - Audio → Text
    """

    def __init__(self, llm_client: Any):
        self.llm = llm_client
        # Ensure Pandoc is available
        try:
            pypandoc.get_pandoc_version()
        except OSError:
            logger.info("Pandoc not found on PATH; downloading bundled Pandoc...")
            pypandoc.download_pandoc()
        logger.info(
            "Initialized FileConversionAgent with pandoc at %s",
            pypandoc.get_pandoc_path(),
        )
        if not PDF2DOCX_AVAILABLE:
            logger.warning(
                "pdf2docx not installed; PDF→DOCX via pdf2docx will be unavailable"
            )

    def _parse_command(self, query: str) -> Tuple[str, str]:
        """
        Parse "Convert report.pdf to docx" → ("report.pdf","docx")
        """
        text = query.strip()
        if not text.lower().startswith("convert "):
            raise ValueError("Usage: Convert <filename> to <format>")
        rest = text[len("convert "):].strip()
        parts = rest.rsplit(" to ", 1)
        if len(parts) != 2:
            raise ValueError("Usage: Convert <filename> to <format>")
        src, dst_ext = parts[0].strip(), parts[1].strip().lower()
        return src, dst_ext

    def run(self, query: str) -> str:
        try:
            src, fmt = self._parse_command(query)
        except ValueError as e:
            return f"⚠️ {e}"

        if not os.path.exists(src):
            return f"⚠️ File not found: {src}"

        src_path = Path(src)
        base = src_path.with_suffix("")
        dst_path = base.with_suffix(f".{fmt}")

        src_ext = src_path.suffix.lstrip(".").lower()

        # 1) PDF → DOCX via pdf2docx
        if src_ext == "pdf" and fmt == "docx" and PDF2DOCX_AVAILABLE:
            logger.info("Converting PDF→DOCX: %s → %s", src, dst_path)
            cv = Converter(src)
            cv.convert(str(dst_path), start=0, end=None)
            cv.close()
            return f"✅ Converted '{src}' → '{dst_path}'"

        # 2) PDF → DOCX via PyPDF2 + python-docx
        if src_ext == "pdf" and fmt == "docx" and not PDF2DOCX_AVAILABLE:
            try:
                from PyPDF2 import PdfReader  # type: ignore
                from docx import Document     # type: ignore
            except ImportError:
                return (
                    "⚠️ Cannot convert PDF→DOCX: "
                    "install `pdf2docx` or `PyPDF2`+`python-docx`"
                )
            logger.info("Converting PDF→DOCX with PyPDF2+docx: %s → %s", src, dst_path)
            reader = PdfReader(str(src_path))
            doc = Document()
            for page in reader.pages:
                doc.add_paragraph(page.extract_text() or "")
            doc.save(str(dst_path))
            return f"✅ Converted '{src}' → '{dst_path}'"

        # 3) Pandoc-powered conversions for everything else
        logger.info("Attempting Pandoc conversion: %s → %s (to='%s')", src, dst_path, fmt)
        try:
            pypandoc.convert_file(src, to=fmt, outputfile=str(dst_path))
            return f"✅ Converted '{src}' → '{dst_path}'"
        except Exception as e:
            logger.exception("Pandoc conversion failed")
            return f"⚠️ Conversion failed: {e}"

    # Optional helpers if you need programmatic calls:

    def csv_to_xlsx(self, csv_path: str, output_path: str | None = None) -> str:
        import pandas as pd  # type: ignore
        csv_p = Path(csv_path)
        out = Path(output_path) if output_path else csv_p.with_suffix(".xlsx")
        df = pd.read_csv(csv_p)
        df.to_excel(out, index=False)
        logger.info("CSV→XLSX: %s → %s", csv_p, out)
        return str(out)

    def xlsx_to_csv(self, xlsx_path: str, output_path: str | None = None) -> str:
        import pandas as pd  # type: ignore
        xlsx_p = Path(xlsx_path)
        out = Path(output_path) if output_path else xlsx_p.with_suffix(".csv")
        df = pd.read_excel(xlsx_p)
        df.to_csv(out, index=False)
        logger.info("XLSX→CSV: %s → %s", xlsx_p, out)
        return str(out)

    def docx_to_pdf(self, docx_path: str, output_path: str | None = None) -> str:
        try:
            from docx2pdf import convert  # type: ignore
        except ImportError:
            raise RuntimeError("docx2pdf is required for DOCX→PDF conversion")
        docx_p = Path(docx_path)
        out = Path(output_path) if output_path else docx_p.with_suffix(".pdf")
        convert(str(docx_p), str(out))
        logger.info("DOCX→PDF: %s → %s", docx_p, out)
        return str(out)

    def audio_to_text(self, audio_path: str, output_path: str | None = None) -> str:
        """Transcribe an audio file (ogg/mp3/wav) to text using SpeechRecognition."""

        # 1) Ensure we have a wav file
        from pydub import AudioSegment  # type: ignore
        try:
            orig = Path(audio_path)
            wav_path = orig.with_suffix(".wav")
            AudioSegment.from_file(str(orig)).export(str(wav_path), format="wav")
            logger.info("Converted %s → %s for transcription", orig, wav_path)
        except Exception as e:
            logger.exception("Failed to convert to wav")
            return f"⚠️ Audio conversion error: {e}"

        # 2) Do the transcription
        import speech_recognition as sr  # type: ignore
        from speech_recognition import UnknownValueError

        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(str(wav_path)) as src:
                audio_data = recognizer.record(src)
            text = recognizer.recognize_google(audio_data)
        except UnknownValueError:
            logger.warning("Could not understand audio %s", wav_path)
            return "⚠️ Sorry, I couldn't understand the audio."
        except Exception as e:
            logger.exception("Transcription failed")
            return f"⚠️ Transcription error: {e}"

        # 3) Write out or return
        if output_path:
            Path(output_path).write_text(text, encoding="utf-8")
            logger.info("Wrote transcript to %s", output_path)
            return str(output_path)

        logger.info("Transcription complete for %s", wav_path)
        return text