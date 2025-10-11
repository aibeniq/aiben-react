#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// UI section that exists in English but might be missing in other languages
const UI_SECTION = {
    "results": "Results",
    "copyText": "Copy Text",
    "copied": "Copied!",
    "downloadDocx": "Download DOCX",
    "downloadCsv": "Download CSV",
    "clearCsv": "Clear CSV",
    "clearResults": "Clear Results"
};

const localesDir = path.join(__dirname, '../frontend/src/locales');
const languages = fs.readdirSync(localesDir).filter(f =>
    fs.statSync(path.join(localesDir, f)).isDirectory()
);

console.log(`\n🔍 Checking UI section in ${languages.length} languages\n`);

let totalAdded = 0;

for (const lang of languages) {
    const commonJsonPath = path.join(localesDir, lang, 'common.json');

    if (!fs.existsSync(commonJsonPath)) {
        console.log(`⚠️  Skipping ${lang}: common.json not found`);
        continue;
    }

    const data = JSON.parse(fs.readFileSync(commonJsonPath, 'utf8'));

    // Check if ui section exists
    if (!data.ui) {
        if (lang === 'en') {
            // English should have it already
            data.ui = UI_SECTION;
            console.log(`✅ ${lang}: Added UI section`);
        } else {
            // Other languages get TODO markers
            data.ui = {};
            for (const [key, englishValue] of Object.entries(UI_SECTION)) {
                data.ui[key] = `[TODO: ${englishValue}]`;
            }
            console.log(`✅ ${lang}: Added UI section with TODO markers`);
        }
        totalAdded++;

        // Write back
        fs.writeFileSync(
            commonJsonPath,
            JSON.stringify(data, null, 2) + '\n'
        );
    } else {
        // Check if all keys are present
        let missing = [];
        for (const key of Object.keys(UI_SECTION)) {
            if (!data.ui[key]) {
                missing.push(key);
                if (lang === 'en') {
                    data.ui[key] = UI_SECTION[key];
                } else {
                    data.ui[key] = `[TODO: ${UI_SECTION[key]}]`;
                }
            }
        }

        if (missing.length > 0) {
            fs.writeFileSync(
                commonJsonPath,
                JSON.stringify(data, null, 2) + '\n'
            );
            console.log(`✅ ${lang}: Added ${missing.length} missing UI keys: ${missing.join(', ')}`);
            totalAdded++;
        } else {
            console.log(`✓  ${lang}: UI section complete`);
        }
    }
}

console.log(`\n📊 Summary:`);
console.log(`   Languages updated: ${totalAdded}`);
console.log(`\n✨ Done!\n`);
