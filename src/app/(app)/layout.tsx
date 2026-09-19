import { api } from "@/api";
import { AppShell } from "@/components/shell/app-shell";
import type { HealthResponse } from "@/types";

/**
 * Routes fetch; components take props.
 *
 * This layout is not re-run when navigating between the four surfaces, so the
 * corpus ledger is read once per load rather than on every click.
 */
export default async function AppLayout({ children }: LayoutProps<"/">) {
  let health: HealthResponse | null = null;

  try {
    health = await api.health();
  } catch {
    // The rail states "Not reachable" rather than failing the whole shell.
    health = null;
  }

  return <AppShell health={health}>{children}</AppShell>;
}
