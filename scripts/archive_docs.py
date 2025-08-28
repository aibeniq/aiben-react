"""Archive historical markdown files into docs/archive/.

Rules:
 - Uses a curated list of known historical / point-in-time files (implementation notes, fixes, summaries)
 - Skips core maintained docs (root README, LICENSE, docs/*)
 - Moves files, adds front-matter style header, updates docs/archive/INDEX.md
"""

from __future__ import annotations

import shutil
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
ARCHIVE_DIR = DOCS_DIR / "archive"
INDEX_FILE = ARCHIVE_DIR / "INDEX.md"

CORE_KEEP = {
    "README.md",
    "LICENSE",
}

# Curated list (filenames only) gathered earlier
CANDIDATES = {
    "CURRENT_ANSWER_ENHANCEMENT.md",
    "CUSTOM_INSTRUCTIONS_IMPLEMENTATION.md",
    "CUSTOM_INSTRUCTIONS_FIX.md",
    "CUSTOM_INSTRUCTIONS_FEATURE.md",
    "CSV_DOWNLOAD_IMPLEMENTATION.md",
    "CONSULT_DOCUMENTS_IMPLEMENTATION.md",
    "CITATION_TRUNCATION_FIX.md",
    "CITATION_READ_MORE_IMPLEMENTATION.md",
    "CITATION_READ_MORE_BUGFIX.md",
    "CHUNK_ANALYSES_KEYERROR_FIX.md",
    "CHECKLIST_OPTIMIZATION.md",
    "VERADOC_CSV_IMPLEMENTATION.md",
    "TEST_GENERATE_OUTLINE.md",
    "TESTING_PERSISTENT_RESULTS.md",
    "TECHNICAL_REQUIREMENTS.md",
    "TECHNICAL_DESCRIPTION.md",
    "SIMPLIFIED_JSON_MAPPING.md",
    "SERVICE_SELECTOR_MISMATCH_FIX.md",
    "SEQUENTIAL_MAPPING_IMPLEMENTATION.md",
    "backend/TWINCHECK_CHUNKING.md",
    "backend/Replicate Readme.md",
    "backend/ENHANCED_RETRY_SUMMARY.md",
    "REPORTGENIE_KEYERROR_FIX.md",
    "REPORTGENIE_FIX_SUMMARY.md",
    "REPORTGENIE_FIX_COMPLETED.md",
    "REPORTGENIE_ALL_FIXES_COMPLETED.md",
    "release-notes.md",
    "REDIS_SESSION_IMPLEMENTATION.md",
    "PERSISTENT_RESULTS_TROUBLESHOOTING.md",
    "PERSISTENT_RESULTS_IMPLEMENTATION.md",
    "PDF_FILENAME_VIEWING_IMPLEMENTATION.md",
    "OPTIMIZE_OUTLINE_VERADOC_PATTERN_FIX.md",
    "OPTIMIZE_OUTLINE_VALIDATION_FIX.md",
    "OPTIMIZE_OUTLINE_SKIP_NON_CONSULT.md",
    "OPTIMIZE_OUTLINE_IMPLEMENTATION.md",
    "OPTIMIZE_OUTLINE_FIX.md",
    "OPTIMIZE_OUTLINE_EXCLUDE_NON_CONSULT.md",
    "OPTIMIZE_OUTLINE_EDITABLE_UI.md",
    "OPTIMIZE_OUTLINE_CONTENT_DISPLAY_ENHANCEMENT.md",
    "OPTIMIZE_OUTLINE_CONSULT_DOCUMENTS.md",
    "OPTIMIZE_OUTLINE_422_FIX.md",
    "OPTIMIZATION_FIX.md",
    "OPENAI_ONLY_DEPLOYMENT_SUMMARY.md",
    "MULTIPLE_DOCUMENT_CHATBOT.md",
    "MAPPING_PROMPT_UPDATE.md",
    "MANUAL_PREREQUISITES.md",
    "MANUAL_EDITING_OPTIMIZATION.md",
    "JSON_PARSING_FIX.md",
    "ISSUE_RESOLUTION_SUMMARY.md",
    "IMPLEMENTATION_COMPLETE.md",
    "HANDWRITTEN_TOGGLE_FIX.md",
    "GENERATE_OUTLINE_COMPLETE.md",
    "FRONTEND_IMPLEMENTATION_COMPLETE.md",
    "FORM_FIELDS_404_FIX.md",
    "FORMCONNECT_METADATA_IMPLEMENTATION.md",
    "FORMCONNECT_FILENAME_DISPLAY_ENHANCEMENT.md",
    "FORMCONNECT_ARCHIVE_HISTORY_ENHANCEMENT.md",
    "FORMCONNECT_ARCHIVE_BUG_FIX_COMPLETE.md",
    "FINAL_STATUS_REPORT.md",
    "FEEDBACK_IMPLEMENTATION_SUMMARY.md",
    "FEEDBACK_DEBUG_GUIDE.md",
    "ENTERPRISE_SCALING_READINESS_ASSESSMENT.md",
    "ENHANCED_SEQUENTIAL_MAPPING.md",
    "ENHANCED_CONTENT_EXTRACTION.md",
    "EMBEDDING_TOKEN_LIMIT_FIX.md",
    "DOCX_CSV_DOWNLOAD_FIX_SUMMARY.md",
    "DOCX_CITATION_VIEWING_IMPLEMENTATION.md",
    "DOCUMENT_SECTION_MAPPING_FIX.md",
    "ARCHIVE_INTERNAL_SERVER_ERROR_FIX.md",
    # De-duplicate per-component READMEs now consolidated
    "backend/README.md",
    "frontend/README.md",
}


def collect_existing_candidate_paths() -> list[Path]:
    paths: list[Path] = []
    for rel in CANDIDATES:
        p = REPO_ROOT / rel
        if p.exists() and p.is_file():
            paths.append(p)
    return paths


def to_archive_name(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT).as_posix()
    # Flatten subdirs into filename-safe token
    if "/" in rel:
        return rel.replace("/", "__")
    return rel


def archive_file(src: Path) -> Path:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    new_name = to_archive_name(src)
    dest = ARCHIVE_DIR / new_name
    content = src.read_text(encoding="utf-8", errors="ignore")
    header = (
        f"<!-- Archived: original path={src.relative_to(REPO_ROOT)}; archived_at={datetime.utcnow().isoformat()}Z -->\n"
        "<!-- This file is retained for historical reference. See docs/changelog.md for current state. -->\n\n"
    )
    dest.write_text(header + content, encoding="utf-8")
    src.unlink()
    return dest


def regenerate_index(archived: list[Path]):
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Archive Index\n",
        "\n",
        "Historical / point-in-time notes.\n",
        "\n",
        "| File | Original Name |",
        "|------|---------------|",
    ]
    for p in sorted(archived, key=lambda x: x.name.lower()):
        display = p.name
        # Attempt to reconstruct original if flattened
        original = display.replace("__", "/")
        lines.append(f"| [{display}](./{display}) | `{original}` |")
    INDEX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    candidates = collect_existing_candidate_paths()
    if not candidates:
        print("No candidate files found to archive.")
        return
    archived_paths = []
    for p in candidates:
        archived_paths.append(archive_file(p))
    regenerate_index(archived_paths)
    print(f"Archived {len(archived_paths)} files -> {ARCHIVE_DIR}")


if __name__ == "__main__":
    main()
