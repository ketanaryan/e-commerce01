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

  return (
    <header className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold cursor-pointer" onClick={() => onPageChange('home')}>
              ShopHub
            </h1>
          </div>
          
          <nav className="flex items-center space-x-4">
            <button
              onClick={() => onPageChange('home')}
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                currentPage === 'home' ? 'bg-blue-700' : 'hover:bg-blue-700'
              }`}
            >
              Home
            </button>
            
            {user ? (
              <>
                <button
                  onClick={() => onPageChange('cart')}
                  className={`px-3 py-2 rounded-md text-sm font-medium relative ${
                    currentPage === 'cart' ? 'bg-blue-700' : 'hover:bg-blue-700'
                  }`}
                >
                  Cart
                  {getCartItemCount() > 0 && (
                    <span className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">
                      {getCartItemCount()}
                    </span>
                  )}
                </button>
                
                <button
                  onClick={() => onPageChange('orders')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentPage === 'orders' ? 'bg-blue-700' : 'hover:bg-blue-700'
                  }`}
                >
                  Orders
                </button>
                
                {user.role === 'admin' && (
                  <button
                    onClick={() => onPageChange('admin')}
                    className={`px-3 py-2 rounded-md text-sm font-medium ${
                      currentPage === 'admin' ? 'bg-blue-700' : 'hover:bg-blue-700'
                    }`}
                  >
                    Admin
                  </button>
                )}
                
                <div className="flex items-center space-x-2">
                  <span className="text-sm">Welcome, {user.name}!</span>
                  <button
                    onClick={logout}
                    className="px-3 py-2 rounded-md text-sm font-medium bg-red-600 hover:bg-red-700"
                  >
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <button
                onClick={() => onPageChange('login')}
                className="px-3 py-2 rounded-md text-sm font-medium bg-green-600 hover:bg-green-700"
              >
                Login
              </button>
            )}
          </nav>
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
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {isLogin ? 'Sign in to your account' : 'Create new account'}
          </h2>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            {!isLogin && (
              <input
                type="text"
                required
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Full Name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            )}
            
            <input
              type="email"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Email address"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
            
            <input
              type="password"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Loading...' : (isLogin ? 'Sign in' : 'Register')}
            </button>
          </div>
          
          <div className="text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-600 hover:text-blue-500"
            >
              {isLogin ? 'Need an account? Register' : 'Already have an account? Sign in'}
            </button>
          </div>
        </form>
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
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <img
        src={product.image_url}
        alt={product.name}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{product.name}</h3>
        <p className="text-gray-600 text-sm mb-3">{product.description}</p>
        <div className="flex justify-between items-center">
          <span className="text-2xl font-bold text-blue-600">${product.price}</span>
          <button
            onClick={handleAddToCart}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Adding...' : 'Add to Cart'}
          </button>
        </div>
        <div className="mt-2 text-sm text-gray-500">
          Category: {product.category_name} | Stock: {product.stock}
        </div>
      </div>
    </div>
  );
};

// Home Component
const Home = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const { user } = useAuth();
  const { addToCart } = useCart();

  useEffect(() => {
    fetchData();
  }, []);

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
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8 mb-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl font-bold mb-4">Welcome to ShopHub</h1>
          <p className="text-xl mb-6">Discover amazing products at unbeatable prices</p>
          <img 
            src="https://images.unsplash.com/photo-1599658880436-c61792e70672?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHxlY29tbWVyY2V8ZW58MHx8fHwxNzUxNDUyMTgyfDA&ixlib=rb-4.1.0&q=85"
            alt="Shopping"
            className="mx-auto rounded-lg shadow-lg max-w-md"
          />
        </div>
      </div>

      {/* Search and Filter */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row gap-4 items-center">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search products..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div>
            <select
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredProducts.map(product => (
          <ProductCard
            key={product.id}
            product={product}
            onAddToCart={handleAddToCart}
          />
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No products found</p>
        </div>
      )}
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Please login to view your cart</h2>
          <button
            onClick={() => onPageChange('login')}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h2 className="text-3xl font-bold mb-8">Shopping Cart</h2>

      {cart.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg mb-4">Your cart is empty</p>
          <button
            onClick={() => onPageChange('home')}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Continue Shopping
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            {cart.map(item => (
              <div key={item.product_id} className="bg-white rounded-lg shadow-md p-6 mb-4">
                <div className="flex items-center gap-4">
                  <img
                    src={item.product.image_url}
                    alt={item.product.name}
                    className="w-16 h-16 object-cover rounded"
                  />
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold">{item.product.name}</h3>
                    <p className="text-gray-600">${item.product.price}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => updateCart(item.product_id, item.quantity - 1)}
                      className="bg-gray-200 px-2 py-1 rounded"
                    >
                      -
                    </button>
                    <span className="px-3 py-1 bg-gray-100 rounded">{item.quantity}</span>
                    <button
                      onClick={() => updateCart(item.product_id, item.quantity + 1)}
                      className="bg-gray-200 px-2 py-1 rounded"
                    >
                      +
                    </button>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-semibold">
                      ${(item.product.price * item.quantity).toFixed(2)}
                    </p>
                    <button
                      onClick={() => removeFromCart(item.product_id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Order Summary</h3>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span>Subtotal:</span>
                  <span>${getCartTotal().toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Shipping:</span>
                  <span>Free</span>
                </div>
                <div className="border-t pt-2">
                  <div className="flex justify-between font-semibold text-lg">
                    <span>Total:</span>
                    <span>${getCartTotal().toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Shipping Address</label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Enter your shipping address"
                  value={shippingAddress}
                  onChange={(e) => setShippingAddress(e.target.value)}
                />
              </div>

              <button
                onClick={handleCheckout}
                disabled={checkoutLoading}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {checkoutLoading ? 'Processing...' : 'Place Order'}
              </button>
            </div>
          </div>
        </div>
      )}
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Please login to view your orders</h2>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h2 className="text-3xl font-bold mb-8">Your Orders</h2>

      {orders.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No orders found</p>
        </div>
      ) : (
        <div className="space-y-6">
          {orders.map(order => (
            <div key={order.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">Order #{order.id.slice(-8)}</h3>
                  <p className="text-gray-600">
                    {new Date(order.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold">${order.total_amount.toFixed(2)}</p>
                  <span className={`inline-block px-2 py-1 rounded text-sm ${
                    order.status === 'completed' ? 'bg-green-100 text-green-800' :
                    order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {order.status}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                {order.items.map((item, index) => (
                  <div key={index} className="flex justify-between items-center py-2 border-b">
                    <div>
                      <p className="font-medium">{item.product_name}</p>
                      <p className="text-gray-600">Quantity: {item.quantity}</p>
                    </div>
                    <p className="font-medium">${item.total.toFixed(2)}</p>
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-4 border-t">
                <p className="text-gray-600">
                  <strong>Shipping Address:</strong> {order.shipping_address}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Access Denied</h2>
          <p className="text-gray-600">You don't have permission to access this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h2 className="text-3xl font-bold mb-8">Admin Dashboard</h2>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="flex space-x-8">
          {[
            { id: 'dashboard', label: 'Dashboard' },
            { id: 'products', label: 'Products' },
            { id: 'orders', label: 'Orders' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {activeTab === 'dashboard' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900">Total Products</h3>
                <p className="text-3xl font-bold text-blue-600">{stats.total_products}</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900">Total Orders</h3>
                <p className="text-3xl font-bold text-green-600">{stats.total_orders}</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900">Total Users</h3>
                <p className="text-3xl font-bold text-purple-600">{stats.total_users}</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900">Total Revenue</h3>
                <p className="text-3xl font-bold text-yellow-600">${stats.total_revenue?.toFixed(2)}</p>
              </div>
            </div>
          )}

          {activeTab === 'products' && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Products Management</h3>
              <p className="text-gray-600">Products: {products.length}</p>
              <div className="mt-4 space-y-2">
                {products.slice(0, 5).map(product => (
                  <div key={product.id} className="flex justify-between items-center py-2 border-b">
                    <div>
                      <p className="font-medium">{product.name}</p>
                      <p className="text-gray-600">${product.price}</p>
                    </div>
                    <span className="text-sm text-gray-500">Stock: {product.stock}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'orders' && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Orders Management</h3>
              <div className="space-y-4">
                {orders.slice(0, 10).map(order => (
                  <div key={order.id} className="flex justify-between items-center py-3 border-b">
                    <div>
                      <p className="font-medium">Order #{order.id.slice(-8)}</p>
                      <p className="text-gray-600">{order.user_name} - {order.user_email}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(order.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">${order.total_amount.toFixed(2)}</p>
                      <span className={`inline-block px-2 py-1 rounded text-sm ${
                        order.status === 'completed' ? 'bg-green-100 text-green-800' :
                        order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {order.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

// Main App Component
const App = () => {
  const [currentPage, setCurrentPage] = useState('home');

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home />;
      case 'login':
        return <Login onPageChange={setCurrentPage} />;
      case 'cart':
        return <Cart onPageChange={setCurrentPage} />;
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
        <div className="min-h-screen bg-gray-50">
          <Header onPageChange={setCurrentPage} currentPage={currentPage} />
          <main>
            {renderCurrentPage()}
          </main>
        </div>
      </CartProvider>
    </AuthProvider>
  );
};

export default App;