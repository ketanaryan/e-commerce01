import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';

// Context for authentication
const AuthContext = createContext();

// Context for cart
const CartContext = createContext();

// Custom hooks
const useAuth = () => useContext(AuthContext);
const useCart = () => useContext(CartContext);

// API base URL
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// API helper functions
const api = {
  async call(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      },
      ...options
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }
    
    return response.json();
  },

  get(endpoint) {
    return this.call(endpoint);
  },

  post(endpoint, data) {
    return this.call(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  put(endpoint, data) {
    return this.call(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  delete(endpoint) {
    return this.call(endpoint, {
      method: 'DELETE'
    });
  }
};

// Auth Provider Component
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.get('/api/me')
        .then(setUser)
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const response = await api.post('/api/login', { email, password });
    localStorage.setItem('token', response.token);
    setUser(response.user);
    return response.user;
  };

  const register = async (email, password, name) => {
    const response = await api.post('/api/register', { email, password, name });
    localStorage.setItem('token', response.token);
    setUser(response.user);
    return response.user;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Cart Provider Component
const CartProvider = ({ children }) => {
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  const fetchCart = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const cartData = await api.get('/api/cart');
      setCart(cartData);
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (productId, quantity = 1) => {
    try {
      await api.post('/api/cart', { product_id: productId, quantity });
      await fetchCart();
    } catch (error) {
      console.error('Error adding to cart:', error);
      throw error;
    }
  };

  const updateCart = async (productId, quantity) => {
    try {
      await api.put(`/api/cart/${productId}?quantity=${quantity}`);
      await fetchCart();
    } catch (error) {
      console.error('Error updating cart:', error);
    }
  };

  const removeFromCart = async (productId) => {
    try {
      await api.delete(`/api/cart/${productId}`);
      await fetchCart();
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
  };

  const getCartTotal = () => {
    return cart.reduce((total, item) => total + (item.product.price * item.quantity), 0);
  };

  const getCartItemCount = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  useEffect(() => {
    fetchCart();
  }, [user]);

  const value = {
    cart,
    loading,
    addToCart,
    updateCart,
    removeFromCart,
    getCartTotal,
    getCartItemCount,
    fetchCart
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

// Header Component
const Header = ({ onPageChange, currentPage }) => {
  const { user, logout } = useAuth();
  const { getCartItemCount } = useCart();
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    onPageChange('home', { search: searchTerm });
  };

  return (
    <header className="bg-gray-900 text-white">
      {/* Top bar */}
      <div className="bg-gray-800 py-2">
        <div className="max-w-7xl mx-auto px-4 flex justify-between items-center text-sm">
          <div className="flex items-center space-x-4">
            <span>📍 Deliver to India</span>
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span>Hello, {user.name}</span>
                <button onClick={logout} className="hover:text-orange-400">Sign Out</button>
              </>
            ) : (
              <button onClick={() => onPageChange('login')} className="hover:text-orange-400">
                Hello, Sign in
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main header */}
      <div className="py-4">
        <div className="max-w-7xl mx-auto px-4 flex items-center space-x-4">
          {/* Logo */}
          <div 
            className="text-2xl font-bold cursor-pointer hover:text-orange-400 transition-colors"
            onClick={() => onPageChange('home')}
          >
            ShopHub
          </div>

          {/* Search bar */}
          <form onSubmit={handleSearch} className="flex-1 max-w-2xl">
            <div className="flex">
              <input
                type="text"
                placeholder="Search ShopHub.in"
                className="flex-1 px-4 py-2 text-black rounded-l-md focus:outline-none"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <button 
                type="submit"
                className="bg-orange-400 hover:bg-orange-500 px-6 py-2 rounded-r-md transition-colors"
              >
                🔍
              </button>
            </div>
          </form>

          {/* Right side */}
          <div className="flex items-center space-x-6">
            {/* Language */}
            <div className="text-sm">
              <span className="font-semibold">EN</span>
            </div>

            {/* Account */}
            <div className="text-sm">
              {user ? (
                <div>
                  <div className="font-semibold">Hello, {user.name}</div>
                  <div className="text-xs">Account & Lists</div>
                </div>
              ) : (
                <button 
                  onClick={() => onPageChange('login')}
                  className="hover:text-orange-400"
                >
                  <div className="font-semibold">Hello, sign in</div>
                  <div className="text-xs">Account & Lists</div>
                </button>
              )}
            </div>

            {/* Orders */}
            <button 
              onClick={() => onPageChange('orders')}
              className="text-sm hover:text-orange-400"
            >
              <div className="font-semibold">Returns</div>
              <div className="text-xs">& Orders</div>
            </button>

            {/* Cart */}
            <button 
              onClick={() => onPageChange('cart')}
              className="flex items-center hover:text-orange-400 relative"
            >
              <div className="text-2xl">🛒</div>
              <div className="ml-2">
                <div className="text-xs">Cart</div>
                <div className="font-semibold">{getCartItemCount()}</div>
              </div>
              {getCartItemCount() > 0 && (
                <span className="absolute -top-2 -right-1 bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
                  {getCartItemCount()}
                </span>
              )}
            </button>

            {/* Admin */}
            {user && user.role === 'admin' && (
              <button
                onClick={() => onPageChange('admin')}
                className="text-sm hover:text-orange-400"
              >
                <div className="font-semibold">Admin</div>
                <div className="text-xs">Dashboard</div>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Navigation bar */}
      <div className="bg-gray-700 py-2">
        <div className="max-w-7xl mx-auto px-4 flex items-center space-x-6 text-sm">
          <button 
            onClick={() => onPageChange('home')}
            className="hover:text-orange-400 font-semibold"
          >
            All
          </button>
          <button className="hover:text-orange-400">Mobiles</button>
          <button className="hover:text-orange-400">Best Sellers</button>
          <button className="hover:text-orange-400">Today's Deals</button>
          <button className="hover:text-orange-400">Customer Service</button>
          <button className="hover:text-orange-400">Electronics</button>
          <button className="hover:text-orange-400">Fashion</button>
          <button className="hover:text-orange-400">Home & Kitchen</button>
          <button className="hover:text-orange-400">Prime</button>
        </div>
      </div>
    </header>
  );
};

// Login Component
const Login = ({ onPageChange }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(formData.email, formData.password);
      } else {
        await register(formData.email, formData.password, formData.name);
      }
      onPageChange('home');
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">ShopHub</h1>
          <h2 className="text-2xl font-semibold text-gray-700">
            {isLogin ? 'Sign in' : 'Create account'}
          </h2>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-lg rounded-lg sm:px-10 border">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}
            
            {!isLogin && (
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Your name
                </label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  placeholder="First and last name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
            )}
            
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 pr-10"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-orange-500 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
              </button>
            </div>
          </form>
          
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">New to ShopHub?</span>
              </div>
            </div>
            
            <div className="mt-6">
              <button
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                {isLogin ? 'Create your ShopHub account' : 'Sign in to existing account'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Product Card Component
const ProductCard = ({ product, onAddToCart }) => {
  const [loading, setLoading] = useState(false);

  const handleAddToCart = async () => {
    setLoading(true);
    try {
      await onAddToCart(product.id);
    } catch (error) {
      alert('Error adding to cart: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow duration-300 overflow-hidden border border-gray-200">
      <div className="relative overflow-hidden">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-64 object-cover hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded text-xs font-semibold">
          {Math.floor(Math.random() * 30 + 10)}% off
        </div>
      </div>
      
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 hover:text-orange-600 cursor-pointer">
          {product.name}
        </h3>
        
        <div className="flex items-center mb-2">
          <div className="flex text-yellow-400">
            {'★'.repeat(4)}{'☆'.repeat(1)}
          </div>
          <span className="text-sm text-gray-600 ml-2">(247)</span>
        </div>
        
        <div className="mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-gray-900">₹{product.price.toLocaleString('en-IN')}</span>
            <span className="text-sm text-gray-500 line-through">₹{(product.price * 1.3).toLocaleString('en-IN')}</span>
          </div>
          <div className="text-sm text-green-600 font-medium">FREE Delivery</div>
        </div>
        
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">{product.description}</p>
        
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            Category: {product.category_name}
          </div>
          <div className="text-sm text-green-600 font-medium">
            In Stock ({product.stock})
          </div>
        </div>
        
        <button
          onClick={handleAddToCart}
          disabled={loading}
          className="w-full mt-4 bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50"
        >
          {loading ? 'Adding...' : 'Add to Cart'}
        </button>
      </div>
    </div>
  );
};

// Home Component
const Home = ({ searchQuery }) => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState(searchQuery || '');
  const [selectedCategory, setSelectedCategory] = useState('');
  const { user } = useAuth();
  const { addToCart } = useCart();

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (searchQuery) {
      setSearchTerm(searchQuery);
    }
  }, [searchQuery]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [productsData, categoriesData] = await Promise.all([
        api.get('/api/products'),
        api.get('/api/categories')
      ]);
      setProducts(productsData);
      setCategories(categoriesData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || product.category_id === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleAddToCart = async (productId) => {
    if (!user) {
      alert('Please login to add items to cart');
      return;
    }
    await addToCart(productId);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-gray-100 min-h-screen">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-orange-400 to-pink-500 text-white py-12 mb-6">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">Great Indian Festival</h1>
          <p className="text-xl mb-6">Discover amazing products at unbeatable prices</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white bg-opacity-20 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-2">📱 Electronics</h3>
              <p>Up to 70% off on mobiles, laptops & more</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-2">👗 Fashion</h3>
              <p>Latest trends at best prices</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-2">🏠 Home & Kitchen</h3>
              <p>Transform your living space</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-center">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search products..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div>
              <select
                className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 min-w-48"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>{category.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Products Grid */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {searchTerm ? `Search results for "${searchTerm}"` : 'All Products'}
            <span className="text-sm font-normal text-gray-600 ml-2">
              ({filteredProducts.length} items)
            </span>
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredProducts.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
              />
            ))}
          </div>

          {filteredProducts.length === 0 && (
            <div className="text-center py-12 bg-white rounded-lg">
              <div className="text-6xl mb-4">😔</div>
              <p className="text-gray-500 text-lg mb-4">No products found</p>
              <p className="text-gray-400">Try adjusting your search or filter criteria</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Cart Component
const Cart = ({ onPageChange }) => {
  const { cart, loading, updateCart, removeFromCart, getCartTotal } = useCart();
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [shippingAddress, setShippingAddress] = useState('');
  const { user } = useAuth();

  const handleCheckout = async () => {
    if (!shippingAddress.trim()) {
      alert('Please enter shipping address');
      return;
    }

    setCheckoutLoading(true);
    try {
      const orderItems = cart.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity
      }));

      await api.post('/api/orders', {
        items: orderItems,
        shipping_address: shippingAddress
      });

      alert('Order placed successfully!');
      onPageChange('orders');
    } catch (error) {
      alert('Error placing order: ' + error.message);
    } finally {
      setCheckoutLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Please login to view your cart</h2>
        <button
          onClick={() => onPageChange('login')}
          className="bg-orange-500 text-white px-6 py-3 rounded-md hover:bg-orange-600"
        >
          Sign In
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-gray-100 min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>

        {cart.length === 0 ? (
          <div className="bg-white rounded-lg p-12 text-center">
            <div className="text-6xl mb-4">🛒</div>
            <h2 className="text-2xl font-semibold mb-4">Your cart is empty</h2>
            <p className="text-gray-600 mb-6">Looks like you haven't added anything to your cart yet</p>
            <button
              onClick={() => onPageChange('home')}
              className="bg-orange-500 text-white px-6 py-3 rounded-md hover:bg-orange-600"
            >
              Continue Shopping
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <div className="lg:col-span-3">
              <div className="bg-white rounded-lg shadow-sm">
                <div className="p-6 border-b">
                  <h2 className="text-xl font-semibold">Cart ({cart.length} items)</h2>
                </div>
                
                {cart.map(item => (
                  <div key={item.product_id} className="p-6 border-b last:border-b-0">
                    <div className="flex items-center gap-6">
                      <img
                        src={item.product.image_url}
                        alt={item.product.name}
                        className="w-24 h-24 object-cover rounded"
                      />
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {item.product.name}
                        </h3>
                        <p className="text-gray-600 mb-2">₹{item.product.price.toLocaleString('en-IN')}</p>
                        <div className="text-sm text-green-600 font-medium mb-2">In Stock</div>
                        <div className="text-sm text-gray-500">
                          Eligible for FREE Shipping
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="flex items-center border rounded">
                          <button
                            onClick={() => updateCart(item.product_id, item.quantity - 1)}
                            className="px-3 py-1 hover:bg-gray-100"
                          >
                            −
                          </button>
                          <span className="px-4 py-1 border-x">{item.quantity}</span>
                          <button
                            onClick={() => updateCart(item.product_id, item.quantity + 1)}
                            className="px-3 py-1 hover:bg-gray-100"
                          >
                            +
                          </button>
                        </div>
                        <button
                          onClick={() => removeFromCart(item.product_id)}
                          className="text-red-600 hover:text-red-800 text-sm underline"
                        >
                          Delete
                        </button>
                      </div>
                      <div className="text-right">
                        <p className="text-xl font-semibold">
                          ₹{(item.product.price * item.quantity).toLocaleString('en-IN')}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-sm p-6 sticky top-6">
                <h3 className="text-lg font-semibold mb-4">Order Summary</h3>
                
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between">
                    <span>Subtotal ({cart.length} items):</span>
                    <span>₹{getCartTotal().toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Shipping:</span>
                    <span className="text-green-600">FREE</span>
                  </div>
                  <div className="border-t pt-3">
                    <div className="flex justify-between font-semibold text-lg">
                      <span>Order Total:</span>
                      <span className="text-red-600">₹{getCartTotal().toLocaleString('en-IN')}</span>
                    </div>
                  </div>
                </div>

                <div className="mb-6">
                  <label className="block text-sm font-medium mb-2">Delivery Address</label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                    rows="3"
                    placeholder="Enter your delivery address"
                    value={shippingAddress}
                    onChange={(e) => setShippingAddress(e.target.value)}
                  />
                </div>

                <button
                  onClick={handleCheckout}
                  disabled={checkoutLoading}
                  className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-medium py-3 px-4 rounded-md disabled:opacity-50"
                >
                  {checkoutLoading ? 'Processing...' : 'Proceed to Buy'}
                </button>
                
                <div className="text-xs text-gray-500 mt-2 text-center">
                  By placing your order, you agree to ShopHub's privacy notice and conditions of use.
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Orders Component
const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchOrders();
    }
  }, [user]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const ordersData = await api.get('/api/orders');
      setOrders(ordersData);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Please login to view your orders</h2>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-gray-100 min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Your Orders</h1>

        {orders.length === 0 ? (
          <div className="bg-white rounded-lg p-12 text-center">
            <div className="text-6xl mb-4">📦</div>
            <h2 className="text-2xl font-semibold mb-4">No orders yet</h2>
            <p className="text-gray-600">You haven't placed any orders yet</p>
          </div>
        ) : (
          <div className="space-y-6">
            {orders.map(order => (
              <div key={order.id} className="bg-white rounded-lg shadow-sm">
                <div className="p-6 border-b bg-gray-50">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-gray-600">ORDER PLACED</div>
                      <div className="font-medium">
                        {new Date(order.created_at).toLocaleDateString('en-IN')}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">TOTAL</div>
                      <div className="font-medium">₹{order.total_amount.toLocaleString('en-IN')}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">STATUS</div>
                      <div className={`font-medium ${
                        order.status === 'completed' ? 'text-green-600' :
                        order.status === 'pending' ? 'text-yellow-600' :
                        'text-gray-600'
                      }`}>
                        {order.status.toUpperCase()}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">ORDER #</div>
                      <div className="font-medium">{order.id.slice(-8)}</div>
                    </div>
                  </div>
                </div>

                <div className="p-6">
                  <h3 className="font-semibold mb-4">Order Items</h3>
                  <div className="space-y-4">
                    {order.items.map((item, index) => (
                      <div key={index} className="flex justify-between items-center py-2 border-b last:border-b-0">
                        <div>
                          <p className="font-medium">{item.product_name}</p>
                          <p className="text-gray-600 text-sm">Quantity: {item.quantity}</p>
                        </div>
                        <p className="font-medium">₹{item.total.toLocaleString('en-IN')}</p>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-6 pt-4 border-t">
                    <p className="text-gray-600">
                      <strong>Delivery Address:</strong> {order.shipping_address}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Admin Component
const Admin = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({});
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user && user.role === 'admin') {
      fetchData();
    }
  }, [user, activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'dashboard') {
        const statsData = await api.get('/api/admin/stats');
        setStats(statsData);
      } else if (activeTab === 'products') {
        const productsData = await api.get('/api/products');
        setProducts(productsData);
        const categoriesData = await api.get('/api/categories');
        setCategories(categoriesData);
      } else if (activeTab === 'orders') {
        const ordersData = await api.get('/api/admin/orders');
        setOrders(ordersData);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user || user.role !== 'admin') {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Access Denied</h2>
        <p className="text-gray-600">You don't have permission to access this page.</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-100 min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm mb-8">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: '📊' },
              { id: 'products', label: 'Products', icon: '📦' },
              { id: 'orders', label: 'Orders', icon: '🛒' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-orange-500 text-orange-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-orange-500"></div>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
                  <div className="flex items-center">
                    <div className="text-3xl mr-4">📦</div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Total Products</h3>
                      <p className="text-3xl font-bold text-blue-600">{stats.total_products}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
                  <div className="flex items-center">
                    <div className="text-3xl mr-4">🛒</div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Total Orders</h3>
                      <p className="text-3xl font-bold text-green-600">{stats.total_orders}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-purple-500">
                  <div className="flex items-center">
                    <div className="text-3xl mr-4">👥</div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Total Users</h3>
                      <p className="text-3xl font-bold text-purple-600">{stats.total_users}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-yellow-500">
                  <div className="flex items-center">
                    <div className="text-3xl mr-4">💰</div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Total Revenue</h3>
                      <p className="text-3xl font-bold text-yellow-600">₹{stats.total_revenue?.toLocaleString('en-IN')}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'products' && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-semibold">Products Management</h3>
                  <div className="text-sm text-gray-600">Total: {products.length} products</div>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {products.slice(0, 10).map(product => (
                        <tr key={product.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <img className="h-10 w-10 rounded-full object-cover" src={product.image_url} alt="" />
                              <div className="ml-4">
                                <div className="text-sm font-medium text-gray-900">{product.name}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            ₹{product.price.toLocaleString('en-IN')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{product.stock}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.category_name}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'orders' && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-semibold">Orders Management</h3>
                  <div className="text-sm text-gray-600">Total: {orders.length} orders</div>
                </div>
                
                <div className="space-y-4">
                  {orders.slice(0, 10).map(order => (
                    <div key={order.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">Order #{order.id.slice(-8)}</p>
                          <p className="text-gray-600">{order.user_name} - {order.user_email}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(order.created_at).toLocaleDateString('en-IN')}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">₹{order.total_amount.toLocaleString('en-IN')}</p>
                          <span className={`inline-block px-2 py-1 rounded text-sm ${
                            order.status === 'completed' ? 'bg-green-100 text-green-800' :
                            order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {order.status.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const [currentPage, setCurrentPage] = useState('home');
  const [pageData, setPageData] = useState({});

  const handlePageChange = (page, data = {}) => {
    setCurrentPage(page);
    setPageData(data);
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home searchQuery={pageData.search} />;
      case 'login':
        return <Login onPageChange={handlePageChange} />;
      case 'cart':
        return <Cart onPageChange={handlePageChange} />;
      case 'orders':
        return <Orders />;
      case 'admin':
        return <Admin />;
      default:
        return <Home />;
    }
  };

  return (
    <AuthProvider>
      <CartProvider>
        <div className="min-h-screen bg-gray-100">
          <Header onPageChange={handlePageChange} currentPage={currentPage} />
          <main>
            {renderCurrentPage()}
          </main>
          <footer className="bg-gray-900 text-white py-12 mt-12">
            <div className="max-w-7xl mx-auto px-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                  <h3 className="font-semibold mb-4">Get to Know Us</h3>
                  <ul className="space-y-2 text-sm">
                    <li><a href="#" className="hover:text-orange-400">About Us</a></li>
                    <li><a href="#" className="hover:text-orange-400">Careers</a></li>
                    <li><a href="#" className="hover:text-orange-400">Press Releases</a></li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold mb-4">Connect with Us</h3>
                  <ul className="space-y-2 text-sm">
                    <li><a href="#" className="hover:text-orange-400">Facebook</a></li>
                    <li><a href="#" className="hover:text-orange-400">Twitter</a></li>
                    <li><a href="#" className="hover:text-orange-400">Instagram</a></li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold mb-4">Make Money with Us</h3>
                  <ul className="space-y-2 text-sm">
                    <li><a href="#" className="hover:text-orange-400">Sell on ShopHub</a></li>
                    <li><a href="#" className="hover:text-orange-400">Become an Affiliate</a></li>
                    <li><a href="#" className="hover:text-orange-400">Advertise Your Products</a></li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold mb-4">Let Us Help You</h3>
                  <ul className="space-y-2 text-sm">
                    <li><a href="#" className="hover:text-orange-400">COVID-19 and ShopHub</a></li>
                    <li><a href="#" className="hover:text-orange-400">Your Account</a></li>
                    <li><a href="#" className="hover:text-orange-400">Returns Centre</a></li>
                    <li><a href="#" className="hover:text-orange-400">Help</a></li>
                  </ul>
                </div>
              </div>
              <div className="border-t border-gray-700 mt-8 pt-8 text-center text-sm text-gray-400">
                <p>&copy; 1996-2024, ShopHub.in, Inc. or its affiliates</p>
              </div>
            </div>
          </footer>
        </div>
      </CartProvider>
    </AuthProvider>
  );
};

export default App;