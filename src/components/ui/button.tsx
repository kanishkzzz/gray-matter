import { Button as ButtonPrimitive } from "@base-ui/react/button";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

/**
 * Button.
 *
 * No transforms on press, no scale, no shadow. State is carried by fill and
 * rule. `--warning` is deliberately absent: it is reserved for conflicts and
 * review-required states and must never be spent on a control.
 */
const buttonVariants = cva(
  [
    "inline-flex shrink-0 items-center justify-center gap-1.5 whitespace-nowrap",
    "rounded-sm border border-transparent font-medium",
    "transition-colors duration-100",
    "disabled:pointer-events-none disabled:opacity-45",
    "[&_svg]:pointer-events-none [&_svg]:shrink-0",
  ],
  {
    variants: {
      variant: {
        /** Primary action. One per view, at most. */
        default: "bg-accent text-on-accent hover:bg-accent/88 active:bg-accent",
        /** Default for most actions. Reads as a ruled control, not a button blob. */
        outline:
          "border-rule-strong bg-panel text-ink hover:bg-tint-hover active:bg-tint-press",
        /** Table row actions, toolbar affordances. */
        ghost: "text-ink-muted hover:bg-tint-hover hover:text-ink active:bg-tint-press",
        /** Inline, in running text. */
        link: "text-accent underline-offset-2 hover:underline",
      },
      size: {
        sm: "h-6 px-2 text-12 [&_svg:not([class*='size-'])]:size-3",
        default: "h-7 px-3 text-13 [&_svg:not([class*='size-'])]:size-3.5",
        lg: "h-8 px-4 text-13 [&_svg:not([class*='size-'])]:size-4",
        icon: "size-7 px-0 [&_svg:not([class*='size-'])]:size-3.5",
        "icon-sm": "size-6 px-0 [&_svg:not([class*='size-'])]:size-3",
      },
    },
    defaultVariants: {
      variant: "outline",
      size: "default",
    },
  },
);

function Button({
  className,
  variant,
  size,
  ...props
}: ButtonPrimitive.Props & VariantProps<typeof buttonVariants>) {
  return (
    <ButtonPrimitive
      data-slot="button"
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  );
}

export { Button, buttonVariants };
