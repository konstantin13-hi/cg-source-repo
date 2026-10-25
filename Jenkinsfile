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
                        echo "Generated JAR:"
                        ls -lh target/*.jar
                    '''
                }
            }
        }

        stage('Publish generated application') {
            steps {
                dir("${GENERATED_REPO_DIR}") {
                    sh '''
                        git config user.name "Jenkins CG/CD"
                        git config user.email "jenkins@devops-01"

                        git add .

                        if git diff --cached --quiet; then
                            echo "No generated changes to commit."
                        else
                            git commit -m "CG: regenerate application from project artifacts"
                            git push origin main
                        fi
                    '''
                }
            }
        }

        stage('Build Docker image') {
            steps {
                 dir("${GENERATED_REPO_DIR}") {
                     sh '''
                       docker build -t generated-app:${BUILD_NUMBER} .
                       docker images generated-app
                     '''
                    }
           }
        }
}

    post {
        success {
            echo 'CG/CI pipeline completed successfully.'
        }

        failure {
            echo 'CG/CI pipeline failed.'
        }
    }
}