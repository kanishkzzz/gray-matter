import { api } from "@/api";
import { PageFrame, Section } from "@/components/shell/page-frame";
import { DecisionRegister } from "@/features/decisions/decision-register";
import { pluralise } from "@/lib/format";

export default async function DecisionsPage() {
  const { decisions } = await api.listDecisions();

  const inForce = decisions.filter(
    (d) => d.status !== "Superseded" && d.status !== "Rejected",
  ).length;

  return (
    <PageFrame
      eyebrow="NovaPay"
      title="Decision Trace"
      lede="Every decision in the knowledge graph. Open one to see what it rests on, what implements it and what it affects."
      meta={`${pluralise(decisions.length, "decision")} · ${inForce} in force`}
    >
      <Section title="All decisions">
        <DecisionRegister decisions={decisions} />
      </Section>
    </PageFrame>
  );
}
