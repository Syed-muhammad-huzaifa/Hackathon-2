import { Pool } from "pg";
import * as dotenv from "dotenv";

dotenv.config({ path: ".env.local" });

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

async function migrate() {
  const client = await pool.connect();

  try {
    console.log("Creating Better Auth tables...");

    await client.query(`
      CREATE TABLE IF NOT EXISTS "user" (
        "id" text PRIMARY KEY NOT NULL,
        "name" text NOT NULL,
        "email" text NOT NULL,
        "emailVerified" boolean DEFAULT false NOT NULL,
        "image" text,
        "createdAt" timestamp DEFAULT now() NOT NULL,
        "updatedAt" timestamp DEFAULT now() NOT NULL,
        CONSTRAINT "user_email_unique" UNIQUE("email")
      )
    `);
    console.log("✓ Created user table");

    await client.query(`
      CREATE TABLE IF NOT EXISTS "session" (
        "id" text PRIMARY KEY NOT NULL,
        "expiresAt" timestamp NOT NULL,
        "token" text NOT NULL,
        "createdAt" timestamp DEFAULT now() NOT NULL,
        "updatedAt" timestamp DEFAULT now() NOT NULL,
        "ipAddress" text,
        "userAgent" text,
        "userId" text NOT NULL,
        CONSTRAINT "session_token_unique" UNIQUE("token")
      )
    `);
    console.log("✓ Created session table");

    await client.query(`
      CREATE TABLE IF NOT EXISTS "account" (
        "id" text PRIMARY KEY NOT NULL,
        "accountId" text NOT NULL,
        "providerId" text NOT NULL,
        "userId" text NOT NULL,
        "accessToken" text,
        "refreshToken" text,
        "idToken" text,
        "accessTokenExpiresAt" timestamp,
        "refreshTokenExpiresAt" timestamp,
        "scope" text,
        "password" text,
        "createdAt" timestamp DEFAULT now() NOT NULL,
        "updatedAt" timestamp DEFAULT now() NOT NULL
      )
    `);
    console.log("✓ Created account table");

    await client.query(`
      CREATE TABLE IF NOT EXISTS "verification" (
        "id" text PRIMARY KEY NOT NULL,
        "identifier" text NOT NULL,
        "value" text NOT NULL,
        "expiresAt" timestamp NOT NULL,
        "createdAt" timestamp DEFAULT now(),
        "updatedAt" timestamp DEFAULT now()
      )
    `);
    console.log("✓ Created verification table");

    await client.query(`
      CREATE TABLE IF NOT EXISTS "jwks" (
        "id" text PRIMARY KEY NOT NULL,
        "publicKey" text NOT NULL,
        "privateKey" text NOT NULL,
        "createdAt" timestamp DEFAULT now() NOT NULL
      )
    `);
    console.log("✓ Created jwks table");

    // Add foreign key constraints if they don't exist
    await client.query(`
      DO $$
      BEGIN
        IF NOT EXISTS (
          SELECT 1 FROM pg_constraint WHERE conname = 'account_userId_user_id_fk'
        ) THEN
          ALTER TABLE "account" ADD CONSTRAINT "account_userId_user_id_fk"
          FOREIGN KEY ("userId") REFERENCES "public"."user"("id") ON DELETE cascade;
        END IF;
      END $$;
    `);
    console.log("✓ Added account foreign key");

    await client.query(`
      DO $$
      BEGIN
        IF NOT EXISTS (
          SELECT 1 FROM pg_constraint WHERE conname = 'session_userId_user_id_fk'
        ) THEN
          ALTER TABLE "session" ADD CONSTRAINT "session_userId_user_id_fk"
          FOREIGN KEY ("userId") REFERENCES "public"."user"("id") ON DELETE cascade;
        END IF;
      END $$;
    `);
    console.log("✓ Added session foreign key");

    console.log("\n✅ Migration completed successfully!");
  } catch (error) {
    console.error("❌ Migration failed:", error);
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

migrate().catch((error) => {
  console.error(error);
  process.exit(1);
});
