pipeline {
    agent any

    environment {
        AWS_ECR_REPO = 'kady-docker-repo'
        AWS_REGION = 'us-east-1'
        DOCKER_IMAGE = "522814709442.dkr.ecr.us-east-1.amazonaws.com/${AWS_ECR_REPO}"
        TARGET_INSTANCE_NAME = 'k3s'
        TARGET_KEY_PATH = '/var/lib/jenkins/.ssh/k3sPair.pem'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/goushaa/DEPI-Code.git', branch: 'main'
            }
        }

        stage('Cleanup Docker Images') {
            steps {
                script {
                    // Remove dangling and old images
                    sh 'docker image prune -f'
                    sh 'docker rmi $(docker images -q --filter "before=dns-resolver:latest") || true'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t dns-resolver .'
            }
        }

        stage('Debug Docker Images') {
            steps {
                // List Docker images
                sh 'docker images'
            }
        }

        stage('Login to ECR') {
            steps {
                script {
                    // Login to AWS ECR
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-ecr-credentials']]) {
                        sh """
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${DOCKER_IMAGE}
                        """
                    }
                }
            }
        }

        stage('Tag & Push to ECR') {
            steps {
                script {
                    // Tag the image with the build number
                    def tags = ["${BUILD_NUMBER}", "latest"]
                    tags.each { tag ->
                        sh "docker tag dns-resolver:latest ${DOCKER_IMAGE}:${tag}"
                        sh "docker push ${DOCKER_IMAGE}:${tag}"
                    }
                }
            }
        }

        stage('Fetch Target EC2 Details') {
            steps {
                script {
                    // Get the public IP of the target EC2 instance by name
                    def instanceDetails = sh(script: "aws ec2 describe-instances --filters \"Name=tag:Name,Values=${TARGET_INSTANCE_NAME}\" --query \"Reservations[*].Instances[?PublicIpAddress!=null].[PublicIpAddress]\" --output text --region ${AWS_REGION}", returnStdout: true).trim()
                    env.TARGET_EC2_IP = instanceDetails

                    // Get the SSH key path from the Terraform output (you might run terraform output command here if needed)
                    env.TARGET_KEY = TARGET_KEY_PATH
                    
                    echo "EC2 IP: ${env.TARGET_EC2_IP}"
                    echo "SSH Key Path: ${env.TARGET_KEY}"
                }
            }
        }

        stage('Transfer Deployment File') {
            steps {
                script {
                    // SSH to verify connection (test)
                    sh """
                    ssh -o StrictHostKeyChecking=no -i ${TARGET_KEY} ubuntu@${TARGET_EC2_IP} \
                    'aws ecr get-login-password --region us-east-1'
                    """

                    // Transfer the deployment YAML file to the target EC2 instance
                    sh """
                    scp -o StrictHostKeyChecking=no -i ${TARGET_KEY} dns_resolver_deployment.yaml ubuntu@${TARGET_EC2_IP}:/home/ubuntu/
                    """
                }
            }
        }

        stage('Apply Deployment') {
            steps {
                script {
                    // SSH into the target EC2 instance and apply the deployment
                    sh """
                    ssh -o StrictHostKeyChecking=no -i ${TARGET_KEY} ubuntu@${TARGET_EC2_IP} "kubectl apply -f /home/ubuntu/dns_resolver_deployment.yaml"
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Image pushed to ECR and deployment applied successfully!'
        }
        failure {
            echo 'Build failed.'
        }
    }
}
