import json
import zipfile
from pathlib import Path

import pytest

from nanobot.utils.knowledge import ingest_repository_knowledge


def _make_bot_scope(repo_root: Path, bot: str = "bot1_core") -> Path:
    raw = repo_root / bot / "workspace" / "knowledge" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    return raw


def _load_manifest(repo_root: Path, bot: str = "bot1_core") -> dict:
    manifest = repo_root / bot / "workspace" / "knowledge" / "index" / "manifest.json"
    return json.loads(manifest.read_text(encoding="utf-8"))


def test_ingest_plain_text_creates_manifest_catalog_and_extracted_cache(tmp_path: Path) -> None:
    raw = _make_bot_scope(tmp_path)
    (raw / "sleep-plan.txt").write_text("作息目标:23:30 前入睡。", encoding="utf-8")

    summaries = ingest_repository_knowledge(tmp_path, bots=["bot1_core"], include_shared=False)

    assert summaries[0].scope == "bot1_core"
    assert summaries[0].total == 1
    assert summaries[0].extracted == 1

    manifest = _load_manifest(tmp_path)
    assert manifest["stats"]["ready"] == 1
    assert manifest["documents"][0]["status"] == "ready"
    assert manifest["documents"][0]["extracted_path"] == "knowledge/extracted/sleep-plan.txt.md"

    extracted = tmp_path / "bot1_core" / "workspace" / "knowledge" / "extracted" / "sleep-plan.txt.md"
    assert extracted.exists()
    assert "作息目标" in extracted.read_text(encoding="utf-8")

    catalog = tmp_path / "bot1_core" / "workspace" / "knowledge" / "index" / "CATALOG.md"
    catalog_text = catalog.read_text(encoding="utf-8")
    assert "sleep-plan.txt" in catalog_text
    assert "knowledge/extracted/sleep-plan.txt.md" in catalog_text


def test_ingest_docx_uses_lightweight_zip_extractor(tmp_path: Path) -> None:
    raw = _make_bot_scope(tmp_path)
    docx_path = raw / "profile.docx"
    with zipfile.ZipFile(docx_path, "w") as archive:
        archive.writestr(
            "word/document.xml",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body><w:p><w:r><w:t>用户偏好:直接、务实。</w:t></w:r></w:p></w:body>"
                "</w:document>"
            ),
        )

    ingest_repository_knowledge(tmp_path, bots=["bot1_core"], include_shared=False)

    manifest = _load_manifest(tmp_path)
    assert manifest["documents"][0]["status"] == "ready"
    assert manifest["documents"][0]["extraction_engine"] == "docx-xml"

    extracted = tmp_path / "bot1_core" / "workspace" / "knowledge" / "extracted" / "profile.docx.md"
    assert "用户偏好:直接、务实。" in extracted.read_text(encoding="utf-8")


def test_ingest_epub_uses_lightweight_zip_extractor(tmp_path: Path) -> None:
    raw = _make_bot_scope(tmp_path)
    epub_path = raw / "guide.epub"
    with zipfile.ZipFile(epub_path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr(
            "META-INF/container.xml",
            (
                "<container version='1.0' "
                "xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>"
                "<rootfiles>"
                "<rootfile full-path='OEBPS/content.opf' media-type='application/oebps-package+xml'/>"
                "</rootfiles>"
                "</container>"
            ),
        )
        archive.writestr(
            "OEBPS/content.opf",
            (
                "<package xmlns='http://www.idpf.org/2007/opf' version='2.0'>"
                "<manifest><item id='chapter1' href='chapter1.xhtml' media-type='application/xhtml+xml'/></manifest>"
                "<spine><itemref idref='chapter1'/></spine>"
                "</package>"
            ),
        )
        archive.writestr(
            "OEBPS/chapter1.xhtml",
            "<html><body><h1>第一章</h1><p>这是一本测试电子书。</p></body></html>",
        )

    ingest_repository_knowledge(tmp_path, bots=["bot1_core"], include_shared=False)

    manifest = _load_manifest(tmp_path)
    assert manifest["documents"][0]["status"] == "ready"
    assert manifest["documents"][0]["extraction_engine"] == "epub-zip"

    extracted = tmp_path / "bot1_core" / "workspace" / "knowledge" / "extracted" / "guide.epub.md"
    content = extracted.read_text(encoding="utf-8")
    assert "第一章" in content
    assert "这是一本测试电子书。" in content


def test_ingest_pdf_without_available_extractor_stays_pending(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = _make_bot_scope(tmp_path)
    (raw / "report.pdf").write_bytes(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n")

    monkeypatch.setattr("nanobot.utils.knowledge._extract_pdf_text_with_pypdf", lambda path: None)
    monkeypatch.setattr("nanobot.utils.knowledge._extract_with_markitdown", lambda path: None)

    ingest_repository_knowledge(tmp_path, bots=["bot1_core"], include_shared=False)

    manifest = _load_manifest(tmp_path)
    document = manifest["documents"][0]
    assert document["status"] == "pending_extraction"
    assert document["recommended_skill"] == "pdf"
    assert document["extracted_path"] == ""


def test_ingest_repository_shared_only_scans_shared_without_bots(tmp_path: Path) -> None:
    raw = tmp_path / "shared" / "knowledge" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "shared-note.txt").write_text("共享知识:这是共享资料。", encoding="utf-8")

    summaries = ingest_repository_knowledge(tmp_path, bots=[], include_shared=True)

    assert len(summaries) == 1
    assert summaries[0].scope == "shared"
    assert summaries[0].total == 1

    manifest = json.loads(
        (tmp_path / "shared" / "knowledge" / "index" / "manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["scope"] == "shared"
    assert manifest["stats"]["ready"] == 1
