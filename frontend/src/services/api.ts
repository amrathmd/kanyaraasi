import axios from 'axios';
import { SignUpRequest, LoginRequest, LoginResponse } from '@/types';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export const signUp = async (data: SignUpRequest): Promise<LoginResponse> => {
  try {
    const response = await api.post('/signup', data);
    return {
      access_token: response.data.token || response.data.access_token,
      token_type: 'Bearer',
      role: response.data.role || 'USER'
    };
  } catch (error) {
    throw error;
  }
};

export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  try {
    const response = await api.post('/login', data);
    return {
      access_token: response.data.token || response.data.access_token,
      token_type: 'Bearer',
      role: response.data.role || 'USER'
    };
  } catch (error) {
    throw error;
  }
};

interface PresignedUrlResponse {
  document_code: string;
  presigned_url: string;
}

export const getPresignedUrl = async (contentType: string): Promise<PresignedUrlResponse> => {
  try {
    const token = localStorage.getItem('token');
    const response = await api.post('/documents/presigned-url', 
      { content_type: contentType },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateDocumentStatus = async (documentCode: string): Promise<void> => {
  try {
    const token = localStorage.getItem('token');
    await api.post(`/documents/update-document-status/${documentCode}`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
  } catch (error) {
    throw error;
  }
};

export const uploadToS3 = async (file: File, presignedUrl: string): Promise<void> => {
  try {
    // Use fetch instead of axios for S3 uploads to avoid CORS preflight issues
    const response = await fetch(presignedUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type,
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('S3 upload error response:', errorText);
      throw new Error(`Upload failed with status: ${response.status}`);
    }
  } catch (error) {
    console.error('S3 upload error:', error);
    throw error;
  }
};

interface Document {
  status: string;
  document_id: string;
  year: string;
  month: string;
  reason: string;
  url: string;
}

interface DocumentResponse {
  documents: Document[];
}

export const getUserDocuments = async (): Promise<Document[]> => {
  try {
    const token = localStorage.getItem('token');
    const response = await api.get('/documents/get-docs', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data.documents || [];
  } catch (error) {
    throw error;
  }
};

interface AccountDetails {
  user_id: string;
  year: number;
  total_balance: number;
  available_balance: number;
}

export const getAccountDetails = async (): Promise<AccountDetails> => {
  try {
    const token = localStorage.getItem('token');
    const response = await api.get('/account/account-details', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
}; 