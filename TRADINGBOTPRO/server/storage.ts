import { 
  User, InsertUser, 
  Wallet, InsertWallet, 
  Transaction, InsertTransaction, 
  BotConfiguration, InsertBotConfiguration, 
  Notification, InsertNotification,
  BotStatusData, InsertBotStatusData,
  users, wallets, transactions, botConfigurations, notifications, botStatus
} from "@shared/schema";
import { db } from "./db";
import { eq, desc, asc, and } from "drizzle-orm";

// Storage interface with all CRUD operations needed
export interface IStorage {
  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // Wallet methods
  getWallet(id: number): Promise<Wallet | undefined>;
  getWalletByAddress(address: string): Promise<Wallet | undefined>;
  createWallet(wallet: InsertWallet): Promise<Wallet>;
  getWallets(): Promise<Wallet[]>;
  getParentWallet(): Promise<Wallet | undefined>;
  getWalletsByLevel(level: number): Promise<Wallet[]>;
  
  // Transaction methods
  getTransaction(id: number): Promise<Transaction | undefined>;
  getTransactionByTxId(txId: string): Promise<Transaction | undefined>;
  createTransaction(transaction: InsertTransaction): Promise<Transaction>;
  updateTransaction(id: number, data: Partial<Transaction>): Promise<Transaction>;
  getTransactions(limit?: number): Promise<Transaction[]>;
  getTransactionsByType(type: string): Promise<Transaction[]>;
  getTransactionStats(): Promise<{ total: number, buys: number, sells: number }>;
  
  // Bot Configuration methods
  getBotConfig(): Promise<BotConfiguration | undefined>;
  createBotConfig(config: InsertBotConfiguration): Promise<BotConfiguration>;
  updateBotConfig(id: number, data: Partial<BotConfiguration>): Promise<BotConfiguration>;
  
  // Notification methods
  getNotification(id: number): Promise<Notification | undefined>;
  createNotification(notification: InsertNotification): Promise<Notification>;
  getNotifications(limit?: number): Promise<Notification[]>;
  markNotificationAsRead(id: number): Promise<Notification>;
  
  // Bot Status methods
  getBotStatus(): Promise<BotStatusData | undefined>;
  createBotStatus(status: InsertBotStatusData): Promise<BotStatusData>;
  updateBotStatus(id: number, data: Partial<BotStatusData>): Promise<BotStatusData>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private wallets: Map<number, Wallet>;
  private transactions: Map<number, Transaction>;
  private botConfigs: Map<number, BotConfiguration>;
  private notifications: Map<number, Notification>;
  private botStatuses: Map<number, BotStatusData>;
  
  private currentUserId: number;
  private currentWalletId: number;
  private currentTransactionId: number;
  private currentBotConfigId: number;
  private currentNotificationId: number;
  private currentBotStatusId: number;

  constructor() {
    this.users = new Map();
    this.wallets = new Map();
    this.transactions = new Map();
    this.botConfigs = new Map();
    this.notifications = new Map();
    this.botStatuses = new Map();
    
    this.currentUserId = 1;
    this.currentWalletId = 1;
    this.currentTransactionId = 1;
    this.currentBotConfigId = 1;
    this.currentNotificationId = 1;
    this.currentBotStatusId = 1;
    
    // Initialize with sample data
    this.setupInitialData();
  }
  
  // User methods
  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }
  
  // Wallet methods
  async getWallet(id: number): Promise<Wallet | undefined> {
    return this.wallets.get(id);
  }
  
  async getWalletByAddress(address: string): Promise<Wallet | undefined> {
    return Array.from(this.wallets.values()).find(
      (wallet) => wallet.address === address,
    );
  }
  
  async createWallet(insertWallet: InsertWallet): Promise<Wallet> {
    const id = this.currentWalletId++;
    const wallet: Wallet = { 
      ...insertWallet, 
      id, 
      dateAdded: new Date() 
    };
    this.wallets.set(id, wallet);
    return wallet;
  }
  
  async getWallets(): Promise<Wallet[]> {
    return Array.from(this.wallets.values());
  }
  
  async getParentWallet(): Promise<Wallet | undefined> {
    return Array.from(this.wallets.values()).find(
      (wallet) => wallet.isParent === true,
    );
  }
  
  async getWalletsByLevel(level: number): Promise<Wallet[]> {
    return Array.from(this.wallets.values()).filter(
      (wallet) => wallet.level === level,
    );
  }
  
  // Transaction methods
  async getTransaction(id: number): Promise<Transaction | undefined> {
    return this.transactions.get(id);
  }
  
  async getTransactionByTxId(txId: string): Promise<Transaction | undefined> {
    return Array.from(this.transactions.values()).find(
      (tx) => tx.txId === txId,
    );
  }
  
  async createTransaction(insertTransaction: InsertTransaction): Promise<Transaction> {
    const id = this.currentTransactionId++;
    const transaction: Transaction = { 
      ...insertTransaction, 
      id, 
      timestamp: new Date() 
    };
    this.transactions.set(id, transaction);
    return transaction;
  }
  
  async updateTransaction(id: number, data: Partial<Transaction>): Promise<Transaction> {
    const transaction = this.transactions.get(id);
    if (!transaction) {
      throw new Error(`Transaction with id ${id} not found`);
    }
    
    const updatedTransaction = { ...transaction, ...data };
    this.transactions.set(id, updatedTransaction);
    return updatedTransaction;
  }
  
  async getTransactions(limit?: number): Promise<Transaction[]> {
    const transactions = Array.from(this.transactions.values())
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    
    return limit ? transactions.slice(0, limit) : transactions;
  }
  
  async getTransactionsByType(type: string): Promise<Transaction[]> {
    return Array.from(this.transactions.values())
      .filter(tx => tx.type === type)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }
  
  async getTransactionStats(): Promise<{ total: number, buys: number, sells: number }> {
    const transactions = Array.from(this.transactions.values());
    const buys = transactions.filter(tx => tx.type === 'buy').length;
    const sells = transactions.filter(tx => tx.type === 'sell').length;
    
    return {
      total: transactions.length,
      buys,
      sells
    };
  }
  
  // Bot Configuration methods
  async getBotConfig(): Promise<BotConfiguration | undefined> {
    // Always return the first config for simplicity
    const configs = Array.from(this.botConfigs.values());
    return configs.length > 0 ? configs[0] : undefined;
  }
  
  async createBotConfig(insertConfig: InsertBotConfiguration): Promise<BotConfiguration> {
    const id = this.currentBotConfigId++;
    const config: BotConfiguration = { 
      ...insertConfig, 
      id, 
      isActive: true,
      lastUpdated: new Date() 
    };
    this.botConfigs.set(id, config);
    return config;
  }
  
  async updateBotConfig(id: number, data: Partial<BotConfiguration>): Promise<BotConfiguration> {
    const config = this.botConfigs.get(id);
    if (!config) {
      throw new Error(`Bot configuration with id ${id} not found`);
    }
    
    const updatedConfig = { 
      ...config, 
      ...data, 
      lastUpdated: new Date() 
    };
    this.botConfigs.set(id, updatedConfig);
    return updatedConfig;
  }
  
  // Notification methods
  async getNotification(id: number): Promise<Notification | undefined> {
    return this.notifications.get(id);
  }
  
  async createNotification(insertNotification: InsertNotification): Promise<Notification> {
    const id = this.currentNotificationId++;
    const notification: Notification = { 
      ...insertNotification, 
      id, 
      timestamp: new Date() 
    };
    this.notifications.set(id, notification);
    return notification;
  }
  
  async getNotifications(limit?: number): Promise<Notification[]> {
    const notifications = Array.from(this.notifications.values())
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    
    return limit ? notifications.slice(0, limit) : notifications;
  }
  
  async markNotificationAsRead(id: number): Promise<Notification> {
    const notification = this.notifications.get(id);
    if (!notification) {
      throw new Error(`Notification with id ${id} not found`);
    }
    
    const updatedNotification = { ...notification, isRead: true };
    this.notifications.set(id, updatedNotification);
    return updatedNotification;
  }
  
  // Bot Status methods
  async getBotStatus(): Promise<BotStatusData | undefined> {
    // Always return the first status for simplicity
    const statuses = Array.from(this.botStatuses.values());
    return statuses.length > 0 ? statuses[0] : undefined;
  }
  
  async createBotStatus(insertStatus: InsertBotStatusData): Promise<BotStatusData> {
    const id = this.currentBotStatusId++;
    const status: BotStatusData = { 
      ...insertStatus, 
      id, 
      updatedAt: new Date() 
    };
    this.botStatuses.set(id, status);
    return status;
  }
  
  async updateBotStatus(id: number, data: Partial<BotStatusData>): Promise<BotStatusData> {
    const status = this.botStatuses.get(id);
    if (!status) {
      throw new Error(`Bot status with id ${id} not found`);
    }
    
    const updatedStatus = { 
      ...status, 
      ...data, 
      updatedAt: new Date() 
    };
    this.botStatuses.set(id, updatedStatus);
    return updatedStatus;
  }
  
  // Initialize with sample data
  private setupInitialData() {
    // Create default user
    this.createUser({
      username: "johndoe",
      password: "password123",
      avatarInitials: "JD",
      role: "user"
    });
    
    // Create default wallet (parent)
    this.createWallet({
      address: "5XmTxU8SJJ7fYnQ5CdY9aNM8yD6MhGPmXf4s15rZ8eG5",
      label: "Parent Wallet",
      isParent: true,
      level: 1,
      isActive: true
    });
    
    // Create secondary wallets
    for (let i = 2; i <= 4; i++) {
      const numWallets = i === 2 ? 3 : i === 3 ? 8 : 17;
      for (let j = 0; j < numWallets; j++) {
        this.createWallet({
          address: `wallet_level_${i}_${j}`,
          label: `Level ${i} Wallet ${j}`,
          isParent: false,
          level: i,
          isActive: true
        });
      }
    }
    
    // Create default bot configuration
    this.createBotConfig({
      parentWalletAddress: "5XmTxU8SJJ7fYnQ5CdY9aNM8yD6MhGPmXf4s15rZ8eG5",
      minAmount: 0.1,
      maxAmount: 10,
      tipAmount: 0.01,
      gasFee: 0.005,
      trackingDepth: 4,
      volumeThreshold: 2.5,
      mcThreshold: 1,
      tokenAge: 30,
      profitTarget: 30,
      stopLoss: 10,
      antiMevProtection: true
    });
    
    // Create default bot status
    this.createBotStatus({
      status: "active",
      message: "Monitoring Transactions",
      lastStartTime: new Date(),
      statsData: {
        transactionsMonitored: 248,
        totalWalletsTracked: 29,
        buyOpportunitiesFound: 35,
        sellSignalsGenerated: 23,
        balance: 82.4
      }
    });
    
    // Create sample transactions
    const tokenSymbols = ["BONK", "WIF", "SOL", "DUST"];
    const types = ["buy", "sell"];
    const statuses = ["completed", "failed", "processing"];
    const transactionTypes = ["normal", "raydium_swap", "wsol_buy"];
    
    for (let i = 0; i < 4; i++) {
      const txType = i === 1 ? "sell" : "buy";
      const txStatus = i === 3 ? "failed" : i === 2 ? "processing" : "completed";
      
      this.createTransaction({
        txId: `tx_${i}`,
        fromWallet: "5XmTxU8SJJ7fYnQ5CdY9aNM8yD6MhGPmXf4s15rZ8eG5",
        toWallet: `wallet_destination_${i}`,
        tokenSymbol: tokenSymbols[i],
        amount: i === 0 ? 2.5 : i === 1 ? 1.2 : i === 2 ? 0.8 : 0.5,
        type: txType,
        transactionType: transactionTypes[i % 3],
        status: txStatus,
        volume: 2500000,
        marketCap: 1000000,
        tokenAge: 30,
        failReason: txStatus === "failed" ? "Insufficient liquidity" : undefined,
        retryCount: txStatus === "failed" ? 3 : 0
      });
    }
    
    // Create sample notifications
    const notificationTypes = ["success", "error", "warning", "info"];
    const notificationTitles = [
      "Buy Order Executed", 
      "Buy Order Failed", 
      "Auto-Retry Triggered", 
      "Bot Status"
    ];
    const notificationMessages = [
      "Successfully bought 2.5 SOL of BONK",
      "Failed to buy DUST: Insufficient liquidity",
      "Retrying buy order for SOL after temporary failure",
      "Bot started monitoring transactions"
    ];
    
    for (let i = 0; i < 4; i++) {
      const timestamp = new Date();
      timestamp.setMinutes(timestamp.getMinutes() - (i === 0 ? 2 : i === 1 ? 32 : i === 2 ? 18 : 45));
      
      this.createNotification({
        type: notificationTypes[i],
        title: notificationTitles[i],
        message: notificationMessages[i],
        isRead: false
      });
    }
  }
}

// Database Storage implementation
export class DatabaseStorage implements IStorage {
  // User methods
  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db.insert(users).values(insertUser).returning();
    return user;
  }
  
  // Wallet methods
  async getWallet(id: number): Promise<Wallet | undefined> {
    const [wallet] = await db.select().from(wallets).where(eq(wallets.id, id));
    return wallet;
  }
  
  async getWalletByAddress(address: string): Promise<Wallet | undefined> {
    const [wallet] = await db.select().from(wallets).where(eq(wallets.address, address));
    return wallet;
  }
  
  async createWallet(insertWallet: InsertWallet): Promise<Wallet> {
    const [wallet] = await db.insert(wallets).values(insertWallet).returning();
    return wallet;
  }
  
  async getWallets(): Promise<Wallet[]> {
    return await db.select().from(wallets);
  }
  
  async getParentWallet(): Promise<Wallet | undefined> {
    const [wallet] = await db.select().from(wallets).where(eq(wallets.isParent, true));
    return wallet;
  }
  
  async getWalletsByLevel(level: number): Promise<Wallet[]> {
    return await db.select().from(wallets).where(eq(wallets.level, level.toString()));
  }
  
  // Transaction methods
  async getTransaction(id: number): Promise<Transaction | undefined> {
    const [transaction] = await db.select().from(transactions).where(eq(transactions.id, id));
    return transaction;
  }
  
  async getTransactionByTxId(txId: string): Promise<Transaction | undefined> {
    const [transaction] = await db.select().from(transactions).where(eq(transactions.txId, txId));
    return transaction;
  }
  
  async createTransaction(insertTransaction: InsertTransaction): Promise<Transaction> {
    const [transaction] = await db.insert(transactions).values(insertTransaction).returning();
    return transaction;
  }
  
  async updateTransaction(id: number, data: Partial<Transaction>): Promise<Transaction> {
    const [updatedTransaction] = await db
      .update(transactions)
      .set(data)
      .where(eq(transactions.id, id))
      .returning();
      
    if (!updatedTransaction) {
      throw new Error(`Transaction with id ${id} not found`);
    }
    
    return updatedTransaction;
  }
  
  async getTransactions(limit?: number): Promise<Transaction[]> {
    const query = db.select().from(transactions).orderBy(desc(transactions.timestamp));
    
    if (limit) {
      query.limit(limit);
    }
    
    return await query;
  }
  
  async getTransactionsByType(type: string): Promise<Transaction[]> {
    return await db
      .select()
      .from(transactions)
      .where(eq(transactions.type, type))
      .orderBy(desc(transactions.timestamp));
  }
  
  async getTransactionStats(): Promise<{ total: number, buys: number, sells: number }> {
    const allTransactions = await db.select().from(transactions);
    const buys = allTransactions.filter(tx => tx.type === 'buy').length;
    const sells = allTransactions.filter(tx => tx.type === 'sell').length;
    
    return {
      total: allTransactions.length,
      buys,
      sells
    };
  }
  
  // Bot Configuration methods
  async getBotConfig(): Promise<BotConfiguration | undefined> {
    const [config] = await db.select().from(botConfigurations).orderBy(desc(botConfigurations.updatedAt)).limit(1);
    return config;
  }
  
  async createBotConfig(insertConfig: InsertBotConfiguration): Promise<BotConfiguration> {
    const [config] = await db
      .insert(botConfigurations)
      .values({
        ...insertConfig
      })
      .returning();
      
    return config;
  }
  
  async updateBotConfig(id: number, data: Partial<BotConfiguration>): Promise<BotConfiguration> {
    const [updatedConfig] = await db
      .update(botConfigurations)
      .set({
        ...data,
        updatedAt: new Date().toISOString()
      })
      .where(eq(botConfigurations.id, id))
      .returning();
      
    if (!updatedConfig) {
      throw new Error(`Bot configuration with id ${id} not found`);
    }
    
    return updatedConfig;
  }
  
  // Notification methods
  async getNotification(id: number): Promise<Notification | undefined> {
    const [notification] = await db.select().from(notifications).where(eq(notifications.id, id));
    return notification;
  }
  
  async createNotification(insertNotification: InsertNotification): Promise<Notification> {
    const [notification] = await db.insert(notifications).values(insertNotification).returning();
    return notification;
  }
  
  async getNotifications(limit?: number): Promise<Notification[]> {
    const query = db.select().from(notifications).orderBy(desc(notifications.timestamp));
    
    if (limit) {
      query.limit(limit);
    }
    
    return await query;
  }
  
  async markNotificationAsRead(id: number): Promise<Notification> {
    const [updatedNotification] = await db
      .update(notifications)
      .set({ isRead: true })
      .where(eq(notifications.id, id))
      .returning();
      
    if (!updatedNotification) {
      throw new Error(`Notification with id ${id} not found`);
    }
    
    return updatedNotification;
  }
  
  // Bot Status methods
  async getBotStatus(): Promise<BotStatusData | undefined> {
    const [status] = await db.select().from(botStatus).orderBy(desc(botStatus.updatedAt)).limit(1);
    return status;
  }
  
  async createBotStatus(insertStatus: InsertBotStatusData): Promise<BotStatusData> {
    const [status] = await db.insert(botStatus).values(insertStatus).returning();
    return status;
  }
  
  async updateBotStatus(id: number, data: Partial<BotStatusData>): Promise<BotStatusData> {
    const [updatedStatus] = await db
      .update(botStatus)
      .set({
        ...data,
        updatedAt: new Date().toISOString()
      })
      .where(eq(botStatus.id, id))
      .returning();
      
    if (!updatedStatus) {
      throw new Error(`Bot status with id ${id} not found`);
    }
    
    return updatedStatus;
  }
}

// Create a storage variable
let storageImplementation: IStorage;

// Use DatabaseStorage by default, fallback to MemStorage if database connection fails
try {
  storageImplementation = new DatabaseStorage();
  console.log("Using DatabaseStorage for data persistence");
  
  // Seed initial data if needed
  (async () => {
    try {
      // Check if users exist, if not, seed initial data
      const users = await storageImplementation.getUser(1);
      if (!users) {
        console.log("No data found, seeding initial data...");
        
        // Create default user
        await storageImplementation.createUser({
          username: "johndoe",
          password: "password123",
          avatarInitials: "JD",
          role: "user"
        });
        
        // Create default wallet (parent)
        await storageImplementation.createWallet({
          address: "5XmTxU8SJJ7fYnQ5CdY9aNM8yD6MhGPmXf4s15rZ8eG5",
          label: "Parent Wallet",
          isParent: true,
          level: "1",
          isActive: true
        });
        
        // Create secondary wallets for levels 2-4
        for (let i = 2; i <= 4; i++) {
          const numWallets = i === 2 ? 3 : i === 3 ? 8 : 17;
          for (let j = 0; j < numWallets; j++) {
            await storageImplementation.createWallet({
              address: `wallet_level_${i}_${j}`,
              label: `Level ${i} Wallet ${j}`,
              isParent: false,
              level: i.toString(),
              isActive: true
            });
          }
        }
        
        // Create default bot configuration
        await storageImplementation.createBotConfig({
          parentWalletAddress: "5XmTxU8SJJ7fYnQ5CdY9aNM8yD6MhGPmXf4s15rZ8eG5",
          minAmount: "0.1",
          maxAmount: "10",
          tipAmount: "0.01",
          gasFee: "0.005",
          trackingDepth: "4",
          volumeThreshold: "2.5",
          mcThreshold: "1",
          tokenAge: "30",
          profitTarget: "30",
          stopLoss: "10",
          antiMevProtection: true
        });
        
        // Create default bot status
        await storageImplementation.createBotStatus({
          status: "active",
          message: "Monitoring Transactions",
          lastStartTime: new Date(),
          statsData: {
            transactionsMonitored: 248,
            totalWalletsTracked: 29,
            buyOpportunitiesFound: 35,
            sellSignalsGenerated: 23,
            balance: 82.4
          }
        });
        
        // Create sample transactions
        const tokenSymbols = ["BONK", "WIF", "SOL", "DUST"];
        const transactionTypes = ["normal", "raydium_swap", "wsol_buy"];
        
        for (let i = 0; i < 4; i++) {
          const txType = i === 1 ? "sell" : "buy";
          const txStatus = i === 3 ? "failed" : i === 2 ? "processing" : "completed";
          
          await storageImplementation.createTransaction({
            txId: `tx_${i}`,
            fromWallet: "5XmTxU8SJJ7fYnQ5CdY9aNM8yD6MhGPmXf4s15rZ8eG5",
            toWallet: `wallet_destination_${i}`,
            tokenSymbol: tokenSymbols[i],
            amount: (i === 0 ? 2.5 : i === 1 ? 1.2 : i === 2 ? 0.8 : 0.5).toString(),
            type: txType,
            transactionType: transactionTypes[i % 3],
            status: txStatus,
            volume: "2500000",
            marketCap: "1000000",
            tokenAge: "30",
            failReason: txStatus === "failed" ? "Insufficient liquidity" : null,
            retryCount: txStatus === "failed" ? "3" : "0"
          });
        }
        
        // Create sample notifications
        const notificationTypes = ["success", "error", "warning", "info"];
        const notificationTitles = [
          "Buy Order Executed", 
          "Buy Order Failed", 
          "Auto-Retry Triggered", 
          "Bot Status"
        ];
        const notificationMessages = [
          "Successfully bought 2.5 SOL of BONK",
          "Failed to buy DUST: Insufficient liquidity",
          "Retrying buy order for SOL after temporary failure",
          "Bot started monitoring transactions"
        ];
        
        for (let i = 0; i < 4; i++) {
          await storageImplementation.createNotification({
            type: notificationTypes[i],
            title: notificationTitles[i],
            message: notificationMessages[i],
            isRead: false
          });
        }
        
        console.log("Initial data seeded successfully");
      }
    } catch (error) {
      console.error("Error seeding initial data:", error);
    }
  })();
} catch (error) {
  console.error("Error initializing DatabaseStorage:", error);
  console.log("Falling back to MemStorage");
  storageImplementation = new MemStorage();
}

// Export the storage implementation
export const storage = storageImplementation;
