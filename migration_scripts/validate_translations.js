#!/usr/bin/env node
/**
 * Validate translation completeness across all languages
 * Compare all language files against the English master
 */

const fs = require('fs');
const path = require('path');

const localesDir = path.join(__dirname, '..', 'frontend', 'src', 'locales');

// Helper to get all keys from an object recursively
function getAllKeys(obj, prefix = '') {
    let keys = [];

    for (const [key, value] of Object.entries(obj)) {
        const fullKey = prefix ? `${prefix}.${key}` : key;

        if (value && typeof value === 'object' && !Array.isArray(value)) {
            keys = keys.concat(getAllKeys(value, fullKey));
        } else {
            keys.push(fullKey);
        }
    }

    return keys;
}

// Read English (master) translations
const enPath = path.join(localesDir, 'en', 'common.json');
const enTranslations = JSON.parse(fs.readFileSync(enPath, 'utf-8'));
const enKeys = getAllKeys(enTranslations);

console.log(`📚 Master English translation has ${enKeys.length} keys\n`);

// Get all language directories
const langDirs = fs.readdirSync(localesDir, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name)
    .sort();

console.log(`🌍 Found ${langDirs.length} language directories\n`);

// Analyze each language
const results = [];

langDirs.forEach(lang => {
    const langPath = path.join(localesDir, lang, 'common.json');

    if (!fs.existsSync(langPath)) {
        console.log(`⚠️  ${lang}: No common.json file`);
        return;
    }

    try {
        const translations = JSON.parse(fs.readFileSync(langPath, 'utf-8'));
        const langKeys = getAllKeys(translations);

        const missingKeys = enKeys.filter(k => !langKeys.includes(k));
        const extraKeys = langKeys.filter(k => !enKeys.includes(k));
        const coverage = ((langKeys.length / enKeys.length) * 100).toFixed(1);

        results.push({
            lang,
            total: langKeys.length,
            missing: missingKeys.length,
            extra: extraKeys.length,
            coverage: parseFloat(coverage),
            missingKeys,
            extraKeys
        });

        const status = coverage === '100.0' ? '✅' : coverage >= '80.0' ? '⚠️ ' : '❌';
        console.log(`${status} ${lang.padEnd(8)} ${coverage.padStart(5)}% complete (${langKeys.length}/${enKeys.length} keys, ${missingKeys.length} missing)`);

    } catch (error) {
        console.log(`❌ ${lang}: Error reading file - ${error.message}`);
    }
});

console.log(`\n${'='.repeat(60)}\n`);

// Summary statistics
const avgCoverage = (results.reduce((sum, r) => sum + r.coverage, 0) / results.length).toFixed(1);
const fullyCovered = results.filter(r => r.coverage === 100).length;

console.log(`📊 Summary:`);
console.log(`   Average coverage: ${avgCoverage}%`);
console.log(`   Fully translated: ${fullyCovered}/${results.length} languages`);
console.log(`   Needs work: ${results.filter(r => r.coverage < 80).length} languages\n`);

// Find most common missing keys
const allMissing = results.flatMap(r => r.missingKeys);
const missingCounts = {};
allMissing.forEach(key => {
    missingCounts[key] = (missingCounts[key] || 0) + 1;
});

const topMissing = Object.entries(missingCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

if (topMissing.length > 0) {
    console.log(`🔍 Most commonly missing keys:`);
    topMissing.forEach(([key, count]) => {
        console.log(`   ${key.padEnd(50)} (missing in ${count} languages)`);
    });
}

// Save detailed report
const report = {
    timestamp: new Date().toISOString(),
    master: {
        language: 'en',
        totalKeys: enKeys.length
    },
    languages: results,
    summary: {
        averageCoverage: parseFloat(avgCoverage),
        fullyTranslated: fullyCovered,
        needsWork: results.filter(r => r.coverage < 80).length
    },
    topMissingKeys: topMissing.map(([key, count]) => ({ key, missingInLanguages: count }))
};

const reportPath = path.join(__dirname, 'translation_report.json');
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), 'utf-8');

console.log(`\n📄 Detailed report saved to: ${reportPath}`);
