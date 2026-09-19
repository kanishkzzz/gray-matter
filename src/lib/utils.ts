import { clsx, type ClassValue } from "clsx";
import { extendTailwindMerge } from "tailwind-merge";

/**
 * tailwind-merge only knows Tailwind's stock theme. Every value we add in
 * `@theme` has to be declared here too, or merging goes wrong in one of two
 * silent ways:
 *
 *   1. A value it cannot classify falls into the wrong conflict group and the
 *      class is dropped. This is what happened to the type scale: `text-32`
 *      was read as a text *colour*, so it collided with `text-ink` and
 *      `cn("font-display text-32 text-ink")` returned `"font-display text-ink"`.
 *      Every page title silently rendered at body size.
 *
 *   2. A value it cannot classify at all is never deduplicated, so a later
 *      `className` prop cannot override an earlier default.
 *
 * If you add a theme value in globals.css, add it here in the same commit.
 */
const twMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      "font-size": [
        { text: ["11", "12", "13", "15", "18", "24", "32", "44"] },
      ],
      "font-family": [{ font: ["display"] }],
      tracking: [{ tracking: ["display", "mono"] }],
      ease: [{ ease: ["out-quiet"] }],
      shadow: [{ shadow: ["drawer", "dialog"] }],
    },
  },
});

/** Conditional class names with Tailwind conflict resolution. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
