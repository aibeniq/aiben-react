#!/usr/bin/env python3
"""
Simplified license checker - displays results in a clean format
"""

# Key packages and their known licenses (manually researched)
packages_licenses = {
    "fastapi": {"license": "MIT", "status": "✅", "commercial": "Safe"},
    "langchain-community": {"license": "MIT", "status": "✅", "commercial": "Safe"},
    "langchain-openai": {"license": "MIT", "status": "✅", "commercial": "Safe"},
    "chromadb": {
        "license": "Apache 2.0",
        "status": "✅",
        "commercial": "Safe with attribution",
    },
    "openai": {"license": "Apache 2.0", "status": "✅", "commercial": "Safe"},
    "pymupdf": {
        "license": "AGPL 3.0",
        "status": "⚠️",
        "commercial": "Requires commercial license",
    },
    "pypdf": {"license": "BSD", "status": "✅", "commercial": "Safe"},
    "replicate": {"license": "Apache 2.0", "status": "✅", "commercial": "Safe"},
    "python-docx": {"license": "MIT", "status": "✅", "commercial": "Safe"},
    "langchain-aws": {"license": "MIT", "status": "✅", "commercial": "Safe"},
    "tiktoken": {"license": "MIT", "status": "✅", "commercial": "Safe"},
    "beautifulsoup4": {"license": "MIT", "status": "✅", "commercial": "Safe"},
    "markdown": {"license": "BSD", "status": "✅", "commercial": "Safe"},
    "rank_bm25": {"license": "Apache 2.0", "status": "✅", "commercial": "Safe"},
    "sqlmodel": {"license": "MIT", "status": "✅", "commercial": "Safe"},
    "pydantic": {"license": "MIT", "status": "✅", "commercial": "Safe"},
    "psycopg": {"license": "BSD", "status": "✅", "commercial": "Safe"},
}

print("🔍 LICENSE ANALYSIS FOR YOUR AI APPLICATION")
print("=" * 60)
print()

problematic = []
safe_count = 0

for package, info in packages_licenses.items():
    print(
        f"{info['status']} {package:<20} | {info['license']:<12} | {info['commercial']}"
    )
    if info["status"] == "⚠️":
        problematic.append(package)
    else:
        safe_count += 1

print()
print("=" * 60)
print(f"✅ SAFE PACKAGES: {safe_count}")
print(f"⚠️  PROBLEMATIC PACKAGES: {len(problematic)}")

if problematic:
    print()
    print("🚨 PACKAGES REQUIRING ATTENTION:")
    for pkg in problematic:
        info = packages_licenses[pkg]
        print(f"   • {pkg}: {info['license']} - {info['commercial']}")

print()
print("📋 KEY RECOMMENDATIONS:")
print()
print("1. 🔴 PyMuPDF Issue:")
print("   - Uses AGPL 3.0 (copyleft license)")
print("   - For commercial use, consider switching to 'pypdf' (BSD license)")
print("   - Or purchase a commercial PyMuPDF license")
print()
print("2. ✅ Good News:")
print("   - Most packages use MIT/Apache/BSD licenses")
print("   - These are very commercial-friendly")
print()
print("3. 📄 Apache 2.0 Requirements:")
print("   - Include license notice and attribution")
print("   - Document any modifications to Apache-licensed code")
print()
print("4. 🔧 Recommended Action for PyMuPDF:")
print("   - Replace with pypdf for PDF processing")
print("   - Or evaluate if you really need PyMuPDF's advanced features")

print()
print("✅ OVERALL: Your application is mostly commercial-friendly!")
print("   Just address the PyMuPDF licensing concern.")
