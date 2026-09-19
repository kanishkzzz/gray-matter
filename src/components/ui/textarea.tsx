import { cn } from "@/lib/utils";

/** Multi-line field. Used by the Truth Engine change composer. */
function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "min-h-16 w-full rounded-sm border border-rule-strong bg-panel px-2 py-1.5 text-13 text-ink",
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

export { Textarea };
