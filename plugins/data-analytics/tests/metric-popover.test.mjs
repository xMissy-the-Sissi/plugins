import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("MetricDescriptionPopover includes aria-expanded and Escape key listener for accessibility", async () => {
  const source = await readFile(
    new URL("../src/analytics-app/App.tsx", import.meta.url),
    "utf8"
  );

  assert.match(
    source,
    /aria-expanded=\{isOpen\}/,
    "MetricDescriptionPopover button should convey expanded state with aria-expanded"
  );
  assert.match(
    source,
    /if\s*\(\s*event\.key\s*===\s*"Escape"\s*\)\s*\{\s*closePopover\(\);\s*\}/,
    "MetricDescriptionPopover should handle Escape keydown to close the popover"
  );
});
