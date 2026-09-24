pipeline {
    agent any

    environment {
        AZURE_CONFIG_DIR = "${WORKSPACE}\\.azure"
        AZURE_RESOURCE_GROUP = "rg-azure-learning"
        ACR_NAME = "acrarmenlearning2026"
        AKS_NAME = "aks-armen-learning-2026"
        AKS_NAMESPACE = "storage-demo"
    }

    stages {
        stage('Environment') {
            steps {
                bat 'python --version'
                bat 'git --version'
                bat 'where helm'
                bat 'helm version --short'
                bat 'where kubectl'
                bat 'kubectl version --client'
                bat 'where kubelogin'
                bat 'kubelogin --version'
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat 'if exist .venv rmdir /s /q .venv'
                bat 'python -m venv .venv'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '.venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt'
            }
        }

        stage('Verify Application') {
            steps {
                bat '.venv\\Scripts\\python.exe -m py_compile app.py'
            }
        }

        stage('Unit Tests') {
            steps {
                bat '.venv\\Scripts\\python.exe -m pytest -v'
            }
        }

        stage('Build Container') {
            steps {
                script {
                    env.IMAGE_TAG = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
                    env.IMAGE = "acrarmenlearning2026.azurecr.io/storage-demo:${env.IMAGE_TAG}"
                }

                bat '''
                    docker build -t "%IMAGE%" .
                '''
            }
        }

        stage('Push to ACR') {
            steps {
                withCredentials([
                    string(credentialsId: 'azure-client-id', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'azure-client-secret', variable: 'AZURE_CLIENT_SECRET'),
                    string(credentialsId: 'azure-tenant-id', variable: 'AZURE_TENANT_ID')
                ]) {
                    bat '''
                        az login --service-principal ^
                            --username "%AZURE_CLIENT_ID%" ^
                            --password "%AZURE_CLIENT_SECRET%" ^
                            --tenant "%AZURE_TENANT_ID%" ^
                            --output none
                        '''

                        bat 'az acr login --name acrarmenlearning2026'

                        bat 'docker push "%IMAGE%"'
                    
                }
            }
        }

        stage('Resolve Image Digest') {
            steps {
                script {
                    env.IMAGE_DIGEST = bat(
                        script: '@az acr repository show --name acrarmenlearning2026 --image storage-demo:%IMAGE_TAG% --query digest --output tsv',
                        returnStdout: true
                    ).trim()

                    echo "Deploying immutable digest: ${env.IMAGE_DIGEST}"
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                withCredentials([
                    string(credentialsId: 'azure-client-id', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'azure-client-secret', variable: 'AZURE_CLIENT_SECRET'),
                    string(credentialsId: 'azure-tenant-id', variable: 'AZURE_TENANT_ID')
                ]) {
                    bat '''
                        az login --service-principal ^
                            --username "%AZURE_CLIENT_ID%" ^
                            --password "%AZURE_CLIENT_SECRET%" ^
                            --tenant "%AZURE_TENANT_ID%" ^
                            --output none
                    '''

                    bat '''
                        if exist "%WORKSPACE%\\.kube-ci" rmdir /s /q "%WORKSPACE%\\.kube-ci"
                        mkdir "%WORKSPACE%\\.kube-ci"
                    '''

                    bat '''
                        set KUBECONFIG=%WORKSPACE%\\.kube-ci\\config
                        az aks get-credentials ^
                            --resource-group rg-azure-learning ^
                            --name aks-armen-learning-2026 ^
                            --file "%KUBECONFIG%" ^
                            --overwrite-existing
                    '''
                    
                    bat '''
                        set KUBECONFIG=%WORKSPACE%\\.kube-ci\\config
                        helm upgrade --install storage-demo helm\\storage-demo ^
                            --namespace storage-demo ^
                            --set image.digest="%IMAGE_DIGEST%" ^
                            --wait ^
                            --atomic ^
                            --timeout 5m
                    '''  

                    bat '''
                        set KUBECONFIG=%WORKSPACE%\\.kube-ci\\config
                        kubectl rollout status deployment/storage-demo ^
                            --namespace storage-demo ^
                            --timeout=180s
                    '''
                }
            }
        }
    }

    post {
        always {
            bat 'az logout 2>NUL || exit /b 0'
            bat 'if exist .azure rmdir /s /q .azure'
            bat 'if exist .kube-ci rmdir /s /q .kube-ci'
        }
    }
}
