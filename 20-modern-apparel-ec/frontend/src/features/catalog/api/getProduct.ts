import axios from 'axios';
import { useQuery } from '@tanstack/react-query';
import type { Product, BaseResponse } from './getProducts';

// Base URL
const API_URL = 'http://localhost:8000/api';

export const getProduct = async (productId: string): Promise<Product> => {
  const { data } = await axios.get<BaseResponse<Product>>(`${API_URL}/products/${productId}`);
  return data.data;
};

export const useProduct = (productId: string) => {
  return useQuery({
    queryKey: ['product', productId],
    queryFn: () => getProduct(productId),
    enabled: !!productId,
  });
};
