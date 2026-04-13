Three‑Tier AWS Architecture Demo (FastAPI • EC2 ASG • ALB • DynamoDB • S3 • Secrets Manager)
This project is a fully automated, production‑style three‑tier cloud application designed to teach students how modern AWS architectures are built and deployed. It demonstrates networking, compute, storage, authentication, scaling, and CI/CD concepts in a single, hands‑on environment.
The system is built using:
- AWS CDK (Python) for Infrastructure‑as‑Code
- FastAPI for the web application
- GitHub Actions for automated deployment
- Auto Scaling Group + Application Load Balancer for high availability
- DynamoDB + S3 for data and file storage
- Secrets Manager for secure token‑based authentication
All infrastructure and application code lives in one repository for clarity and teaching value.

What This Project Teaches
Students learn how to build and operate a real cloud application using AWS best practices:
- How a three‑tier architecture works (presentation → application → data)
- Why EC2 instances should run in private subnets
- How an Application Load Balancer exposes the app securely
- How an Auto Scaling Group maintains availability and elasticity
- How applications use IAM roles instead of credentials
- How to store and retrieve secrets using AWS Secrets Manager
- How to upload files to S3 and store metadata in DynamoDB
- How to deploy infrastructure using AWS CDK
- How to automate deployments using GitHub Actions
This project is intentionally simple enough for beginners but realistic enough for intermediate and advanced cloud learners.

Architecture Overview
Public Tier
- Application Load Balancer (ALB)
- Receives all incoming traffic
- Performs health checks on backend instances
Application Tier
- EC2 Auto Scaling Group (private subnets)
- FastAPI application served via Uvicorn
- IAM role grants access to S3, DynamoDB, Secrets Manager
Data Tier
- DynamoDB table for metadata
- S3 bucket for uploaded files
- Secrets Manager for bearer‑token authentication
Networking
- VPC with public and private subnets
- NAT Gateway for outbound internet access
- Security groups restricting traffic to ALB → EC2 only

FastAPI Application Features
- Token‑based authentication using a Bearer token stored in Secrets Manager
- Login page that validates the token
- File upload form (images, documents, etc.)
- Files stored in Amazon S3
- Metadata stored in DynamoDB
- Items listing page showing uploaded files
- Health check endpoint (/health) for ALB
- Clean UI with footer credit:



Deployment Pipeline
Every push to the main branch triggers:
- CDK dependency installation
- AWS authentication via GitHub OIDC
- CDK bootstrap (first time only)
- CDK deploy of all stacks
- EC2 instances automatically pull the latest FastAPI code
This ensures the entire system is always up‑to‑date and reproducible.

How to Use This Project
1. Clone the repository


2. Install CDK dependencies
cd cdk
pip install -r requirements.txt


3. Bootstrap your AWS environment
cdk bootstrap


4. Deploy the full architecture
cdk deploy --all


5. Access the application
After deployment, CDK outputs the ALB DNS name.
Open it in your browser and log in using the Bearer token stored in Secrets Manager.

Designed and Developed by Moges K
This project is built for learning, teaching, and demonstrating real AWS cloud architecture patterns. It is intentionally structured to be clear, modular, and production‑inspired.
![ThreeTier](https://github.com/user-attachments/assets/8a99cf9e-d24c-4925-8f41-80ea705b8d9d)

