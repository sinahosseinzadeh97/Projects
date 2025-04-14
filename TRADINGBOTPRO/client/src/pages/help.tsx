import Layout from '@/components/layout';
import { Card, CardContent } from '@/components/ui/card';
import { 
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from "@/components/ui/tabs";
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, FileText, MessageCircleQuestion, Book, PlayCircle, ExternalLink } from 'lucide-react';
import { useState } from 'react';

interface GuideItemProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  link: string;
}

function GuideItem({ title, description, icon, link }: GuideItemProps) {
  return (
    <Card className="hover:bg-secondary/40 transition-colors">
      <CardContent className="p-6">
        <div className="flex items-start">
          <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center mr-4 flex-shrink-0">
            {icon}
          </div>
          <div>
            <h3 className="text-lg font-medium mb-2">{title}</h3>
            <p className="text-sm text-muted-foreground mb-4">{description}</p>
            <Button variant="link" className="p-0 h-auto flex items-center text-primary">
              Read more <ExternalLink className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function Help() {
  const [searchQuery, setSearchQuery] = useState('');
  
  const faqItems = [
    {
      question: "How does the wallet tracking work?",
      answer: "The bot monitors transfers from a parent wallet through multiple layers (up to a depth of 5) and performs buy/sell actions automatically based on the configured parameters. It tracks various transaction types including normal transactions, Raydium swaps, and WSOL buys."
    },
    {
      question: "What transaction types are supported?",
      answer: "The bot supports normal buys/sells, Raydium swaps, and WSOL buys. It can detect and process different transaction patterns across multiple wallet layers."
    },
    {
      question: "How do I set up buy conditions?",
      answer: "In the Bot Configuration section, you can set parameters such as volume threshold, market cap requirements, and token age to define when the bot should execute a buy. For example, you might set 'If volume is 2.5M, MC is 1M, and token age is 30 minutes, then buy 1 SOL'."
    },
    {
      question: "How do I set up sell conditions?",
      answer: "In the Bot Configuration section, you can set profit targets and stop loss percentages. For example, you might configure 'If price increases 30%, then sell' or set automatic selling if the price drops below a certain threshold."
    },
    {
      question: "What is Anti-MEV protection?",
      answer: "Anti-MEV (Miner Extractable Value) protection helps prevent front-running attacks on your transactions. When enabled, the bot uses techniques to protect your trades from being exploited by validators or other traders who might try to manipulate transaction ordering for profit."
    },
    {
      question: "How does the auto-retry mechanism work?",
      answer: "If a transaction fails, the bot will automatically attempt to retry it based on your settings. You can configure the number of retry attempts and the delay between retries in the Settings page under Bot Behavior."
    },
    {
      question: "Can I track multiple parent wallets?",
      answer: "Currently, the bot supports tracking one parent wallet at a time with multiple transaction layers beneath it. In future updates, we plan to add support for monitoring multiple parent wallets simultaneously."
    },
    {
      question: "How do I get notified of transactions?",
      answer: "The bot provides real-time notifications in the dashboard interface. You can enable/disable different types of notifications (success, error, warning) in the Settings page under Bot Behavior."
    }
  ];
  
  // Filter FAQ items based on search query
  const filteredFaqItems = faqItems.filter(item => 
    item.question.toLowerCase().includes(searchQuery.toLowerCase()) || 
    item.answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Layout title="Help">
      <Card className="mb-6">
        <CardContent className="p-6">
          <h2 className="text-2xl font-semibold mb-2">Help Center</h2>
          <p className="text-muted-foreground mb-6">
            Find answers to common questions and learn how to use the Trading Bot effectively.
          </p>
          
          <div className="relative mb-6">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input 
              placeholder="Search for answers..." 
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <Tabs defaultValue="faq">
            <TabsList className="mb-4">
              <TabsTrigger value="faq">FAQ</TabsTrigger>
              <TabsTrigger value="guides">Guides</TabsTrigger>
              <TabsTrigger value="videos">Video Tutorials</TabsTrigger>
            </TabsList>
            
            <TabsContent value="faq">
              <Card>
                <CardContent className="p-6">
                  <Accordion type="single" collapsible className="w-full">
                    {filteredFaqItems.length > 0 ? (
                      filteredFaqItems.map((item, index) => (
                        <AccordionItem key={index} value={`item-${index}`} className="border-b">
                          <AccordionTrigger className="text-left font-medium py-4">
                            {item.question}
                          </AccordionTrigger>
                          <AccordionContent className="text-muted-foreground pb-4">
                            {item.answer}
                          </AccordionContent>
                        </AccordionItem>
                      ))
                    ) : (
                      <div className="py-8 text-center">
                        <MessageCircleQuestion className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                        <h3 className="text-lg font-medium mb-1">No results found</h3>
                        <p className="text-muted-foreground">
                          Try adjusting your search query or browse the guides section
                        </p>
                      </div>
                    )}
                  </Accordion>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="guides">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <GuideItem
                  title="Getting Started"
                  description="Learn how to set up your trading bot and configure it for the first time."
                  icon={<FileText className="h-5 w-5 text-primary" />}
                  link="#"
                />
                <GuideItem
                  title="Wallet Setup"
                  description="Instructions for setting up and connecting your Solana wallet."
                  icon={<Book className="h-5 w-5 text-primary" />}
                  link="#"
                />
                <GuideItem
                  title="Trading Strategies"
                  description="Learn effective trading strategies for different market conditions."
                  icon={<Book className="h-5 w-5 text-primary" />}
                  link="#"
                />
                <GuideItem
                  title="Configuration Guide"
                  description="Detailed guide on all configuration options and their effects."
                  icon={<FileText className="h-5 w-5 text-primary" />}
                  link="#"
                />
                <GuideItem
                  title="Advanced Features"
                  description="Explore advanced bot features for experienced traders."
                  icon={<FileText className="h-5 w-5 text-primary" />}
                  link="#"
                />
                <GuideItem
                  title="Troubleshooting"
                  description="Solutions for common issues and error messages."
                  icon={<MessageCircleQuestion className="h-5 w-5 text-primary" />}
                  link="#"
                />
              </div>
            </TabsContent>
            
            <TabsContent value="videos">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <GuideItem
                  title="Bot Setup Tutorial"
                  description="Step-by-step video guide on setting up your trading bot."
                  icon={<PlayCircle className="h-5 w-5 text-primary" />}
                  link="#"
                />
                <GuideItem
                  title="Wallet Tracking Tutorial"
                  description="Learn how to effectively track wallet transactions."
                  icon={<PlayCircle className="h-5 w-5 text-primary" />}
                  link="#"
                />
                <GuideItem
                  title="Configuration Tutorial"
                  description="Detailed walkthrough of all bot configuration options."
                  icon={<PlayCircle className="h-5 w-5 text-primary" />}
                  link="#"
                />
                <GuideItem
                  title="Advanced Trading Tutorial"
                  description="Advanced strategies for maximizing bot performance."
                  icon={<PlayCircle className="h-5 w-5 text-primary" />}
                  link="#"
                />
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-6">
          <h2 className="text-xl font-semibold mb-4">Need More Help?</h2>
          <p className="text-muted-foreground mb-6">
            If you can't find what you're looking for, reach out for personalized support.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-start">
                  <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center mr-4 flex-shrink-0">
                    <MessageCircleQuestion className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium mb-1">Contact Support</h3>
                    <p className="text-sm text-muted-foreground mb-3">
                      Get help from our technical support team
                    </p>
                    <Button size="sm">Contact Support</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-start">
                  <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center mr-4 flex-shrink-0">
                    <Book className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium mb-1">Documentation</h3>
                    <p className="text-sm text-muted-foreground mb-3">
                      Browse our detailed technical documentation
                    </p>
                    <Button size="sm" variant="outline">
                      View Docs <ExternalLink className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>
    </Layout>
  );
}
