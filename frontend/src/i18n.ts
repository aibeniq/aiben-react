import i18n from "i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import { initReactI18next } from "react-i18next"

// Import all JSON translation files
import arCommon from "./locales/ar/common.json"
import bgCommon from "./locales/bg/common.json"
import csCommon from "./locales/cs/common.json"
import daCommon from "./locales/da/common.json"
import deCommon from "./locales/de/common.json"
import elCommon from "./locales/el/common.json"
import enCommon from "./locales/en/common.json"
import esCommon from "./locales/es/common.json"
import esLATAMCommon from "./locales/es-LATAM/common.json"
import etCommon from "./locales/et/common.json"
import faCommon from "./locales/fa/common.json"
import fiCommon from "./locales/fi/common.json"
import frCommon from "./locales/fr/common.json"
import heCommon from "./locales/he/common.json"
import hiCommon from "./locales/hi/common.json"
import hrCommon from "./locales/hr/common.json"
import huCommon from "./locales/hu/common.json"
import idCommon from "./locales/id/common.json"
import itCommon from "./locales/it/common.json"
import jaCommon from "./locales/ja/common.json"
import koCommon from "./locales/ko/common.json"
import ltCommon from "./locales/lt/common.json"
import lvCommon from "./locales/lv/common.json"
import msCommon from "./locales/ms/common.json"
import nlCommon from "./locales/nl/common.json"
import noCommon from "./locales/no/common.json"
import plCommon from "./locales/pl/common.json"
import ptCommon from "./locales/pt/common.json"
import ptBRCommon from "./locales/pt-BR/common.json"
import roCommon from "./locales/ro/common.json"
import ruCommon from "./locales/ru/common.json"
import skCommon from "./locales/sk/common.json"
import slCommon from "./locales/sl/common.json"
import srCommon from "./locales/sr/common.json"
import svCommon from "./locales/sv/common.json"
import swCommon from "./locales/sw/common.json"
import thCommon from "./locales/th/common.json"
import tlCommon from "./locales/tl/common.json"
import trCommon from "./locales/tr/common.json"
import ukCommon from "./locales/uk/common.json"
import viCommon from "./locales/vi/common.json"
import zhCommon from "./locales/zh/common.json"
import zhTWCommon from "./locales/zh-TW/common.json"

// Build resources object
const resources = {
    ar: { common: arCommon },
    bg: { common: bgCommon },
    cs: { common: csCommon },
    da: { common: daCommon },
    de: { common: deCommon },
    el: { common: elCommon },
    en: { common: enCommon },
    es: { common: esCommon },
    "es-LATAM": { common: esLATAMCommon },
    et: { common: etCommon },
    fa: { common: faCommon },
    fi: { common: fiCommon },
    fr: { common: frCommon },
    he: { common: heCommon },
    hi: { common: hiCommon },
    hr: { common: hrCommon },
    hu: { common: huCommon },
    id: { common: idCommon },
    it: { common: itCommon },
    ja: { common: jaCommon },
    ko: { common: koCommon },
    lt: { common: ltCommon },
    lv: { common: lvCommon },
    ms: { common: msCommon },
    nl: { common: nlCommon },
    no: { common: noCommon },
    pl: { common: plCommon },
    pt: { common: ptCommon },
    "pt-BR": { common: ptBRCommon },
    ro: { common: roCommon },
    ru: { common: ruCommon },
    sk: { common: skCommon },
    sl: { common: slCommon },
    sr: { common: srCommon },
    sv: { common: svCommon },
    sw: { common: swCommon },
    th: { common: thCommon },
    tl: { common: tlCommon },
    tr: { common: trCommon },
    uk: { common: ukCommon },
    vi: { common: viCommon },
    zh: { common: zhCommon },
    "zh-TW": { common: zhTWCommon },
}

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        fallbackLng: "en",
        debug: false, // Set to true for debugging

        // Language detection options
        detection: {
            order: ["localStorage", "navigator"],
            caches: ["localStorage"],
            lookupLocalStorage: "i18nextLng",
        },

        interpolation: {
            escapeValue: false, // not needed for react as it escapes by default
        },

        // Default namespace
        defaultNS: "common",
        ns: ["common"],

        // React options for Suspense support
        react: {
            useSuspense: true,
        },
    })

export default i18n
