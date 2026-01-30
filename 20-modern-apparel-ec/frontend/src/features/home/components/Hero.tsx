import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Hero = () => {
  return (
    <section className="relative h-[90vh] w-full overflow-hidden flex items-center justify-center">
      {/* Background Image */}
      <div className="absolute inset-0 z-0">
        <img 
          src="https://images.unsplash.com/photo-1492446845049-9c50cc313f00?q=80&w=2574&auto=format&fit=crop" 
          alt="Urban Fashion Campaign" 
          className="w-full h-full object-cover object-center brightness-75"
        />
        <div className="absolute inset-0 bg-black/30" />
      </div>

      {/* Content */}
      <div className="relative z-10 text-center text-white space-y-8 px-4 max-w-4xl mx-auto animate-fade-in-up">
        {/* Caption */}
        <p className="text-sm md:text-base font-bold tracking-[0.3em] uppercase opacity-90">
          Spring / Summer 2026
        </p>
        
        {/* Main Heading */}
        <h1 className="text-6xl md:text-8xl font-heading font-bold tracking-tighter leading-none">
          ESSENTIAL <br /> SIMPLICITY
        </h1>
        
        {/* Subtitle */}
        <p className="text-lg md:text-xl font-light tracking-wide max-w-2xl mx-auto opacity-90">
          Elevate your daily uniform with our premium collection of urban essentials.
          Designed for the modern minimalist.
        </p>

        {/* CTA Button */}
        <div className="pt-8">
          <Link 
            to="/new" 
            className="group inline-flex items-center gap-3 px-8 py-4 bg-white text-black font-bold uppercase tracking-widest text-sm hover:bg-neutral-200 transition-all duration-300"
          >
            Shop Collection
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </div>
      
      {/* Scroll indicator */}
      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce text-white/50">
        <div className="w-[1px] h-16 bg-gradient-to-b from-transparent via-white to-transparent"></div>
      </div>
    </section>
  );
};
