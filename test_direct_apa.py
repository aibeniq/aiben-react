#!/usr/bin/env python3
"""
Direct test of the APA demographic table extraction to validate the vision prompt fix.
"""

import requests
import json


def test_current_extraction():
    """Test the current system by asking about the demographic table directly"""

    print("=" * 60)
    print("TESTING CURRENT APA DEMOGRAPHIC TABLE EXTRACTION")
    print("=" * 60)

    # Test with a question that should trigger table processing
    url = "http://localhost:8000/api/v1/chat/document"

    test_questions = [
        "How many participants are in the High School/Some College education category?",
        "What are the exact numbers for Female participants in each treatment group?",
        "Show me all the demographic data from the baseline characteristics table.",
        "Extract all the numbers from the sociodemographic table.",
    ]

    for i, question in enumerate(test_questions):
        print(f"\n--- TEST {i+1}: {question} ---")

        try:
            params = {
                "question": question,
                "chat_history": f"User: {question}",
                "use_default_models": "true",
                "session_id": "",
                "is_follow_up": "false",
                "search_mode": "vector",
            }

            response = requests.post(url, params=params, timeout=60)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "No answer field")
                sources = result.get("sources", [])

                print(f"Answer: {answer}")
                print(f"Sources: {len(sources)} items")

                # Look for specific numbers that should be extracted
                expected_numbers = ["25", "20", "23", "68", "50", "40", "46", "45"]
                found_numbers = []

                for num in expected_numbers:
                    if num in answer:
                        found_numbers.append(num)

                print(f"Expected numbers found: {found_numbers}")
                print(
                    f"Coverage: {len(found_numbers)}/{len(expected_numbers)} = {len(found_numbers)/len(expected_numbers)*100:.1f}%"
                )

                # Check if the response mentions multi-column structure
                structure_keywords = [
                    "treatment group",
                    "guided self-help",
                    "unguided self-help",
                    "wait-list control",
                    "full sample",
                ]
                structure_found = sum(
                    1
                    for keyword in structure_keywords
                    if keyword.lower() in answer.lower()
                )

                print(
                    f"Structure keywords found: {structure_found}/{len(structure_keywords)}"
                )

                if structure_found >= 2 and len(found_numbers) >= 4:
                    print(
                        "✅ GOOD: Response shows understanding of multi-column structure"
                    )
                elif len(found_numbers) >= 2:
                    print("⚠️ PARTIAL: Some numbers found but structure unclear")
                else:
                    print("❌ POOR: Missing key demographic data")

            elif response.status_code == 401:
                print("❌ Authentication required - testing with curl")

                # Try direct request to see backend logs
                import subprocess

                result = subprocess.run(
                    [
                        "curl",
                        "-X",
                        "POST",
                        f"{url}?{requests.packages.urllib3.util.parse.urlencode(params)}",
                        "-H",
                        "Accept: application/json",
                    ],
                    capture_output=True,
                    text=True,
                    shell=True,
                )

                print(f"Curl result: {result.returncode}")
                if result.stdout:
                    print(f"Stdout: {result.stdout[:200]}...")
                if result.stderr:
                    print(f"Stderr: {result.stderr[:200]}...")
            else:
                print(f"❌ Error: {response.status_code} - {response.text[:200]}...")

        except Exception as e:
            print(f"❌ Request failed: {e}")

        print("-" * 40)


def analyze_backend_logs():
    """Check backend logs for vision processing details"""
    print("\n" + "=" * 60)
    print("ANALYZING BACKEND LOGS FOR VISION PROCESSING")
    print("=" * 60)

    try:
        import subprocess

        result = subprocess.run(
            ["docker-compose", "logs", "backend", "--tail=50"],
            capture_output=True,
            text=True,
            shell=True,
        )

        if result.returncode == 0:
            logs = result.stdout

            # Look for vision processing indicators
            vision_indicators = [
                "Processing",
                "table pages",
                "extracted",
                "vision",
                "JSON",
                "batch",
                "Female",
                "Male",
                "25",
                "68",
            ]

            relevant_lines = []
            for line in logs.split("\n"):
                if any(indicator in line for indicator in vision_indicators):
                    relevant_lines.append(line.strip())

            print(f"Found {len(relevant_lines)} relevant log lines:")
            for line in relevant_lines[-10:]:  # Show last 10 relevant lines
                print(f"  {line}")

            # Check for specific error patterns
            if "TypeError" in logs:
                print("⚠️ TypeError found in logs - may indicate processing issues")
            if "JSON" in logs and "extracted" in logs:
                print("✅ JSON extraction appears to be happening")
            if any(num in logs for num in ["25", "68", "50"]):
                print("✅ Specific demographic numbers found in processing")
            else:
                print("❌ No demographic numbers visible in recent logs")

        else:
            print(f"❌ Failed to get logs: {result.stderr}")

    except Exception as e:
        print(f"❌ Error analyzing logs: {e}")


if __name__ == "__main__":
    test_current_extraction()
    analyze_backend_logs()
