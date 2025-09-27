from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .normalize import normalize_code
from .similarity import pairwise_compare
from .types import Document


app = FastAPI(title="PlagDetect Web")


static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    idx = static_dir / "index.html"
    return idx.read_text(encoding="utf-8")


@app.post("/api/analyze")
async def analyze(
    files: List[UploadFile] = File(...),
    strip_comments: bool = Form(False),
    k_gram: int = Form(5),
    unit: str = Form("word"),
    winnow: bool = Form(True),
    window: int = Form(4),
    threshold: float = Form(0.5),
):
    documents: List[Document] = []
    for f in files:
        raw_bytes = await f.read()
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = raw_bytes.decode("latin-1", errors="ignore")
        normalized = normalize_code(text, path=None, strip_comments=strip_comments)
        documents.append(Document(doc_id=f.filename or "upload", path=Path(f.filename or "upload"), content=normalized))

    matches = pairwise_compare(
        documents,
        k_gram=k_gram,
        unit=unit,
        use_winnowing=winnow,
        window_size=window,
        threshold=threshold,
        num_workers=0,
    )
    return JSONResponse({"count": len(matches), "matches": matches})


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="plagdetect-web", description="Run PlagDetect web server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        import uvicorn  # type: ignore
    except Exception as exc:  # noqa: BLE001
        print("uvicorn is required to run the web server. Install with: pip install uvicorn[standard]", file=sys.stderr)
        return 1
    uvicorn.run("plagdetect.webapp:app", host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

