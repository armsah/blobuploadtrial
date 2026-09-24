pipeline {
    agent any

    environment {
        AZURE_CONFIG_DIR = "${WORKSPACE}\\.azure"
        AZURE_RESOURCE_GROUP = "rg-azure-learning"
        AZURE_WEBAPP_NAME = "armen-storage-demo-2026"
        APP_BASE_URL = "https://${AZURE_WEBAPP_NAME}.azurewebsites.net"
        AZURE_BICEP_FILE = "infrastructure\\main.bicep"
        AZURE_DEPLOYMENT_NAME = "application-infrastructure"
        JENKINS_APP_PRINCIPAL_ID = "7288611a-48dd-45bc-9b02-7bbf46403aa2"
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

        stage('Docker Check') {
            steps {
                bat 'docker version'
            }
        }

        stage('Build Infrastructure') {
            steps {
                bat 'az bicep build --file "%AZURE_BICEP_FILE%" --stdout > NUL'
            }
        }

        stage('Azure Infrastructure Authentication') {
            steps {
                withCredentials([
                    string(credentialsId: 'azure-infra-client-id', variable: 'AZURE_INFRA_CLIENT_ID'),
                    string(credentialsId: 'azure-infra-client-secret', variable: 'AZURE_INFRA_CLIENT_SECRET'),
                    string(credentialsId: 'azure-infra-tenant-id', variable: 'AZURE_INFRA_TENANT_ID')
                ]) {
                    bat '''
                        az login --service-principal ^
                            --username "%AZURE_INFRA_CLIENT_ID%" ^
                            --password "%AZURE_INFRA_CLIENT_SECRET%" ^
                            --tenant "%AZURE_INFRA_TENANT_ID%" ^
                            --output none
                    '''

                    bat 'az account show --query "{identity:user.name,type:user.type}" --output table'
                }
            }
        }

        stage('Validate Infrastructure') {
            steps {
                bat '''
                    az deployment group validate ^
                        --resource-group "%AZURE_RESOURCE_GROUP%" ^
                        --template-file "%AZURE_BICEP_FILE%" ^
                        --parameters jenkinsPrincipalId="%JENKINS_APP_PRINCIPAL_ID%" ^
                        --output none
                '''
            }
        }

        stage('Infrastructure What-If') {
            steps {
                bat '''
                    az deployment group what-if ^
                        --resource-group "%AZURE_RESOURCE_GROUP%" ^
                        --template-file "%AZURE_BICEP_FILE%" ^
                        --parameters jenkinsPrincipalId="%JENKINS_APP_PRINCIPAL_ID%"
                '''
            }
        }

        stage('Deploy Infrastructure') {
            steps {
                bat '''
                    az deployment group create ^
                        --resource-group "%AZURE_RESOURCE_GROUP%" ^
                        --template-file "%AZURE_BICEP_FILE%" ^
                        --parameters jenkinsPrincipalId="%JENKINS_APP_PRINCIPAL_ID%" ^
                        --name "%AZURE_DEPLOYMENT_NAME%" ^
                        --output none
                '''
            }
        }

        stage('Package Application') {
            steps {
                bat 'if exist deploy.zip del deploy.zip'
                bat 'git archive --format=zip --output=deploy.zip HEAD'
                bat 'tar -tf deploy.zip'
                bat '''
                    powershell -NoProfile -Command ^
                        "$files = @(tar -tf deploy.zip); $expected = @('app.py', 'rag_service.py', 'requirements.txt'); if (Compare-Object $files $expected) { Write-Host 'Unexpected deployment artifact contents:'; $files; throw 'Deployment artifact validation failed' }; Write-Host 'Deployment artifact validated:' $files"
                '''
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
                        "$response = Invoke-RestMethod -Uri \\"$env:APP_BASE_URL/health\\"; if ($response.status -ne 'healthy') { throw 'Health check failed' }; Write-Host 'Health check passed:' $response.status"
                '''
            }
        }

        stage('Blob Integration Test') {
            steps {
                bat '''
                    powershell -NoProfile -Command ^
                        "$response = Invoke-RestMethod -Uri \\"$env:APP_BASE_URL/blob\\"; if ($response.container -ne 'documents') { throw 'Unexpected container' }; if ($response.blob -ne 'hello.txt') { throw 'Unexpected blob' }; if (-not $response.content) { throw 'Blob content is empty' }; Write-Host 'Blob integration test passed:' $response.blob"
                '''
            }
        }

        stage('Test AI endpoint') {
            steps {
                powershell '''
                    $body = @{
                        message = "Read hello.txt and tell me what it contains."
                    } | ConvertTo-Json

                    $response = Invoke-RestMethod `
                        -Method Post `
                        -Uri "https://armen-storage-demo-2026.azurewebsites.net/ai" `
                        -ContentType "application/json" `
                        -Body $body

                    if ([string]::IsNullOrWhiteSpace($response.answer)) {
                        throw "AI smoke test failed: response.answer is empty."
                   }

                    Write-Host "AI endpoint smoke test passed."
                    Write-Host "Answer received successfully."
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