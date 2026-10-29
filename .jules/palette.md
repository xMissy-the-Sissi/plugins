## 2026-05-07 - Chart Legend Series Disabling Accessibility
**Learning:** When interactive chart legends prevent users from toggling off all series (minimum 1 visible series invariant), buttons must reflect `disabled` and `aria-disabled="true"` with an informative `title` attribute explaining the constraint, rather than silently ignoring click events on active-looking controls.
**Action:** When enforcing minimum selection limits in multi-select controls or interactive legend toggles, always disable the last active item and expose the visual/screen-reader explanation for why it cannot be deselected.

## 2026-05-18 - Hover/Focus Metric Description Popover Dismissal & ARIA State
**Learning:** Popovers and tooltips triggered on hover or focus (such as metric description popovers) must support dismissal via the `Escape` key without moving pointer or keyboard focus (WCAG 2.1 SC 1.4.13) and convey `aria-expanded` state on their trigger control.
**Action:** Whenever implementing a hover/focus popover or tooltip component, attach an `Escape` key listener during open state and set `aria-expanded={isOpen}` on the trigger element.
