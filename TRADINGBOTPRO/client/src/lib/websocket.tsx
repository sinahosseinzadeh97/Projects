import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useToast } from '@/hooks/use-toast';

type WebSocketStatus = 'connecting' | 'open' | 'closed' | 'error';

interface WebSocketState {
  socket: WebSocket | null;
  status: WebSocketStatus;
  sendMessage: (message: any) => void;
}

const WebSocketContext = createContext<WebSocketState>({
  socket: null,
  status: 'closed',
  sendMessage: () => {}
});

export const useWebSocket = () => useContext(WebSocketContext);

interface WebSocketProviderProps {
  children: ReactNode;
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [status, setStatus] = useState<WebSocketStatus>('closed');
  const { toast } = useToast();

  useEffect(() => {
    const connectWebSocket = () => {
      try {
        setStatus('connecting');
        
        // Create WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          setStatus('open');
          console.log('WebSocket connection established');
        };
        
        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            if (message.type === 'notificationAdded' && message.data) {
              // Show toast for new notifications
              toast({
                title: message.data.title,
                description: message.data.message,
                variant: message.data.type === 'success' ? 'default' : 
                         message.data.type === 'error' ? 'destructive' : 
                         message.data.type === 'warning' ? 'warning' : 'default'
              });
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        ws.onclose = () => {
          setStatus('closed');
          console.log('WebSocket connection closed');
          // Try to reconnect after a delay
          setTimeout(connectWebSocket, 5000);
        };
        
        ws.onerror = (error) => {
          setStatus('error');
          console.error('WebSocket error:', error);
          toast({
            title: 'Connection Error',
            description: 'Failed to connect to the server. Retrying...',
            variant: 'destructive'
          });
        };
        
        setSocket(ws);
      } catch (error) {
        setStatus('error');
        console.error('Error setting up WebSocket:', error);
      }
    };
    
    connectWebSocket();
    
    // Cleanup function
    return () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [toast]);
  
  const sendMessage = (message: any) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
      toast({
        title: 'Connection Error',
        description: 'Cannot send message, connection is closed',
        variant: 'destructive'
      });
    }
  };
  
  return (
    <WebSocketContext.Provider value={{ socket, status, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
}
