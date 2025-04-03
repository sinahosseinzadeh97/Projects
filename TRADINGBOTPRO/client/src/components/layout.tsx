import { ReactNode } from 'react';
import Sidebar from './sidebar';
import Header from './header';

interface LayoutProps {
  children: ReactNode;
  title: string;
}

export default function Layout({ children, title }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <Sidebar />
      
      <div className="flex-1 min-h-screen flex flex-col">
        <Header title={title} />
        
        <main className="flex-1 p-4 md:p-6 overflow-auto bg-background">
          {children}
        </main>
      </div>
    </div>
  );
}
