Deploying LLM-Eval-System to AWS EC2 from Mac – Complete Guide
1. Prerequisites

Before starting, ensure you have:

A Mac with:

Docker Desktop installed

AWS CLI v2 installed

Homebrew installed (optional, for convenience)

An AWS account with a user having the following permissions:

AmazonEC2FullAccess

AmazonSSMFullAccess

AmazonSSMManagedInstanceCore

AmazonECRFullAccess

An EC2 instance running Ubuntu 24.04 LTS with SSM enabled.

Local Docker images for LLM-Eval-System:

orchestrator

agent

judge

optimiser

ollama

2. Configure AWS CLI on Mac

Open Terminal:

aws configure

Enter:

AWS Access Key ID: AKIA...

AWS Secret Access Key: ...

Default region: eu-north-1

Output format: json

Verify identity:

aws sts get-caller-identity
3. Prepare Docker Images Locally

List Docker images:

docker images

Example images:

llm-eval-system-orchestrator:latest

llm-eval-system-agent:latest

llm-eval-system-judge:latest

llm-eval-system-optimiser:latest

ollama/ollama:latest

Tag images for AWS ECR:

docker tag llm-eval-system-orchestrator:latest 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-orchestrator:latest
docker tag llm-eval-system-agent:latest 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-agent:latest
docker tag llm-eval-system-judge:latest 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-judge:latest
docker tag llm-eval-system-optimiser:latest 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-optimiser:latest
docker tag ollama/ollama:latest 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-ollama:latest
4. Push Images to AWS ECR

Login to AWS ECR:

aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 963777256515.dkr.ecr.eu-north-1.amazonaws.com

Push each image:

docker push 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-orchestrator:latest
docker push 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-agent:latest
docker push 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-judge:latest
docker push 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-optimiser:latest
docker push 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-ollama:latest
5. Prepare EC2 Instance
5.1 Connect via AWS SSM
aws ssm start-session --target <instance-id> --region eu-north-1
5.2 Install Docker
sudo apt-get update -y
sudo apt-get install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

If you see permission denied, use sudo docker ... or log out and log back in to apply group changes.

5.3 Install AWS CLI (if missing)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
6. Pull Docker Images on EC2

Login to ECR on EC2:

aws ecr get-login-password --region eu-north-1 | sudo docker login --username AWS --password-stdin 963777256515.dkr.ecr.eu-north-1.amazonaws.com

Pull all images:

sudo docker pull 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-orchestrator:latest
sudo docker pull 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-agent:latest
sudo docker pull 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-judge:latest
sudo docker pull 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-optimiser:latest
sudo docker pull 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-ollama:latest
7. Run Docker Containers on EC2
sudo docker run -d -p 8004:8000 --name orchestrator 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-orchestrator:latest
sudo docker run -d -p 8001:8000 --name agent 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-agent:latest
sudo docker run -d -p 8002:8000 --name judge 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-judge:latest
sudo docker run -d -p 8003:8000 --name optimiser 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-optimiser:latest
sudo docker run -d -p 11434:11434 --name ollama 963777256515.dkr.ecr.eu-north-1.amazonaws.com/llm-eval-system-ollama:latest
8. Test the API
curl -X POST http://localhost:8004/run \
-H "Content-Type: application/json" \
-d '{"input":"Explain reinforcement learning simply"}'

Expected output: JSON with the explanation from the orchestrator.

9. Tips / Troubleshooting

Docker permission errors

Use sudo docker ...

Ensure your user is in the docker group and start a new session (exit and reconnect).

SSM Session issues

Make sure the instance has the AmazonSSMManagedInstanceCore role.

Ports and Security

EC2 Security Groups must allow incoming connections on ports: 8001-8004 and 11434.

Automation

Consider using docker-compose.yml to run all containers together.

If you want, I can also provide a ready-to-use docker-compose.yml and deployment script for EC2 that will automatically pull all images and run all containers. This makes deployment one command instead of 10+ manual commands.

Do you want me to create that?