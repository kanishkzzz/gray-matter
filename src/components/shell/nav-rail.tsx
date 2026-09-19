"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { GraphLedger } from "@/components/shell/graph-ledger";
import { cn } from "@/lib/utils";
import type { HealthResponse } from "@/types";

/**
 * Fixed 220px navigation rail.
 *
 * A label list, not an icon strip: these are four named surfaces, and an icon
 * for "Truth Engine" would be a guess the reader has to decode.
 */

const NAV_ITEMS = [
  { href: "/", label: "Overview" },
  { href: "/ask", label: "Ask Company Brain" },
  { href: "/decisions", label: "Decision Trace" },
  { href: "/truth-engine", label: "Truth Engine" },
] as const;

interface NavRailProps {
  health: HealthResponse | null;
}

export function NavRail({ health }: NavRailProps) {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Primary"
      className="sticky top-0 flex h-svh w-55 shrink-0 flex-col border-r border-rule bg-surface"
    >
      <div className="px-4 py-6">
        <Link
          href="/"
          className="font-display text-18 tracking-display text-ink"
        >
          Gray Matter
        </Link>
        <p className="mono-label mt-1 text-ink-faint">
          Evidence you can inspect
        </p>
      </div>

      <ul className="flex flex-col border-t border-rule py-2">
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);

          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "flex h-8 items-center border-l-2 border-transparent pr-3 pl-4",
                  "text-13 text-ink-muted transition-colors duration-100",
                  "hover:bg-tint-hover hover:text-ink",
                  active &&
                    "border-accent bg-accent-soft font-medium text-ink hover:bg-accent-soft",
                )}
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>

      <div className="mt-auto border-t border-rule px-4 py-4">
        <GraphLedger health={health} />
      </div>
    </nav>
  );
}
