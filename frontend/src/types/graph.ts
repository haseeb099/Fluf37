export interface GraphNodeData {
  id: string;
  type?: string;
  description?: string;
  severity?: string;
  dollar_loss?: number;
  [key: string]: unknown;
}

export interface GraphEdgeData {
  source: string;
  target: string;
  type?: string;
  probability?: number;
}
