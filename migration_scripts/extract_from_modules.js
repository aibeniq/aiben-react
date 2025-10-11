#!/usr/bin/env node
/**
 * Extract translations from translations_*.ts files
 * These use a function pattern: resources.lang = { common: {...} }
 */

const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, '..', 'frontend', 'src');
const localesDir = path.join(srcDir, 'locales');

// Translation files to process
const translationFiles = [
    'translations_nordic.ts',          // sv, no, da, fi
    'translations_asian.ts',           // zh-TW, th, vi, id, ms, tl
    'translations_baltic_eastern_european.ts', // et, lv, lt, el
    'translations_central_european.ts',  // cs, sk, hu, ro, bg, hr, sr, sl
    'translations_middle_eastern_other.ts'  // he, fa, tr, sw, pt-BR, es-LATAM
];

console.log('🔍 Extracting from translation modules...\n');

translationFiles.forEach(filename => {
    console.log(`📁 Processing ${filename}...`);

    const filePath = path.join(srcDir, filename);

    if (!fs.existsSync(filePath)) {
        console.log(`   ⚠️  File not found, skipping\n`);
        return;
    }

    const content = fs.readFileSync(filePath, 'utf-8');

    // Find all language blocks in this file
    const langRegex = /resources\.(\w+(?:-\w+)?)\s*=\s*{/g;
    let match;
    const languages = [];

    while ((match = langRegex.exec(content)) !== null) {
        languages.push(match[1]);
    }

    // Remove duplicates
    const uniqueLangs = [...new Set(languages)];

    console.log(`   Found languages: ${uniqueLangs.join(', ')}`);

    // Extract each language block
    uniqueLangs.forEach(lang => {
        try {
            // Find the specific language block
            const blockStart = `resources.${lang} = {`;

            let startIdx = content.indexOf(blockStart);
            if (startIdx === -1) {
                // Try with brackets
                startIdx = content.indexOf(`resources["${lang}"] = {`);
            }
            if (startIdx === -1) {
                console.log(`   ❌ Could not find block for ${lang}`);
                return;
            }

            // Find matching closing brace
            let braceDepth = 0;
            let i = content.indexOf('{', startIdx);
            let endIdx = i;

            while (i < content.length && (braceDepth > 0 || i === content.indexOf('{', startIdx))) {
                if (content[i] === '{') braceDepth++;
                else if (content[i] === '}') braceDepth--;

                if (braceDepth === 0 && i > content.indexOf('{', startIdx)) {
                    endIdx = i;
                    break;
                }
                i++;
            }

            const block = content.substring(content.indexOf('{', startIdx), endIdx + 1);

            // Evaluate the block
            const evalCode = `
                const resources = {};
                resources["${lang}"] = ${block};
                JSON.stringify(resources["${lang}"].common || resources["${lang}"], null, 2);
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

            console.log(`   ✅ ${lang}: ${Object.keys(translations).length} top-level keys`);

        } catch (error) {
            console.log(`   ❌ ${lang}: Error - ${error.message}`);
        }
    });

    console.log('');
});

console.log('✨ Extraction from translation modules complete!');
console.log('\n📊 Run validation to see updated coverage:');
console.log('   node migration_scripts/validate_translations.js');
