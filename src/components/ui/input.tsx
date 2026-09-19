import { Input as InputPrimitive } from "@base-ui/react/input";

import { cn } from "@/lib/utils";

/** Single-line field. Ruled, not filled. Focus ring comes from the base layer. */
function Input({ className, ...props }: React.ComponentProps<"input">) {
  return (
    <InputPrimitive
      data-slot="input"
      className={cn(
        "h-7 w-full min-w-0 rounded-sm border border-rule-strong bg-panel px-2 text-13 text-ink",
        "transition-colors duration-100",
        "placeholder:text-ink-faint",
        "hover:border-ink-faint",
        "focus-visible:border-accent",
        "disabled:pointer-events-none disabled:bg-surface disabled:text-ink-faint",
        "aria-invalid:border-warning",
        className,
      )}
      {...props}
    />
  );
}

export { Input };
