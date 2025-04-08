import { drizzle } from 'drizzle-orm/better-sqlite3';
import Database from 'better-sqlite3';
import * as schema from '../shared/schema';

// Create a SQLite connection
const sqliteDb = process.env.DATABASE_URL?.replace('file:', '') || 'dev.db';
console.log(`Using SQLite database at: ${sqliteDb}`);
const sqlite = new Database(sqliteDb);

// Initialize Drizzle with our schema
export const db = drizzle(sqlite, { schema });

// Function to test database connection
export async function testConnection() {
  try {
    const result = sqlite.prepare('SELECT datetime("now") as now').get();
    console.log('Database connection successful:', result.now);
    return true;
  } catch (error) {
    console.error('Database connection failed:', error);
    return false;
  }
}

// Function to initialize database tables if they don't exist
export async function initDatabase() {
  console.log('Database tables are managed through Drizzle ORM');
  return true;
}