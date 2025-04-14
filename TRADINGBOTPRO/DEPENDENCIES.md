# Project Dependencies

## System Requirements

- **Node.js**: Version 20.x or later recommended
- **PostgreSQL**: Version 13.x or later
- **npm**: Version 9.x or later

## Main Dependencies

This project uses the following key libraries and frameworks:

### Frontend
- React
- TailwindCSS
- shadcn UI components
- React Query (TanStack Query)
- Wouter (routing)
- React Hook Form
- Zod (validation)
- Recharts (data visualization)
- Framer Motion (animations)

### Backend
- Express
- PostgreSQL
- Drizzle ORM
- WebSockets (ws)
- Zod (validation)

## Installation Steps

1. Install Node.js and npm:
   - Download from [https://nodejs.org/](https://nodejs.org/)
   - Choose version 20.x or later

2. Install PostgreSQL:
   - Download from [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
   - Create a database for the project

3. Clone the project repository

4. Install project dependencies:
   ```bash
   npm install
   ```

5. Set up environment variables:
   Create a `.env` file in the project root with:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/yourdatabase
   ```

6. Initialize the database:
   ```bash
   npm run db:push
   ```

7. Start the development server:
   ```bash
   npm run dev
   ```

## IDE Setup

For the best development experience, we recommend:

- **Visual Studio Code** with the following extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - TypeScript support

- **Database Tools**:
  - pgAdmin or DBeaver for PostgreSQL management

## Development Workflow

1. Start the development server with `npm run dev`
2. Make changes to the code
3. The server will automatically restart when changes are detected

## Additional Tools (Optional)

- **Postman** or **Insomnia**: For testing API endpoints
- **React Developer Tools**: For debugging React components
- **Redux DevTools**: For monitoring state changes

This document provides an overview of the dependencies required to run the project in any code editor. The actual JavaScript dependencies are managed through the package.json file, and you can install them using npm.