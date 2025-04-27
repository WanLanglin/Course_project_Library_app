# Library Project - 个人项目仓库

*注意：这是从团队项目 [project-a-22](https://github.com/uva-cs3240-s25/project-a-22) 复制而来的个人仓库，用于展示我的个人项目。*

## 项目说明 (Project Description)

### 中文说明
这是一个我个人完成的图书馆管理系统项目。项目包含完整的前端和后端实现，使用了Django框架和PostgreSQL数据库。系统实现了图书管理、用户认证、图书检索、借阅记录等核心功能，并提供了直观的用户界面。整个项目的设计、开发和测试全部由我独立完成。

### English Description
This is a library management system project that I completed independently. The project includes complete front-end and back-end implementation using Django framework and PostgreSQL database. The system implements core functions such as book management, user authentication, book search, borrowing records, etc., and provides an intuitive user interface. The entire project's design, development, and testing were all completed by me independently.

### 使用的技术栈 (Technology Stack)
- Django
- PostgreSQL
- Bootstrap
- Docker
- HTML/CSS/JavaScript
- Git

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
