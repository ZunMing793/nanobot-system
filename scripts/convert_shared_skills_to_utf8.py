from __future__ import annotations

from pathlib import Path


TEXT_SUFFIXES = {".md", ".json", ".py", ".sh", ".txt", ".yaml", ".yml"}


def _looks_like_utf16(data: bytes) -> bool:
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return True
    sample = data[:200]
    return sample.count(0) > max(4, len(sample) // 4)


def _decode_best_effort(data: bytes) -> tuple[str, str]:
    for encoding in ("utf-8", "utf-8-sig"):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            pass

    if _looks_like_utf16(data):
        for encoding in ("utf-16", "utf-16-le", "utf-16-be"):
            try:
                return data.decode(encoding), encoding
            except UnicodeDecodeError:
                pass

    for encoding in ("gb18030", "cp1252", "latin1"):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            pass

    return data.decode("utf-8", errors="replace"), "utf-8-replace"


def convert_tree(root: Path) -> list[tuple[Path, str]]:
    converted: list[tuple[Path, str]] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue

        data = path.read_bytes()
        try:
            data.decode("utf-8")
            continue
        except UnicodeDecodeError:
            pass

        text, encoding = _decode_best_effort(data)
        path.write_text(text, encoding="utf-8", newline="\n")
        converted.append((path, encoding))
    return converted


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "shared" / "skills"
    converted = convert_tree(root)
    print(f"converted_count={len(converted)}")
    for path, encoding in converted[:50]:
        print(f"{path.relative_to(root)} <- {encoding}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
