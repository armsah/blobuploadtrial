pipeline {
    agent any

    stages {
        stage('Environment') {
            steps {
                bat 'python --version'
                bat 'git --version'
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

                        bat 'az webapp show --name armen-storage-demo-2026 --resource-group rg-azure-learning --query "{name:name,state:state,location:location}" --output table'

                        bat 'az account show --query "{name:name,user:user.name,type:user.type}" --output table'
                }
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat 'python -m venv .venv'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
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

        stage('Deploy to Azure') {
            steps {
                withCredentials([
                    string(credentialsId: 'azure-client-id', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'azure-client-secret', variable: 'AZURE_CLIENT_SECRET'),
                    string(credentialsId: 'azure-tenant-id', variable: 'AZURE_TENANT_ID')
                ]) {
                     bat 'az login --service-principal --username "%AZURE_CLIENT_ID%" --password "%AZURE_CLIENT_SECRET%" --tenant "%AZURE_TENANT_ID%" --output none'

                     bat 'az webapp deploy --name armen-storage-demo-2026 --resource-group rg-azure-learning --src-path deploy.zip --type zip'
                }
            }
        }
    }
    
}