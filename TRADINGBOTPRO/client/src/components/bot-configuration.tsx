import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/queryClient';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';

// Define the form schema with validation
const botConfigSchema = z.object({
  parentWalletAddress: z.string().min(10, { message: 'Wallet address is too short' }),
  minAmount: z.number().min(0.01, { message: 'Minimum amount must be at least 0.01 SOL' }),
  maxAmount: z.number().min(0.1, { message: 'Maximum amount must be at least 0.1 SOL' }),
  tipAmount: z.number().min(0, { message: 'Tip amount must be a positive number' }),
  gasFee: z.number().min(0, { message: 'Gas fee must be a positive number' }),
  trackingDepth: z.number().int().min(1).max(5),
  volumeThreshold: z.number().min(0, { message: 'Volume threshold must be a positive number' }),
  mcThreshold: z.number().min(0, { message: 'Market cap threshold must be a positive number' }),
  tokenAge: z.number().min(0, { message: 'Token age must be a positive number' }),
  profitTarget: z.number().min(0, { message: 'Profit target must be a positive number' }),
  stopLoss: z.number().min(0, { message: 'Stop loss must be a positive number' }),
  antiMevProtection: z.boolean()
});

type BotConfigFormValues = z.infer<typeof botConfigSchema>;

export default function BotConfiguration() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [depthValue, setDepthValue] = useState<number>(4);
  
  // Fetch current bot configuration
  const { data: botConfig, isLoading: isConfigLoading } = useQuery({
    queryKey: ['/api/bot/config'],
  });
  
  // Initialize form with current config or defaults
  const form = useForm<BotConfigFormValues>({
    resolver: zodResolver(botConfigSchema),
    defaultValues: botConfig || {
      parentWalletAddress: '5XmTxU8SJJ7fYnQ5CdY9aNM8yD6MhGPmXf4s15rZ8eG5',
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
    }
  });
  
  // Update form values when data is loaded
  useEffect(() => {
    if (botConfig) {
      form.reset(botConfig);
      setDepthValue(botConfig.trackingDepth);
    }
  }, [botConfig, form]);
  
  // Mutation for saving configuration
  const saveMutation = useMutation({
    mutationFn: async (data: BotConfigFormValues) => {
      return await apiRequest('POST', '/api/bot/config', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/bot/config'] });
      toast({
        title: 'Configuration Saved',
        description: 'Your bot configuration has been updated successfully.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Save Failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
  
  const onSubmit = (data: BotConfigFormValues) => {
    saveMutation.mutate(data);
  };
  
  const handleReset = () => {
    form.reset();
    toast({
      title: 'Form Reset',
      description: 'Form values have been reset to the last saved configuration.',
    });
  };
  
  const handleSliderChange = (value: number[]) => {
    setDepthValue(value[0]);
    form.setValue('trackingDepth', value[0]);
  };

  if (isConfigLoading) {
    return (
      <Card>
        <div className="border-b border-border px-5 py-4">
          <h2 className="text-lg font-medium">Bot Configuration</h2>
        </div>
        <CardContent className="p-5">
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <div className="border-b border-border px-5 py-4">
        <h2 className="text-lg font-medium">Bot Configuration</h2>
      </div>
      <CardContent className="p-5">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {/* Parent Wallet Address */}
            <FormField
              control={form.control}
              name="parentWalletAddress"
              render={({ field }) => (
                <FormItem className="space-y-2">
                  <FormLabel>Parent Wallet Address</FormLabel>
                  <div className="flex">
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <Button type="button" className="ml-2">Verify</Button>
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Transaction Amount Settings */}
              <div className="space-y-2">
                <Label>Transaction Amounts</Label>
                <div className="grid grid-cols-2 gap-2">
                  <FormField
                    control={form.control}
                    name="minAmount"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs text-muted-foreground">Minimum (SOL)</FormLabel>
                        <FormControl>
                          <Input 
                            type="number" 
                            step="0.01"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="maxAmount"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs text-muted-foreground">Maximum (SOL)</FormLabel>
                        <FormControl>
                          <Input 
                            type="number" 
                            step="0.1"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
              
              {/* Fee Settings */}
              <div className="space-y-2">
                <Label>Fees & MEV Protection</Label>
                <div className="grid grid-cols-2 gap-2">
                  <FormField
                    control={form.control}
                    name="tipAmount"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs text-muted-foreground">Tip (SOL)</FormLabel>
                        <FormControl>
                          <Input 
                            type="number" 
                            step="0.001"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="gasFee"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs text-muted-foreground">Gas Fee</FormLabel>
                        <FormControl>
                          <Input 
                            type="number" 
                            step="0.001"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            </div>
            
            {/* Tracking Depth */}
            <FormField
              control={form.control}
              name="trackingDepth"
              render={({ field }) => (
                <FormItem className="space-y-2">
                  <div className="flex items-center justify-between">
                    <FormLabel>Tracking Depth</FormLabel>
                    <span className="text-sm text-muted-foreground">{depthValue} Levels</span>
                  </div>
                  <FormControl>
                    <Slider
                      value={[field.value]}
                      min={1}
                      max={5}
                      step={1}
                      onValueChange={handleSliderChange}
                    />
                  </FormControl>
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>1</span>
                    <span>2</span>
                    <span>3</span>
                    <span>4</span>
                    <span>5</span>
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            {/* Buy Conditions */}
            <div className="space-y-2">
              <Label>Buy Conditions</Label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                <FormField
                  control={form.control}
                  name="volumeThreshold"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-xs text-muted-foreground">Volume (M)</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          step="0.1"
                          {...field}
                          onChange={(e) => field.onChange(parseFloat(e.target.value))}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="mcThreshold"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-xs text-muted-foreground">Market Cap (M)</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          step="0.1"
                          {...field}
                          onChange={(e) => field.onChange(parseFloat(e.target.value))}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="tokenAge"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-xs text-muted-foreground">Token Age (min)</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value))}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>
            
            {/* Sell Conditions */}
            <div className="space-y-2">
              <Label>Sell Conditions</Label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                <FormField
                  control={form.control}
                  name="profitTarget"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-xs text-muted-foreground">Profit Target (%)</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value))}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="stopLoss"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-xs text-muted-foreground">Stop Loss (%)</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value))}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>
            
            {/* Anti-MEV Settings */}
            <FormField
              control={form.control}
              name="antiMevProtection"
              render={({ field }) => (
                <FormItem className="space-y-2">
                  <div className="flex items-center justify-between">
                    <FormLabel>Anti-MEV Protection</FormLabel>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </div>
                  <p className="text-xs text-muted-foreground">Protect your transactions from front-running and other MEV attacks.</p>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="pt-2 flex justify-end space-x-2">
              <Button 
                type="button" 
                variant="outline" 
                onClick={handleReset}
                disabled={saveMutation.isPending}
              >
                Reset
              </Button>
              <Button 
                type="submit"
                disabled={saveMutation.isPending}
              >
                {saveMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Configuration'
                )}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
