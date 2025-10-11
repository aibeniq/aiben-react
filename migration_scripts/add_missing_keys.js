#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Define all the missing keys that need to be added
const MISSING_KEYS = {
    // Progress section
    "generate.progress.starting": "Starting...",
    "generate.progress.initializing": "Initializing...",

    "compare.progress.starting": "Starting...",
    "compare.progress.initializing": "Initializing...",

    "match.progress.starting": "Starting...",
    "match.progress.initializing": "Initializing...",

    // Match section missing keys
    "match.pleaseWait": "Please wait while we match your documents",
    "match.matchSuccess": "Form processing completed successfully!",

    // Feedback section (top-level for all features)
    "feedback.modalTitlePositive": "What was helpful?",
    "feedback.modalTitleNegative": "What could be improved?",
    "feedback.descriptionPositive": "Tell us what you liked about this response.",
    "feedback.descriptionNegative": "Tell us how we can improve this response.",
    "feedback.placeholder": "Your comments (optional)",
    "feedback.cancel": "Cancel",
    "feedback.updateFeedback": "Update Feedback",
    "feedback.submit": "Submit",
    "feedback.tooltipEditPositive": "Edit your helpful feedback",
    "feedback.tooltipMarkPositive": "Mark as helpful",
    "feedback.tooltipEditNegative": "Edit your feedback for improvements",
    "feedback.tooltipMarkNegative": "Mark as not helpful",
    "feedback.feedbackSaved": "Feedback saved",
    "feedback.thankYouMessage": "Thank you for your feedback!",
    "feedback.submitErrorMessage": "Failed to submit feedback. Please try again.",

    // UI Buttons (used across features)
    "ui.results": "Results",
    "ui.copyText": "Copy Text",
    "ui.copied": "Copied!",
    "ui.downloadDocx": "Download DOCX",
    "ui.downloadCsv": "Download CSV",
    "ui.clearCsv": "Clear CSV",
    "ui.clearResults": "Clear Results",
};

// Helper to set nested property
function setNestedProperty(obj, path, value) {
    const keys = path.split('.');
    const lastKey = keys.pop();
    let current = obj;

    for (const key of keys) {
        if (!current[key]) {
            current[key] = {};
        }
        current = current[key];
    }

    current[lastKey] = value;
}

// Helper to get nested property
function getNestedProperty(obj, path) {
    const keys = path.split('.');
    let current = obj;

    for (const key of keys) {
        if (!current || !current[key]) {
            return undefined;
        }
        current = current[key];
    }

    return current;
}

// Process all language files
const localesDir = path.join(__dirname, '../frontend/src/locales');
const languages = fs.readdirSync(localesDir).filter(f =>
    fs.statSync(path.join(localesDir, f)).isDirectory()
);

console.log(`\n🔍 Found ${languages.length} language directories\n`);

let totalAdded = 0;
let languageStats = {};

for (const lang of languages) {
    const commonJsonPath = path.join(localesDir, lang, 'common.json');

    if (!fs.existsSync(commonJsonPath)) {
        console.log(`⚠️  Skipping ${lang}: common.json not found`);
        continue;
    }

    const data = JSON.parse(fs.readFileSync(commonJsonPath, 'utf8'));
    let added = 0;
    let missingKeys = [];

    // Check and add missing keys
    for (const [keyPath, englishValue] of Object.entries(MISSING_KEYS)) {
        const existing = getNestedProperty(data, keyPath);

        if (!existing) {
            // For non-English languages, use English as placeholder
            const value = lang === 'en' ? englishValue : `[TODO: ${englishValue}]`;
            setNestedProperty(data, keyPath, value);
            added++;
            missingKeys.push(keyPath);
        }
    }

    if (added > 0) {
        // Write back with nice formatting
        fs.writeFileSync(
            commonJsonPath,
            JSON.stringify(data, null, 2) + '\n'
        );

        console.log(`✅ ${lang}: Added ${added} missing keys`);
        totalAdded += added;
        languageStats[lang] = { added, keys: missingKeys };
    } else {
        console.log(`✓  ${lang}: All keys present`);
    }
}

console.log(`\n📊 Summary:`);
console.log(`   Total keys added: ${totalAdded}`);
console.log(`   Languages updated: ${Object.keys(languageStats).length}`);

if (Object.keys(languageStats).length > 0) {
    console.log(`\n📝 Details by language:`);
    for (const [lang, stats] of Object.entries(languageStats)) {
        console.log(`\n   ${lang} (${stats.added} keys):`);
        stats.keys.forEach(key => {
            console.log(`      - ${key}`);
        });
    }
}

console.log(`\n✨ Done! All languages now have the required keys.`);
console.log(`   Note: Non-English translations are marked with [TODO:...] for manual translation.\n`);
