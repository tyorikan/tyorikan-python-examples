import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

// Base URL (Assuming CORS is set for localhost:8000)
const API_URL = 'http://localhost:8000/api';

export interface ProductVariant {
  variant_id: string;
  color: string;
  size: string;
  stock_quantity: number;
}

export interface Product {
  product_id: string;
  name: string;
  description: string;
  base_price: number;
  category_id: string;
  created_at: string;
  variants: ProductVariant[];
}

export interface BaseResponse<T> {
  success: boolean;
  data: T;
  meta?: {
    page: number;
    total: number;
  };
  error?: string;
}

export const getProducts = async (limit = 20): Promise<Product[]> => {
  const { data } = await axios.get<BaseResponse<Product[]>>(`${API_URL}/products/`, {
    params: { limit }
  });
  return data.data;
};

export const useProducts = () => {
  return useQuery({
    queryKey: ['products'],
    queryFn: () => getProducts(),
  });
};
