import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("ChartLegend sets disabled, aria-disabled, and title on the last visible interactive series button", async () => {
  const source = await readFile(
    new URL("../src/analytics-app/charting/ChartLegend.tsx", import.meta.url),
    "utf8"
  );

  assert.match(source, /const isOnlyVisible = activeIds\.size === 1 && isVisible;/);
  assert.match(source, /aria-disabled=\{isOnlyVisible\}/);
  assert.match(source, /disabled=\{isOnlyVisible\}/);
  assert.match(
    source,
    /title=\{isOnlyVisible \? "At least one series must remain visible" : undefined\}/
  );
});

test("chart-tokens CSS includes disabled styling for legend buttons", async () => {
  const css = await readFile(
    new URL("../src/analytics-app/charting/chart-tokens.css", import.meta.url),
    "utf8"
  );

  assert.match(css, /\.chart-legend-button:disabled\s*\{/);
  assert.match(css, /cursor:\s*not-allowed;/);
  assert.match(css, /\.chart-legend-button:hover:not\(:disabled\)/);
});
