#!/usr/bin/env node
/**
 * Extract all translations from i18n.ts and create JSON files
 * This uses JavaScript to properly parse the TypeScript object
 */

const fs = require('fs');
const path = require('path');

// Read i18n.ts
const i18nPath = path.join(__dirname, '..', 'frontend', 'src', 'i18n.ts');
const content = fs.readFileSync(i18nPath, 'utf-8');

console.log("🔍 Parsing i18n.ts...");

// Find where each language starts
const languageBlocks = {};
const lines = content.split('\n');

let currentLang = null;
let currentBlock = [];
let braceDepth = 0;
let inResources = false;

for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check if this is a language definition
    const langMatch = line.match(/resources\.([\w-]+)\s*=\s*{/) || line.match(/resources\["([\w-]+)"\]\s*=\s*{/);

    if (langMatch) {
        // Save previous language if any
        if (currentLang && currentBlock.length > 0) {
            languageBlocks[currentLang] = currentBlock.join('\n');
        }

        currentLang = langMatch[1];
        currentBlock = ['{'];
        braceDepth = 1;
        inResources = true;
        continue;
    }

    if (inResources && currentLang) {
        // Count braces
        const openBraces = (line.match(/{/g) || []).length;
        const closeBraces = (line.match(/}/g) || []).length;
        braceDepth += openBraces - closeBraces;

        currentBlock.push(line);

        if (braceDepth === 0) {
            // End of this language block
            languageBlocks[currentLang] = currentBlock.join('\n');
            currentLang = null;
            currentBlock = [];
            inResources = false;
        }
    }
}

console.log(`📦 Found ${Object.keys(languageBlocks).length} language blocks`);

// Now extract just the 'common' object from each language
const localesDir = path.join(__dirname, '..', 'frontend', 'src', 'locales');

Object.entries(languageBlocks).forEach(([lang, block]) => {
    console.log(`\n🌐 Processing ${lang}...`);

    try {
        // Create a safe evaluation context
        const evalCode = `
            const resources = {};
            resources.${lang} = ${block};
            JSON.stringify(resources.${lang}.common || resources.${lang}, null, 2);
        `;

        const jsonStr = eval(evalCode);
        const translations = JSON.parse(jsonStr);

        // Save to file
        const langDir = path.join(localesDir, lang);
        if (!fs.existsSync(langDir)) {
            fs.mkdirSync(langDir, { recursive: true });
        }

        const outputFile = path.join(langDir, 'common.json');
        fs.writeFileSync(outputFile, jsonStr, 'utf-8');

        console.log(`✅ Saved ${lang} (${Object.keys(translations).length} top-level keys)`);

    } catch (error) {
        console.log(`❌ Failed to parse ${lang}: ${error.message}`);
    }
});

console.log(`\n✨ Extraction complete! Check ${localesDir}`);
