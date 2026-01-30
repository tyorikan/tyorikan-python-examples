import { Link } from 'react-router-dom';
import type { Product } from '../../features/catalog/api/getProducts';

interface ProductCardProps {
  product: Product;
}

export const ProductCard = ({ product }: ProductCardProps) => {
  // Use first variant or default for display (colors)
  const colors = [...new Set(product.variants.map(v => v.color))];

  return (
    <div className="group relative">
      <div className="aspect-[3/4] w-full overflow-hidden rounded-md bg-gray-200 lg:aspect-none group-hover:opacity-75 lg:h-80">
        {/* Placeholder image - dynamic based on ID to be distinct */}
        <div className="h-full w-full bg-gray-300 flex items-center justify-center text-gray-500">
           No Image
        </div>
      </div>
      <div className="mt-4 flex justify-between">
        <div>
          <h3 className="text-sm text-gray-700">
            <Link to={`/product/${product.product_id}`}>
              <span aria-hidden="true" className="absolute inset-0" />
              {product.name}
            </Link>
          </h3>
          <p className="mt-1 text-sm text-gray-500">{colors.join(', ')}</p>
        </div>
        <p className="text-sm font-medium text-gray-900">¥{product.base_price.toLocaleString()}</p>
      </div>
    </div>
  );
};
