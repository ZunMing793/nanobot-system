"""Lightweight knowledge base indexing and extraction helpers."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree as ET


BOT_NAMES = ("bot1_core", "bot2_health", "bot3_finance", "bot4_emotion", "bot5_media")
TEXT_EXTENSIONS = {
    ".csv",
    ".json",
    ".markdown",
    ".md",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
HTML_EXTENSIONS = {".htm", ".html", ".xhtml"}
SKILL_BY_EXTENSION = {
    ".docx": "docx",
    ".epub": "summarize",
    ".htm": "web",
    ".html": "web",
    ".pdf": "pdf",
    ".pptx": "pptx",
    ".xlsx": "xlsx",
}


@dataclass(frozen=True)
class KnowledgeScope:
    """A single knowledge base scope."""

    name: str
    scope_type: str
    base_path: Path
    knowledge_path: Path
    raw_path: Path
    extracted_path: Path
    index_path: Path


@dataclass(frozen=True)
class ScopeSummary:
    """Summary for one ingested scope."""

    scope: str
    scope_type: str
    total: int
    extracted: int
    pending: int
    indexed_only: int
    failed: int


class _HTMLTextExtractor(HTMLParser):
    """Very small HTML to text converter."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in {"script", "style"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in {"br", "li"}:
            self._parts.append("\n")
        elif tag in {"article", "div", "h1", "h2", "h3", "h4", "h5", "h6", "p", "section"}:
            self._parts.append("\n\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if data.strip():
            self._parts.append(data)

    def text(self) -> str:
        joined = "".join(self._parts)
        joined = re.sub(r"\n{3,}", "\n\n", joined)
        return re.sub(r"[ \t]+", " ", joined).strip()


def now_iso() -> str:
    """Return current local time in a readable format."""
    from nanobot.utils.timezone import now

    return now().strftime("%Y-%m-%d %H:%M:%S")


def discover_knowledge_scopes(
    repo_root: Path,
    *,
    bots: list[str] | None = None,
    include_shared: bool = True,
) -> list[KnowledgeScope]:
    """Discover all available knowledge scopes in the repository."""
    selected_bots = list(BOT_NAMES) if bots is None else list(bots)
    scopes: list[KnowledgeScope] = []

    if include_shared:
        shared_base = repo_root / "shared"
        knowledge_path = shared_base / "knowledge"
        scopes.append(
            KnowledgeScope(
                name="shared",
                scope_type="shared",
                base_path=shared_base,
                knowledge_path=knowledge_path,
                raw_path=knowledge_path / "raw",
                extracted_path=knowledge_path / "extracted",
                index_path=knowledge_path / "index",
            )
        )

    for bot in selected_bots:
        base_path = repo_root / bot / "workspace"
        knowledge_path = base_path / "knowledge"
        scopes.append(
            KnowledgeScope(
                name=bot,
                scope_type="bot",
                base_path=base_path,
                knowledge_path=knowledge_path,
                raw_path=knowledge_path / "raw",
                extracted_path=knowledge_path / "extracted",
                index_path=knowledge_path / "index",
            )
        )

    return scopes


def ingest_repository_knowledge(
    repo_root: Path,
    *,
    bots: list[str] | None = None,
    include_shared: bool = True,
    force: bool = False,
) -> list[ScopeSummary]:
    """Scan and ingest knowledge documents for all matching scopes."""
    summaries: list[ScopeSummary] = []
    for scope in discover_knowledge_scopes(repo_root, bots=bots, include_shared=include_shared):
        summaries.append(ingest_scope(scope, force=force))
    return summaries


def ingest_scope(scope: KnowledgeScope, *, force: bool = False) -> ScopeSummary:
    """Scan one scope, update its manifest and catalog, and extract text when possible."""
    scope.raw_path.mkdir(parents=True, exist_ok=True)
    scope.extracted_path.mkdir(parents=True, exist_ok=True)
    scope.index_path.mkdir(parents=True, exist_ok=True)

    manifest_path = scope.index_path / "manifest.json"
    previous_documents = _load_previous_manifest(manifest_path)
    previous_by_source = {
        doc.get("source_path"): doc
        for doc in previous_documents
        if isinstance(doc, dict) and doc.get("source_path")
    }

    documents: list[dict[str, Any]] = []
    counts = {"ready": 0, "pending_extraction": 0, "indexed_only": 0, "error": 0}

    for source_path in _iter_source_files(scope.raw_path):
        source_rel = _to_posix(source_path.relative_to(scope.base_path))
        extracted_rel = _build_extracted_relpath(scope, source_path)
        extracted_path = scope.base_path / extracted_rel
        sha256 = _sha256_file(source_path)
        previous = previous_by_source.get(source_rel)
        recommended_skill = SKILL_BY_EXTENSION.get(source_path.suffix.lower(), "")

        if (
            not force
            and previous
            and previous.get("sha256") == sha256
            and (
                previous.get("status") != "ready"
                or (previous.get("extracted_path") and (scope.base_path / previous["extracted_path"]).exists())
            )
        ):
            entry = dict(previous)
            entry.update(
                {
                    "recommended_skill": recommended_skill,
                    "modified_at": _mtime(source_path),
                    "size_bytes": source_path.stat().st_size,
                }
            )
        else:
            text, engine, error = extract_text_from_source(source_path)
            title = _derive_title(source_path)
            summary = _make_summary(text or "")

            if text:
                extracted_path.parent.mkdir(parents=True, exist_ok=True)
                extracted_path.write_text(
                    _render_extracted_markdown(
                        title=title,
                        source_path=source_rel,
                        extracted_at=now_iso(),
                        engine=engine or "unknown",
                        text=text,
                    ),
                    encoding="utf-8",
                )
                status = "ready"
                needs_extraction = False
            else:
                status = "error" if error and _looks_extractable(source_path) else _classify_pending_status(source_path)
                needs_extraction = status == "pending_extraction"
                extracted_rel = ""

            entry = {
                "id": sha256[:12],
                "title": title,
                "source_path": source_rel,
                "source_name": source_path.name,
                "scope": scope.name,
                "scope_type": scope.scope_type,
                "file_type": source_path.suffix.lower().lstrip(".") or "unknown",
                "size_bytes": source_path.stat().st_size,
                "modified_at": _mtime(source_path),
                "sha256": sha256,
                "status": status,
                "needs_extraction": needs_extraction,
                "recommended_skill": recommended_skill,
                "extracted_path": extracted_rel,
                "summary": summary,
                "tags": _build_tags(scope, source_path),
                "extraction_engine": engine or "",
                "error": error or "",
            }

        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
        documents.append(entry)

    documents.sort(key=lambda item: item["source_path"])
    manifest = {
        "version": 2,
        "scope": scope.name,
        "scope_type": scope.scope_type,
        "updated_at": now_iso(),
        "stats": {
            "total": len(documents),
            "ready": counts["ready"],
            "pending_extraction": counts["pending_extraction"],
            "indexed_only": counts["indexed_only"],
            "error": counts["error"],
        },
        "documents": documents,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    catalog_path = scope.index_path / "CATALOG.md"
    catalog_path.write_text(_render_catalog(scope, manifest), encoding="utf-8")

    return ScopeSummary(
        scope=scope.name,
        scope_type=scope.scope_type,
        total=len(documents),
        extracted=counts["ready"],
        pending=counts["pending_extraction"],
        indexed_only=counts["indexed_only"],
        failed=counts["error"],
    )


def extract_text_from_source(source_path: Path) -> tuple[str | None, str | None, str | None]:
    """Best-effort extraction with lightweight local parsers first."""
    suffix = source_path.suffix.lower()

    try:
        if suffix in TEXT_EXTENSIONS:
            return _read_text_file(source_path), "text", None
        if suffix in HTML_EXTENSIONS:
            return _extract_html_file(source_path), "html", None
        if suffix == ".docx":
            return _extract_docx_text(source_path), "docx-xml", None
        if suffix == ".epub":
            return _extract_epub_text(source_path), "epub-zip", None
        if suffix == ".pdf":
            pdf_text = _extract_pdf_text_with_pypdf(source_path)
            if pdf_text:
                return pdf_text, "pypdf", None
    except Exception as exc:
        return None, None, str(exc)

    markitdown_text = _extract_with_markitdown(source_path)
    if markitdown_text:
        return markitdown_text, "markitdown", None

    return None, None, None


def build_arg_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(description="Ingest workspace/shared knowledge bases.")
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to script parent.")
    parser.add_argument("--bot", action="append", choices=BOT_NAMES, help="Only ingest selected bot.")
    parser.add_argument("--shared-only", action="store_true", help="Only ingest shared knowledge.")
    parser.add_argument("--force", action="store_true", help="Re-extract even if hash is unchanged.")
    return parser


def _load_previous_manifest(manifest_path: Path) -> list[dict[str, Any]]:
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    documents = data.get("documents", [])
    return documents if isinstance(documents, list) else []


def _iter_source_files(raw_path: Path) -> list[Path]:
    files: list[Path] = []
    for path in raw_path.rglob("*"):
        if not path.is_file():
            continue
        if path.relative_to(raw_path).as_posix() == "README.md":
            continue
        if any(part.startswith(".") for part in path.relative_to(raw_path).parts):
            continue
        files.append(path)
    return sorted(files)


def _read_text_file(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return raw.decode(encoding).strip()
        except UnicodeDecodeError:
            continue

    try:
        import chardet

        detected = chardet.detect(raw).get("encoding")
        if detected:
            return raw.decode(detected, errors="replace").strip()
    except Exception:
        pass

    return raw.decode("utf-8", errors="replace").strip()


def _extract_html_file(path: Path) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(_read_text_file(path))
    return parser.text()


def _extract_docx_text(path: Path) -> str:
    xml_members: list[str] = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if name == "word/document.xml" or (
                name.startswith("word/") and name.endswith(".xml") and ("header" in name or "footer" in name)
            ):
                xml_members.append(name)

        blocks: list[str] = []
        for member in sorted(xml_members):
            root = ET.fromstring(archive.read(member))
            for paragraph in root.findall(".//{*}p"):
                texts = [node.text or "" for node in paragraph.findall(".//{*}t")]
                line = "".join(texts).strip()
                if line:
                    blocks.append(line)

    return "\n\n".join(blocks).strip()


def _extract_epub_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        container = ET.fromstring(archive.read("META-INF/container.xml"))
        rootfile = container.find(".//{*}rootfile")
        if rootfile is None or not rootfile.get("full-path"):
            return ""

        opf_rel = PurePosixPath(rootfile.get("full-path", ""))
        package = ET.fromstring(archive.read(opf_rel.as_posix()))
        manifest = {
            item.get("id"): item.get("href", "")
            for item in package.findall(".//{*}manifest/{*}item")
            if item.get("id")
        }
        spine = [item.get("idref", "") for item in package.findall(".//{*}spine/{*}itemref")]
        opf_dir = opf_rel.parent

        pages: list[str] = []
        ordered_items = [manifest[item_id] for item_id in spine if item_id in manifest]
        if not ordered_items:
            ordered_items = [href for href in manifest.values() if href.lower().endswith(tuple(HTML_EXTENSIONS))]

        for href in ordered_items:
            member = (opf_dir / PurePosixPath(href)).as_posix()
            if member not in archive.namelist():
                continue
            parser = _HTMLTextExtractor()
            parser.feed(_read_archive_text(archive, member))
            text = parser.text()
            if text:
                pages.append(text)

    return "\n\n".join(pages).strip()


def _read_archive_text(archive: zipfile.ZipFile, member: str) -> str:
    raw = archive.read(member)
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return raw.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace").strip()


def _extract_pdf_text_with_pypdf(path: Path) -> str | None:
    try:
        from pypdf import PdfReader
    except Exception:
        return None

    try:
        reader = PdfReader(str(path))
        parts = [(page.extract_text() or "").strip() for page in reader.pages]
    except Exception:
        return None

    text = "\n\n".join(part for part in parts if part)
    return text.strip() or None


def _extract_with_markitdown(path: Path) -> str | None:
    try:
        from markitdown import MarkItDown
    except Exception:
        return None

    try:
        result = MarkItDown(enable_plugins=False).convert(str(path))
    except Exception:
        return None

    text = getattr(result, "text_content", "") or ""
    return text.strip() or None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def _to_posix(path: Path) -> str:
    return path.as_posix()


def _derive_title(path: Path) -> str:
    title = path.stem.replace("_", " ").replace("-", " ").strip()
    return title or path.name


def _make_summary(text: str, max_chars: int = 120) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return ""
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 1].rstrip() + "…"


def _classify_pending_status(path: Path) -> str:
    if path.suffix.lower() in {".docx", ".epub", ".pdf", ".pptx", ".xlsx"}:
        return "pending_extraction"
    return "indexed_only"


def _looks_extractable(path: Path) -> bool:
    return path.suffix.lower() in {".docx", ".epub", ".pdf"} | TEXT_EXTENSIONS | HTML_EXTENSIONS


def _build_tags(scope: KnowledgeScope, source_path: Path) -> list[str]:
    tags = [scope.name, source_path.suffix.lower().lstrip(".") or "unknown"]
    tags.append("private" if scope.scope_type == "bot" else "shared")
    return tags


def _build_extracted_relpath(scope: KnowledgeScope, source_path: Path) -> str:
    relative = source_path.relative_to(scope.raw_path)
    return _to_posix(Path("knowledge") / "extracted" / relative.parent / f"{relative.name}.md")


def _render_extracted_markdown(
    *,
    title: str,
    source_path: str,
    extracted_at: str,
    engine: str,
    text: str,
) -> str:
    return (
        f"# {title}\n\n"
        f"- 来源文件:`{source_path}`\n"
        f"- 提取时间:`{extracted_at}`\n"
        f"- 提取方式:`{engine}`\n\n"
        "---\n\n"
        f"{text.strip()}\n"
    )


def _render_catalog(scope: KnowledgeScope, manifest: dict[str, Any]) -> str:
    stats = manifest.get("stats", {})
    documents = manifest.get("documents", [])
    lines = [
        "# Knowledge Catalog",
        "",
        "> 自动生成:先看这里的概览,再决定是否继续读取原文或提取文本。",
        "",
        f"- 范围:`{scope.name}`",
        f"- 更新时间:`{manifest.get('updated_at', '')}`",
        (
            "- 统计:"
            f"共 `{stats.get('total', 0)}` 份,"
            f"已提取 `{stats.get('ready', 0)}`,"
            f"待提取 `{stats.get('pending_extraction', 0)}`,"
            f"仅索引 `{stats.get('indexed_only', 0)}`,"
            f"失败 `{stats.get('error', 0)}`"
        ),
        "",
        "| 文件 | 类型 | 状态 | 提取文本 | 推荐技能 | 摘要 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    if not documents:
        lines.append("| — | — | 空 | — | — | 当前还没有已登记资料 |")
    else:
        for doc in documents:
            source_name = _escape_table(doc.get("source_name", ""))
            file_type = _escape_table(doc.get("file_type", ""))
            status = _escape_table(_status_label(doc.get("status", "")))
            extracted_path = _escape_table(doc.get("extracted_path") or "—")
            skill = _escape_table(doc.get("recommended_skill") or "—")
            summary = _escape_table(doc.get("summary") or "—")
            lines.append(
                f"| `{source_name}` | `{file_type}` | {status} | `{extracted_path}` | `{skill}` | {summary} |"
            )

    lines.append("")
    return "\n".join(lines)


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _status_label(status: str) -> str:
    return {
        "error": "提取失败",
        "indexed_only": "仅索引",
        "pending_extraction": "待提取",
        "ready": "已提取",
    }.get(status, status or "未知")
