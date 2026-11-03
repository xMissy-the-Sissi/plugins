import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("DataTable wraps pagination buttons with title containers and sets aria-disabled", async () => {
  const source = await readFile(
    new URL("../src/analytics-app/tables/DataTable.jsx", import.meta.url),
    "utf8"
  );

  assert.match(
    source,
    /<span className="table-arrow-button-wrap" title=\{currentPage === 0 \? "First page reached" : "Previous page"\}>/
  );
  assert.match(
    source,
    /<span className="table-arrow-button-wrap" title=\{currentPage >= totalPages - 1 \? "Last page reached" : "Next page"\}>/
  );
  assert.match(source, /aria-disabled=\{currentPage === 0\}/);
  assert.match(source, /aria-disabled=\{currentPage >= totalPages - 1\}/);
});

test("App.tsx wraps embedded table pagination buttons with title containers and sets aria-disabled", async () => {
  const source = await readFile(
    new URL("../src/analytics-app/App.tsx", import.meta.url),
    "utf8"
  );

  assert.match(
    source,
    /<span className="table-arrow-button-wrap" title=\{currentPage === 0 \? "First page reached" : "Previous page"\}>/
  );
  assert.match(
    source,
    /<span className="table-arrow-button-wrap" title=\{currentPage >= totalPages - 1 \? "Last page reached" : "Next page"\}>/
  );
  assert.match(source, /aria-disabled=\{currentPage === 0\}/);
  assert.match(source, /aria-disabled=\{currentPage >= totalPages - 1\}/);
});
