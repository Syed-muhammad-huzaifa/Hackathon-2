import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    include: ["./tests/**/*.test.ts", "./tests/**/*.test.tsx"],
    coverage: {
      reporter: ["text", "json", "html"],
    },
    // Integration tests run in node; all other tests use jsdom
    // Override per-file with @vitest-environment docblock or config below
    environmentOptions: {},
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
