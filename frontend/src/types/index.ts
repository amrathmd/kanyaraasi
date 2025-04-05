export interface SignUpRequest {
  name: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: 'USER' | 'ADMIN';
}

export interface Document {
  document_id: string;
  status: string;
  year: string;
  month: string;
  reason: string;
  url: string;
} 