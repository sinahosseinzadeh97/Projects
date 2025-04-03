import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/queryClient';
import { useWebSocket } from '@/lib/websocket';
import { Loader2, StopCircle, RefreshCw } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

export default function BotStatus() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { sendMessage } = useWebSocket();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: botStatus, isLoading } = useQuery({
    queryKey: ['/api/bot/status'],
  });

  const startBotMutation = useMutation({
    mutationFn: async () => {
      return await apiRequest('POST', '/api/bot/start', {});
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/bot/status'] });
      toast({
        title: 'Bot Started',
        description: 'The bot is now actively monitoring transactions.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Failed to Start Bot',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const stopBotMutation = useMutation({
    mutationFn: async () => {
      return await apiRequest('POST', '/api/bot/stop', {});
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/bot/status'] });
      toast({
        title: 'Bot Stopped',
        description: 'The bot has stopped monitoring transactions.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Failed to Stop Bot',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const restartBotMutation = useMutation({
    mutationFn: async () => {
      return await apiRequest('POST', '/api/bot/restart', {});
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/bot/status'] });
      toast({
        title: 'Bot Restarted',
        description: 'The bot has been restarted and is now monitoring transactions.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Failed to Restart Bot',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const handleStartBot = async () => {
    setIsSubmitting(true);
    try {
      await startBotMutation.mutateAsync();
      sendMessage({ type: 'startBot' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStopBot = async () => {
    setIsSubmitting(true);
    try {
      await stopBotMutation.mutateAsync();
      sendMessage({ type: 'stopBot' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRestartBot = async () => {
    setIsSubmitting(true);
    try {
      await restartBotMutation.mutateAsync();
      sendMessage({ type: 'restartBot' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const isActive = botStatus?.status === 'active';

  return (
    <Card className="mb-6">
      <CardContent className="p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-medium">Bot Status</h2>
            <div className="flex items-center mt-2 space-x-2">
              <span 
                className={`h-3 w-3 rounded-full ${
                  isLoading ? 'bg-yellow-500 animate-pulse' : 
                  isActive ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-sm">
                {isLoading ? 'Checking status...' : 
                 isActive ? `Active - ${botStatus?.message || 'Monitoring Transactions'}` : 
                 'Inactive - Bot is stopped'}
              </span>
            </div>
          </div>
          <div className="mt-4 md:mt-0 flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-2">
            {isActive ? (
              <Button
                variant="destructive"
                onClick={handleStopBot}
                disabled={isSubmitting}
              >
                {isSubmitting && stopBotMutation.isPending ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <StopCircle className="h-4 w-4 mr-2" />
                )}
                Stop Bot
              </Button>
            ) : (
              <Button
                onClick={handleStartBot}
                disabled={isSubmitting}
              >
                {isSubmitting && startBotMutation.isPending ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <StopCircle className="h-4 w-4 mr-2" />
                )}
                Start Bot
              </Button>
            )}
            <Button
              onClick={handleRestartBot}
              disabled={isSubmitting}
            >
              {isSubmitting && restartBotMutation.isPending ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Restart Bot
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
