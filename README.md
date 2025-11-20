# RAG Q&A Application - Automated CI/CD Deployment

This is a RAG (Retrieval-Augmented Generation) Q&A application based on LangChain, automatically deployed to AWS App Runner via GitHub Actions (OIDC).

## Project Structure

```
Rag_501/
├── app.py                 # Flask web application main file
├── ingest.py              # Data ingestion script to create vector index
├── data.txt               # Knowledge base data file
├── faiss_index/           # Pre-built FAISS vector index (included in repo)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image build file
├── docker-entrypoint.sh   # Container startup script
├── main.tf                # Terraform infrastructure configuration
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Actions CI/CD workflow
└── README.md              # This file
```

## What the Code Does

### Terraform (`main.tf`)

Creates AWS infrastructure:

- **GitHub OIDC Provider**: Enables GitHub Actions to authenticate with AWS without storing credentials
- **IAM Roles**:
  - `github-actions-deploy-role`: Allows GitHub Actions to push to ECR and deploy to App Runner
  - `bee-edu-apprunner-role`: Allows App Runner to pull images from ECR
  - `bee-edu-apprunner-instance-role`: Allows App Runner instances to read from Secrets Manager
- **ECR Repository**: Stores Docker images
- **Secrets Manager Secret**: Stores OpenAI API key securely
- **IAM Policies**: Grants necessary permissions for ECR, Secrets Manager, and App Runner operations

### GitHub Actions Workflow (`.github/workflows/deploy.yml`)

Automated deployment pipeline that runs on every push to `main`:

1. **Checkout code**: Retrieves the latest code from repository
2. **Configure AWS credentials**: Uses OIDC to authenticate with AWS (no stored credentials)
3. **Log in to ECR**: Authenticates with Amazon ECR
4. **Build and push Docker image**: 
   - Builds Docker image for `linux/amd64` platform
   - Tags with commit SHA (first 7 characters) and `latest`
   - Pushes to ECR repository
5. **Get App Runner service details**: 
   - Dynamically retrieves IAM role ARNs from AWS IAM
   - Checks if App Runner service exists
6. **Get or create Secrets Manager secret**:
   - Checks if `bee-edu-openai-key-secret` exists
   - Creates it automatically if missing (using GitHub Secret `OPENAI_API_KEY` if available)
   - Validates secret accessibility
7. **Deploy to App Runner**:
   - Creates new service if it doesn't exist
   - Updates existing service if it exists
   - Configures `RuntimeEnvironmentSecrets` to inject `OPENAI_API_KEY` from Secrets Manager
   - Waits for service to become stable (up to 10 minutes)
   - Handles service state transitions (waits for `OPERATION_IN_PROGRESS` to complete)

### Application Code (`app.py`)

Flask web application with RAG functionality:

- **API Key Retrieval**: 
  - First checks `OPENAI_API_KEY` environment variable
  - Falls back to AWS Secrets Manager if not found
  - Handles both JSON and plain string secret formats
- **FAISS Index Management**:
  - Loads pre-built index from `faiss_index/` directory if available
  - Automatically creates index from `data.txt` if missing
  - Handles errors gracefully
- **RAG System**:
  - Uses LangChain RetrievalQA chain
  - Retrieves top 3 relevant documents
  - Generates answers using OpenAI GPT
- **Endpoints**:
  - `GET /`: Web interface for Q&A
  - `POST /api/query`: API endpoint for RAG queries
  - `GET /health`: Health check endpoint

### Docker Configuration

**Dockerfile**:
- Base image: `python:3.9-slim`
- Installs system dependencies (gcc for Python packages)
- Installs Python dependencies from `requirements.txt`
- Copies application code and FAISS index
- Exposes port 8080
- Runs `docker-entrypoint.sh` on startup

**docker-entrypoint.sh**:
- Checks for `OPENAI_API_KEY` environment variable (injected by App Runner from Secrets Manager)
- Verifies FAISS index exists (uses pre-built index from repository)
- Optionally creates index if missing (requires API key)
- Starts Flask application

## Deployment Steps

### 1. Prerequisites

Ensure you have installed:
- [Terraform](https://www.terraform.io/downloads) (>= 1.0)
- [AWS CLI](https://aws.amazon.com/cli/) with configured credentials
- [Docker](https://www.docker.com/) (for local testing)

### 2. Create AWS Infrastructure with Terraform

Run the following commands in the project root directory:

```bash
# Initialize Terraform
terraform init

# Apply configuration (create all AWS resources)
TF_VAR_manage_apprunner_via_terraform=false \
TF_VAR_github_org_or_user=your_github_username \
TF_VAR_github_repo_name=your_repo_name \
TF_VAR_openai_api_key="your-openai-api-key-here" \
terraform apply -auto-approve
```

**Important Output Values**: Terraform will output the following values, please save them:

- `github_actions_role_arn` → For GitHub Secret: `AWS_IAM_ROLE_TO_ASSUME`
- `ecr_repository_name` → For GitHub Secret: `ECR_REPOSITORY`
- `apprunner_service_arn` → For GitHub Secret: `APP_RUNNER_ARN` (optional, may be empty if service is created by GitHub Actions)

**Note**: The workflow automatically retrieves `apprunner_access_role_arn` and `apprunner_instance_role_arn` from IAM by role name, so they don't need to be added as secrets.

### 3. Configure GitHub Secrets

In your GitHub repository:

1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**
3. Add the following 4 Secrets:

| Secret Name | Value Source | Example Value |
|------------|--------------|---------------|
| `AWS_REGION` | Fixed value | `us-east-1` |
| `ECR_REPOSITORY` | Terraform output `ecr_repository_name` | `bee-edu-rag-app` |
| `APP_RUNNER_ARN` | Terraform output `apprunner_service_arn` | `arn:aws:apprunner:us-east-1:...` (optional) |
| `AWS_IAM_ROLE_TO_ASSUME` | Terraform output `github_actions_role_arn` | `arn:aws:iam::...:role/github-actions-deploy-role` |

### 4. Push Code to GitHub

```bash
# Initialize Git repository (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: RAG app with CI/CD"

# Add remote repository
git remote add origin https://github.com/your_username/your_repo_name.git

# Push to main branch (this will trigger GitHub Actions)
git branch -M main
git push -u origin main
```

### 5. Verify Deployment

1. **Check GitHub Actions**:
   - Go to the repository's **Actions** tab
   - View workflow execution status
   - Ensure all steps are successful

2. **Get App Runner URL**:
   - Log in to AWS Console
   - Go to App Runner service
   - Find service `bee-edu-rag-service`
   - Copy the service URL (format: `https://xxxxx.us-east-1.awsapprunner.com`)

3. **Test the Application**:
   - Visit the App Runner URL
   - Enter questions in the web page to test RAG functionality

### 6. Configure Cloudflare Custom Domain

To use a custom domain:

1. **Associate domain in App Runner**:
   ```bash
   SERVICE_ARN=$(aws apprunner list-services --region us-east-1 \
     --query "ServiceSummaryList[?ServiceName=='bee-edu-rag-service'].ServiceArn" \
     --output text)
   aws apprunner associate-custom-domain \
     --service-arn "$SERVICE_ARN" \
     --domain-name rag.yourdomain.com \
     --region us-east-1
   ```

2. **Add DNS records in Cloudflare**:
   - Add CNAME record: `rag` → `your-apprunner-url.us-east-1.awsapprunner.com`
   - Use **DNS only** (gray cloud), not Proxied
   - Add SSL certificate validation records (provided by App Runner) as CNAME with DNS only
   - Wait 10-30 minutes for SSL certificate validation

## Local Development

### Run Data Ingestion

```bash
# Set OpenAI API Key
export OPENAI_API_KEY="your-api-key"

# Run ingestion script
python ingest.py
```

### Run Application

```bash
# Set OpenAI API Key
export OPENAI_API_KEY="your-api-key"

# Run Flask application
python app.py
```

The application will start at `http://localhost:8080`.

### Local Docker Testing

```bash
# Build image
docker build -t rag-app:local .

# Run container
docker run -p 8080:8080 -e OPENAI_API_KEY="your-api-key" rag-app:local
```

## Tech Stack

- **Backend Framework**: Flask
- **AI Framework**: LangChain
- **Vector Database**: FAISS
- **LLM**: OpenAI GPT
- **Containerization**: Docker
- **Infrastructure as Code**: Terraform
- **CI/CD**: GitHub Actions (OIDC authentication)
- **Cloud Services**: AWS (ECR, App Runner, Secrets Manager, IAM)

## Troubleshooting

### Terraform Errors

- Ensure AWS CLI is configured with correct credentials
- Check Terraform version (requires >= 1.0)
- Ensure all required variables are set

### GitHub Actions Failures

- Check that all GitHub Secrets are correctly configured
- Verify IAM role permissions
- View Actions logs for detailed error messages

### App Runner Deployment Failures

- Check if Docker image was successfully pushed to ECR
- Verify OpenAI API Key in Secrets Manager
- View App Runner service logs
- Check if service is in `OPERATION_IN_PROGRESS` state (workflow will wait)

### Application Not Accessible

- Check if App Runner service status is "Running"
- Verify health check endpoint: `https://your-url/health`
- Check if FAISS index exists in the container

## License

This project is for educational purposes.

## Reference Resources

- [LangChain Documentation](https://python.langchain.com/)
- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
