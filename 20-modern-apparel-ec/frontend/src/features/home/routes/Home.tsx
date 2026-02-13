import { Hero } from '../components/Hero';
import { ProductCard } from '../../products/components/ProductCard';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useProducts } from '../../catalog/api/getProducts';

export const Home = () => {
  const { data: products, isLoading, error } = useProducts();

  // Pick top 3 products for the trending section
  const trendingProducts = products?.slice(0, 3) || [];

  return (
    <div className="flex flex-col space-y-0">
      <Hero />
      
      {/* Featured Section */}
      <section className="py-24 bg-background px-6">
        <div className="container mx-auto">
          <div className="flex justify-between items-end mb-12">
            <h2 className="text-4xl font-heading font-bold uppercase tracking-tight">Trending Now</h2>
            <Link to="/new" className="hidden md:flex items-center gap-2 text-sm font-bold uppercase tracking-widest hover:text-muted-foreground transition-colors">
              View All <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          
          {isLoading && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 animate-pulse">
              {[1, 2, 3].map((i) => (
                <div key={i} className="aspect-[3/4] bg-muted" />
              ))}
            </div>
          )}

          {error && (
            <div className="py-12 text-center">
              <p className="text-red-500 font-bold uppercase tracking-widest">Error loading pieces</p>
            </div>
          )}

          {!isLoading && !error && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {trendingProducts.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          )}

          {!isLoading && !error && trendingProducts.length === 0 && (
            <p className="text-center text-muted-foreground uppercase tracking-widest py-12">No pieces found</p>
          )}
        </div>
      </section>

      {/* Categories Montage */}
      <section className="py-0 grid grid-cols-1 md:grid-cols-2 h-[80vh]">
        <Link to="/category/men" className="relative group overflow-hidden">
          <img 
            src="https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?q=80&w=2187&auto=format&fit=crop" 
            alt="Men" 
            className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors duration-300" />
          <div className="absolute bottom-12 left-12 text-white">
            <h3 className="text-5xl font-heading font-bold uppercase tracking-tight mb-2">Men</h3>
            <span className="inline-block border-b border-white pb-1 text-sm tracking-widest uppercase">Shop Now</span>
          </div>
        </Link>
        <Link to="/category/women" className="relative group overflow-hidden">
          <img 
            src="https://images.unsplash.com/photo-1548036328-c9fa89d128fa?q=80&w=2669&auto=format&fit=crop" 
            alt="Women" 
            className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors duration-300" />
          <div className="absolute bottom-12 left-12 text-white">
            <h3 className="text-5xl font-heading font-bold uppercase tracking-tight mb-2">Women</h3>
            <span className="inline-block border-b border-white pb-1 text-sm tracking-widest uppercase">Shop Now</span>
          </div>
        </Link>
      </section>

      {/* Editorial / Brand Story */}
      <section className="py-32 bg-secondary text-secondary-foreground text-center px-6">
        <div className="max-w-3xl mx-auto space-y-8">
          <h2 className="text-3xl font-heading font-bold uppercase tracking-widest">Philosophy</h2>
          <p className="text-lg md:text-2xl font-light leading-relaxed">
            "True luxury is found in the absence of excess. We strip away the unnecessary, focusing on silhouette, texture, and uncompromising quality."
          </p>
          <div className="pt-8">
             <Link to="/about" className="text-sm font-bold uppercase tracking-widest border-b border-black pb-1 hover:text-muted-foreground hover:border-muted-foreground transition-colors">
               Read Our Story
             </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
