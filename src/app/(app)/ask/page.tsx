import { PageFrame, Section } from "@/components/shell/page-frame";

export default function AskPage() {
  return (
    <PageFrame
      eyebrow="NovaPay"
      title="Ask Company Brain"
      lede="Ask why something exists and read the evidence behind the answer."
    >
      <Section
        title="Not built yet"
        description="Ask Company Brain is step 6, built on assistant-ui with fully custom presentation."
      >
        <p className="text-13 text-ink-muted">Nothing to show here yet.</p>
      </Section>
    </PageFrame>
  );
}
