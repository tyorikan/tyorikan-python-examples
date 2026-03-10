import { Link } from 'react-router-dom';
import { ShoppingBag, Search, User, Menu } from 'lucide-react';
import { useState } from 'react';

export const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-white/10 transition-all duration-300">
      <div className="container mx-auto px-6 h-20 flex items-center justify-between">
        {/* Mobile Menu Button */}
        <button 
          className="md:hidden p-2 text-foreground"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <Menu className="w-6 h-6" />
        </button>

        {/* Logo */}
        <Link to="/" className="text-2xl font-heading font-bold tracking-tighter uppercase z-50">
          Tyorikan
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-12">
          <NavLink to="/">Collection</NavLink>
          <NavLink to="/category/men">Men</NavLink>
          <NavLink to="/category/women">Women</NavLink>
          <NavLink to="/category/accessories">Accessories</NavLink>
        </div>

        {/* Icons */}
        <div className="flex items-center space-x-6">
          <button className="p-2 hover:text-muted-foreground transition-colors">
            <Search className="w-5 h-5" />
          </button>
          <Link to="/login" className="p-2 hover:text-muted-foreground transition-colors">
            <User className="w-5 h-5" />
          </Link>
          <Link to="/cart" className="p-2 hover:text-muted-foreground transition-colors relative">
            <ShoppingBag className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-foreground rounded-full"></span>
          </Link>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isMenuOpen && (
        <div className="absolute top-20 left-0 w-full bg-background border-b border-border md:hidden animate-accordion-down">
          <div className="flex flex-col p-6 space-y-4">
            <MobileNavLink to="/" onClick={() => setIsMenuOpen(false)}>Collection</MobileNavLink>
            <MobileNavLink to="/category/men" onClick={() => setIsMenuOpen(false)}>Men</MobileNavLink>
            <MobileNavLink to="/category/women" onClick={() => setIsMenuOpen(false)}>Women</MobileNavLink>
            <MobileNavLink to="/category/accessories" onClick={() => setIsMenuOpen(false)}>Accessories</MobileNavLink>
          </div>
        </div>
      )}
    </nav>
  );
};

const NavLink = ({ to, children }: { to: string; children: React.ReactNode }) => (
  <Link 
    to={to} 
    className="text-sm font-medium tracking-wide hover:text-muted-foreground transition-colors uppercase"
  >
    {children}
  </Link>
);

const MobileNavLink = ({ to, onClick, children }: { to: string; onClick: () => void; children: React.ReactNode }) => (
  <Link 
    to={to} 
    onClick={onClick}
    className="text-lg font-medium py-2 border-b border-border"
  >
    {children}
  </Link>
);
