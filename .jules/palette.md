## 2026-05-07 - Chart Legend Series Disabling Accessibility
**Learning:** When interactive chart legends prevent users from toggling off all series (minimum 1 visible series invariant), buttons must reflect `disabled` and `aria-disabled="true"` with an informative `title` attribute explaining the constraint, rather than silently ignoring click events on active-looking controls.
**Action:** When enforcing minimum selection limits in multi-select controls or interactive legend toggles, always disable the last active item and expose the visual/screen-reader explanation for why it cannot be deselected.

## 2026-05-18 - Tooltips on Disabled Buttons
**Learning:** Browsers suppress mouse and pointer events on `<button disabled>`, preventing native `title` tooltips from displaying when hovering over disabled buttons.
**Action:** When providing tooltips on disabled buttons (such as boundary pagination controls), wrap the disabled button in a `<span>` container with the `title` attribute so hover tooltips render reliably.
