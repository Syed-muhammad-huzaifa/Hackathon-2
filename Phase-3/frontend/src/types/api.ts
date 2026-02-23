// API error response types

export interface ErrorResponse {
  status: "error";
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}
