import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { Layout } from './components/layout/Layout';
import { Home } from './features/home/routes/Home';
import { CategoryPage } from './pages/CategoryPage';
import { ProductPage } from './pages/ProductPage';
import { Cart } from './features/cart/routes/Cart';
import { AuthenticationPage } from './pages/docs/AuthenticationPage';

// Scroll to top on navigation to fix "router not working correctly" behavior
const ScrollToTop = () => {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
};

function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="category/:categoryId" element={<CategoryPage />} />
          <Route path="new" element={<CategoryPage />} />
          <Route path="products/:productId" element={<ProductPage />} />
          <Route path="cart" element={<Cart />} />
          <Route path="docs/authentication" element={<AuthenticationPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
