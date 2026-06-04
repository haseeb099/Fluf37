import { z } from "zod";

export const wsEventSchema = z.object({
  type: z.string(),
  agent_id: z.string(),
  data: z.unknown(),
  timestamp: z.string().optional(),
});

export type ParsedWSEvent = z.infer<typeof wsEventSchema>;

export function parseWSEvent(raw: unknown): ParsedWSEvent | null {
  const result = wsEventSchema.safeParse(raw);
  return result.success ? result.data : null;
}
