import { jsonb, pgTable, text, timestamp } from "drizzle-orm/pg-core";

export const kaushalyaStateTable = pgTable("kaushalya_state", {
  key: text("key").primaryKey(),
  payload: jsonb("payload").notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});

export type KaushalyaState = typeof kaushalyaStateTable.$inferSelect;