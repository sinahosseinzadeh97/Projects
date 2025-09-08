# Trading Bot Pro by Sina Mohammadhosseinzadeh

An automated cryptocurrency trading solution designed to track and execute trades on blockchain networks, with initial focus on Solana blockchain.

![Dashboard Screenshot](screenshots/dashboard.png)

## Features

- Real-time transaction monitoring
- Multi-layer wallet tracking
- Automated trade execution based on configurable parameters
- Transaction history and analytics dashboard
- Performance metrics and statistics
- WebSocket integration for real-time updates

## Technology Stack

- **Frontend**: React with Tailwind CSS, shadcn UI components
- **Backend**: Node.js with Express
- **Database**: PostgreSQL with Drizzle ORM (SQLite for development)
- **State Management**: TanStack Query (React Query)
- **WebSockets**: Real-time updates and notifications

## Prerequisites

- Node.js (v20.x or later recommended)
- PostgreSQL database or SQLite for development
- API keys for blockchain services (Solana Explorer, Jupiter)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sinahosseinzadeh97/Projects.git
cd Projects
```

2. Install dependencies:
```bash
npm install
```

3. Set up your environment variables:
Create a `.env` file in the root directory and add the following variables:
```
DATABASE_URL=file:./dev.db
```

4. Initialize the database:
```bash
npm run db:push
```

5. Start the development server:
```bash
npm run dev
```

6. Open your browser and navigate to:
```
http://localhost:8080
```

## Usage

1. Start the bot from the Dashboard using the "Start Bot" button
2. Monitor transactions in real-time on the Dashboard
3. View detailed analytics and performance metrics
4. Configure alerts and notifications for important events

## API Endpoints

- `/api/bot/status` - Get the current status of the bot
- `/api/bot/config` - Get or update bot configuration
- `/api/transactions` - List all transactions
- `/api/wallets` - Manage tracked wallets
- `/api/notifications` - Get system notifications

## WebSocket Events

The application provides real-time updates through WebSocket connections:
- Transaction events
- Wallet updates
- Bot status changes
- Trading opportunities

## License

MIT
