#!/usr/bin/env python3
"""
Comprehensive license checker for ALL Python packages
Outputs complete dependency tree with licenses to CSV
"""

import pkg_resources
import requests
import json
import csv
import subprocess
import sys
from datetime import datetime


def get_all_installed_packages():
    """Get all installed packages in the current environment"""
    try:
        # Use pip list to get all installed packages
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
        )
        packages = json.loads(result.stdout)
        return [pkg["name"] for pkg in packages]
    except Exception as e:
        print(f"Error getting installed packages: {e}")
        # Fallback to pkg_resources
        return [pkg.project_name for pkg in pkg_resources.working_set]


def get_package_license(package_name, version=None):
    """Get license information for a package from PyPI"""
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            info = data.get("info", {})
            license_info = info.get("license", "Unknown")
            classifiers = info.get("classifiers", [])

            # Extract license from classifiers
            license_classifiers = [c for c in classifiers if c.startswith("License ::")]

            return {
                "package": package_name,
                "version": info.get("version", "Unknown"),
                "license": license_info,
                "license_classifiers": license_classifiers,
                "home_page": info.get("home_page", ""),
            }
    except Exception as e:
        return {"package": package_name, "error": str(e)}


def write_licenses_to_csv(license_data, filename="all_package_licenses.csv"):
    """Write license information to CSV file"""
    fieldnames = [
        "package_name",
        "version",
        "license",
        "license_classifiers",
        "home_page",
        "is_problematic",
        "risk_level",
        "notes",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for data in license_data:
            if "error" in data:
                writer.writerow(
                    {
                        "package_name": data["package"],
                        "version": "Unknown",
                        "license": f"ERROR: {data['error']}",
                        "license_classifiers": "",
                        "home_page": "",
                        "is_problematic": "Unknown",
                        "risk_level": "Unknown",
                        "notes": "Failed to retrieve license info",
                    }
                )
            else:
                license_text = (data["license"] or "").lower()
                classifiers_text = " ".join(data["license_classifiers"]).lower()

                # Enhanced problematic license detection
                is_problematic = any(
                    term in license_text + classifiers_text
                    for term in ["gpl", "agpl", "copyleft", "cddl", "mpl"]
                )

                # Risk assessment
                risk_level = (
                    "HIGH"
                    if any(
                        term in license_text + classifiers_text
                        for term in ["agpl", "gpl v3", "gplv3"]
                    )
                    else (
                        "MEDIUM"
                        if any(
                            term in license_text + classifiers_text
                            for term in ["gpl", "lgpl", "mpl", "cddl"]
                        )
                        else "LOW"
                    )
                )

                # Generate notes
                notes = []
                if "mit" in license_text + classifiers_text:
                    notes.append("Commercial-friendly")
                if "bsd" in license_text + classifiers_text:
                    notes.append("Commercial-friendly")
                if "apache" in license_text + classifiers_text:
                    notes.append("Commercial-friendly")
                if "agpl" in license_text + classifiers_text:
                    notes.append("AVOID: Viral copyleft license")
                if (
                    "gpl" in license_text + classifiers_text
                    and "agpl" not in license_text + classifiers_text
                ):
                    notes.append("CAUTION: Copyleft license")

                writer.writerow(
                    {
                        "package_name": data["package"],
                        "version": data["version"],
                        "license": data["license"] or "Unknown",
                        "license_classifiers": "; ".join(data["license_classifiers"]),
                        "home_page": data["home_page"],
                        "is_problematic": "Yes" if is_problematic else "No",
                        "risk_level": risk_level,
                        "notes": "; ".join(notes) if notes else "Review manually",
                    }
                )


def main():
    print("🔍 Comprehensive License Analysis - ALL Dependencies")
    print("=" * 60)

    # Get all installed packages
    print("📦 Discovering all installed packages...")
    all_packages = get_all_installed_packages()
    print(f"Found {len(all_packages)} installed packages")

    license_data = []
    problematic_packages = []

    print("\n🔎 Analyzing licenses (this may take a while)...")

    for i, package in enumerate(all_packages, 1):
        print(f"[{i}/{len(all_packages)}] Checking {package}...", end=" ")

        info = get_package_license(package)
        license_data.append(info)

        if "error" in info:
            print(f"❌ Error")
            continue

        license_text = (info["license"] or "").lower()
        classifiers = " ".join(info["license_classifiers"]).lower()

        # Check for potentially problematic licenses
        is_problematic = any(
            term in license_text + classifiers
            for term in ["gpl", "agpl", "copyleft", "cddl", "mpl"]
        )

        if is_problematic:
            problematic_packages.append(info)
            print(f"⚠️ {info['license']}")
        else:
            print("✅")

    # Write to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"all_package_licenses_{timestamp}.csv"

    print(f"\n💾 Writing results to {csv_filename}...")
    write_licenses_to_csv(license_data, csv_filename)

    # Summary
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY:")
    print(f"   Total packages analyzed: {len(all_packages)}")
    print(f"   Problematic licenses found: {len(problematic_packages)}")
    print(f"   CSV report saved as: {csv_filename}")

    if problematic_packages:
        print(f"\n⚠️  PACKAGES REQUIRING ATTENTION:")
        for pkg in problematic_packages[:10]:  # Show first 10
            print(f"   • {pkg['package']}: {pkg['license']}")
        if len(problematic_packages) > 10:
            print(
                f"   ... and {len(problematic_packages) - 10} more (see CSV for complete list)"
            )
    else:
        print("\n✅ No obviously problematic licenses detected!")

    print(f"\n📋 RECOMMENDATIONS:")
    print(f"1. Review the complete CSV report: {csv_filename}")
    print(f"2. Pay special attention to packages marked as 'HIGH' or 'MEDIUM' risk")
    print(f"3. Consider legal review for commercial deployment")
    print(f"4. Replace any GPL/AGPL packages with commercial-friendly alternatives")


if __name__ == "__main__":
    main()
