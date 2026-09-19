import { PageFrame, Section } from "@/components/shell/page-frame";

export default function TruthEnginePage() {
  return (
    <PageFrame
      eyebrow="NovaPay"
      title="Truth Engine"
      lede="Describe a proposed change and see the records, decisions and tickets it touches."
    >
      <Section
        title="Not built yet"
        description="Truth Engine is step 5."
      >
        <p className="text-13 text-ink-muted">Nothing to show here yet.</p>
      </Section>
    </PageFrame>
  );
}
