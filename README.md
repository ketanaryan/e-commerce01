# 🛒 ShopHub - Full-Stack Ecommerce Platform

A modern, full-featured ecommerce platform built with React, FastAPI, and MongoDB. Features a complete customer shopping experience and comprehensive admin dashboard.

## 🚀 Project Overview

ShopHub is a full-stack ecommerce application that provides:

- **Customer Interface**: Product browsing, shopping cart, user authentication, order management
- **Admin Interface**: Product management, order management, category management, dashboard analytics
- **RESTful API**: Comprehensive backend with authentication, CRUD operations, and business logic
- **Modern UI**: Responsive design with Tailwind CSS and professional styling

## 🛠️ Tech Stack

### Frontend
- **React 19.0.0** - Modern React with hooks and context
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **React Router** - Client-side routing

### Backend
- **FastAPI 0.110.1** - Modern, fast web framework for Python
- **MongoDB 4.5.0** - NoSQL database with PyMongo
- **JWT Authentication** - Secure token-based authentication
- **BCrypt** - Password hashing
- **Uvicorn** - ASGI server

### Database
- **MongoDB** - Document-based NoSQL database
- **Collections**: Users, Products, Categories, Orders, Cart

## 📋 Prerequisites

- **Node.js 18+** - JavaScript runtime
- **Python 3.11+** - Backend runtime
- **MongoDB** - Database server
- **Yarn** - Package manager for frontend

## 🔧 Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd shophub
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables (already configured)
# MONGO_URL=mongodb://localhost:27017/
# JWT_SECRET=your-secret-key-here
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
yarn install

# Environment variables are already configured
# REACT_APP_BACKEND_URL=<your-backend-url>
```

### 4. Database Setup
```bash
# Seed the database with sample data
cd ../
python scripts/seed_database.py
```

### 5. Running the Application

#### Option 1: Run Both Services Together
```bash
# From the frontend directory
cd frontend
npm run dev
```

#### Option 2: Run Services Separately
```bash
# Terminal 1 - Backend
cd backend
python server.py

# Terminal 2 - Frontend  
cd frontend
yarn start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001

## 🗄️ Database Seeding

The application comes with a comprehensive seed script that populates the database with:

- **5 Categories**: Electronics, Beauty & Health, Fashion, Home & Living, Sports & Outdoors
- **12 Products**: Diverse product catalog with real images and descriptions
- **4 Users**: 1 admin user + 3 customer users
- **2 Sample Orders**: Pre-populated order history

### Seed Database Command
```bash
python scripts/seed_database.py
```

### Default Login Credentials
**Admin Access:**
- Email: `admin@shophub.com`
- Password: `admin123`

**Customer Access:**
- Email: `customer1@example.com`
- Password: `customer123`
- Email: `customer2@example.com`
- Password: `customer123`
- Email: `customer3@example.com`
- Password: `customer123`

## 🌐 Environment Setup

### Backend Environment Variables (`backend/.env`)
```env
MONGO_URL=mongodb://localhost:27017/
JWT_SECRET=your-secret-key-here
```

### Frontend Environment Variables (`frontend/.env`)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
```

## 🎯 Features

### Customer Features
- **Product Catalog**: Browse products with search and category filtering
- **Shopping Cart**: Add/remove items, update quantities
- **User Authentication**: Register, login, secure sessions
- **Order Management**: Place orders, view order history
- **Responsive Design**: Mobile-friendly interface

### Admin Features
- **Dashboard**: Overview statistics and analytics
- **Product Management**: Add, edit, delete products
- **Order Management**: View and update order statuses
- **Category Management**: Manage product categories
- **User Management**: View customer accounts

### Technical Features
- **JWT Authentication**: Secure token-based auth
- **Role-Based Access**: Customer/Admin permissions
- **RESTful API**: Comprehensive backend API
- **Real-time Updates**: Context-based state management
- **Error Handling**: Comprehensive error management
- **Input Validation**: Client and server-side validation

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/me` - Get current user profile

### Product Endpoints
- `GET /api/products` - Get all products (with search/filter)
- `GET /api/products/{id}` - Get specific product
- `POST /api/products` - Create product (admin only)
- `PUT /api/products/{id}` - Update product (admin only)
- `DELETE /api/products/{id}` - Delete product (admin only)

### Category Endpoints
- `GET /api/categories` - Get all categories
- `POST /api/categories` - Create category (admin only)
- `DELETE /api/categories/{id}` - Delete category (admin only)

### Cart Endpoints
- `GET /api/cart` - Get user's cart
- `POST /api/cart` - Add item to cart
- `PUT /api/cart/{product_id}` - Update cart item quantity
- `DELETE /api/cart/{product_id}` - Remove item from cart

### Order Endpoints
- `GET /api/orders` - Get user's orders
- `POST /api/orders` - Create new order
- `GET /api/admin/orders` - Get all orders (admin only)
- `PUT /api/admin/orders/{id}` - Update order status (admin only)

### Admin Endpoints
- `GET /api/admin/stats` - Get dashboard statistics (admin only)

## 🏗️ Project Structure

```
shophub/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Styling
│   │   ├── index.js          # React entry point
│   │   └── index.css         # Global styles
│   ├── package.json          # Node.js dependencies
│   ├── tailwind.config.js    # Tailwind configuration
│   └── .env                  # Frontend environment variables
├── scripts/
│   └── seed_database.py      # Database seeding script
├── tests/
│   └── backend_test.py       # Backend API tests
└── README.md                 # Project documentation
```

## 🧪 Testing

### Backend Testing
```bash
# Run comprehensive backend tests
python tests/backend_test.py
```

### Manual Testing
1. **Customer Flow**:
   - Register/Login as customer
   - Browse products
   - Add items to cart
   - Place order
   - View order history

2. **Admin Flow**:
   - Login as admin
   - View dashboard statistics
   - Manage products
   - Manage orders
   - Manage categories

## 🔒 Security Features

- **Password Hashing**: BCrypt for secure password storage
- **JWT Tokens**: Secure authentication tokens
- **Role-Based Access**: Admin/Customer permissions
- **Input Validation**: Server-side validation
- **CORS Configuration**: Proper cross-origin setup

## 📱 Responsive Design

The application is fully responsive and works on:
- **Desktop**: Full-featured interface
- **Tablet**: Optimized layout
- **Mobile**: Touch-friendly interface

## 🚀 Development

### Adding New Features
1. **Backend**: Add new routes to `server.py`
2. **Frontend**: Add new components to `App.js`
3. **Database**: Update seed script if needed
4. **Testing**: Add tests for new features

### Code Style
- **Backend**: Follow PEP 8 Python standards
- **Frontend**: Follow React best practices
- **Database**: Use UUID for all IDs

## 📈 Performance

- **Database Indexing**: Optimized queries
- **Image Optimization**: Compressed product images
- **Caching**: Browser caching for static assets
- **Code Splitting**: Optimized bundle sizes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, email support@shophub.com or create an issue in the repository.

## 🔄 Updates

- **v1.0.0**: Initial release with core ecommerce features
- Full product catalog and shopping cart
- User authentication and order management
- Admin dashboard and management tools
- Responsive design and mobile support

---

**Built with ❤️ using React, FastAPI, and MongoDB**