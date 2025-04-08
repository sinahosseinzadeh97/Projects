import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// User schema
export const users = sqliteTable("users", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  avatarInitials: text("avatar_initials"),
  role: text("role").default("user").notNull(),
});

export const insertUserSchema = createInsertSchema(users);

// Wallet schema
export const wallets = sqliteTable("wallets", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  address: text("address").notNull().unique(),
  label: text("label"),
  isParent: integer("is_parent", { mode: "boolean" }).default(0).notNull(),
  level: real("level").notNull(),
  isActive: integer("is_active", { mode: "boolean" }).default(1).notNull(),
  balance: real("balance"),
  createdAt: text("created_at").default(String(new Date().toISOString())).notNull(),
});

export const insertWalletSchema = createInsertSchema(wallets);

// Transaction schema
export const transactions = sqliteTable("transactions", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  txId: text("tx_id").notNull().unique(),
  fromWallet: text("from_wallet").notNull(),
  toWallet: text("to_wallet").notNull(),
  tokenSymbol: text("token_symbol").notNull(),
  amount: real("amount").notNull(),
  type: text("type").notNull(), // 'buy', 'sell', 'transfer'
  transactionType: text("transaction_type"), // 'normal', 'raydium_swap', 'wsol_buy'
  status: text("status").notNull(), // 'pending', 'completed', 'failed'
  timestamp: text("timestamp").default(String(new Date().toISOString())).notNull(),
  volume: real("volume"),
  marketCap: real("market_cap"),
  tokenAge: real("token_age"),
  failReason: text("fail_reason"),
  retryCount: real("retry_count").default("0"),
});

export const insertTransactionSchema = createInsertSchema(transactions);

// Bot Configuration schema
export const botConfigurations = sqliteTable("bot_configurations", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  parentWalletAddress: text("parent_wallet_address").notNull(),
  minAmount: real("min_amount").notNull(),
  maxAmount: real("max_amount").notNull(),
  tipAmount: real("tip_amount").notNull(),
  gasFee: real("gas_fee").notNull(),
  trackingDepth: real("tracking_depth").notNull(),
  volumeThreshold: real("volume_threshold").notNull(),
  mcThreshold: real("mc_threshold").notNull(),
  tokenAge: real("token_age").notNull(),
  profitTarget: real("profit_target").notNull(),
  stopLoss: real("stop_loss").notNull(),
  antiMevProtection: integer("anti_mev_protection", { mode: "boolean" }).default(1).notNull(),
  aiPredictionEnabled: integer("ai_prediction_enabled", { mode: "boolean" }).default(0).notNull(),
  sentimentAnalysisEnabled: integer("sentiment_analysis_enabled", { mode: "boolean" }).default(0).notNull(),
  huggingfaceApiKey: text("huggingface_api_key"),
  mlModelId: text("ml_model_id").default("finBERT/finbert-sentiment"),
  createdAt: text("created_at").default(String(new Date().toISOString())).notNull(),
  updatedAt: text("updated_at").default(String(new Date().toISOString())).notNull(),
});

export const insertBotConfigSchema = createInsertSchema(botConfigurations);

// Notification schema
export const notifications = sqliteTable("notifications", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  type: text("type").notNull(), // 'success', 'error', 'warning', 'info'
  title: text("title").notNull(),
  message: text("message").notNull(),
  timestamp: text("timestamp").default(String(new Date().toISOString())).notNull(),
  isRead: integer("is_read", { mode: "boolean" }).default(0).notNull(),
});

export const insertNotificationSchema = createInsertSchema(notifications);

// Bot Status schema
export const botStatus = sqliteTable("bot_status", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  status: text("status").notNull(), // 'active', 'inactive', 'error'
  message: text("message"),
  lastStartTime: text("last_start_time").default(String(new Date().toISOString())),
  lastStopTime: text("last_stop_time"),
  statsData: text("stats_data"),
  updatedAt: text("updated_at").default(String(new Date().toISOString())).notNull(),
});

export const insertBotStatusSchema = createInsertSchema(botStatus);

// Types
export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;

export type Wallet = typeof wallets.$inferSelect;
export type InsertWallet = z.infer<typeof insertWalletSchema>;

export type Transaction = typeof transactions.$inferSelect;
export type InsertTransaction = z.infer<typeof insertTransactionSchema>;

export type BotConfiguration = typeof botConfigurations.$inferSelect;
export type InsertBotConfiguration = z.infer<typeof insertBotConfigSchema>;

export type Notification = typeof notifications.$inferSelect;
export type InsertNotification = z.infer<typeof insertNotificationSchema>;

export type BotStatusData = typeof botStatus.$inferSelect;
export type InsertBotStatusData = z.infer<typeof insertBotStatusSchema>;
