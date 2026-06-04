import type { GraphNodeData } from "@/types/graph";

/** Display label for traceback graph nodes (prefer API `label` / `title`). */
export function graphNodeLabel(node: GraphNodeData): string {
  if (node.label && typeof node.label === "string") return node.label;
  if (node.title) return node.title;
  if (node.description) {
    return node.description.length <= 72 ? node.description : `${node.description.slice(0, 69)}…`;
  }
  return node.id;
}

export function graphNodeSubtitle(node: GraphNodeData): string | null {
  const parts: string[] = [];
  if (node.affected_entities?.length) {
    parts.push(`Affected: ${node.affected_entities.slice(0, 3).join(", ")}`);
  } else if (node.impact_summary && typeof node.impact_summary === "string") {
    parts.push(node.impact_summary);
  }
  if (node.source_ids?.length) {
    parts.push(`Sources: ${node.source_ids.join(", ")}`);
  }
  return parts.length ? parts.join(" · ") : null;
}
