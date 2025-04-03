import Layout from '@/components/layout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Save, RotateCcw } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';

// Define form schema for API keys settings
const apiKeysSchema = z.object({
  solanaRpcUrl: z.string().url({ message: 'Please enter a valid URL' }),
  useCustomRpc: z.boolean(),
  explorerApiKey: z.string().min(1, { message: 'Explorer API key is required' }),
  jupiterApiKey: z.string().optional(),
});

type ApiKeysFormValues = z.infer<typeof apiKeysSchema>;

// Define form schema for bot behavior settings
const botBehaviorSchema = z.object({
  autoRetryCount: z.number().int().min(0).max(10),
  retryDelaySeconds: z.number().int().min(1),
  notifyOnSuccess: z.boolean(),
  notifyOnError: z.boolean(),
  notifyOnWarning: z.boolean(),
  preventFrontrunning: z.boolean(),
  autoSellOnPump: z.boolean(),
  pumpThresholdPercent: z.number().min(1).max(1000),
});

// Define form schema for AI/ML settings
const aiMlSchema = z.object({
  huggingfaceApiKey: z.string().min(1, { message: 'Hugging Face API key is required' }),
  aiPredictionEnabled: z.boolean(),
  sentimentAnalysisEnabled: z.boolean(),
  mlModelId: z.string().optional(),
});

type BotBehaviorFormValues = z.infer<typeof botBehaviorSchema>;
type AiMlFormValues = z.infer<typeof aiMlSchema>;

export default function Settings() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('api-keys');
  
  // API Keys form setup
  const apiKeysForm = useForm<ApiKeysFormValues>({
    resolver: zodResolver(apiKeysSchema),
    defaultValues: {
      solanaRpcUrl: 'https://api.mainnet-beta.solana.com',
      useCustomRpc: false,
      explorerApiKey: '',
      jupiterApiKey: '',
    }
  });
  
  // Bot Behavior form setup
  const botBehaviorForm = useForm<BotBehaviorFormValues>({
    resolver: zodResolver(botBehaviorSchema),
    defaultValues: {
      autoRetryCount: 3,
      retryDelaySeconds: 5,
      notifyOnSuccess: true,
      notifyOnError: true,
      notifyOnWarning: true,
      preventFrontrunning: true,
      autoSellOnPump: true,
      pumpThresholdPercent: 50,
    }
  });
  
  // AI/ML form setup
  const aiMlForm = useForm<AiMlFormValues>({
    resolver: zodResolver(aiMlSchema),
    defaultValues: {
      huggingfaceApiKey: '',
      aiPredictionEnabled: false,
      sentimentAnalysisEnabled: false,
      mlModelId: '',
    }
  });
  
  // API Keys form submission
  const saveApiKeysMutation = useMutation({
    mutationFn: async (data: ApiKeysFormValues) => {
      return await apiRequest('POST', '/api/settings/api-keys', data);
    },
    onSuccess: () => {
      toast({
        title: 'API Keys Saved',
        description: 'Your API key settings have been updated successfully.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Save Failed',
        description: error.message,
        variant: 'destructive',
      });
    }
  });
  
  // Bot Behavior form submission
  const saveBotBehaviorMutation = useMutation({
    mutationFn: async (data: BotBehaviorFormValues) => {
      return await apiRequest('POST', '/api/settings/bot-behavior', data);
    },
    onSuccess: () => {
      toast({
        title: 'Bot Behavior Settings Saved',
        description: 'Your bot behavior settings have been updated successfully.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Save Failed',
        description: error.message,
        variant: 'destructive',
      });
    }
  });
  
  const onSubmitApiKeys = (data: ApiKeysFormValues) => {
    saveApiKeysMutation.mutate(data);
  };
  
  const onSubmitBotBehavior = (data: BotBehaviorFormValues) => {
    saveBotBehaviorMutation.mutate(data);
  };
  
  const resetApiKeysForm = () => {
    apiKeysForm.reset();
    toast({
      title: 'Form Reset',
      description: 'API key settings have been reset to default values.',
    });
  };
  
  const resetBotBehaviorForm = () => {
    botBehaviorForm.reset();
    toast({
      title: 'Form Reset',
      description: 'Bot behavior settings have been reset to default values.',
    });
  };
  
  // AI/ML form submission
  const saveAiMlMutation = useMutation({
    mutationFn: async (data: AiMlFormValues) => {
      return await apiRequest('POST', '/api/bot/config', { 
        huggingfaceApiKey: data.huggingfaceApiKey,
        aiPredictionEnabled: data.aiPredictionEnabled,
        sentimentAnalysisEnabled: data.sentimentAnalysisEnabled,
        mlModelId: data.mlModelId || null
      });
    },
    onSuccess: () => {
      toast({
        title: 'ML Settings Saved',
        description: 'Your machine learning settings have been updated successfully.',
      });
      queryClient.invalidateQueries({ queryKey: ['/api/bot/config'] });
    },
    onError: (error) => {
      toast({
        title: 'Save Failed',
        description: error.message,
        variant: 'destructive',
      });
    }
  });
  
  const onSubmitAiMl = (data: AiMlFormValues) => {
    saveAiMlMutation.mutate(data);
  };
  
  const resetAiMlForm = () => {
    aiMlForm.reset();
    toast({
      title: 'Form Reset',
      description: 'AI & ML settings have been reset to default values.',
    });
  };

  return (
    <Layout title="Settings">
      <Card className="mb-6">
        <CardContent className="p-5">
          <h2 className="text-xl font-semibold mb-4">Trading Bot Settings</h2>
          <p className="text-sm text-muted-foreground mb-6">
            Configure the advanced settings for your trading bot. These settings control API connections, 
            bot behavior, and notification preferences.
          </p>
          
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="mb-6">
              <TabsTrigger value="api-keys">API Keys</TabsTrigger>
              <TabsTrigger value="bot-behavior">Bot Behavior</TabsTrigger>
              <TabsTrigger value="ai-ml">AI & ML</TabsTrigger>
              <TabsTrigger value="security">Security</TabsTrigger>
            </TabsList>
            
            {/* API Keys Tab */}
            <TabsContent value="api-keys">
              <Form {...apiKeysForm}>
                <form onSubmit={apiKeysForm.handleSubmit(onSubmitApiKeys)} className="space-y-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Blockchain Connections</h3>
                    
                    <FormField
                      control={apiKeysForm.control}
                      name="useCustomRpc"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">Use Custom RPC</FormLabel>
                            <FormDescription>
                              Use a custom RPC endpoint for Solana blockchain access
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={apiKeysForm.control}
                      name="solanaRpcUrl"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Solana RPC URL</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="https://api.mainnet-beta.solana.com"
                              {...field}
                              disabled={!apiKeysForm.watch('useCustomRpc')}
                            />
                          </FormControl>
                          <FormDescription>
                            The RPC endpoint used for Solana blockchain interactions
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">API Keys</h3>
                    
                    <FormField
                      control={apiKeysForm.control}
                      name="explorerApiKey"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Solana Explorer API Key</FormLabel>
                          <FormControl>
                            <Input
                              type="password"
                              placeholder="Enter your Solana Explorer API key"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>
                            Required for transaction monitoring and analysis
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={apiKeysForm.control}
                      name="jupiterApiKey"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Jupiter API Key (Optional)</FormLabel>
                          <FormControl>
                            <Input
                              type="password"
                              placeholder="Enter your Jupiter API key"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>
                            For enhanced swap routing and better price execution
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={resetApiKeysForm}
                      disabled={saveApiKeysMutation.isPending}
                    >
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Reset
                    </Button>
                    <Button
                      type="submit"
                      disabled={saveApiKeysMutation.isPending}
                    >
                      {saveApiKeysMutation.isPending ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="h-4 w-4 mr-2" />
                          Save API Keys
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </Form>
            </TabsContent>
            
            {/* Bot Behavior Tab */}
            <TabsContent value="bot-behavior">
              <Form {...botBehaviorForm}>
                <form onSubmit={botBehaviorForm.handleSubmit(onSubmitBotBehavior)} className="space-y-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Error Handling</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormField
                        control={botBehaviorForm.control}
                        name="autoRetryCount"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Auto-Retry Count</FormLabel>
                            <FormControl>
                              <Input
                                type="number"
                                {...field}
                                onChange={(e) => field.onChange(parseInt(e.target.value))}
                              />
                            </FormControl>
                            <FormDescription>
                              Number of times to retry failed transactions
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={botBehaviorForm.control}
                        name="retryDelaySeconds"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Retry Delay (seconds)</FormLabel>
                            <FormControl>
                              <Input
                                type="number"
                                {...field}
                                onChange={(e) => field.onChange(parseInt(e.target.value))}
                              />
                            </FormControl>
                            <FormDescription>
                              Delay between retry attempts
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Notifications</h3>
                    
                    <div className="space-y-2">
                      <FormField
                        control={botBehaviorForm.control}
                        name="notifyOnSuccess"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                            <div className="space-y-0.5">
                              <FormLabel className="text-base">Success Notifications</FormLabel>
                              <FormDescription>
                                Receive notifications for successful transactions
                              </FormDescription>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={botBehaviorForm.control}
                        name="notifyOnError"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                            <div className="space-y-0.5">
                              <FormLabel className="text-base">Error Notifications</FormLabel>
                              <FormDescription>
                                Receive notifications for failed transactions
                              </FormDescription>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={botBehaviorForm.control}
                        name="notifyOnWarning"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                            <div className="space-y-0.5">
                              <FormLabel className="text-base">Warning Notifications</FormLabel>
                              <FormDescription>
                                Receive notifications for warnings and alerts
                              </FormDescription>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Trading Safety</h3>
                    
                    <FormField
                      control={botBehaviorForm.control}
                      name="preventFrontrunning"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">Prevent Frontrunning</FormLabel>
                            <FormDescription>
                              Apply anti-MEV measures to protect against frontrunning attacks
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={botBehaviorForm.control}
                      name="autoSellOnPump"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">Auto-Sell on Pump</FormLabel>
                            <FormDescription>
                              Automatically sell when token price pumps rapidly
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={botBehaviorForm.control}
                      name="pumpThresholdPercent"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Pump Threshold (%)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              {...field}
                              onChange={(e) => field.onChange(parseInt(e.target.value))}
                              disabled={!botBehaviorForm.watch('autoSellOnPump')}
                            />
                          </FormControl>
                          <FormDescription>
                            Trigger auto-sell when price increases by this percentage
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={resetBotBehaviorForm}
                      disabled={saveBotBehaviorMutation.isPending}
                    >
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Reset
                    </Button>
                    <Button
                      type="submit"
                      disabled={saveBotBehaviorMutation.isPending}
                    >
                      {saveBotBehaviorMutation.isPending ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="h-4 w-4 mr-2" />
                          Save Settings
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </Form>
            </TabsContent>
            
            {/* AI & ML Tab */}
            <TabsContent value="ai-ml">
              <Form {...aiMlForm}>
                <form onSubmit={aiMlForm.handleSubmit(onSubmitAiMl)} className="space-y-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Machine Learning Configuration</h3>
                    
                    <FormField
                      control={aiMlForm.control}
                      name="huggingfaceApiKey"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Hugging Face API Key</FormLabel>
                          <FormControl>
                            <Input
                              type="password"
                              placeholder="Enter your Hugging Face API key"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>
                            Required for AI price prediction and sentiment analysis
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <div className="space-y-2 mt-4">
                      <h3 className="text-lg font-medium">ML Features</h3>
                      
                      <FormField
                        control={aiMlForm.control}
                        name="aiPredictionEnabled"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                            <div className="space-y-0.5">
                              <FormLabel className="text-base">Price Prediction</FormLabel>
                              <FormDescription>
                                Use AI to predict token price movements
                              </FormDescription>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={aiMlForm.control}
                        name="sentimentAnalysisEnabled"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                            <div className="space-y-0.5">
                              <FormLabel className="text-base">Sentiment Analysis</FormLabel>
                              <FormDescription>
                                Analyze news and social media sentiment for trading decisions
                              </FormDescription>
                            </div>
                            <FormControl>
                              <Switch
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                    </div>
                    
                    <FormField
                      control={aiMlForm.control}
                      name="mlModelId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Custom Model ID (Optional)</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="e.g. finBERT/finbert-sentiment"
                              {...field}
                              value={field.value || ''}
                            />
                          </FormControl>
                          <FormDescription>
                            Custom Hugging Face model ID for sentiment analysis
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={resetAiMlForm}
                      disabled={saveAiMlMutation.isPending}
                    >
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Reset
                    </Button>
                    <Button
                      type="submit"
                      disabled={saveAiMlMutation.isPending}
                    >
                      {saveAiMlMutation.isPending ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="h-4 w-4 mr-2" />
                          Save ML Settings
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </Form>
            </TabsContent>
            
            {/* Security Tab */}
            <TabsContent value="security">
              <div className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Authentication</h3>
                  
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div>
                          <h4 className="text-base font-medium">Two-Factor Authentication</h4>
                          <p className="text-sm text-muted-foreground">
                            Add an extra layer of security to your account with 2FA
                          </p>
                        </div>
                        <Button variant="outline">Setup 2FA</Button>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div>
                          <h4 className="text-base font-medium">Change Password</h4>
                          <p className="text-sm text-muted-foreground">
                            Update your account password regularly for better security
                          </p>
                        </div>
                        <Button variant="outline">Change Password</Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
                
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">API Security</h3>
                  
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div>
                          <h4 className="text-base font-medium">API Access Log</h4>
                          <p className="text-sm text-muted-foreground">
                            Monitor all API access to your wallet accounts
                          </p>
                        </div>
                        <Button variant="outline">View Logs</Button>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div>
                          <h4 className="text-base font-medium">Wallet Permissions</h4>
                          <p className="text-sm text-muted-foreground">
                            Manage which wallets the bot can access
                          </p>
                        </div>
                        <Button variant="outline">Manage Permissions</Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
                
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-red-500">Danger Zone</h3>
                  
                  <Card className="border-red-500/30">
                    <CardContent className="p-4">
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div>
                          <h4 className="text-base font-medium">Revoke All Permissions</h4>
                          <p className="text-sm text-muted-foreground">
                            Immediately revoke all wallet access permissions from the bot
                          </p>
                        </div>
                        <Button variant="destructive">Revoke All</Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </Layout>
  );
}
