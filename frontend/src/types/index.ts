export interface User {
  id: number;
  email: string;
  full_name?: string;
}

export interface File {
  id: number;
  filename: string;
  file_size: number;
  file_type: string;
  upload_time: string;
}

export interface Query {
  id: number;
  query_text: string;
  response: string;
  visualization_data?: string;
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface ApiError {
  detail: string;
}
