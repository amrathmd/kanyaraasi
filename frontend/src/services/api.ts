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