import { HfInference } from '@huggingface/inference';
import { BotConfiguration } from '../shared/schema';
import { storage } from './storage';

interface SentimentResult {
  label: 'positive' | 'negative' | 'neutral';
  score: number;
}

interface PredictionResult {
  predictedPrice: number;
  direction: 'up' | 'down' | 'stable';
  confidence: number;
}

export class MLService {
  private hf: HfInference | null = null;
  private config: BotConfiguration | null = null;
  private defaultModel = 'distilbert-base-uncased-finetuned-sst-2-english'; // A commonly available sentiment model
  
  constructor() {
    this.initialize();
  }
  
  private async initialize() {
    try {
      // Load bot configuration to get settings
      try {
        this.config = await storage.getBotConfig() || null;
      } catch (error) {
        console.log('Unable to get bot config from database, using default settings');
        this.config = null;
      }
      
      // First try to use the environment variable
      const apiKey = process.env.HUGGINGFACE_API_KEY || this.config?.huggingfaceApiKey;
      
      if (apiKey) {
        this.hf = new HfInference(apiKey);
        console.log('ML service initialized with Hugging Face API');
        
        // If we're using env var but the config doesn't have it, update the config
        if (process.env.HUGGINGFACE_API_KEY && this.config && !this.config.huggingfaceApiKey) {
          try {
            await storage.updateBotConfig(this.config.id, {
              huggingfaceApiKey: process.env.HUGGINGFACE_API_KEY
            });
          } catch (error) {
            console.log('Unable to update bot config with API key');
          }
        }
      } else {
        console.log('No Hugging Face API key found');
      }
    } catch (error) {
      console.error('Error initializing ML service:', error);
    }
  }
  
  /**
   * Analyzes the sentiment of news or social media content related to a token
   * @param tokenSymbol The symbol of the token to analyze
   * @param content The text content to analyze
   * @returns Sentiment analysis result
   */
  public async analyzeSentiment(tokenSymbol: string, content: string): Promise<SentimentResult | null> {
    try {
      // Re-initialize if needed
      const apiKey = process.env.HUGGINGFACE_API_KEY || this.config?.huggingfaceApiKey;
      if (!this.hf && apiKey) {
        this.hf = new HfInference(apiKey);
      }
      
      if (!this.hf) {
        console.error('Hugging Face client not initialized');
        return null;
      }
      
      if (!this.config?.sentimentAnalysisEnabled) {
        console.log('Sentiment analysis is disabled in configuration');
        return null;
      }
      
      const modelToUse = this.config?.mlModelId || this.defaultModel;
      
      // Call Hugging Face for sentiment analysis
      const result = await this.hf.textClassification({
        model: modelToUse,
        inputs: content,
      });
      
      // Map the result to our interface
      const sentiment: SentimentResult = {
        label: this.mapSentimentLabel(result[0].label),
        score: result[0].score
      };
      
      console.log(`Sentiment analysis for ${tokenSymbol}: ${sentiment.label} (${sentiment.score})`);
      return sentiment;
    } catch (error) {
      console.error('Error analyzing sentiment:', error);
      return null;
    }
  }
  
  /**
   * Predicts future price movement for a token based on historical data
   * @param tokenSymbol The symbol of the token
   * @param historicalPrices Array of historical prices
   * @returns Price prediction result
   */
  public async predictPriceMovement(
    tokenSymbol: string, 
    historicalPrices: number[]
  ): Promise<PredictionResult | null> {
    try {
      // Re-initialize if needed
      const apiKey = process.env.HUGGINGFACE_API_KEY || this.config?.huggingfaceApiKey;
      if (!this.hf && apiKey) {
        this.hf = new HfInference(apiKey);
      }
      
      if (!this.hf) {
        console.error('Hugging Face client not initialized');
        return null;
      }
      
      if (!this.config?.aiPredictionEnabled) {
        console.log('AI price prediction is disabled in configuration');
        return null;
      }
      
      // For demonstration purposes, we'll use a simple algorithm
      // In a real implementation, this would call a Hugging Face time-series model
      const lastPrice = historicalPrices[historicalPrices.length - 1];
      const prevPrice = historicalPrices[historicalPrices.length - 2] || lastPrice;
      
      // Calculate moving averages for simple prediction
      const shortTermMA = this.calculateMA(historicalPrices, 5);
      const longTermMA = this.calculateMA(historicalPrices, 15);
      
      let direction: 'up' | 'down' | 'stable' = 'stable';
      let confidence = 0.5;
      
      if (shortTermMA > longTermMA * 1.02) {
        direction = 'up';
        confidence = 0.6 + (shortTermMA / longTermMA - 1) * 2;
      } else if (shortTermMA < longTermMA * 0.98) {
        direction = 'down';
        confidence = 0.6 + (1 - shortTermMA / longTermMA) * 2;
      }
      
      // Cap confidence at 0.95
      confidence = Math.min(confidence, 0.95);
      
      // Calculate predicted price
      const priceDiff = lastPrice - prevPrice;
      const predictedPrice = direction === 'up' 
        ? lastPrice + (priceDiff * confidence * 2)
        : direction === 'down'
        ? lastPrice - (Math.abs(priceDiff) * confidence * 2)
        : lastPrice;
      
      console.log(`Price prediction for ${tokenSymbol}: ${direction} (conf: ${confidence.toFixed(2)}), predicted: ${predictedPrice}`);
      
      return {
        predictedPrice,
        direction,
        confidence
      };
    } catch (error) {
      console.error('Error predicting price movement:', error);
      return null;
    }
  }
  
  /**
   * Determines if a trade should be executed based on ML insights
   * @param tokenSymbol The symbol of the token
   * @param currentPrice Current token price
   * @param historicalPrices Array of historical prices
   * @param newsContent Related news content if available
   * @returns Boolean indicating whether to proceed with trade
   */
  public async shouldExecuteTrade(
    tokenSymbol: string,
    currentPrice: number,
    historicalPrices: number[],
    newsContent?: string
  ): Promise<boolean> {
    try {
      // Get price prediction
      const pricePrediction = await this.predictPriceMovement(tokenSymbol, historicalPrices);
      
      // Get sentiment analysis if content is provided
      let sentiment: SentimentResult | null = null;
      if (newsContent) {
        sentiment = await this.analyzeSentiment(tokenSymbol, newsContent);
      }
      
      // Decision logic based on both price prediction and sentiment
      if (pricePrediction) {
        // Strong buy signal: predicted price increase with high confidence
        if (pricePrediction.direction === 'up' && pricePrediction.confidence > 0.7) {
          // If we have sentiment data, make sure it's not negative
          if (sentiment && sentiment.label === 'negative' && sentiment.score > 0.7) {
            console.log(`Not trading ${tokenSymbol} despite price signal due to negative sentiment`);
            return false;
          }
          return true;
        }
        
        // Medium buy signal: price increase with medium confidence plus positive sentiment
        if (pricePrediction.direction === 'up' && 
            pricePrediction.confidence > 0.5 && 
            sentiment?.label === 'positive' &&
            sentiment.score > 0.6) {
          return true;
        }
        
        // Avoid trading on predicted price drops
        if (pricePrediction.direction === 'down' && pricePrediction.confidence > 0.6) {
          return false;
        }
      }
      
      // Default to conservative behavior if ML insights are inconclusive
      return false;
    } catch (error) {
      console.error('Error in trade decision logic:', error);
      // Default to not trading on error
      return false;
    }
  }
  
  // Helper method to map sentiment labels from model output
  private mapSentimentLabel(label: string): 'positive' | 'negative' | 'neutral' {
    const lowerLabel = label.toLowerCase();
    if (lowerLabel.includes('positive') || lowerLabel.includes('bull')) {
      return 'positive';
    } else if (lowerLabel.includes('negative') || lowerLabel.includes('bear')) {
      return 'negative';
    } else {
      return 'neutral';
    }
  }
  
  // Helper method to calculate moving average
  private calculateMA(prices: number[], period: number): number {
    if (prices.length < period) {
      return prices.reduce((sum, price) => sum + price, 0) / prices.length;
    }
    
    const relevantPrices = prices.slice(prices.length - period);
    return relevantPrices.reduce((sum, price) => sum + price, 0) / period;
  }
}

// Export a singleton instance
export const mlService = new MLService();