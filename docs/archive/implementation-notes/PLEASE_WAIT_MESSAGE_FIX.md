# "Please Wait" Message Translation Fix

## Issue

After implementing the translation system unification, two "Please wait" messages were still showing in English when Finnish was selected:

1. **Generate page**: "Please wait while we generate your report"
2. **Compare page**: "Please wait while we compare your documents"

Meanwhile, the Review and Match functions correctly showed Finnish translations for their "pleaseWait" messages.

## Root Cause

### Compare Page
The compare.tsx component had a conditional fallback that showed hardcoded English text when the i18n system wasn't ready yet:

```typescript
// BEFORE (Line 550-552):
{ready
  ? t("compare.pleaseWait")
  : "Please wait while we compare your documents"}
```

This was unnecessary because i18next handles its own fallback behavior gracefully.

### Generate Page & Finnish Translations
The generate.tsx component was already using `t("generate.pleaseWait")` correctly, but the Finnish translation file was missing the translations:

1. **Missing `compare.pleaseWait`** - The Finnish compare section existed but lacked the `pleaseWait` key
2. **Missing `generate.pleaseWait`** - The Finnish generate section completely lacked this key

## Solution

### 1. Removed Unnecessary Conditional in Compare Component

**File**: `/frontend/src/routes/_layout/compare.tsx`

```typescript
// AFTER (Line 550):
{t("compare.pleaseWait")}
```

Also removed the unused `ready` variable from useTranslation destructuring:
```typescript
// BEFORE:
const { t, ready } = useTranslation()

// AFTER:
const { t } = useTranslation()
```

### 2. Added Missing Finnish Translation Keys

**File**: `/frontend/src/locales/fi/common.json`

#### Generate Section (Line 252)
```json
{
  "generate": {
    "pageDescription": "Luo asiakirja käyttäjän määrittelemän jäsentelyn ja asiakirjatietokannan perusteella.",
    "generatingDocument": "Luodaan asiakirjaa...",
    "pleaseWait": "Odota hetki, kun luomme raporttisi",  // ← ADDED
    "knowledgeBaseTitle": "Tietokanta",
    // ...
  }
}
```

#### Compare Section (Line 357)
```json
{
  "compare": {
    // ... existing keys ...
    "loadingComparison": "Ladataan vertailua...",
    "pleaseWait": "Odota hetki, kun vertaamme asiakirjojasi",  // ← ADDED
    "topicList": "Aiheluettelo",
    // ...
  }
}
```

## Testing

### Generate Page
- [x] Switch to Finnish language
- [x] Start report generation
- [x] Verify progress bar shows: **"Odota hetki, kun luomme raporttisi"** ✅

### Compare Page
- [x] Switch to Finnish language
- [x] Start document comparison
- [x] Verify progress bar shows: **"Odota hetki, kun vertaamme asiakirjojasi"** ✅

### Review & Match Pages (Already Working)
- Review: "Odota, kun tarkistamme asiakirjasi"
- Match: "Odota, kun yhdistämme asiakirjoja"

## Why This Works

1. **No Conditional Fallbacks Needed**: i18next handles the "not ready" state internally. If translations aren't loaded yet, it falls back to the key or a default. There's no need for manual `ready` checks in most cases.

2. **Consistent Approach**: All four main features (Generate, Compare, Review, Match) now use the same pattern:
   ```typescript
   {t("feature.pleaseWait")}
   ```

3. **Complete Finnish Coverage**: All "pleaseWait" keys now have proper Finnish translations:
   - `generate.pleaseWait` → "Odota hetki, kun luomme raporttisi"
   - `compare.pleaseWait` → "Odota hetki, kun vertaamme asiakirjojasi"
   - `review.pleaseWait` → "Odota, kun tarkistamme asiakirjasi"
   - `match.pleaseWait` → "Odota, kun yhdistämme asiakirjoja"

## Files Modified

1. `/frontend/src/routes/_layout/compare.tsx`
   - Removed `ready` conditional
   - Removed unused `ready` variable

2. `/frontend/src/locales/fi/common.json`
   - Added `generate.pleaseWait`
   - Added `compare.pleaseWait`

## Result

✅ All progress bar "Please wait" messages now display correctly in Finnish
✅ No TypeScript compilation errors
✅ Consistent translation approach across all features
✅ Simpler code without unnecessary conditionals
