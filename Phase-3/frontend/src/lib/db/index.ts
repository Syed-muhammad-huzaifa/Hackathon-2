import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import * as schema from "./schema";

let db: ReturnType<typeof drizzle<typeof schema>> | null = null;

function shouldUseSsl(connectionString: string) {
  return /sslmode=(require|verify-full|verify-ca)/i.test(connectionString);
}

export function getDb() {
  if (!db) {
    const connectionString = process.env.DATABASE_URL;
    if (!connectionString) {
      throw new Error("DATABASE_URL is not set");
    }

    const pool = new Pool({
      connectionString,
      ssl: shouldUseSsl(connectionString) ? { rejectUnauthorized: false } : undefined,
      connectionTimeoutMillis: 5000,
      idleTimeoutMillis: 30_000,
      max: 5,
      keepAlive: true,
      family: 4,
    });

    pool.on("error", (err) => {
      console.error("Postgres pool error:", err);
    });

    db = drizzle(pool, { schema });
  }
  return db;
}

export { schema };
