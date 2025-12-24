  Student Management Backend System
  
  1. Student Management Backend System
    End-to-end backend system for managing academic records in Vietnamese high school,
    designed with complex business rules, strong data integrity, and set-based SQL processing.

  2. Project Overview
     This project is an end-to-end student management system backend, covering:
     - Control user: students, teachers
     - Academic records
     - Retest and promotion / retention logic
     - Role-based access control (Admin / Teacher / Student)
     The system focuses on **Correct business logic, **Data consistency, and **Transaction safety rather than UI features

  3. Core Backend Challenges Solved
     - Semester / Year summary is allowed only when all subjects are finalized
     - Yearly evalution follows official Vietnamese education grading rules
     - Retest workflow with full recalculation and status update
     - Promotion / retention decision based on aggregated results
     - Schedule conflict detection for teachers
     - safe update of teachers / subjects with cascading business impact
     - All write operations are executed inside database transactions
     - Automatic rollback on any business / validation / DB error
    
  4. Architecture
     Client (Vue) -> API layer (Flask Routes) -> Service layer (Business logic) -> Repository layer (SQL / ORM) -> PostgreSQL
     - Route: auth, role checking, input validation
     - Service: business rules, transaction control
     - Repository: set-based SQL, no Python loops
     Detailed architecture is described in [Doc][ARCHITECTURE.md]

  5. Tech Stack
     - Backend: Flask REST API
     - ORM: SQLAlchemy
     - Validation: Pydantic
     - Auth: JWT (acess & refresh token)
     - Database: PostgreSQL
     - Background jobs: Celery + Redis
     - Object storage: MinIO
     - Logging: Audit log & Activity log

  6. Business Workflows
     Some complex workflows are documented separately:
     - Add Lesson workflow: business_flow.md
     - Add Teacher workflow: business_flow.md
     - Yearly Academic summary: business_flow.md
     - Retest evaluation workflow: business_flow.md

  7. Data safety & Integrity
     - All DB write operations run inside transactions
     - Automatic rollback on any raised error
     - Input validation with Pydantic
     - Unique constraints at DB level to prevent race conditions
     - Audit log for failed critical operations
     - Activity log for successful critical operations

  8. How to run
    A. Quick start (Recommended)
        a. Requirements
           - Docker
           - Docker compose
      
        b. Start all services
        Bash:
            git clone https://github.com/ductruongcm/school.git
            cd school

            # Backend env
            cp backend/.env.docker.exmple backend/.env.example

            # Fronted env
            cp frontend/.env.docker.example frontend/.env.docker

            docker-compose up -d
     
        c. Enviroment variables
            Copy .env.docker.example to .env.docker and update values if needed.
            Default values are for local development only.
     
    B. Manual Setup 
        1. Install service
            1.1 PostgreSQL 
            docker run -d --name postgres -e POSTGRES_USER=school_user -e POSTGRES_PASSWORD=school_password -e POSTGRES_DB=school -p 5432:5432 postgres:15 

            1.2 Redis
            docker run -d --name redis -p 6379:6379 redis:7

            1.3 Minio
            docker run -d --name minio -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=minio_demo -e MINIO_ROOT_PASSWORD=minio_demo_password minio/minio server /data --console-address ":9001" 
            
        2. git clone: 
            git clone https://github.com/ductruongcm/school.git 
            cd school

            # Backend env
            cp backend/.env.docker.exmple backend/.env.example

            # Fronted env
            cp frontend/.env.docker.example frontend/.env.docker
            
        3. Enviroment variables 
            Copy .env.example to .env and update values if needed. 
            Default values are for local development only. 
            
        4. Requirement 
            pip install -r requirements.txt 

        5. Initialize system 
            Create database tables: python -m app.cli.migrate 

            Create admin user: python -m app.cli.seed_admin 
            
            Initialize MinIO bucker: python -m app.cli.init_minio 

        6. Run backend
            (local) python main.py 

        7. Run background worker 
            celery -A worker.celery worker --loglevel=info 
        
        *** This project requires PostgreSQL, Redis, and MiniO to be running. Without these services, the application will not start *** For quick start, 
        Docker compose setup is recommended. Manual setup is provided for development and debugging purposes.


*** This project requires PostgreSQL, Redis, and MiniO to be running
*** Without these services, the application will not start
       
        
     