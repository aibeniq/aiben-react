"""
Clean version of the improved table extraction prompt for demographic tables
"""

IMPROVED_TABLE_PROMPT = """Analyze the image and extract ALL table data with complete precision. This may be a demographic/research table with multiple treatment groups.

CRITICAL: Look for tables with grouped column headers like:
- Treatment groups: "Guided self-help", "Unguided self-help", "Wait-list control", "Full sample"  
- Each group may have subcolumns like "n" and "%"
- Row categories like "Gender", "Employment" may be section headers
- Data rows like "Female", "Male", "Single" contain actual values

For EACH table found, return this EXACT format:

{{
  "table_id": "table_N",
  "page": N,
  "title": "exact table title from image",
  "headers": {{
    "Group1Name": ["n", "%"],
    "Group2Name": ["n", "%"], 
    "Group3Name": ["n", "%"],
    "Group4Name": ["n", "%"]
  }},
  "rows": [
    {{
      "Baseline characteristic": "category or data row name",
      "is_subheader": true/false,
      "values": {{
        "Group1Name": {{"n": number, "%": number}},
        "Group2Name": {{"n": number, "%": number}},
        "Group3Name": {{"n": number, "%": number}},
        "Group4Name": {{"n": number, "%": number}}
      }}
    }}
  ],
  "summary": "what this table shows"
}}

EXTRACTION REQUIREMENTS:
1. **Multi-level headers**: If you see grouped columns (e.g., "Guided self-help" spanning "n" and "%"), capture the group names as keys in headers object
2. **Precise numbers**: Extract EVERY number exactly as shown - both "n" (count) and "%" (percentage) values
3. **Category detection**: Rows like "Gender", "Marital status", "Employment" are category headers (is_subheader: true, empty values)
4. **Data rows**: Rows like "Female", "Male", "Single" contain actual data (is_subheader: false, with values for each group)
5. **Complete coverage**: Every cell must be captured - no data should be missing
6. **Exact group names**: Use the EXACT text from column headers, don't abbreviate

Document: {filename}
Pages: {batch_pages}

Return JSON array in ```json``` blocks. Extract ALL numbers precisely.
"""
