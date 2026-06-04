export interface GraphNodeData {
  id: string;
  type?: string;
  label?: string;
  title?: string;
  description?: string;
  severity?: string;
  dollar_loss?: number;
  source_ids?: string[];
  affected_entities?: string[];
  impact_summary?: string;
  occurred_at?: string;
  [key: string]: unknown;
}

export interface GraphEdgeData {
  source: string;
  target: string;
  type?: string;
  probability?: number;
}
