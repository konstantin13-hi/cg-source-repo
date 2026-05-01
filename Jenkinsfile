pipeline {
    agent any

    environment {
        GENERATED_REPO_URL = 'git@github.com:YOUR_USER/generated-app-repo.git'
        GENERATED_REPO_DIR = 'generated-app-repo'
    }

    stages {
        stage('Install generator dependencies') {
            steps {
                sh 'python3 -m pip install -r requirements.txt'
            }
        }

        stage('Validate design artifacts') {
            steps {
                sh 'python3 generator/validate_model.py artifacts/model.yaml'
            }
        }

        stage('Clone generated code repository') {
            steps {
                sh '''
                rm -rf $GENERATED_REPO_DIR
                git clone $GENERATED_REPO_URL $GENERATED_REPO_DIR
                '''
            }
        }

        stage('Generate application code') {
            steps {
                sh 'python3 generator/generate.py artifacts/model.yaml $GENERATED_REPO_DIR'
            }
        }

        stage('Commit generated code') {
            steps {
                dir("${GENERATED_REPO_DIR}") {
                    sh '''
                    git add .
                    git commit -m "CG: regenerate application from project artifacts" || echo "No changes to commit"
                    git push origin main
                    '''
                }
            }
        }
    }
}
