[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/BwsfqDfD)

# CodeMart - Django Student E-commerce Marketplace

CodeMart is a complete Django marketplace where students can buy and sell academic resources such as code, papers, projects, and internships.

## Tech Stack
- Python 3.11+
- Django (see `requirements.txt`)
- SQLite
- Django Templates + React (CDN on product listing page)
- HTML, CSS, JavaScript

## Implemented Features

### Buyer Features
- Product listing, search, category filter, and product detail pages
- Add to cart with quantity validation against stock
- Cart update and remove actions
- Checkout with phone validation and order creation
- Order confirmation and buyer order history

### Seller Features
- Seller role support via user profile
- Seller dashboard with product stats and recent sales
- Seller product CRUD (create, edit, delete)
- Product type support:
	- Code
	- Papers
	- Projects
	- Internships
	- Other Academic Resource
- Seller order view for sold items

### Admin Features
- Django admin customization for Category, Product, CartItem, UserProfile, Order, OrderItem
- OrderAdmin includes:
	- list_display
	- list_filter
	- date_hierarchy
	- readonly_fields
	- TabularInline for order items
	- custom action: Mark selected orders as shipped
	- restricted delete for non-superuser staff
- Private custom admin dashboard route:
	- `/admin-panel/`

### Template and UI Features
- Base layout with reusable blocks
- Reusable components (`product_card`, `pagination`, `top_products`)
- Custom template tag for top products by sales
- Django messages shown globally
- Responsive marketplace UI with CodeMart branding
- React-powered storefront rendering on product listing page
- Live stock and price polling from API on listing and detail pages

### Authentication and Profile
- Register with custom `UserCreationForm` (email required)
- Django built-in login/logout with custom templates
- Auto-created UserProfile via post_save signal
- Profile update form
- Protected cart and checkout routes using `@login_required`

## Django Concepts Covered (Assignment Mapping)
- Models & ORM
- Views & URLs (CBV + FBV)
- Templates and inheritance
- Forms and validation (`clean_*`)
- Authentication and permissions
- Admin panel customization (actions + inlines)

## Project Structure
```
django-project-sudhher1s/
	manage.py
	requirements.txt
	README.md
	shopify_clone/
		settings.py
		urls.py
		asgi.py
		wsgi.py
	store/
		admin.py
		apps.py
		forms.py
		models.py
		signals.py
		tests.py
		urls.py
		views.py
		orm_examples.py
		fixtures/
			sample_data.json
		migrations/
			0001_initial.py
			0002_order_userprofile_orderitem_cartitem.py
			0003_product_is_active_product_seller_product_updated_at_and_more.py
			0004_product_product_type.py
		templatetags/
			store_tags.py
	templates/
		base.html
		registration/
			login.html
			logged_out.html
		store/
			admin_dashboard.html
			product_list.html
			product_detail.html
			cart.html
			checkout.html
			order_confirmation.html
			buyer_orders.html
			seller_dashboard.html
			seller_orders.html
			seller_product_form.html
			seller_product_delete.html
			register.html
			profile.html
			components/
				product_card.html
				pagination.html
				top_products.html
	static/
		css/
			style.css
```

## Local Setup
1. Clone the repository
	 - `git clone https://github.com/GMRITCSEWeb/django-project-sudhher1s.git`
2. Enter project folder
	 - `cd django-project-sudhher1s`
3. Create virtual environment
	 - Windows: `py -m venv .venv`
4. Activate virtual environment
	 - Windows: `.venv\Scripts\activate`
5. Install dependencies
	 - `pip install -r requirements.txt`
6. Apply migrations
	 - `python manage.py migrate`
7. Load sample data (optional)
	 - `python manage.py loaddata store/fixtures/sample_data.json`
8. Create superuser
	 - `python manage.py createsuperuser`
9. Run server
	 - `python manage.py runserver`

## Main Routes
- `/` - Home
- `/products/` - Product listing
- `/products/<slug>/` - Product detail
- `/category/<slug>/` - Category view
- `/search/?q=...` - Search
- `/register/` - Register
- `/accounts/login/` - Login
- `/profile/` - Profile update
- `/cart/` - Cart
- `/checkout/` - Checkout
- `/orders/` - Buyer orders
- `/seller/dashboard/` - Seller dashboard
- `/seller/orders/` - Seller orders
- `/admin/` - Django admin
- `/admin-panel/` - Custom admin dashboard (staff only)

## Verification Commands
- `python manage.py check`
- `python manage.py test`

## Sample ORM Practice
See `store/orm_examples.py` for examples using:
- `filter`
- `exclude`
- `annotate`

## Deliverables Covered
- GitHub repository with clean commits
- Working Django project (`runserver`)
- `requirements.txt`
- Updated `README.md`
- Sample fixture for demo data
