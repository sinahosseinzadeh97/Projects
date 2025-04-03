import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer, WebSocket } from "ws";
import { storage } from "./storage";
import { mlService } from "./ml-service";
import {
  insertBotConfigSchema,
  insertTransactionSchema,
  insertWalletSchema,
  insertNotificationSchema,
  insertBotStatusSchema
} from "@shared/schema";
import { z } from "zod";

// Keep track of all connected WebSocket clients
const clients = new Set<WebSocket>();

// Broadcast to all connected clients
function broadcast(message: any) {
  clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });
}

export async function registerRoutes(app: Express): Promise<Server> {
  const httpServer = createServer(app);

  // Set up WebSocket server
  const wss = new WebSocketServer({ server: httpServer, path: '/ws' });

  wss.on('connection', (ws) => {
    clients.add(ws);
    
    // Send initial data to newly connected client
    sendInitialData(ws);
    
    ws.on('message', async (message) => {
      try {
        const data = JSON.parse(message.toString());
        
        // Handle different message types
        if (data.type === 'startBot') {
          await handleStartBot();
        } else if (data.type === 'stopBot') {
          await handleStopBot();
        } else if (data.type === 'restartBot') {
          await handleRestartBot();
        }
      } catch (error) {
        console.error('Error handling WebSocket message:', error);
      }
    });
    
    ws.on('close', () => {
      clients.delete(ws);
    });
  });

  // User routes
  app.get('/api/user', async (req: Request, res: Response) => {
    try {
      const user = await storage.getUserByUsername('johndoe');
      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }
      
      // Don't return the password
      const { password, ...userWithoutPassword } = user;
      res.json(userWithoutPassword);
    } catch (error) {
      res.status(500).json({ message: `Error fetching user: ${error}` });
    }
  });

  // Bot status routes
  app.get('/api/bot/status', async (req: Request, res: Response) => {
    try {
      const status = await storage.getBotStatus();
      if (!status) {
        return res.status(404).json({ message: 'Bot status not found' });
      }
      res.json(status);
    } catch (error) {
      res.status(500).json({ message: `Error fetching bot status: ${error}` });
    }
  });

  app.post('/api/bot/start', async (req: Request, res: Response) => {
    try {
      await handleStartBot();
      res.json({ message: 'Bot started successfully' });
    } catch (error) {
      res.status(500).json({ message: `Error starting bot: ${error}` });
    }
  });

  app.post('/api/bot/stop', async (req: Request, res: Response) => {
    try {
      await handleStopBot();
      res.json({ message: 'Bot stopped successfully' });
    } catch (error) {
      res.status(500).json({ message: `Error stopping bot: ${error}` });
    }
  });

  app.post('/api/bot/restart', async (req: Request, res: Response) => {
    try {
      await handleRestartBot();
      res.json({ message: 'Bot restarted successfully' });
    } catch (error) {
      res.status(500).json({ message: `Error restarting bot: ${error}` });
    }
  });

  // Bot configuration routes
  app.get('/api/bot/config', async (req: Request, res: Response) => {
    try {
      const config = await storage.getBotConfig();
      if (!config) {
        return res.status(404).json({ message: 'Bot configuration not found' });
      }
      res.json(config);
    } catch (error) {
      res.status(500).json({ message: `Error fetching bot configuration: ${error}` });
    }
  });

  app.post('/api/bot/config', async (req: Request, res: Response) => {
    try {
      const validatedData = insertBotConfigSchema.parse(req.body);
      
      const existingConfig = await storage.getBotConfig();
      let config;
      
      if (existingConfig) {
        config = await storage.updateBotConfig(existingConfig.id, validatedData);
      } else {
        config = await storage.createBotConfig(validatedData);
      }
      
      // Create notification
      await storage.createNotification({
        type: 'info',
        title: 'Configuration Updated',
        message: 'Bot configuration updated successfully',
        isRead: false
      });
      
      // Broadcast the updated config to all clients
      broadcast({ type: 'configUpdated', data: config });
      
      res.json(config);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: 'Invalid data', errors: error.errors });
      }
      res.status(500).json({ message: `Error updating bot configuration: ${error}` });
    }
  });

  // Wallet routes
  app.get('/api/wallets', async (req: Request, res: Response) => {
    try {
      const wallets = await storage.getWallets();
      res.json(wallets);
    } catch (error) {
      res.status(500).json({ message: `Error fetching wallets: ${error}` });
    }
  });

  app.post('/api/wallets', async (req: Request, res: Response) => {
    try {
      const validatedData = insertWalletSchema.parse(req.body);
      
      // Check if wallet already exists
      const existingWallet = await storage.getWalletByAddress(validatedData.address);
      if (existingWallet) {
        return res.status(400).json({ message: 'Wallet with this address already exists' });
      }
      
      const wallet = await storage.createWallet(validatedData);
      
      // Broadcast the new wallet to all clients
      broadcast({ type: 'walletAdded', data: wallet });
      
      res.status(201).json(wallet);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: 'Invalid data', errors: error.errors });
      }
      res.status(500).json({ message: `Error creating wallet: ${error}` });
    }
  });

  // Transaction routes
  app.get('/api/transactions', async (req: Request, res: Response) => {
    try {
      const limit = req.query.limit ? parseInt(req.query.limit as string) : undefined;
      const transactions = await storage.getTransactions(limit);
      res.json(transactions);
    } catch (error) {
      res.status(500).json({ message: `Error fetching transactions: ${error}` });
    }
  });

  app.get('/api/transactions/stats', async (req: Request, res: Response) => {
    try {
      const stats = await storage.getTransactionStats();
      res.json(stats);
    } catch (error) {
      res.status(500).json({ message: `Error fetching transaction stats: ${error}` });
    }
  });

  app.post('/api/transactions', async (req: Request, res: Response) => {
    try {
      const validatedData = insertTransactionSchema.parse(req.body);
      
      // Check if transaction already exists
      const existingTransaction = await storage.getTransactionByTxId(validatedData.txId);
      if (existingTransaction) {
        return res.status(400).json({ message: 'Transaction with this ID already exists' });
      }
      
      const transaction = await storage.createTransaction(validatedData);
      
      // Create notification based on transaction type and status
      let notificationType = 'info';
      let notificationTitle = '';
      let notificationMessage = '';
      
      if (transaction.type === 'buy') {
        if (transaction.status === 'completed') {
          notificationType = 'success';
          notificationTitle = 'Buy Order Executed';
          notificationMessage = `Successfully bought ${transaction.amount} SOL of ${transaction.tokenSymbol}`;
        } else if (transaction.status === 'failed') {
          notificationType = 'error';
          notificationTitle = 'Buy Order Failed';
          notificationMessage = `Failed to buy ${transaction.tokenSymbol}: ${transaction.failReason || 'Unknown error'}`;
        } else {
          notificationType = 'warning';
          notificationTitle = 'Buy Order Processing';
          notificationMessage = `Processing buy order for ${transaction.amount} SOL of ${transaction.tokenSymbol}`;
        }
      } else if (transaction.type === 'sell') {
        if (transaction.status === 'completed') {
          notificationType = 'success';
          notificationTitle = 'Sell Order Executed';
          notificationMessage = `Successfully sold ${transaction.amount} SOL of ${transaction.tokenSymbol}`;
        } else if (transaction.status === 'failed') {
          notificationType = 'error';
          notificationTitle = 'Sell Order Failed';
          notificationMessage = `Failed to sell ${transaction.tokenSymbol}: ${transaction.failReason || 'Unknown error'}`;
        } else {
          notificationType = 'warning';
          notificationTitle = 'Sell Order Processing';
          notificationMessage = `Processing sell order for ${transaction.amount} SOL of ${transaction.tokenSymbol}`;
        }
      }
      
      if (notificationTitle) {
        await storage.createNotification({
          type: notificationType as any,
          title: notificationTitle,
          message: notificationMessage,
          isRead: false
        });
      }
      
      // Broadcast the new transaction to all clients
      broadcast({ type: 'transactionAdded', data: transaction });
      
      res.status(201).json(transaction);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: 'Invalid data', errors: error.errors });
      }
      res.status(500).json({ message: `Error creating transaction: ${error}` });
    }
  });

  // Notification routes
  app.get('/api/notifications', async (req: Request, res: Response) => {
    try {
      const limit = req.query.limit ? parseInt(req.query.limit as string) : undefined;
      const notifications = await storage.getNotifications(limit);
      res.json(notifications);
    } catch (error) {
      res.status(500).json({ message: `Error fetching notifications: ${error}` });
    }
  });

  app.post('/api/notifications', async (req: Request, res: Response) => {
    try {
      const validatedData = insertNotificationSchema.parse(req.body);
      const notification = await storage.createNotification(validatedData);
      
      // Broadcast the new notification to all clients
      broadcast({ type: 'notificationAdded', data: notification });
      
      res.status(201).json(notification);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: 'Invalid data', errors: error.errors });
      }
      res.status(500).json({ message: `Error creating notification: ${error}` });
    }
  });

  app.post('/api/notifications/:id/read', async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      const notification = await storage.markNotificationAsRead(id);
      
      // Broadcast the updated notification to all clients
      broadcast({ type: 'notificationUpdated', data: notification });
      
      res.json(notification);
    } catch (error) {
      res.status(500).json({ message: `Error marking notification as read: ${error}` });
    }
  });

  // Bot mock trading functions
  app.post('/api/bot/buy', async (req: Request, res: Response) => {
    try {
      const { tokenSymbol, amount } = req.body;
      
      if (!tokenSymbol || !amount) {
        return res.status(400).json({ message: 'Token symbol and amount are required' });
      }
      
      // Simulate a buy transaction
      const transaction = await storage.createTransaction({
        txId: `tx_buy_${Date.now()}`,
        fromWallet: "5XmTxU8SJJ7fYnQ5CdY9aNM8yD6MhGPmXf4s15rZ8eG5",
        toWallet: `wallet_destination_${Date.now()}`,
        tokenSymbol,
        amount,
        type: 'buy',
        transactionType: 'normal',
        status: 'completed',
        volume: 2500000,
        marketCap: 1000000,
        tokenAge: 30,
        retryCount: 0
      });
      
      // Create notification
      const notification = await storage.createNotification({
        type: 'success',
        title: 'Buy Order Executed',
        message: `Successfully bought ${amount} SOL of ${tokenSymbol}`,
        isRead: false
      });
      
      // Broadcast updates
      broadcast({ type: 'transactionAdded', data: transaction });
      broadcast({ type: 'notificationAdded', data: notification });
      
      res.json({ transaction, notification });
    } catch (error) {
      res.status(500).json({ message: `Error executing buy order: ${error}` });
    }
  });

  app.post('/api/bot/sell', async (req: Request, res: Response) => {
    try {
      const { tokenSymbol, amount } = req.body;
      
      if (!tokenSymbol || !amount) {
        return res.status(400).json({ message: 'Token symbol and amount are required' });
      }
      
      // Simulate a sell transaction
      const transaction = await storage.createTransaction({
        txId: `tx_sell_${Date.now()}`,
        fromWallet: `wallet_source_${Date.now()}`,
        toWallet: "5XmTxU8SJJ7fYnQ5CdY9aNM8yD6MhGPmXf4s15rZ8eG5",
        tokenSymbol,
        amount,
        type: 'sell',
        transactionType: 'normal',
        status: 'completed',
        volume: 2500000,
        marketCap: 1000000,
        tokenAge: 30,
        retryCount: 0
      });
      
      // Create notification
      const notification = await storage.createNotification({
        type: 'success',
        title: 'Sell Order Executed',
        message: `Successfully sold ${amount} SOL of ${tokenSymbol}`,
        isRead: false
      });
      
      // Broadcast updates
      broadcast({ type: 'transactionAdded', data: transaction });
      broadcast({ type: 'notificationAdded', data: notification });
      
      res.json({ transaction, notification });
    } catch (error) {
      res.status(500).json({ message: `Error executing sell order: ${error}` });
    }
  });

  // ML Service Routes
  app.post('/api/ml/sentiment', async (req: Request, res: Response) => {
    try {
      const { tokenSymbol, content } = req.body;
      
      if (!tokenSymbol || !content) {
        return res.status(400).json({ message: 'Token symbol and content are required' });
      }
      
      // Check if ML is enabled in config
      const config = await storage.getBotConfig();
      if (!config?.sentimentAnalysisEnabled) {
        return res.status(400).json({ message: 'Sentiment analysis is not enabled in bot configuration' });
      }
      
      // Check for API key
      if (!config.huggingfaceApiKey) {
        return res.status(400).json({ message: 'Hugging Face API key is required for sentiment analysis' });
      }
      
      const result = await mlService.analyzeSentiment(tokenSymbol, content);
      
      if (!result) {
        return res.status(500).json({ message: 'Failed to analyze sentiment' });
      }
      
      res.json(result);
    } catch (error) {
      res.status(500).json({ message: `Error analyzing sentiment: ${error}` });
    }
  });
  
  app.post('/api/ml/predict-price', async (req: Request, res: Response) => {
    try {
      const { tokenSymbol, historicalPrices } = req.body;
      
      if (!tokenSymbol || !historicalPrices || !Array.isArray(historicalPrices)) {
        return res.status(400).json({ message: 'Token symbol and historical prices array are required' });
      }
      
      // Check if ML is enabled in config
      const config = await storage.getBotConfig();
      if (!config?.aiPredictionEnabled) {
        return res.status(400).json({ message: 'AI price prediction is not enabled in bot configuration' });
      }
      
      // Check for API key
      if (!config.huggingfaceApiKey) {
        return res.status(400).json({ message: 'Hugging Face API key is required for price prediction' });
      }
      
      const result = await mlService.predictPriceMovement(tokenSymbol, historicalPrices);
      
      if (!result) {
        return res.status(500).json({ message: 'Failed to predict price movement' });
      }
      
      res.json(result);
    } catch (error) {
      res.status(500).json({ message: `Error predicting price movement: ${error}` });
    }
  });
  
  app.post('/api/ml/trade-decision', async (req: Request, res: Response) => {
    try {
      const { tokenSymbol, currentPrice, historicalPrices, newsContent } = req.body;
      
      if (!tokenSymbol || !currentPrice || !historicalPrices || !Array.isArray(historicalPrices)) {
        return res.status(400).json({ 
          message: 'Token symbol, current price, and historical prices array are required' 
        });
      }
      
      // Check if ML is enabled in config
      const config = await storage.getBotConfig();
      if (!config?.aiPredictionEnabled && !config?.sentimentAnalysisEnabled) {
        return res.status(400).json({ 
          message: 'AI price prediction or sentiment analysis must be enabled in bot configuration' 
        });
      }
      
      // Check for API key
      if (!config.huggingfaceApiKey) {
        return res.status(400).json({ 
          message: 'Hugging Face API key is required for ML-based trade decisions' 
        });
      }
      
      const shouldTrade = await mlService.shouldExecuteTrade(
        tokenSymbol, 
        currentPrice, 
        historicalPrices, 
        newsContent
      );
      
      res.json({ shouldTrade });
    } catch (error) {
      res.status(500).json({ message: `Error making trade decision: ${error}` });
    }
  });

  return httpServer;
}

// Send initial data to a newly connected WebSocket client
async function sendInitialData(ws: WebSocket) {
  try {
    const [botStatus, botConfig, transactions, notifications, wallets, stats] = await Promise.all([
      storage.getBotStatus(),
      storage.getBotConfig(),
      storage.getTransactions(4),
      storage.getNotifications(4),
      storage.getWallets(),
      storage.getTransactionStats()
    ]);
    
    ws.send(JSON.stringify({ 
      type: 'initialData', 
      data: {
        botStatus,
        botConfig,
        transactions,
        notifications,
        wallets,
        stats
      }
    }));
  } catch (error) {
    console.error('Error sending initial data:', error);
  }
}

// Bot control handlers
async function handleStartBot() {
  const status = await storage.getBotStatus();
  
  if (status) {
    await storage.updateBotStatus(status.id, {
      status: 'active',
      message: 'Monitoring Transactions',
      lastStartTime: new Date().toISOString()
    });
  } else {
    await storage.createBotStatus({
      status: 'active',
      message: 'Monitoring Transactions',
      lastStartTime: new Date().toISOString(),
      statsData: JSON.stringify({
        transactionsMonitored: 0,
        totalWalletsTracked: 0,
        buyOpportunitiesFound: 0,
        sellSignalsGenerated: 0,
        balance: 0
      })
    });
  }
  
  const notification = await storage.createNotification({
    type: 'info',
    title: 'Bot Started',
    message: 'Bot started monitoring transactions',
    isRead: false
  });
  
  const updatedStatus = await storage.getBotStatus();
  
  // Broadcast updates
  broadcast({ type: 'botStatusUpdated', data: updatedStatus });
  broadcast({ type: 'notificationAdded', data: notification });
}

async function handleStopBot() {
  const status = await storage.getBotStatus();
  
  if (status) {
    await storage.updateBotStatus(status.id, {
      status: 'inactive',
      message: 'Bot stopped',
      lastStopTime: new Date().toISOString()
    });
  }
  
  const notification = await storage.createNotification({
    type: 'warning',
    title: 'Bot Stopped',
    message: 'Bot has stopped monitoring transactions',
    isRead: false
  });
  
  const updatedStatus = await storage.getBotStatus();
  
  // Broadcast updates
  broadcast({ type: 'botStatusUpdated', data: updatedStatus });
  broadcast({ type: 'notificationAdded', data: notification });
}

async function handleRestartBot() {
  // First stop the bot
  await handleStopBot();
  
  // Then start it again
  await handleStartBot();
  
  const notification = await storage.createNotification({
    type: 'info',
    title: 'Bot Restarted',
    message: 'Bot has been restarted and is now monitoring transactions',
    isRead: false
  });
  
  // Broadcast notification
  broadcast({ type: 'notificationAdded', data: notification });
}
