# Library Project - 个人项目仓库

*注意：这是从团队项目 [project-a-22](https://github.com/uva-cs3240-s25/project-a-22) 复制而来的个人仓库，用于展示我在项目中的贡献。*

## 我在项目中的角色与贡献

### 我的主要职责
- [在这里描述你的主要角色，例如：前端开发、后端开发、数据库设计等]
- [详细列出你负责的功能模块]
- [提及你使用的关键技术]

### 我实现的功能
- [功能1：详细描述]
- [功能2：详细描述]
- [功能3：详细描述]

### 技术挑战与解决方案
- [描述你在项目中遇到的技术挑战]
- [你如何解决这些挑战]

### 使用的技术栈
- Django
- PostgreSQL
- Bootstrap
- Docker
- [其他你使用的技术]

---

## 原始项目文档

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/hLqvXyMi)

# A22 Library Project

## Development Setup Guide

### Prerequisites
- Docker Desktop installed and running (or OrbStack as a lighter alternative)
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - [Download OrbStack](https://orbstack.dev/)
- Git installed
  - [Download Git](https://git-scm.com/downloads)

### Getting Started

1. **Clone the Repository**
   ```bash
   git clone https://github.com/uva-cs3240-s25/project-a-22
   cd project-a-22
   ```

2. **Environment Setup**
   - Make sure Docker Desktop is running
   - No additional virtual environment is needed as we're using Docker containers

3. **Build and Start the Application**
   ```bash
   # Build and start all services
   docker compose up --build

   # To run in detached mode (in the background):
   docker compose up -d --build
   ```

4. **Access the Application**
   - Web application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

### Database Connection

The PostgreSQL database is accessible with these credentials:
- Host: `localhost`
- Port: `5432`
- Database: `library_db`
- Username: `postgres`
- Password: `postgres`

Connection string: `postgres://postgres:postgres@localhost:5432/library_db`

You can use database management tools like TablePlus, DBeaver, or pgAdmin to connect to and manage the database:
- [Download TablePlus](https://tableplus.com/) (recommended)
- [Download DBeaver](https://dbeaver.io/)
- [Download pgAdmin](https://www.pgadmin.org/)

### Common Commands

**Note:** All docker commands must be run from the root directory of the repository (project-a-22/).

```bash
# Start the application
docker compose up

# Stop the application
docker compose down

# View logs
docker compose logs

# View logs for a specific service
docker compose logs web  # for the Django service
docker compose logs db   # for the database service

# Rebuild containers after dependency changes
docker compose build --no-cache

# Run Django management commands
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic

# Generate test data (100 books for development)
docker compose exec web python manage.py create_test_books
# Options:
# --count <number>: Specify how many books to create (default: 100)
# --clear: Remove existing test books before creating new ones
docker compose exec web python manage.py create_test_books --count 50 --clear

# Access PostgreSQL CLI
docker compose exec db psql -U postgres -d library_db
```

### Heroku Pipeline Jobs

These jobs allow you to manage book data in the production environment:

```bash
# Populate the production site with books (default: 100)
heroku run:detached populate_books -a a22-library

# Specify the number of books to create
heroku run:detached populate_books -a a22-library --env COUNT=50

# Clear all existing books and create new ones
heroku run:detached populate_books_and_clear -a a22-library

# Clear all books from the production database (use with caution!)
heroku run:detached clear_all_books -a a22-library
```

**Important Notes:**
- These commands will run detached from your terminal and continue execution on Heroku's servers
- Use `heroku logs -a a22-library` to monitor the progress of these operations
- The `clear_all_books` command should be used with extreme caution as it removes ALL books from the database
- Production data operations require appropriate Heroku permissions

### Default Admin User
For local development, a default admin user is automatically created with these credentials:
- Username: `admin`
- Password: `admin`
- Email: `admin@virginia.edu`

⚠️ **Important Security Note:** 
These default admin credentials are only used in local development. For production (Heroku):
1. The admin user is created during deployment using GitHub Secrets
2. Set the following secrets in your GitHub repository:
   - `DJANGO_ADMIN_PASSWORD`: A secure password for the admin user
   - `DJANGO_ADMIN_EMAIL`: The admin user's email address
Ask [yabood](https://github.com/yabood) for the superuser password and email
