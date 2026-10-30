## 2026-05-07 - Chart Legend Series Disabling Accessibility
**Learning:** When interactive chart legends prevent users from toggling off all series (minimum 1 visible series invariant), buttons must reflect `disabled` and `aria-disabled="true"` with an informative `title` attribute explaining the constraint, rather than silently ignoring click events on active-looking controls.
**Action:** When enforcing minimum selection limits in multi-select controls or interactive legend toggles, always disable the last active item and expose the visual/screen-reader explanation for why it cannot be deselected.

## 2026-05-18 - Disabled Pagination Tooltip Rendering
**Learning:** Browsers suppress mouse hover events on disabled `<button>` elements, preventing `title` tooltips from displaying when users hover over disabled pagination controls.
**Action:** Wrap disabled icon controls in a `<span>` container carrying dynamic `title` attributes (e.g. `"First page reached"`) so hover tooltips render reliably at boundary states.
