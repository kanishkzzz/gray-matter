"use client";

import * as React from "react";

import { PageFrame, Section } from "@/components/shell/page-frame";
import { EvidencePanel } from "@/components/evidence-panel";
import { RelationshipPathView } from "@/components/relationship-path";
import { Button } from "@/components/ui/button";
// Internal proof sheet only: the product surfaces receive this data as props
// from a route that fetched it. Imported directly here so the page stays a
// single self-contained reference.
import { ASK_FIXTURES, DECISION_DETAILS } from "@/api/mock/data";
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerBody,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

/**
 * Design system proof sheet.
 *
 * Internal reference, not a product surface. Every primitive is rendered with
 * the tokens it will use in the real screens, so drift is visible in one place.
 */
export default function SystemPage() {
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [paletteOpen, setPaletteOpen] = React.useState(false);
  const [selectedId, setSelectedId] = React.useState<string | null>("MTG-004");

  const dec004 = DECISION_DETAILS["DEC-004"];
  const longPath = ASK_FIXTURES[1].path!;

  React.useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "k" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        setPaletteOpen((open) => !open);
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <PageFrame
      eyebrow="Internal"
      title="Design system"
      lede="Every primitive restyled to the Gray Matter tokens. If something here looks like default shadcn, it is a bug."
      meta="step 2 · 3 typefaces · 10 colour tokens · 8 type sizes · radius 2–4px"
    >
      {/* ---------------------------------------------------------------- */}
      <Section
        title="Relationship path"
        description="Plain SVG connectors, no graph library. Left is what came before, right is what it led to. Edge verbs in mono uppercase; node type above the node name. Select a node to open its source in the evidence rail."
      >
        <RelationshipPathView
          path={dec004.path}
          selectedId={selectedId}
          onSelectNode={(node) => setSelectedId(node.id)}
        />
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Relationship path — collapsed"
        description="Seven nodes. Anything over six collapses its middle columns behind an expandable marker, so a long lineage stays readable."
      >
        <RelationshipPathView path={longPath} />
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Evidence panel"
        description="The right rail at its real width of 380px. A source is never summarised away — kind, id, date and its own words."
      >
        <div className="w-95 border border-rule bg-panel">
          <EvidencePanel
            eyebrow="DEC-004"
            sources={dec004.evidence}
            selectedId={selectedId}
            onSelect={(source) => setSelectedId(source.id)}
          />
        </div>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Evidence panel — nothing found"
        description="An empty result states what was searched rather than showing a shrug."
      >
        <div className="w-95 border border-rule bg-panel">
          <EvidencePanel
            eyebrow="PAY-133"
            sources={[]}
            emptyMessage="No indexed source supports this record. Searched 10 sources across the NovaPay corpus."
          />
        </div>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Typeface"
        description="Display for titles and record statements. UI sans for chrome. Mono for anything traceable — IDs, keys, timestamps, edge labels."
      >
        <div className="flex flex-col divide-y divide-rule border-y border-rule">
          <SpecimenRow face="Display — Instrument Serif 400">
            <span className="font-display text-32 tracking-display">
              Select PostgreSQL for Payment Service
            </span>
          </SpecimenRow>
          <SpecimenRow face="UI — IBM Plex Sans 400 / 500 / 600">
            <span className="text-15">
              Evidence indicates the decision was recorded on 10 September 2026.
            </span>
          </SpecimenRow>
          <SpecimenRow face="Mono — IBM Plex Mono, uppercase, 0.06em">
            <span className="mono-label">
              DEC-004 · MTG-004 · PAY-101 · RESULTED IN
            </span>
          </SpecimenRow>
        </div>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Type scale"
        description="11 / 12 / 13 / 15 / 18 / 24 / 32 / 44. Body is 13–15px. Sizes above 44px do not exist in the theme."
      >
        <div className="flex flex-col divide-y divide-rule border-y border-rule">
          {(
            [
              ["44", "text-44", "font-display tracking-display", "Page title"],
              ["32", "text-32", "font-display tracking-display", "Record title"],
              ["24", "text-24", "font-display tracking-display", "Section title"],
              ["18", "text-18", "font-display", "Subsection"],
              ["15", "text-15", "", "Lede, reading text"],
              ["13", "text-13", "", "Body, tables, controls"],
              ["12", "text-12", "", "Secondary metadata"],
              ["11", "text-11", "", "Mono labels"],
            ] as const
          ).map(([px, sizeClass, extra, use]) => (
            <div key={px} className="flex items-baseline gap-4 py-2">
              <span className="mono-label w-10 shrink-0 text-ink-faint">
                {px}
              </span>
              <span className={`${sizeClass} ${extra} min-w-0 flex-1 truncate text-ink`}>
                Evidence you can inspect
              </span>
              <span className="mono-meta shrink-0 text-ink-muted">{use}</span>
            </div>
          ))}
        </div>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Colour"
        description="Warm, paper-like, light only. Colour carries meaning: accent marks trace paths, links and selection; warning is reserved for conflicts and review-required states and appears nowhere else."
      >
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-16">Swatch</TableHead>
              <TableHead className="w-48">Token</TableHead>
              <TableHead className="w-28">Value</TableHead>
              <TableHead>Meaning</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {(
              [
                ["bg-surface", "--surface", "#FBFAF7", "App background"],
                ["bg-panel", "--panel", "#FFFFFF", "Raised regions, tables, drawers"],
                ["bg-ink", "--ink", "#14140F", "Primary text"],
                ["bg-ink-muted", "--ink-muted", "#6B6B60", "Secondary text, metadata"],
                ["bg-ink-faint", "--ink-faint", "#9A9A8E", "Tertiary, disabled"],
                ["bg-rule", "--rule", "#E3E1D8", "All borders and dividers"],
                ["bg-rule-strong", "--rule-strong", "#C9C6B8", "Emphasised borders, active states"],
                ["bg-accent", "--accent", "#1F4E3D", "Trace paths, links, selection, primary action"],
                ["bg-accent-soft", "--accent-soft", "#E8EFE9", "Accent background wash"],
                ["bg-warning", "--warning", "#B4541A", "Conflicts and review-required only"],
                ["bg-warning-soft", "--warning-soft", "#FBEDE4", "Conflict background wash"],
              ] as const
            ).map(([swatch, token, value, meaning]) => (
              <TableRow key={token}>
                <TableCell>
                  <span
                    className={`block size-5 rounded-sm border border-rule-strong ${swatch}`}
                  />
                </TableCell>
                <TableCell className="mono-meta text-ink">{token}</TableCell>
                <TableCell className="mono-meta text-ink-muted">{value}</TableCell>
                <TableCell className="text-ink-muted">{meaning}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Buttons"
        description="No transforms on press, no shadows, no pill shapes. Warning is absent by design — it is not spent on controls."
      >
        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="default">Analyse change</Button>
            <Button variant="outline">Open source</Button>
            <Button variant="ghost">Dismiss</Button>
            <Button variant="link">DEC-004</Button>
            <Button variant="outline" disabled>
              Disabled
            </Button>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button size="sm" variant="outline">
              Small 24px
            </Button>
            <Button size="default" variant="outline">
              Default 28px
            </Button>
            <Button size="lg" variant="outline">
              Large 32px
            </Button>
          </div>
        </div>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section title="Fields">
        <div className="flex max-w-125 flex-col gap-4">
          <Field label="Search records">
            <Input placeholder="Decision, source, ticket or entity" />
          </Field>
          <Field label="Proposed change">
            <Textarea
              rows={3}
              placeholder="Change payment database from MySQL to PostgreSQL"
            />
          </Field>
          <Field label="Invalid state">
            <Input aria-invalid defaultValue="DEC-999" />
          </Field>
        </div>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Tabs"
        description="Underlined section markers, not a segmented pill control."
      >
        <Tabs defaultValue="evidence">
          <TabsList>
            <TabsTrigger value="evidence">Evidence</TabsTrigger>
            <TabsTrigger value="implementation">Implementation</TabsTrigger>
            <TabsTrigger value="affects">Affects</TabsTrigger>
          </TabsList>
          <TabsContent value="evidence" className="pt-4 text-13 text-ink-muted">
            Two sources support this decision: MTG-004 and DOC-014.
          </TabsContent>
          <TabsContent
            value="implementation"
            className="pt-4 text-13 text-ink-muted"
          >
            PAY-101 — Migrate payment datastore to PostgreSQL.
          </TabsContent>
          <TabsContent value="affects" className="pt-4 text-13 text-ink-muted">
            Payment Service, Database Architecture, Database Migration.
          </TabsContent>
        </Tabs>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Table"
        description="A register: hairline rules, mono column labels, no zebra striping, no rounded container."
      >
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-24">ID</TableHead>
              <TableHead>Decision</TableHead>
              <TableHead className="w-28">Date</TableHead>
              <TableHead className="w-28">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {(
              [
                ["DEC-004", "Select PostgreSQL for Payment Service", "2026-09-10", "Implemented"],
                ["DEC-005", "Introduce real-time transaction monitoring", "2026-09-16", "Approved"],
                ["DEC-006", "Deprecate legacy settlement batch job", "2026-09-18", "Proposed"],
              ] as const
            ).map(([id, title, date, status], index) => (
              <TableRow key={id} data-selected={index === 0 ? "" : undefined}>
                <TableCell className="mono-meta text-ink-muted">{id}</TableCell>
                <TableCell>{title}</TableCell>
                <TableCell className="mono-meta text-ink-muted">{date}</TableCell>
                <TableCell className="text-ink-muted">{status}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Overlays"
        description="Dialog and drawer are the only two surfaces permitted a shadow. The drawer slides in from the right in 180ms; nothing else about it animates."
      >
        <div className="flex flex-wrap items-center gap-2">
          <Tooltip>
            <TooltipTrigger render={<Button variant="outline">Tooltip</Button>} />
            <TooltipContent>Recorded 10 September 2026</TooltipContent>
          </Tooltip>

          <Button variant="outline" onClick={() => setDialogOpen(true)}>
            Dialog
          </Button>
          <Button variant="outline" onClick={() => setDrawerOpen(true)}>
            Evidence drawer
          </Button>
          <Button variant="outline" onClick={() => setPaletteOpen(true)}>
            Command palette
            <CommandShortcut>⌘K</CommandShortcut>
          </Button>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Supersede DEC-007?</DialogTitle>
              <DialogDescription>
                This records DEC-002 as the decision in force and marks DEC-007
                superseded.
              </DialogDescription>
            </DialogHeader>
            <DialogBody className="text-13 text-ink-muted">
              Both records stay in the graph. Superseded decisions remain
              readable and keep their evidence.
            </DialogBody>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button variant="default" onClick={() => setDialogOpen(false)}>
                Supersede
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Drawer open={drawerOpen} onOpenChange={setDrawerOpen}>
          <DrawerContent>
            <DrawerHeader>
              <DrawerTitle>Database Architecture Meeting</DrawerTitle>
              <DrawerDescription>
                MTG-004 · meeting · 2026-09-08
              </DrawerDescription>
            </DrawerHeader>
            <DrawerBody className="px-4 py-4">
              <p className="mono-label text-ink-faint">Excerpt</p>
              <p className="mt-2 text-13 text-ink">
                Reviewed datastore options for the Payment Service. MySQL&rsquo;s
                default isolation behaviour under concurrent settlement writes
                was raised as the deciding constraint.
              </p>
            </DrawerBody>
          </DrawerContent>
        </Drawer>

        <CommandDialog open={paletteOpen} onOpenChange={setPaletteOpen}>
          <CommandInput placeholder="Search decisions, sources, entities…" />
          <CommandList>
            <CommandEmpty>No matching record.</CommandEmpty>
            <CommandGroup heading="Decisions">
              <CommandItem>
                Select PostgreSQL for Payment Service
                <CommandShortcut>DEC-004</CommandShortcut>
              </CommandItem>
              <CommandItem>
                Introduce real-time transaction monitoring
                <CommandShortcut>DEC-005</CommandShortcut>
              </CommandItem>
            </CommandGroup>
            <CommandSeparator />
            <CommandGroup heading="Sources">
              <CommandItem>
                Database Architecture Meeting
                <CommandShortcut>MTG-004</CommandShortcut>
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </CommandDialog>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Inline command list"
        description="The same palette rendered in place, without the dialog."
      >
        <div className="max-w-125 border border-rule">
          <Command>
            <CommandInput placeholder="Filter records…" />
            <CommandList>
              <CommandEmpty>No matching record.</CommandEmpty>
              <CommandGroup heading="Entities">
                <CommandItem>
                  Payment Service
                  <CommandShortcut>ENT-001</CommandShortcut>
                </CommandItem>
                <CommandItem>
                  Database Architecture
                  <CommandShortcut>ENT-003</CommandShortcut>
                </CommandItem>
              </CommandGroup>
            </CommandList>
          </Command>
        </div>
      </Section>

      {/* ---------------------------------------------------------------- */}
      <Section
        title="Geometry"
        description="Radius 2px default, 4px maximum. Borders over shadows. Spacing 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64."
      >
        <div className="flex flex-wrap items-end gap-6">
          <GeometrySwatch label="rounded-sm · 2px" className="rounded-sm" />
          <GeometrySwatch label="rounded-lg · 4px" className="rounded-lg" />
          <GeometrySwatch label="border-rule" className="rounded-sm border-rule" />
          <GeometrySwatch
            label="border-rule-strong"
            className="rounded-sm border-rule-strong"
          />
        </div>
      </Section>
    </PageFrame>
  );
}

/* -------------------------------------------------------------------------- */

function SpecimenRow({
  face,
  children,
}: {
  face: string;
  children: React.ReactNode;
}) {
  return (
    <div className="py-4">
      <p className="mono-label text-ink-faint">{face}</p>
      <div className="mt-2 text-ink">{children}</div>
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="mono-label text-ink-muted">{label}</span>
      {children}
    </label>
  );
}

function GeometrySwatch({
  label,
  className,
}: {
  label: string;
  className: string;
}) {
  return (
    <div className="flex flex-col gap-2">
      <div className={`size-12 border bg-panel ${className}`} />
      <span className="mono-meta text-ink-muted">{label}</span>
    </div>
  );
}
