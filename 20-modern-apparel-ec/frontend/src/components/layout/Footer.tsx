import { Link } from 'react-router-dom';

export const Footer = () => {
  return (
    <footer className="bg-foreground text-background pt-24 pb-12">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-20">
          
          {/* Brand Column */}
          <div className="space-y-6">
            <h3 className="text-2xl font-heading font-bold tracking-tighter uppercase">Tyorikan</h3>
            <p className="text-muted-foreground text-sm leading-relaxed max-w-xs">
              Redefining modern urban lifestyle through minimalist design and premium functionality.
            </p>
          </div>

          {/* Shop Column */}
          <div className="space-y-6">
            <h4 className="font-bold uppercase tracking-wider text-sm">Shop</h4>
            <ul className="space-y-4 text-sm text-muted-foreground">
              <li><Link to="/new" className="hover:text-white transition-colors">New Arrivals</Link></li>
              <li><Link to="/men" className="hover:text-white transition-colors">Men</Link></li>
              <li><Link to="/women" className="hover:text-white transition-colors">Women</Link></li>
              <li><Link to="/accessories" className="hover:text-white transition-colors">Accessories</Link></li>
            </ul>
          </div>

          {/* Help Column */}
          <div className="space-y-6">
            <h4 className="font-bold uppercase tracking-wider text-sm">Help</h4>
            <ul className="space-y-4 text-sm text-muted-foreground">
              <li><Link to="/shipping" className="hover:text-white transition-colors">Shipping & Returns</Link></li>
              <li><Link to="/faq" className="hover:text-white transition-colors">FAQ</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">Contact Us</Link></li>
              <li><Link to="/terms" className="hover:text-white transition-colors">Terms & Conditions</Link></li>
            </ul>
          </div>

          {/* Newsletter Column */}
          <div className="space-y-6">
            <h4 className="font-bold uppercase tracking-wider text-sm">Newsletter</h4>
            <p className="text-sm text-muted-foreground">Subscribe to receive updates, access to exclusive deals, and more.</p>
            <form className="flex flex-col space-y-4">
              <input 
                type="email" 
                placeholder="Enter your email" 
                className="bg-transparent border-b border-muted-foreground focus:border-white py-2 outline-none text-sm transition-colors"
              />
              <button className="text-left text-sm font-bold uppercase tracking-wider hover:text-muted-foreground transition-colors">
                Subscribe
              </button>
            </form>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-white/10 text-xs text-muted-foreground">
          <p>© 2026 Tyorikan Inc. All rights reserved.</p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className="hover:text-white transition-colors">Instagram</a>
            <a href="#" className="hover:text-white transition-colors">Twitter</a>
            <a href="#" className="hover:text-white transition-colors">Facebook</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
