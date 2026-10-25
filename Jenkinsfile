pipeline {
    agent any

    environment {
        GENERATED_REPO_URL = 'git@github.com:konstantin13-hi/generated-app-repo.git'
        GENERATED_REPO_DIR = 'generated-app-repo'
    }

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

        stage('Clone generated application repository') {
            steps {
                sh '''
                    rm -rf "$GENERATED_REPO_DIR"
                    git clone "$GENERATED_REPO_URL" "$GENERATED_REPO_DIR"
                '''
            }
        }

        stage('Generate application code') {
            steps {
                sh '''
                    .venv/bin/python generator/generate.py artifacts/model.yaml "$GENERATED_REPO_DIR"
                '''
            }
        }

        stage('Verify generated application') {
            steps {
                dir("${GENERATED_REPO_DIR}") {
                    sh '''
                        echo "Generated application files:"
                        ls -la
                        test -f pom.xml
                        test -f Dockerfile
                        test -d src
                    '''
                }
            }
        }

        stage('Build and test generated application') {
            steps {
                dir("${GENERATED_REPO_DIR}") {
                  sh '''
                    mvn clean test
                '''
                 }
            }
        }

        stage('Package generated application') {
            steps {
                 dir("${GENERATED_REPO_DIR}") {
                    sh '''
                     mvn package -DskipTests
                     test -f target/*.jar
                     ls -lh target/*.jar
            '''
                }
             }
        }
    }

    post {
        success {
            echo 'CG pipeline completed successfully.'
        }

        failure {
            echo 'CG pipeline failed.'
        }
    }
}