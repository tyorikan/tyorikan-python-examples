import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import { useProduct } from '../features/catalog/api/getProduct';
import { useAddToCart } from '../features/cart/api/cart';
import { ChevronRight, Minus, Plus, ShoppingBag, Truck, ShieldCheck, RotateCcw, Loader2, Check } from 'lucide-react';

export const ProductPage = () => {
    const { productId } = useParams();
    const { data: product, isLoading, error } = useProduct(productId || '');
    
    const [selectedColor, setSelectedColor] = useState<string | null>(null);
    const [selectedSize, setSelectedSize] = useState<string | null>(null);
    const [quantity, setQuantity] = useState(1);
    const addToCartMutation = useAddToCart();

    const handleAddToCart = () => {
        if (!product || !selectedColor || !selectedSize) {
            alert('Please select color and size');
            return;
        }

        const variant = product.variants.find(
            v => v.color === selectedColor && v.size === selectedSize
        );

        if (variant) {
            addToCartMutation.mutate({
                product_id: product.product_id,
                variant_id: variant.variant_id,
                quantity: quantity
            });
        }
    };

    if (isLoading) return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
        </div>
    );

    if (error || !product) return (
        <div className="min-h-screen flex flex-col items-center justify-center space-y-4">
            <h1 className="text-2xl font-heading font-bold uppercase tracking-tight">Product Not Found</h1>
            <Link to="/" className="text-sm border-b border-black pb-1 hover:text-muted-foreground transition-colors">Return to Collection</Link>
        </div>
    );

    const colors = [...new Set(product.variants.map(v => v.color))];
    const sizes = [...new Set(product.variants.map(v => v.size))];
    const image = `https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=2536&auto=format&fit=crop&sig=${product.product_id}`;

    return (
        <div className="bg-background pt-24 pb-24">
            {/* Breadcrumbs */}
            <div className="container mx-auto px-6 mb-12">
                <nav className="flex items-center space-x-2 text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
                    <Link to="/" className="hover:text-foreground transition-colors">Collection</Link>
                    <ChevronRight className="w-3 h-3" />
                    <Link to={`/category/${product.category_id.toLowerCase()}`} className="hover:text-foreground transition-colors">{product.category_id}</Link>
                    <ChevronRight className="w-3 h-3" />
                    <span className="text-foreground">{product.name}</span>
                </nav>
            </div>

            <div className="container mx-auto px-6">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-start">
                    
                    {/* Image Section */}
                    <div className="lg:col-span-7 grid grid-cols-1 gap-4">
                        <div className="aspect-[3/4] overflow-hidden bg-muted">
                            <img 
                                src={image} 
                                alt={product.name} 
                                className="w-full h-full object-cover"
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="aspect-[1/1] bg-muted overflow-hidden">
                                <img src={image + "1"} className="w-full h-full object-cover opacity-80" alt="detail 1" />
                            </div>
                            <div className="aspect-[1/1] bg-muted overflow-hidden">
                                <img src={image + "2"} className="w-full h-full object-cover opacity-80" alt="detail 2" />
                            </div>
                        </div>
                    </div>

                    {/* Content Section */}
                    <div className="lg:col-span-5 space-y-12">
                        <div className="space-y-4">
                            <span className="text-[10px] font-bold tracking-[0.3em] uppercase text-muted-foreground">
                                {product.category_id}
                            </span>
                            <h1 className="text-5xl font-heading font-bold uppercase tracking-tighter leading-none">
                                {product.name}
                            </h1>
                            <p className="text-2xl font-medium tabular-nums">
                                ¥{product.base_price.toLocaleString()}
                            </p>
                        </div>

                        <div className="text-sm text-muted-foreground leading-relaxed max-w-md">
                            {product.description}
                        </div>

                        {/* Selectors */}
                        <div className="space-y-8">
                            <div className="space-y-4">
                                <div className="flex justify-between items-end">
                                    <label className="text-[10px] font-bold uppercase tracking-widest text-foreground">Color</label>
                                    <span className="text-[10px] uppercase text-muted-foreground tracking-widest">{selectedColor || 'Select Color'}</span>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {colors.map(color => (
                                        <button
                                            key={color}
                                            onClick={() => setSelectedColor(color)}
                                            className={`h-12 px-6 border text-xs font-bold uppercase tracking-widest transition-all
                                                ${selectedColor === color ? 'bg-black text-white border-black' : 'hover:border-black'}`}
                                        >
                                            {color}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="flex justify-between items-end">
                                    <label className="text-[10px] font-bold uppercase tracking-widest text-foreground">Size</label>
                                    <span className="text-[10px] uppercase text-muted-foreground tracking-widest">Size Guide</span>
                                </div>
                                <div className="grid grid-cols-4 gap-2">
                                    {sizes.map(size => (
                                        <button
                                            key={size}
                                            onClick={() => setSelectedSize(size)}
                                            className={`h-12 border text-xs font-bold uppercase tracking-widest transition-all
                                                ${selectedSize === size ? 'bg-black text-white border-black' : 'hover:border-black'}`}
                                        >
                                            {size}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <label className="text-[10px] font-bold uppercase tracking-widest text-foreground">Quantity</label>
                                <div className="flex items-center w-32 h-12 border border-border">
                                    <button 
                                        onClick={() => setQuantity(Math.max(1, quantity - 1))}
                                        className="flex-1 flex justify-center hover:bg-muted"
                                    >
                                        <Minus className="w-4 h-4" />
                                    </button>
                                    <span className="flex-1 text-center text-sm font-bold tabular-nums">{quantity}</span>
                                    <button 
                                        onClick={() => setQuantity(quantity + 1)}
                                        className="flex-1 flex justify-center hover:bg-muted"
                                    >
                                        <Plus className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="space-y-4 pt-4">
                            <button 
                                onClick={handleAddToCart}
                                disabled={addToCartMutation.isPending}
                                className="w-full h-16 bg-black text-white text-xs font-bold uppercase tracking-[0.2em] flex items-center justify-center gap-3 hover:bg-black/90 transition-all disabled:bg-slate-400"
                            >
                                {addToCartMutation.isPending ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : addToCartMutation.isSuccess ? (
                                    <Check className="w-5 h-5" />
                                ) : (
                                    <ShoppingBag className="w-5 h-5" />
                                )}
                                {addToCartMutation.isSuccess ? 'Added to Cart' : 'Add to Cart'}
                            </button>
                            <button className="w-full h-16 border border-black text-black text-xs font-bold uppercase tracking-[0.2em] hover:bg-black hover:text-white transition-all">
                                Buy It Now
                            </button>
                        </div>

                        {/* Benefits */}
                        <div className="grid grid-cols-1 gap-6 pt-12 border-t border-border">
                            <div className="flex items-start gap-4">
                                <Truck className="w-5 h-5 text-muted-foreground" />
                                <div>
                                    <p className="text-[10px] font-bold uppercase tracking-widest">Free Express Shipping</p>
                                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest mt-1">On orders over ¥50,000</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-4">
                                <RotateCcw className="w-5 h-5 text-muted-foreground" />
                                <div>
                                    <p className="text-[10px] font-bold uppercase tracking-widest">30-Day Returns</p>
                                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest mt-1">Hassle-free return policy</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-4">
                                <ShieldCheck className="w-5 h-5 text-muted-foreground" />
                                <div>
                                    <p className="text-[10px] font-bold uppercase tracking-widest">Secure Checkout</p>
                                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest mt-1">SSL Encrypted Payment System</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

