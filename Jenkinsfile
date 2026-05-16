pipeline {
    agent any

    environment {
        ACR_LOGIN_SERVER = credentials('acr-login-server')
        ACR_REPOSITORY = 'inventoryops'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        IMAGE_NAME = "${ACR_LOGIN_SERVER}/${ACR_REPOSITORY}:${IMAGE_TAG}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Venv') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r backend/requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest backend/tests
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -f docker/Dockerfile -t inventoryops:${IMAGE_TAG} .'
            }
        }

        stage('Push Docker Image to Azure ACR') {
            steps {
                withCredentials([
                    string(credentialsId: 'azure-client-id', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'azure-client-secret', variable: 'AZURE_CLIENT_SECRET'),
                    string(credentialsId: 'azure-tenant-id', variable: 'AZURE_TENANT_ID'),
                    string(credentialsId: 'azure-subscription-id', variable: 'AZURE_SUBSCRIPTION_ID')
                ]) {
                    sh '''
                        az login --service-principal \
                            --username ${AZURE_CLIENT_ID} \
                            --password ${AZURE_CLIENT_SECRET} \
                            --tenant ${AZURE_TENANT_ID}
                        az account set --subscription ${AZURE_SUBSCRIPTION_ID}
                        docker login ${ACR_LOGIN_SERVER} \
                            --username ${AZURE_CLIENT_ID} \
                            --password ${AZURE_CLIENT_SECRET}
                        docker tag inventoryops:${IMAGE_TAG} ${IMAGE_NAME}
                        docker push ${IMAGE_NAME}
                        docker tag inventoryops:${IMAGE_TAG} ${ACR_LOGIN_SERVER}/${ACR_REPOSITORY}:latest
                        docker push ${ACR_LOGIN_SERVER}/${ACR_REPOSITORY}:latest
                    '''
                }
            }
        }

        stage('Deploy with Ansible') {
            steps {
                withCredentials([
                    string(credentialsId: 'azure-client-id', variable: 'ACR_USERNAME'),
                    string(credentialsId: 'azure-client-secret', variable: 'ACR_PASSWORD')
                ]) {
                    sh '''
                        export ACR_LOGIN_SERVER=${ACR_LOGIN_SERVER}
                        export ACR_REPOSITORY=${ACR_REPOSITORY}
                        export IMAGE_TAG=${IMAGE_TAG}
                        ansible-playbook -i ansible/inventory.ini ansible/deploy.yml
                    '''
                }
            }
        }

        stage('Verify Health') {
            steps {
                sh 'curl -f http://127.0.0.1:8000/health'
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
        }
    }
}

