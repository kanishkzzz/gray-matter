/**
 * CSS verification.
 *
 *   npm run verify:css        (dev server must be running on :3000)
 *
 * Drives real Chrome and asserts *computed* styles, not class names. Class
 * names lie: `cn()` can drop a class through tailwind-merge, and a non-utility
 * used inside a variant generates no rule at all. Both failures look fine in
 * the DOM and wrong on screen. This checks what the browser actually resolved.
 *
 * Screenshots are written to SHOT_DIR (default: cwd).
 */
import { chromium } from "playwright-core";

const BASE = process.env.BASE_URL || "http://localhost:3000";
const OUT = process.env.SHOT_DIR || ".";

/** selector -> expected computed values. Regex for fontFamily, exact otherwise. */
const CHECKS = {
  "/": {
    h1: { sel: "h1", fontSize: "32px", fontFamily: /Instrument Serif/ },
    lede: { sel: "header p", fontSize: "15px", fontFamily: /Plex Sans/ },
    body: { sel: "body", fontSize: "13px", fontFamily: /Plex Sans/ },
    wordmark: {
      sel: 'nav a[href="/"]',
      fontSize: "18px",
      fontFamily: /Instrument Serif/,
    },
    monoLabel: {
      sel: ".mono-label",
      fontSize: "11px",
      fontFamily: /Plex Mono/,
      textTransform: "uppercase",
      letterSpacing: "0.66px",
    },
    monoMeta: { sel: ".mono-meta", fontSize: "12px", fontFamily: /Plex Mono/ },
    activeNav: {
      sel: 'nav a[aria-current="page"]',
      backgroundColor: "rgb(232, 239, 233)",
      borderLeftColor: "rgb(31, 78, 61)",
      borderLeftWidth: "2px",
    },
    sectionHeading: { sel: "section h2", fontSize: "18px", fontFamily: /Instrument Serif/ },
  },
  "/system": {
    h1: { sel: "h1", fontSize: "32px", fontFamily: /Instrument Serif/ },
    buttonPrimary: {
      sel: 'button[data-slot="button"]',
      fontSize: "13px",
      height: "28px",
      borderRadius: "2px",
    },
    input: {
      sel: 'input[data-slot="input"]',
      fontSize: "13px",
      height: "28px",
      borderColor: "rgb(201, 198, 184)",
    },
    tableHead: {
      sel: 'th[data-slot="table-head"]',
      fontSize: "11px",
      textTransform: "uppercase",
      fontFamily: /Plex Mono/,
    },
    tabTrigger: { sel: '[data-slot="tabs-trigger"]', fontSize: "13px" },
    // The bug this file exists to catch: a custom class used inside a variant.
    cmdkGroupHeading: {
      sel: "[cmdk-group-heading]",
      fontSize: "11px",
      fontFamily: /Plex Mono/,
      textTransform: "uppercase",
    },
  },
};

const PROPS = [
  "fontSize",
  "fontFamily",
  "color",
  "backgroundColor",
  "borderColor",
  "borderLeftColor",
  "borderLeftWidth",
  "borderRadius",
  "height",
  "textTransform",
  "letterSpacing",
  "lineHeight",
];

const browser = await chromium.launch({ channel: "chrome" });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

const consoleErrors = [];
page.on("console", (m) => m.type() === "error" && consoleErrors.push(m.text()));
page.on("pageerror", (e) => consoleErrors.push(String(e)));

let failures = 0;

for (const [route, checks] of Object.entries(CHECKS)) {
  await page.goto(BASE + route, { waitUntil: "networkidle" });
  console.log(`\n=== ${route} ===`);

  const measured = await page.evaluate(
    ({ checks, props }) => {
      const out = {};
      for (const [name, spec] of Object.entries(checks)) {
        const el = document.querySelector(spec.sel);
        if (!el) {
          out[name] = null;
          continue;
        }
        const s = getComputedStyle(el);
        const o = {};
        for (const p of props) o[p] = s[p];
        out[name] = o;
      }
      return out;
    },
    { checks, props: PROPS },
  );

  for (const [name, spec] of Object.entries(checks)) {
    const got = measured[name];
    if (!got) {
      console.log(`  FAIL  ${name}: no element matching "${spec.sel}"`);
      failures++;
      continue;
    }
    const problems = [];
    for (const [prop, want] of Object.entries(spec)) {
      if (prop === "sel") continue;
      const actual = prop === "fontFamily" ? got[prop] : got[prop];
      const ok = want instanceof RegExp ? want.test(actual) : actual === want;
      if (!ok) problems.push(`${prop}: want ${want}, got ${actual}`);
    }
    if (problems.length) {
      console.log(`  FAIL  ${name.padEnd(18)} ${problems.join("; ")}`);
      failures += problems.length;
    } else {
      const summary = [got.fontSize, got.fontFamily.split(",")[0]]
        .filter(Boolean)
        .join(" ");
      console.log(`  ok    ${name.padEnd(18)} ${summary}`);
    }
  }

  const name = route === "/" ? "overview" : route.slice(1).replace(/\//g, "-");
  await page.screenshot({ path: `${OUT}/shot-${name}.png` });
}

if (consoleErrors.length) {
  console.log("\n=== browser console errors ===");
  consoleErrors.slice(0, 10).forEach((e) => console.log("  " + e));
  failures += consoleErrors.length;
}

console.log(
  failures === 0
    ? "\nALL COMPUTED STYLES CORRECT"
    : `\n${failures} FAILURE(S)`,
);
await browser.close();
process.exit(failures === 0 ? 0 : 1);
