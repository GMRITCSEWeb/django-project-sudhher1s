[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/BwsfqDfD)

# ShopKart - Django E-commerce Project

## Tech Stack
- Python 3.11+
- Django 4.2
- SQLite
- Django Templates, HTML, CSS

## Project Features
- Product listing and detail pages
- Category and subcategory support
- Search with query parameter
- User registration, login, logout
- Auto-created user profile with signals
- Cart management (add, update, remove)
- Checkout and order placement flow
- Order confirmation page
- Admin customization with inline order items and custom actions

## Full Folder Structure
```
shopify_clone/
  settings.py
  urls.py
store/
  admin.py
  apps.py
  forms.py
  models.py
  signals.py
  urls.py
  views.py
  fixtures/
	 sample_data.json
  templatetags/
	 store_tags.py
templates/
  base.html
  registration/
	 login.html
	 logged_out.html
  store/
	 product_list.html
	 product_detail.html
	 cart.html
	 checkout.html
	 register.html
	 profile.html
	 order_confirmation.html
	 components/
		product_card.html
		pagination.html
		top_products.html
static/
  css/
	 style.css
```

## Setup Steps
1. Clone repository
	- `git clone https://github.com/GMRITCSEWeb/django-project-sudhher1s.git`
2. Go into project directory
	- `cd django-project-sudhher1s`
3. Create virtual environment
	- Windows: `py -m venv .venv`
4. Activate virtual environment
	- Windows: `.venv\Scripts\activate`
5. Install dependencies
	- `pip install -r requirements.txt`
6. Apply migrations
	- `python manage.py migrate`
7. Load sample fixture data
	- `python manage.py loaddata store/fixtures/sample_data.json`
8. Create admin user
	- `python manage.py createsuperuser`
9. Run project
	- `python manage.py runserver`

## Common URLs
- Home: `/`
- Products: `/products/`
- Category: `/category/<slug>/`
- Product detail: `/products/<slug>/`
- Search: `/search/?q=phone`
- Register: `/register/`
- Login: `/accounts/login/`
- Cart: `/cart/`
- Checkout: `/checkout/`
- Admin: `/admin/`

## ORM Query Examples
See `store/orm_examples.py` for:
- `filter`
- `exclude`
- `annotate`

## Suggested Git Workflow
Create branch before major task and commit after each task.

### Branch Example
- `git checkout -b task-2-views-templates`

### Task-wise Commit Message Suggestions
1. `Task 1: setup project and add category/product models`
2. `Task 2: implement product views search and category routing`
3. `Task 3: add templates components tags and messages UI`
4. `Task 4: implement authentication and user profile flow`
5. `Task 5: build cart checkout order management system`
6. `Task 6: customize admin for orders and permissions`
7. `docs: update README and add sample fixture data`

### Push Commands
- `git add -A`
- `git commit -m "<message>"`
- `git push -u origin <branch-name>`
