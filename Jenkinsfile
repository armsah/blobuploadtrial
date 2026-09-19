pipeline {
    agent any

    stages {
        stage('Environment') {
            steps {
                bat 'python --version'
                bat 'git --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Verify Application') {
            steps {
                bat 'python -m py_compile app.py'
            }
        }
    }
}