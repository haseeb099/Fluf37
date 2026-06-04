"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";
import type { HealthInfo } from "@/types/integrations";

let cachedHealth: HealthInfo | null = null;
let inflight: Promise<HealthInfo> | null = null;

export function fetchHealthCached(): Promise<HealthInfo> {
  if (cachedHealth) return Promise.resolve(cachedHealth);
  if (inflight) return inflight;
  inflight = getHealth()
    .then((h) => {
      cachedHealth = h;
      return h;
    })
    .finally(() => {
      inflight = null;
    });
  return inflight;
}

export function useHealthStatus() {
  const [health, setHealth] = useState<HealthInfo | null>(cachedHealth);

  useEffect(() => {
    fetchHealthCached().then(setHealth).catch(() => setHealth(null));
  }, []);

  return health;
}
