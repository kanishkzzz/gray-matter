import { cn } from "@/lib/utils";

/**
 * Page frame.
 *
 * Header block, content column capped at 1100px and left-aligned, and an
 * optional 380px evidence rail. Nothing is centred; the eye should start at the
 * same x on every screen.
 *
 * Below 1280px the evidence rail is not rendered here — Decision Trace and
 * Truth Engine move their evidence into a drawer at that width.
 */

interface PageFrameProps {
  /** Mono uppercase kicker, e.g. `DECISION · DEC-004`. */
  eyebrow?: React.ReactNode;
  title: string;
  /** One sentence in UI sans under the title. */
  lede?: React.ReactNode;
  /** Mono metadata line: IDs, dates, counts. */
  meta?: React.ReactNode;
  actions?: React.ReactNode;
  /** Right evidence rail. Rendered from 1280px up. */
  rail?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function PageFrame({
  eyebrow,
  title,
  lede,
  meta,
  actions,
  rail,
  children,
  className,
}: PageFrameProps) {
  return (
    <div className="flex min-w-0 flex-1">
      <main className="min-w-0 flex-1">
        <header className="border-b border-rule">
          <div className="max-w-275 px-8 py-6">
            {eyebrow ? (
              <div className="mono-label text-ink-muted">{eyebrow}</div>
            ) : null}

            <div className="flex items-start justify-between gap-6">
              <h1
                className={cn(
                  "font-display text-32 tracking-display text-ink",
                  eyebrow && "mt-1",
                )}
              >
                {title}
              </h1>
              {actions ? (
                <div className="flex shrink-0 items-center gap-2 pt-2">
                  {actions}
                </div>
              ) : null}
            </div>

            {lede ? (
              <p className="mt-2 max-w-[68ch] text-15 text-ink-muted">{lede}</p>
            ) : null}

            {meta ? (
              <div className="mono-meta mt-3 text-ink-muted">{meta}</div>
            ) : null}
          </div>
        </header>

        <div className={cn("max-w-275 px-8 py-6", className)}>{children}</div>
      </main>

      {rail ? (
        <aside
          aria-label="Evidence"
          className="hidden w-95 shrink-0 border-l border-rule bg-panel xl:block"
        >
          <div className="sticky top-0 max-h-svh overflow-y-auto">{rail}</div>
        </aside>
      ) : null}
    </div>
  );
}

/**
 * A titled block inside the content column. Section headings are display-face
 * and sit above a rule — the same device the page header uses, one level down.
 */
export function Section({
  title,
  description,
  actions,
  children,
  className,
}: {
  title: string;
  description?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("mt-8 first:mt-0", className)}>
      <div className="flex items-baseline justify-between gap-4 border-b border-rule pb-2">
        <h2 className="font-display text-18 text-ink">{title}</h2>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </div>
      {description ? (
        <p className="mt-2 max-w-[68ch] text-13 text-ink-muted">{description}</p>
      ) : null}
      <div className="mt-4">{children}</div>
    </section>
  );
}
