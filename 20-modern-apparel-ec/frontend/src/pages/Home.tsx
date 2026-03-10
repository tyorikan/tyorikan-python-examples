import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Home = () => {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative h-[600px] w-full bg-gray-100 flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-neutral-200">
           {/* Placeholder for Hero Image */}
           <div className="w-full h-full bg-gradient-to-r from-gray-200 to-gray-300" />
        </div>
        <div className="relative z-10 text-center space-y-4 max-w-2xl px-4">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tighter">
            LifeWear. <br /> Designed for you.
          </h1>
          <p className="text-lg md:text-xl text-gray-700">
            Simple, high-quality, everyday clothing with a practical sense of beauty.
          </p>
          <div className="pt-4">
             <Link to="/category/new" className="inline-flex items-center gap-2 bg-black text-white px-8 py-3 rounded-full hover:bg-gray-800 transition-colors">
               Shop New Arrivals <ArrowRight className="h-4 w-4" />
             </Link>
          </div>
        </div>
      </section>

      {/* Categories Grid */}
      <section className="py-16 container mx-auto px-4">
        <h2 className="text-2xl font-bold mb-8">Collections</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
           {['WOMEN', 'MEN', 'KIDS'].map((cat) => (
             <Link key={cat} to={`/category/${cat.toLowerCase()}`} className="group relative aspect-[3/4] overflow-hidden bg-gray-100 block">
               <div className="absolute inset-0 flex items-center justify-center">
                 <span className="text-xl font-bold">{cat}</span>
               </div>
               <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors" />
             </Link>
           ))}
        </div>
      </section>
    </div>
  );
};
