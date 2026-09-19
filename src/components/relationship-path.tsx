"use client";

import * as React from "react";

import {
  COLLAPSED_ID,
  DRAW_EDGE_MS,
  NODE_H,
  NODE_W,
  edgeDelay,
  layoutPath,
} from "@/lib/path-layout";
import { cn } from "@/lib/utils";
import type { RelationshipNode, RelationshipPath } from "@/types";

/**
 * Relationship path.
 *
 * Plain SVG connectors, no graph library. Nodes are HTML buttons positioned
 * over the SVG so they keep real focus rings, real text wrapping and real
 * keyboard behaviour.
 *
 * Reading direction is causal: left is what came before, right is what it led
 * to. Edges are labelled with the verb from the graph, in mono uppercase.
 */

const TYPE_LABEL: Record<RelationshipNode["type"] | "collapsed", string> = {
  meeting: "Meeting",
  document: "Document",
  message: "Message",
  decision: "Decision",
  ticket: "Ticket",
  entity: "Entity",
  change: "Proposed change",
  collapsed: "Collapsed",
};

interface RelationshipPathViewProps {
  path: RelationshipPath;
  /** Record id of the node to mark as current. */
  selectedId?: string | null;
  onSelectNode?: (node: { id: string; type: string; label: string }) => void;
  /** Suppresses the draw animation, e.g. when re-rendering after a filter. */
  animate?: boolean;
  className?: string;
}

export function RelationshipPathView({
  path,
  selectedId,
  onSelectNode,
  animate = true,
  className,
}: RelationshipPathViewProps) {
  const [expanded, setExpanded] = React.useState(false);
  const layout = React.useMemo(
    () => layoutPath(path, expanded),
    [path, expanded],
  );

  // A long path scrolls horizontally. Say so, rather than leaving the diagram
  // silently cut off at the edge of the column.
  const scrollRef = React.useRef<HTMLDivElement>(null);
  const [more, setMore] = React.useState(false);

  React.useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;

    const update = () =>
      setMore(el.scrollLeft + el.clientWidth < el.scrollWidth - 2);

    update();
    el.addEventListener("scroll", update, { passive: true });
    const observer = new ResizeObserver(update);
    observer.observe(el);
    return () => {
      el.removeEventListener("scroll", update);
      observer.disconnect();
    };
  }, [layout.width]);

  if (layout.nodes.length === 0) {
    return (
      <p className="text-13 text-ink-muted">
        No relationship path is recorded for this record.
      </p>
    );
  }

  return (
    <div className={cn("w-full", className)}>
      <div ref={scrollRef} className="overflow-x-auto pb-2">
        <div
          className="relative"
          style={{ width: layout.width, height: layout.height }}
        >
          {/* Connectors. Decorative — the relationships are also stated in the
              screen-reader list below. */}
          <svg
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 overflow-visible"
            width={layout.width}
            height={layout.height}
          >
            {layout.edges.map((edge, i) => (
              <path
                key={`${edge.from}->${edge.to}`}
                d={edge.d}
                fill="none"
                stroke="var(--accent)"
                strokeWidth={1.5}
                strokeLinecap="butt"
                strokeLinejoin="miter"
                style={
                  animate
                    ? {
                        strokeDasharray: edge.length,
                        strokeDashoffset: edge.length,
                        animation: `edge-draw ${DRAW_EDGE_MS}ms var(--ease-out-quiet) ${edgeDelay(i, layout.edges.length)}ms both`,
                      }
                    : undefined
                }
              />
            ))}
          </svg>

          {/* Edge labels, knocked out of the line. Synthetic connectors into
              and out of a collapsed marker carry no verb, so they get no label. */}
          {layout.edges.map((edge, i) =>
            !edge.label ? null : (
            <span
              key={`label-${edge.from}->${edge.to}`}
              aria-hidden="true"
              className="mono-label pointer-events-none absolute bg-surface px-1 text-ink-muted"
              style={{
                left: edge.labelX,
                top: edge.labelY,
                transform: "translate(-50%, -50%)",
                animation: animate
                  ? `edge-label-in 120ms linear ${edgeDelay(i, layout.edges.length) + DRAW_EDGE_MS - 60}ms both`
                  : undefined,
              }}
            >
              {edge.label}
            </span>
            ),
          )}

          {/* Nodes. */}
          {layout.nodes.map((node) => {
            const isCollapsed = node.id === COLLAPSED_ID;
            const isSelected = !isCollapsed && node.id === selectedId;

            if (isCollapsed) {
              return (
                <button
                  key={node.id}
                  type="button"
                  onClick={() => setExpanded(true)}
                  className={cn(
                    "absolute flex flex-col items-center justify-center rounded-sm",
                    "border border-dashed border-rule-strong bg-surface",
                    "text-ink-muted transition-colors duration-100 hover:bg-tint-hover hover:text-ink",
                  )}
                  style={{ left: node.x, top: node.y, width: NODE_W, height: NODE_H }}
                >
                  <span className="mono-label">+{node.hiddenCount} more</span>
                  <span className="mt-1 text-12">Show full path</span>
                </button>
              );
            }

            const interactive = Boolean(onSelectNode);
            const Tag = interactive ? "button" : "div";

            return (
              <Tag
                key={node.id}
                {...(interactive
                  ? {
                      type: "button" as const,
                      onClick: () =>
                        onSelectNode?.({
                          id: node.id,
                          type: node.type,
                          label: node.label,
                        }),
                      "aria-pressed": isSelected,
                    }
                  : {})}
                className={cn(
                  "absolute flex flex-col justify-center overflow-hidden rounded-sm border px-3 text-left",
                  "transition-colors duration-100",
                  isSelected
                    ? "border-accent bg-accent-soft"
                    : "border-rule-strong bg-panel",
                  interactive && !isSelected && "hover:bg-tint-hover",
                )}
                style={{ left: node.x, top: node.y, width: NODE_W, height: NODE_H }}
              >
                <span className="mono-label block truncate text-ink-faint">
                  {TYPE_LABEL[node.type]} · {node.id}
                </span>
                <span className="mt-1 line-clamp-2 text-13 leading-[1.15rem] text-ink">
                  {node.label}
                </span>
              </Tag>
            );
          })}
        </div>
      </div>

      {layout.collapsed || more ? (
        <div className="mono-label mt-2 flex items-baseline justify-between gap-4 text-ink-faint">
          <span>
            {layout.collapsed
              ? `${layout.hiddenCount} intermediate records hidden`
              : ""}
          </span>
          {more ? <span>scroll for full path →</span> : null}
        </div>
      ) : null}

      {/* The path stated in words, for screen readers and for anyone who
          cannot read the diagram. */}
      <ul className="sr-only">
        {path.edges.map((edge) => {
          const from = path.nodes.find((n) => n.id === edge.from);
          const to = path.nodes.find((n) => n.id === edge.to);
          return (
            <li key={`${edge.from}->${edge.to}`}>
              {from ? `${TYPE_LABEL[from.type]} ${from.id}, ${from.label},` : edge.from}{" "}
              {edge.label}{" "}
              {to ? `${TYPE_LABEL[to.type]} ${to.id}, ${to.label}.` : edge.to}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
