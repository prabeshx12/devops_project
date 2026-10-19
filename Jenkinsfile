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
                    pip install ruff==0.8.4
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . venv/bin/activate
                    ruff check backend
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

        stage('Scan Image') {
            steps {
                // Report-only: change --exit-code to 1 to fail the build on findings.
                sh '''
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v trivy-cache:/root/.cache/ \
                        aquasec/trivy:0.58.1 image \
                            --severity HIGH,CRITICAL \
                            --ignore-unfixed \
                            --exit-code 0 \
                            inventoryops:${IMAGE_TAG}
                '''
            }
        }

        stage('Push Docker Image to Azure ACR') {
            steps {
                withCredentials([
                    string(credentialsId: 'azure-client-id', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'azure-client-secret', variable: 'AZURE_CLIENT_SECRET')
                ]) {
                    sh '''
                        echo "${AZURE_CLIENT_SECRET}" | docker login ${ACR_LOGIN_SERVER} \
                            --username ${AZURE_CLIENT_ID} \
                            --password-stdin
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
                sh '''
                    docker exec inventoryops \
                        python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)"
                '''
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
        }
    }
}
