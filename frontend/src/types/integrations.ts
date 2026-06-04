export type PluginCategory =
  | "revenue"
  | "finance"
  | "banking"
  | "markets"
  | "intelligence"
  | "custom";

export type PluginIntegrationType = "builtin" | "webhook" | "rest" | "sdk";
export type PluginTier = "official" | "partner" | "community";

export interface PluginManifest {
  id: string;
  name: string;
  description: string;
  category: PluginCategory;
  integration_type: PluginIntegrationType;
  tier: PluginTier;
  vendor: string;
  version: string;
  source_type?: string;
  supports_webhook: boolean;
  live_vendor?: string;
  docs_url?: string;
  setup_steps: string[];
  required_env: string[];
  icon: string;
  installed: boolean;
  connection_state?: string;
  data_mode?: string;
}

export interface PluginCatalogSummary {
  total: number;
  installed: number;
  official: number;
  community: number;
  categories: string[];
}

export interface PluginCatalogResponse {
  plugins: PluginManifest[];
  summary: PluginCatalogSummary;
}

export interface PluginRegistrationRequest {
  name: string;
  description: string;
  category: PluginCategory;
  integration_type: "webhook" | "rest";
  vendor: string;
  webhook_source?: string;
  docs_url?: string;
}

export interface PlatformInfo {
  product_name: string;
  product_wedge: string;
  deployment_mode: string;
  launch_verdict: string;
  uses_demo_pipeline: boolean;
  llm_mode: string;
  llm_provider?: string;
  pilot_blockers: string[];
}

export interface HealthInfo {
  status: string;
  llm_mode?: string;
  llm_provider?: string;
  live_llm_enabled?: boolean;
  uses_demo_pipeline?: boolean;
}

export const CATEGORY_LABELS: Record<PluginCategory, string> = {
  revenue: "Revenue & CRM",
  finance: "Finance & ERP",
  banking: "Banking",
  markets: "Markets & Trading",
  intelligence: "News & Intelligence",
  custom: "Custom & Webhooks",
};
