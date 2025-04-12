# Developer Setup Guide

This guide will help you set up the Custom Buy-Sell Bot project in your preferred code editor.

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd custom-buy-sell-bot
```

### 2. Install Node.js and npm

Make sure you have Node.js (v20.x or later) and npm installed:
- Download from [https://nodejs.org/](https://nodejs.org/)
- Verify installation:
  ```bash
  node --version
  npm --version
  ```

### 3. Install Project Dependencies

```bash
npm install
```

### 4. Set Up PostgreSQL Database

- Install PostgreSQL from [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
- Create a new database:
  ```sql
  CREATE DATABASE botdatabase;
  ```
- Create a user with appropriate permissions:
  ```sql
  CREATE USER botuser WITH PASSWORD 'yourpassword';
  GRANT ALL PRIVILEGES ON DATABASE botdatabase TO botuser;
  ```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://botuser:yourpassword@localhost:5432/botdatabase
```

### 6. Initialize Database Schema

```bash
npm run db:push
```

## Development Workflow

### Starting the Development Server

```bash
npm run dev
```

This will start both the backend server and the frontend development server.

### Making Changes

1. The application uses TypeScript for type safety
2. Schema definitions are in `shared/schema.ts`
3. Server routes are in `server/routes.ts`
4. Frontend components are in `client/src/components`
5. Database operations are handled in `server/storage.ts`

### Database Migrations

Whenever you make changes to the database schema:

1. Update the models in `shared/schema.ts`
2. Run `npm run db:push` to update the database schema

## Code Editor Setup

### Visual Studio Code (Recommended)

1. Install VS Code from [https://code.visualstudio.com/](https://code.visualstudio.com/)

2. Install recommended extensions:
   - ESLint
   - Prettier
   - Tailwind CSS IntelliSense
   - TypeScript
   - PostgreSQL

3. Configure settings:
   ```json
   {
     "editor.formatOnSave": true,
     "editor.defaultFormatter": "esbenp.prettier-vscode",
     "editor.codeActionsOnSave": {
       "source.fixAll.eslint": true
     }
   }
   ```

### Other Editors

For other editors like WebStorm, Atom, or Sublime Text, install plugins for:
- ESLint
- Prettier
- TypeScript
- Tailwind CSS

## Testing

Run tests using:

```bash
npm test
```

## Debugging

### Backend

Use Node.js debugging in your editor:
- VS Code: Use the "Node.js: Attach" debug configuration
- Add breakpoints in your code
- Check server logs in the terminal

### Frontend

- Use React Developer Tools browser extension
- Check browser console for errors and logs
- Use the Network tab to monitor API requests

## Deployment

Prepare for production with:

```bash
npm run build
```

This creates optimized production builds of both frontend and backend.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Ensure user has correct permissions

2. **Node.js Version Issues**:
   - Use nvm to manage Node.js versions
   - Ensure you're using Node.js 20.x or later

3. **TypeScript Errors**:
   - Run `npm run type-check` to find type issues
   - Ensure you're using correct types from schema

## Getting Help

If you encounter issues:
1. Check existing issues in the repository
2. Create a new issue with detailed information
3. Include error logs and steps to reproduce