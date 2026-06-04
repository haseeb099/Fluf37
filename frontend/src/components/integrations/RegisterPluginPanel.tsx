"use client";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input, Label, Select, Textarea } from "@/components/ui/Input";
import { registerPlugin } from "@/lib/api";
import type { PluginCategory, PluginRegistrationRequest } from "@/types/integrations";
import { Plus, X } from "lucide-react";
import { useState } from "react";

export function RegisterPluginPanel({
  onRegistered,
  onClose,
}: {
  onRegistered: () => void;
  onClose?: () => void;
}) {
  const [form, setForm] = useState<PluginRegistrationRequest>({
    name: "",
    description: "",
    category: "custom",
    integration_type: "webhook",
    vendor: "",
    webhook_source: "",
    docs_url: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await registerPlugin({
        ...form,
        webhook_source: form.webhook_source || undefined,
        docs_url: form.docs_url || undefined,
      });
      onRegistered();
      setForm({
        name: "",
        description: "",
        category: "custom",
        integration_type: "webhook",
        vendor: "",
        webhook_source: "",
        docs_url: "",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card className="border-sky-500/20">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Plus className="h-4 w-4 text-sky-400" />
              Add your integration
            </CardTitle>
            <CardDescription>
              Register a webhook or REST bridge. No code deploy required — your team pushes signed JSON to Fluf37.
            </CardDescription>
          </div>
          {onClose && (
            <button type="button" onClick={onClose} className="text-muted hover:text-slate-200">
              <X className="h-5 w-5" />
            </button>
          )}
        </div>
      </CardHeader>

      <form onSubmit={submit} className="grid gap-4 md:grid-cols-2">
        <div>
          <Label htmlFor="name">Integration name</Label>
          <Input
            id="name"
            required
            placeholder="Acme ERP Bridge"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </div>
        <div>
          <Label htmlFor="vendor">Your organization</Label>
          <Input
            id="vendor"
            required
            placeholder="Acme Corp IT"
            value={form.vendor}
            onChange={(e) => setForm({ ...form, vendor: e.target.value })}
          />
        </div>
        <div className="md:col-span-2">
          <Label htmlFor="description">What data does this send?</Label>
          <Textarea
            id="description"
            required
            placeholder="Nightly vendor payments and GL snapshots for pre-release risk review…"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </div>
        <div>
          <Label htmlFor="category">Category</Label>
          <Select
            id="category"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value as PluginCategory })}
          >
            <option value="custom">Custom</option>
            <option value="finance">Finance & ERP</option>
            <option value="revenue">Revenue & CRM</option>
            <option value="banking">Banking</option>
            <option value="markets">Markets</option>
            <option value="intelligence">Intelligence</option>
          </Select>
        </div>
        <div>
          <Label htmlFor="type">Integration type</Label>
          <Select
            id="type"
            value={form.integration_type}
            onChange={(e) =>
              setForm({
                ...form,
                integration_type: e.target.value as "webhook" | "rest",
              })
            }
          >
            <option value="webhook">Webhook (push JSON)</option>
            <option value="rest">REST adapter</option>
          </Select>
        </div>
        {form.integration_type === "webhook" && (
          <div className="md:col-span-2">
            <Label htmlFor="source">Webhook source slug</Label>
            <Input
              id="source"
              placeholder="acme_erp"
              pattern="[a-z][a-z0-9_]{1,24}"
              value={form.webhook_source}
              onChange={(e) => setForm({ ...form, webhook_source: e.target.value })}
            />
            <p className="text-xs text-muted mt-1">
              Ingest URL: POST /ingest/{form.webhook_source || "{source}"} with HMAC signature
            </p>
          </div>
        )}
        <div className="md:col-span-2 flex items-center gap-3">
          <Button type="submit" variant="primary" disabled={busy}>
            {busy ? "Registering…" : "Register integration"}
          </Button>
          <Badge variant="outline">Admin role required</Badge>
        </div>
        {error && (
          <p className="md:col-span-2 text-sm text-red-400" role="alert">
            {error}
          </p>
        )}
      </form>
    </Card>
  );
}
