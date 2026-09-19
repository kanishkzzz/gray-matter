"use client";

import { TooltipProvider } from "@/components/ui/tooltip";
import { NavRail } from "@/components/shell/nav-rail";
import type { HealthResponse } from "@/types";

/**
 * The application frame: rail on the left, everything else to the right of a
 * 1px rule. Pages supply their own `PageFrame` so the header and the optional
 * evidence rail stay consistent between surfaces.
 */
export function AppShell({
  health,
  children,
}: {
  health: HealthResponse | null;
  children: React.ReactNode;
}) {
  return (
    <TooltipProvider>
      <div className="flex min-h-svh bg-surface">
        <NavRail health={health} />
        {children}
      </div>
    </TooltipProvider>
  );
}
