pipeline {
    agent any

    stages {
        stage('Environment') {
            steps {
                bat 'python --version'
                bat 'git --version'
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
    }
}