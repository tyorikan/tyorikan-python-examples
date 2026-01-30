import { ShoppingCart, Menu, Search, User } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Header = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white text-black">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Left: Logo & Mobile Menu */}
        <div className="flex items-center gap-4">
          <button className="lg:hidden p-2 hover:bg-gray-100 rounded-full">
            <Menu className="h-6 w-6" />
          </button>
          <Link to="/" className="text-2xl font-bold tracking-tighter text-red-600">
            UNIQLO-ISH
          </Link>
        </div>

        {/* Center: Navigation (Desktop) */}
        <nav className="hidden lg:flex items-center gap-8 font-medium text-sm">
          <Link to="/category/women" className="hover:text-gray-600">WOMEN</Link>
          <Link to="/category/men" className="hover:text-gray-600">MEN</Link>
          <Link to="/category/kids" className="hover:text-gray-600">KIDS</Link>
          <Link to="/category/baby" className="hover:text-gray-600">BABY</Link>
        </nav>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-gray-100 rounded-full">
            <Search className="h-6 w-6" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-full">
            <User className="h-6 w-6" />
          </button>
          <Link to="/cart" className="p-2 hover:bg-gray-100 rounded-full relative">
            <ShoppingCart className="h-6 w-6" />
            {/* Badge Placeholder */}
            {/* <span className="absolute top-1 right-1 h-2 w-2 bg-red-600 rounded-full" /> */}
          </Link>
        </div>
      </div>
    </header>
  );
};
