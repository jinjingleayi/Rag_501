# RAG Q&A Application - Automated CI/CD Deployment

This is a RAG (Retrieval-Augmented Generation) Q&A application based on LangChain, automatically deployed to AWS App Runner via GitHub Actions (OIDC).

## Project Structure

```
Rag_501/
├── app.py                 # Flask web application main file
├── ingest.py              # Data ingestion script to create vector index
├── data.txt               # Knowledge base data file
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image build file
├── main.tf                # Terraform infrastructure configuration
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Actions CI/CD workflow
└── README.md              # This file
```

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
- `apprunner_access_role_arn` → Used internally by workflow (dynamically retrieved)
- `apprunner_instance_role_arn` → Used internally by workflow (dynamically retrieved)

### 3. Configure GitHub Secrets

In your GitHub repository:

1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**
3. Add the following 4 Secrets:

| Secret Name | Value Source | Example Value |
|------------|--------------|---------------|
| `AWS_REGION` | Fixed value | `us-east-1` |
| `ECR_REPOSITORY` | Terraform output `ecr_repository_name` | `bee-edu-rag-app` |
| `APP_RUNNER_ARN` | Terraform output `apprunner_service_arn` | `arn:aws:apprunner:us-east-1:...` (optional, if service is created by GitHub Actions) |
| `AWS_IAM_ROLE_TO_ASSUME` | Terraform output `github_actions_role_arn` | `arn:aws:iam::...:role/github-actions-deploy-role` |

**Note**: The workflow automatically retrieves `apprunner_access_role_arn` and `apprunner_instance_role_arn` from IAM, so they don't need to be added as secrets.

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

### 6. Configure Cloudflare Custom Domain (Optional)

To use a custom domain with your App Runner service:

#### Step 1: Add Custom Domain in App Runner

First, you need to associate your custom domain with the App Runner service:

```bash
# Get your service ARN
SERVICE_ARN=$(aws apprunner list-services \
  --region us-east-1 \
  --query "ServiceSummaryList[?ServiceName=='bee-edu-rag-service'].ServiceArn" \
  --output text)

# Associate custom domain
aws apprunner associate-custom-domain \
  --service-arn "$SERVICE_ARN" \
  --domain-name rag.yourdomain.com \
  --region us-east-1
```

This will return DNS validation records that need to be added to Cloudflare.

#### Step 2: Configure DNS in Cloudflare

1. Log in to your Cloudflare account: https://dash.cloudflare.com/
2. Select your domain
3. Go to **DNS** → **Records**
4. Add the main **CNAME** record:
   - **Type**: CNAME
   - **Name**: `rag` (or your desired subdomain)
   - **Target**: Your App Runner URL (e.g., `ugxaymsvp3.us-east-1.awsapprunner.com`)
   - **Proxy status**: ⚪ **DNS only** (gray cloud, **NOT** proxied/orange cloud)
   - Click **Save**

5. Add SSL certificate validation records:
   - App Runner will provide 2-3 CNAME records for SSL certificate validation
   - Add each validation record as a CNAME:
     - **Type**: CNAME
     - **Name**: The validation record name (e.g., `_xxxxx.rag`)
     - **Target**: The validation target (e.g., `_xxxxx.acm-validations.aws.`)
     - **Proxy status**: ⚪ **DNS only** (gray cloud, **required** for validation)
   - These are temporary records for SSL certificate validation

#### Step 3: Wait for SSL Certificate Validation

- Wait 10-30 minutes for AWS to validate the DNS records and issue the SSL certificate
- Check the status:
  ```bash
  aws apprunner describe-custom-domains \
    --service-arn "$SERVICE_ARN" \
    --region us-east-1
  ```
- When status changes to `active`, your custom domain is ready

#### Step 4: Verify Access

Once the domain status is `active`, you can access your application at:
- `https://rag.yourdomain.com`

**Important Notes:**
- Use **DNS only** (gray cloud) for all CNAME records, not Proxied (orange cloud)
- App Runner handles SSL certificates automatically through AWS Certificate Manager
- DNS propagation typically takes 5-15 minutes
- SSL certificate validation may take 10-30 minutes

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

## CI/CD Workflow Description

The `.github/workflows/deploy.yml` workflow automatically executes on every push to the `main` branch:

1. **Checkout code**: Check out the code
2. **Configure AWS credentials**: Log in to AWS using OIDC keyless authentication
3. **Log in to ECR**: Log in to Amazon ECR
4. **Build and push Docker image**: Build Docker image and push to ECR
5. **Get App Runner service details**: Retrieve App Runner service configuration
6. **Deploy to AWS App Runner**: Deploy new image to App Runner

## Tech Stack

- **Backend Framework**: Flask
- **AI Framework**: LangChain
- **Vector Database**: FAISS
- **LLM**: OpenAI GPT
- **Containerization**: Docker
- **Infrastructure as Code**: Terraform
- **CI/CD**: GitHub Actions
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

### Application Not Accessible

- Check if App Runner service status is "Running"
- Verify health check endpoint: `https://your-url/health`
- Check Cloudflare DNS configuration

## License

This project is for educational purposes.

## Reference Resources

- [LangChain Documentation](https://python.langchain.com/)
- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
