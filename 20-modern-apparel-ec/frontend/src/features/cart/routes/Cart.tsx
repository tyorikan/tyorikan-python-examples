import { useCart, useRemoveFromCart, useUpdateCartItem } from '../api/cart';
import { Trash2, Minus, Plus, ShoppingBag } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Cart = () => {
  const { data: cart, isLoading, error } = useCart();
  const removeMutation = useRemoveFromCart();
  const updateMutation = useUpdateCartItem();

  const handleUpdateQuantity = (productId: string, variantId: string, currentQty: number, delta: number) => {
    const newQty = currentQty + delta;
    if (newQty > 0) {
      updateMutation.mutate({ product_id: productId, variant_id: variantId, quantity: newQty });
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-6 py-24 animate-pulse">
        <div className="h-10 w-48 bg-muted mb-8" />
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-24 bg-muted w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-6 py-24 text-center">
        <p className="text-red-500 font-bold uppercase tracking-widest">Error loading cart</p>
      </div>
    );
  }

  const items = cart?.items || [];

  return (
    <div className="container mx-auto px-6 py-12 md:py-24 max-w-4xl">
      <h1 className="text-4xl font-heading font-bold uppercase tracking-tight mb-12">Your Cart</h1>
      
      {items.length === 0 ? (
        <div className="text-center py-24 border-2 border-dashed border-slate-200">
          <ShoppingBag className="w-16 h-16 mx-auto mb-6 text-slate-300" />
          <p className="text-xl text-slate-500 mb-8 font-medium">Your cart is empty</p>
          <Link 
            to="/" 
            className="inline-block bg-indigo-600 text-white px-8 py-4 font-bold uppercase tracking-widest hover:bg-indigo-700 transition-colors"
          >
            Start Shopping
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-12">
          <div className="space-y-8">
            {items.map((item) => (
              <div key={`${item.product_id}-${item.variant_id}`} className="flex flex-col md:flex-row gap-6 pb-8 border-b border-slate-100">
                <div className="w-full md:w-32 aspect-[3/4] bg-slate-100 overflow-hidden">
                  <img 
                    src={`https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=2536&auto=format&fit=crop&sig=${item.product_id}`} 
                    alt={item.product_name}
                    className="w-full h-full object-cover"
                  />
                </div>
                
                <div className="flex-1 space-y-2">
                  <div className="flex justify-between items-start">
                    <h3 className="text-xl font-bold uppercase tracking-tight">{item.product_name}</h3>
                    <button 
                      onClick={() => removeMutation.mutate({ product_id: item.product_id, variant_id: item.variant_id })}
                      className="text-slate-400 hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                  <p className="text-slate-500 text-sm uppercase tracking-widest font-medium">
                    {item.color} / {item.size}
                  </p>
                  
                  <div className="flex justify-between items-end mt-4">
                    <div className="flex items-center border border-slate-200">
                      <button 
                        onClick={() => handleUpdateQuantity(item.product_id, item.variant_id, item.quantity, -1)}
                        className="p-2 hover:bg-slate-50 transition-colors"
                      >
                        <Minus className="w-4 h-4" />
                      </button>
                      <span className="w-12 text-center font-bold">{item.quantity}</span>
                      <button 
                        onClick={() => handleUpdateQuantity(item.product_id, item.variant_id, item.quantity, 1)}
                        className="p-2 hover:bg-slate-50 transition-colors"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-xl font-bold">¥{item.unit_price * item.quantity}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="bg-slate-50 p-8 space-y-6">
            <div className="flex justify-between items-center border-b border-slate-200 pb-4">
              <span className="text-slate-500 uppercase tracking-widest font-bold text-sm">Subtotal</span>
              <span className="text-2xl font-bold">¥{cart?.total_amount}</span>
            </div>
            <p className="text-slate-400 text-xs uppercase tracking-widest leading-loose">
              Shipping and taxes calculated at checkout.
            </p>
            <button className="w-full bg-indigo-600 text-white py-5 font-bold uppercase tracking-widest hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-100">
              Proceed to Checkout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
