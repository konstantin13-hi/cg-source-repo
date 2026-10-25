pipeline {
    agent any

    stages {
        stage('Setup Python environment') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Validate design artifacts') {
            steps {
                sh '''
                    .venv/bin/python generator/validate_model.py artifacts/model.yaml
                '''
            }
        }
    }

    post {
        success {
            echo 'CG validation pipeline completed successfully.'
        }

        failure {
            echo 'CG validation pipeline failed.'
        }
    }
}