import axios from 'axios';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_URL = 'http://localhost:8000/api';

export interface CartItem {
  product_id: string;
  variant_id: string;
  product_name: string;
  color: string;
  size: string;
  unit_price: number;
  quantity: number;
  updated_at: string;
}

export interface CartResponse {
  items: CartItem[];
  total_amount: number;
}

interface BaseResponse<T> {
  success: boolean;
  data: T;
}

export const getCart = async (): Promise<CartResponse> => {
  const { data } = await axios.get<BaseResponse<CartResponse>>(`${API_URL}/cart/`);
  return data.data;
};

export const useCart = () => {
  return useQuery({
    queryKey: ['cart'],
    queryFn: getCart,
  });
};

export const useAddToCart = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ product_id, variant_id, quantity }: { product_id: string; variant_id: string; quantity: number }) => {
      const { data } = await axios.post(`${API_URL}/cart/`, { product_id, variant_id, quantity });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });
};

export const useRemoveFromCart = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ product_id, variant_id }: { product_id: string; variant_id: string }) => {
      const { data } = await axios.delete(`${API_URL}/cart/${product_id}/${variant_id}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });
};

export const useUpdateCartItem = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ product_id, variant_id, quantity }: { product_id: string; variant_id: string; quantity: number }) => {
      const { data } = await axios.put(`${API_URL}/cart/${product_id}/${variant_id}`, { quantity });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });
};
