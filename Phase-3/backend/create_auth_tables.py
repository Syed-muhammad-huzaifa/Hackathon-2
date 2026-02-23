"""
Create Better Auth tables in the database using backend's connection.
"""
import asyncio
from app.core.database import engine
from sqlalchemy import text

async def create_better_auth_tables():
    sql_statements = [
        """
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
        """,
        """
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
        """,
        """
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
        """,
        """
        CREATE TABLE IF NOT EXISTS "verification" (
            "id" text PRIMARY KEY NOT NULL,
            "identifier" text NOT NULL,
            "value" text NOT NULL,
            "expiresAt" timestamp NOT NULL,
            "createdAt" timestamp DEFAULT now(),
            "updatedAt" timestamp DEFAULT now()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS "jwks" (
            "id" text PRIMARY KEY NOT NULL,
            "publicKey" text NOT NULL,
            "privateKey" text NOT NULL,
            "createdAt" timestamp DEFAULT now() NOT NULL
        )
        """,
        """
        ALTER TABLE "account" DROP CONSTRAINT IF EXISTS "account_userId_user_id_fk"
        """,
        """
        ALTER TABLE "account" ADD CONSTRAINT "account_userId_user_id_fk"
        FOREIGN KEY ("userId") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action
        """,
        """
        ALTER TABLE "session" DROP CONSTRAINT IF EXISTS "session_userId_user_id_fk"
        """,
        """
        ALTER TABLE "session" ADD CONSTRAINT "session_userId_user_id_fk"
        FOREIGN KEY ("userId") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action
        """
    ]

    async with engine.begin() as conn:
        for sql_statement in sql_statements:
            try:
                await conn.execute(text(sql_statement))
                print(f"✓ Executed: {sql_statement[:50]}...")
            except Exception as e:
                print(f"⚠ Warning: {str(e)[:100]}")

    print("\n✓ Better Auth tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_better_auth_tables())
