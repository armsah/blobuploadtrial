pipeline {
    agent any

    environment {
        AZURE_CONFIG_DIR = "${WORKSPACE}\\.azure"
        AZURE_RESOURCE_GROUP = "rg-azure-learning"
        AZURE_WEBAPP_NAME = "armen-storage-demo-2026"
    }

    stages {
        stage('Environment') {
            steps {
                bat 'python --version'
                bat 'git --version'
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

        stage('Package Application') {
            steps {
                bat 'if exist deploy.zip del deploy.zip'
                bat 'git archive --format=zip --output=deploy.zip HEAD'
                bat 'tar -tf deploy.zip'
            }
        }

        stage('Azure Authentication') {
            steps {
                withCredentials([
                    string(credentialsId: 'azure-client-id', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'azure-client-secret', variable: 'AZURE_CLIENT_SECRET'),
                    string(credentialsId: 'azure-tenant-id', variable: 'AZURE_TENANT_ID')
                ]) {
                        bat 'az login --service-principal --username "%AZURE_CLIENT_ID%" --password "%AZURE_CLIENT_SECRET%" --tenant "%AZURE_TENANT_ID%" --output none'

                        bat 'az webapp show --name "%AZURE_WEBAPP_NAME%" --resource-group "%AZURE_RESOURCE_GROUP%" --query "{name:name,state:state,location:location}" --output table'

                        bat 'az account show --query "{name:name,user:user.name,type:user.type}" --output table'
                }
            }
        }


        stage('Deploy to Azure') {
            steps {
                bat 'az webapp deploy --name "%AZURE_WEBAPP_NAME%" --resource-group "%AZURE_RESOURCE_GROUP%" --src-path deploy.zip --type zip'
            }
        }

        stage('Smoke Test') {
            steps {
                bat '''
                    powershell -NoProfile -Command ^
                        "$response = Invoke-RestMethod -Uri 'https://armen-storage-demo-2026.azurewebsites.net/health'; if ($response.status -ne 'healthy') { throw 'Health check failed' }; Write-Host 'Health check passed:' $response.status"
                '''
            }
        }

        stage('Blob Integration Test') {
            steps {
                bat '''
                    powershell -NoProfile -Command ^
                        "$response = Invoke-RestMethod -Uri 'https://armen-storage-demo-2026.azurewebsites.net/blob'; if ($response.container -ne 'documents') { throw 'Unexpected container' }; if ($response.blob -ne 'hello.txt') { throw 'Unexpected blob' }; if (-not $response.content) { throw 'Blob content is empty' }; Write-Host 'Blob integration test passed:' $response.blob"
                '''
            }
        }

    }

    post {
        always {
            bat 'if exist .azure rmdir /s /q .azure'
        }
    }
    
}