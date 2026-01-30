import { Link } from 'react-router-dom';
import { Plus } from 'lucide-react';

interface ProductCardProps {
  product: {
    product_id: string;
    name: string;
    base_price: number;
    category_id: string;
    description?: string;
  };
}

export const ProductCard = ({ product }: ProductCardProps) => {
  // Map internal business data to UI display
  const { product_id: id, name, base_price: price, category_id: category } = product;
  
  // Use a deterministic placeholder image based on name/id for visual variety
  const image = `https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=2536&auto=format&fit=crop&sig=${id}`;

  return (
    <Link to={`/products/${id}`} className="group relative block">
      {/* Image Container */}
      <div className="relative aspect-[3/4] overflow-hidden bg-muted">
        <img 
          src={image} 
          alt={name} 
          className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
        />
        
        {/* Overlay / Quick Add */}
        <div className="absolute inset-0 bg-black/0 transition-colors duration-300 group-hover:bg-black/10" />
        
        <button className="absolute bottom-4 right-4 p-3 bg-white text-black opacity-0 translate-y-4 transition-all duration-300 group-hover:opacity-100 group-hover:translate-y-0 hover:bg-black hover:text-white">
          <Plus className="w-5 h-5" />
        </button>
        
        {/* Badge */}
        <span className="absolute top-4 left-4 text-[10px] font-bold tracking-[0.2em] uppercase bg-white/90 backdrop-blur-sm px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          {category}
        </span>
      </div>

      {/* Details */}
      <div className="mt-4 space-y-1">
        <h3 className="text-xs font-heading font-medium uppercase tracking-wider group-hover:underline decoration-1 underline-offset-4">
          {name}
        </h3>
        <p className="text-sm text-muted-foreground tabular-nums">
          ¥{price.toLocaleString()}
        </p>
      </div>
    </Link>
  );
};

