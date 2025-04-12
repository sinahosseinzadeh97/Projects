/**
 * Simple logger for the workflow engine
 */
export class Logger {
  private context: string;

  /**
   * Create a new logger
   * @param context The context for this logger (e.g., component name)
   */
  constructor(context: string) {
    this.context = context;
  }

  /**
   * Log an informational message
   * @param message The message to log
   * @param data Optional data to include
   */
  info(message: string, data?: any): void {
    this.log('INFO', message, data);
  }

  /**
   * Log a warning message
   * @param message The message to log
   * @param data Optional data to include
   */
  warn(message: string, data?: any): void {
    this.log('WARN', message, data);
  }

  /**
   * Log an error message
   * @param message The message to log
   * @param error Optional error to include
   */
  error(message: string, error?: any): void {
    this.log('ERROR', message, error);
  }

  /**
   * Log a debug message
   * @param message The message to log
   * @param data Optional data to include
   */
  debug(message: string, data?: any): void {
    // Only log in development or when debug is enabled
    if (process.env.NODE_ENV === 'development' || process.env.DEBUG) {
      this.log('DEBUG', message, data);
    }
  }

  /**
   * Internal logging method
   * @param level The log level
   * @param message The message to log
   * @param data Optional data to include
   */
  private log(level: string, message: string, data?: any): void {
    const timestamp = new Date().toISOString();
    const formattedMessage = `[${timestamp}] [${level}] [${this.context}] ${message}`;
    
    // For the simple implementation, just use console
    // In a real application, this would use a proper logging library
    if (level === 'ERROR') {
      console.error(formattedMessage);
      if (data) {
        console.error(data);
      }
    } else if (level === 'WARN') {
      console.warn(formattedMessage);
      if (data) {
        console.warn(data);
      }
    } else {
      console.log(formattedMessage);
      if (data) {
        console.log(data);
      }
    }
  }
} 