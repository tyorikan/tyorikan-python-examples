import { useParams } from 'react-router-dom';
import { useProducts } from '../features/catalog/api/getProducts';
import { ProductCard } from '../features/products/components/ProductCard';

export const CategoryPage = () => {
    const { categoryId } = useParams();
    const { data: products, isLoading, error } = useProducts();
    
    // Determine the title based on route param or path
    const isNew = window.location.pathname.endsWith('/new');
    const displayTitle = isNew ? 'New Arrivals' : (categoryId || 'All Products');

    if (isLoading) return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
        </div>
    );

    if (error) return (
        <div className="min-h-screen flex items-center justify-center">
            <p className="text-red-500 font-bold tracking-widest uppercase">Error loading collection</p>
        </div>
    );

    // Client-side filtering for MVP
    let filteredProducts = products; 
    if (isNew) {
        filteredProducts = products?.slice(0, 5);
    } else if (categoryId && categoryId !== 'all') {
        filteredProducts = products?.filter(p => p.category_id.toLowerCase().includes(categoryId.toLowerCase()));
    }

    return (
        <div className="bg-background pt-32 pb-24">
            <div className="container mx-auto px-6">
                <header className="mb-16 space-y-4">
                    <h1 className="text-6xl font-heading font-bold uppercase tracking-tighter">{displayTitle}</h1>
                    <div className="flex justify-between items-end border-b border-border pb-8">
                        <p className="text-xs text-muted-foreground uppercase tracking-widest">
                            Showing {filteredProducts?.length || 0} items
                        </p>
                        <div className="flex gap-8 text-[10px] font-bold uppercase tracking-widest">
                            <button className="hover:text-muted-foreground transition-colors">Sort By</button>
                            <button className="hover:text-muted-foreground transition-colors">Filter</button>
                        </div>
                    </div>
                </header>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-16">
                    {filteredProducts?.map((product) => (
                        <ProductCard key={product.product_id} product={product} />
                    ))}
                </div>

                {(!filteredProducts || filteredProducts.length === 0) && (
                    <div className="py-24 text-center">
                        <p className="text-sm text-muted-foreground uppercase tracking-[0.2em]">No pieces found in this collection.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

