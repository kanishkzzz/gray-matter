import { notFound } from "next/navigation";

import { api, GrayMatterApiError } from "@/api";
import { DecisionTrace } from "@/features/decisions/decision-trace";
import type { DecisionDetail } from "@/types";

export default async function DecisionTracePage({
  params,
}: PageProps<"/decisions/[id]">) {
  const { id } = await params;

  // Only the fetch is guarded — wrapping the render too would swallow errors
  // thrown while building the tree.
  let decision: DecisionDetail;
  try {
    decision = await api.getDecision(id);
  } catch (error) {
    if (error instanceof GrayMatterApiError && error.code === "not_found") {
      notFound();
    }
    throw error;
  }

  return <DecisionTrace decision={decision} />;
}
