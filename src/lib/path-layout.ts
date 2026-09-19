import type {
  RelationshipEdge,
  RelationshipNode,
  RelationshipPath,
} from "@/types";

/**
 * Relationship path layout.
 *
 * Pure geometry, no React and no DOM, so it can be reasoned about and tested on
 * its own. Left-to-right layered layout: a node's column is the longest
 * distance from a root, which makes the reading direction causal — sources on
 * the left, what they led to on the right.
 *
 * Nodes are laid out here but *rendered as HTML*; only the connectors are SVG.
 * That keeps text wrapping, focus rings and real buttons, which an all-SVG
 * diagram gives up.
 */

export const NODE_W = 168;
export const NODE_H = 62;
export const COL_GAP = 116;
export const ROW_GAP = 20;
/** Gap between the arrowhead tip and the node it points at. */
const ARROW_GAP = 7;
const ARROW_W = 7;
const ARROW_H = 4;
/** Corner radius on elbow connectors. Matches the 2px product geometry. */
const CORNER = 3;

/** Paths longer than this collapse their middle columns behind a marker. */
export const COLLAPSE_THRESHOLD = 6;

export const COLLAPSED_ID = "__collapsed__";

export interface PositionedNode {
  id: string;
  type: RelationshipNode["type"] | "collapsed";
  label: string;
  col: number;
  row: number;
  x: number;
  y: number;
  /** Number of nodes hidden behind this marker. Only set on the collapsed node. */
  hiddenCount?: number;
}

export interface RoutedEdge {
  from: string;
  to: string;
  label: string;
  /** SVG path data, arrowhead included as a trailing subpath. */
  d: string;
  /** Approximate stroke length, used to seed the draw animation. */
  length: number;
  labelX: number;
  labelY: number;
}

export interface PathLayout {
  nodes: PositionedNode[];
  edges: RoutedEdge[];
  width: number;
  height: number;
  /** True when the middle was collapsed, so the caller can offer to expand. */
  collapsed: boolean;
  hiddenCount: number;
}

/* -------------------------------------------------------------------------- */

/** Longest-path depth per node. Defensive against cycles in graph data. */
function computeDepths(
  nodes: RelationshipNode[],
  edges: RelationshipEdge[],
): Map<string, number> {
  const ids = new Set(nodes.map((n) => n.id));
  const parents = new Map<string, string[]>();
  for (const id of ids) parents.set(id, []);
  for (const e of edges) {
    if (ids.has(e.from) && ids.has(e.to)) parents.get(e.to)!.push(e.from);
  }

  const depth = new Map<string, number>();
  const visiting = new Set<string>();

  function resolve(id: string): number {
    const cached = depth.get(id);
    if (cached !== undefined) return cached;
    // A cycle would otherwise recurse forever; treat the back-edge as depth 0.
    if (visiting.has(id)) return 0;

    visiting.add(id);
    const ps = parents.get(id) ?? [];
    const d = ps.length === 0 ? 0 : Math.max(...ps.map(resolve)) + 1;
    visiting.delete(id);

    depth.set(id, d);
    return d;
  }

  for (const n of nodes) resolve(n.id);
  return depth;
}

/** Elbow connector from a node's right edge to the next node's left edge. */
function route(
  sx: number,
  sy: number,
  ex: number,
  ey: number,
): { d: string; length: number; labelX: number; labelY: number } {
  const tipX = ex - ARROW_GAP;
  const arrow = `M${tipX - ARROW_W},${ey - ARROW_H}L${tipX},${ey}L${tipX - ARROW_W},${ey + ARROW_H}`;
  const midX = Math.round((sx + tipX) / 2);

  // Same row: a straight run.
  if (Math.abs(ey - sy) < 1) {
    return {
      d: `M${sx},${sy}L${tipX},${ey}${arrow}`,
      length: tipX - sx + 24,
      labelX: midX,
      labelY: sy,
    };
  }

  const dir = ey > sy ? 1 : -1;
  const d = [
    `M${sx},${sy}`,
    `L${midX - CORNER},${sy}`,
    `Q${midX},${sy} ${midX},${sy + dir * CORNER}`,
    `L${midX},${ey - dir * CORNER}`,
    `Q${midX},${ey} ${midX + CORNER},${ey}`,
    `L${tipX},${ey}`,
    arrow,
  ].join("");

  const length = midX - sx + Math.abs(ey - sy) + (tipX - midX) + 24;
  return { d, length, labelX: midX, labelY: (sy + ey) / 2 };
}

/* -------------------------------------------------------------------------- */

/**
 * Lay out a relationship path.
 *
 * @param expanded when false, paths over COLLAPSE_THRESHOLD nodes hide their
 *                 middle columns behind a marker node.
 */
export function layoutPath(
  path: RelationshipPath,
  expanded = false,
): PathLayout {
  if (path.nodes.length === 0) {
    return { nodes: [], edges: [], width: 0, height: 0, collapsed: false, hiddenCount: 0 };
  }

  const depths = computeDepths(path.nodes, path.edges);
  const maxDepth = Math.max(...path.nodes.map((n) => depths.get(n.id) ?? 0));

  // Which columns are visible.
  const shouldCollapse =
    !expanded && path.nodes.length > COLLAPSE_THRESHOLD && maxDepth >= 4;

  let visibleNodes = path.nodes.map((n) => ({
    ...n,
    col: depths.get(n.id) ?? 0,
  }));
  let edges = path.edges;
  let hiddenCount = 0;

  if (shouldCollapse) {
    const keepLeft = 1; // columns 0..1
    const keepRight = maxDepth - 1; // columns maxDepth-1..maxDepth
    const hidden = visibleNodes.filter(
      (n) => n.col > keepLeft && n.col < keepRight,
    );
    hiddenCount = hidden.length;

    if (hiddenCount > 0) {
      const hiddenIds = new Set(hidden.map((n) => n.id));
      const leftEdge = visibleNodes.filter((n) => n.col === keepLeft);
      const rightEdge = visibleNodes.filter((n) => n.col === keepRight);

      // Original column numbers are kept; the gap they leave behind is closed
      // by the re-indexing below, so no manual shifting is needed (and a shift
      // here would collide with the marker column).
      visibleNodes = visibleNodes.filter((n) => !hiddenIds.has(n.id));

      const markerCol = keepLeft + 1;
      visibleNodes.push({
        id: COLLAPSED_ID,
        type: "collapsed" as RelationshipNode["type"],
        label: `${hiddenCount} more`,
        col: markerCol,
      });

      edges = [
        ...path.edges.filter(
          (e) => !hiddenIds.has(e.from) && !hiddenIds.has(e.to),
        ),
        ...leftEdge.map((n) => ({
          from: n.id,
          to: COLLAPSED_ID,
          label: "",
        })),
        ...rightEdge.map((n) => ({
          from: COLLAPSED_ID,
          to: n.id,
          label: "",
        })),
      ];
    }
  }

  // Stack nodes within each column, in stable input order.
  const byCol = new Map<number, typeof visibleNodes>();
  for (const n of visibleNodes) {
    if (!byCol.has(n.col)) byCol.set(n.col, []);
    byCol.get(n.col)!.push(n);
  }

  const colHeights = new Map<number, number>();
  for (const [col, members] of byCol) {
    colHeights.set(col, members.length * NODE_H + (members.length - 1) * ROW_GAP);
  }
  const height = Math.max(...colHeights.values());
  const cols = [...byCol.keys()].sort((a, b) => a - b);
  const width =
    cols.length * NODE_W + Math.max(0, cols.length - 1) * COL_GAP;

  // Columns are re-indexed so a collapsed layout has no empty gaps.
  const colIndex = new Map(cols.map((c, i) => [c, i]));

  const positioned: PositionedNode[] = [];
  for (const [col, members] of byCol) {
    const top = (height - colHeights.get(col)!) / 2;
    members.forEach((n, row) => {
      positioned.push({
        id: n.id,
        type: n.type,
        label: n.label,
        col: colIndex.get(col)!,
        row,
        x: colIndex.get(col)! * (NODE_W + COL_GAP),
        y: top + row * (NODE_H + ROW_GAP),
        hiddenCount: n.id === COLLAPSED_ID ? hiddenCount : undefined,
      });
    });
  }

  const pos = new Map(positioned.map((n) => [n.id, n]));

  const routed: RoutedEdge[] = [];
  for (const e of edges) {
    const a = pos.get(e.from);
    const b = pos.get(e.to);
    if (!a || !b || a.x === b.x) continue;

    const r = route(
      a.x + NODE_W,
      a.y + NODE_H / 2,
      b.x,
      b.y + NODE_H / 2,
    );
    routed.push({ from: e.from, to: e.to, label: e.label, ...r });
  }

  return {
    nodes: positioned.sort((a, b) => a.col - b.col || a.row - b.row),
    edges: routed,
    width,
    height,
    collapsed: shouldCollapse && hiddenCount > 0,
    hiddenCount,
  };
}

/** Total draw time for the whole path, in ms. Kept at ~400ms per the spec. */
export const DRAW_TOTAL_MS = 400;
export const DRAW_EDGE_MS = 180;

/** Stagger so the last edge finishes at DRAW_TOTAL_MS. */
export function edgeDelay(index: number, count: number): number {
  if (count <= 1) return 0;
  const span = DRAW_TOTAL_MS - DRAW_EDGE_MS;
  return Math.round((span / (count - 1)) * index);
}
