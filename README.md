# SaaS Platform Demo

A minimal SaaS skeleton project built with React (frontend) and Django (backend) featuring user authentication, subscription management with Stripe, and a dashboard with placeholder metrics.

## Features

- **User Authentication**: Email/password signup and login flows
- **Multi-step Signup**: Email validation → Password creation → Pricing plan selection
- **Stripe Integration**: Test mode customer and subscription creation
- **Protected Dashboard**: Displays placeholder business metrics, activities, and reviews
- **Responsive Design**: Clean, modern UI that works on all devices

## Tech Stack

### Backend
- Django 4.2.7
- PostgreSQL
- Django REST Framework
- Stripe API
- CORS headers for frontend communication

### Frontend
- React 18
- React Router DOM
- Axios for API calls
- Modern CSS with responsive design

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL
- Stripe Test Account

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Setup environment variables**
   Copy `env.example` to `.env` and update with your settings:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your database and Stripe credentials:
   ```
   SECRET_KEY=your-secret-key-here
   DB_NAME=saas_db
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
   STRIPE_SECRET_KEY=sk_test_your_secret_key
   ```

5. **Setup PostgreSQL database**
   ```bash
   createdb saas_db
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start Django server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start React development server**
   ```bash
   npm start
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Django Admin: http://localhost:8000/admin

## Stripe Setup

1. **Create Stripe Account**: Visit [Stripe Dashboard](https://dashboard.stripe.com)
2. **Get Test Keys**: Copy your test publishable and secret keys
3. **Create Products** (Optional): Create test products with IDs matching the backend configuration:
   - `price_basic_test`
   - `price_pro_test` 
   - `price_enterprise_test`

Note: The app will work with placeholder price IDs for demo purposes.

## Usage Flow

### 1. Signup Process
1. Visit http://localhost:3000
2. Click "Sign Up" or navigate to `/signup/email`
3. Enter email address (validates format)
4. Create password (minimum 6 characters)
5. Select pricing plan
6. Account created with Stripe customer and subscription

### 2. Login
1. Visit `/login`
2. Enter email and password
3. Redirected to dashboard upon success

### 3. Dashboard
- View placeholder business metrics
- See recent activities
- Check customer review analytics
- Access navigation (Dashboard, Profile, Logout)

## API Endpoints

### Authentication
- `POST /api/accounts/signup/` - Create new user with Stripe integration
- `POST /api/accounts/login/` - User login
- `POST /api/accounts/logout/` - User logout
- `GET /api/accounts/pricing/` - Get pricing plans

### Dashboard
- `GET /api/dashboard/data/` - Get dashboard metrics (requires authentication)

## Project Structure

```
├── backend/
│   ├── saas_project/          # Django project settings
│   ├── accounts/              # User authentication app
│   ├── dashboard/             # Dashboard data app
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── App.js            # Main app component
│   │   └── index.js          # Entry point
│   ├── public/
│   └── package.json
├── requirements.txt           # Python dependencies
└── README.md
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-django-secret-key
DB_NAME=saas_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
```

## Demo Data

The dashboard displays placeholder data including:
- User metrics (1,200+ total users)
- Subscription data (890+ active subscriptions)
- Revenue figures ($15,000-$25,000 monthly)
- Recent activities
- Customer review analytics

## Security Notes

- This is a demo project - not production ready
- Uses Django sessions for authentication
- CORS configured for localhost development
- Stripe in test mode only
- No email verification implemented

## Customization

### Adding Real Stripe Products
1. Create products in Stripe Dashboard
2. Update price IDs in `backend/accounts/views.py`
3. Modify pricing plans in the pricing endpoint

### Styling
- Global styles in `frontend/src/index.css`
- Component-specific styles inline
- Responsive grid system included

### Database Models
- `UserProfile`: Links users to Stripe customers
- `Activity`: Tracks user actions
- `Metric`: Stores business metrics

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend is running on port 8000
2. **Database Connection**: Check PostgreSQL service and credentials
3. **Stripe Errors**: Verify test keys are correctly set
4. **Module Not Found**: Ensure all dependencies are installed

### Development Tips

- Use Django Admin to view created users and profiles
- Check browser dev tools for API request errors
- Stripe test cards: `4242 4242 4242 4242`

## License

This project is for demonstration purposes only. 