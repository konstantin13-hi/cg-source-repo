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

        stage('Deploy application') {

             steps {

                sh '''

                     echo "Stopping previous application container..."

                     docker rm -f generated-app || true

                    echo "Starting generated-app:${BUILD_NUMBER}..."

                     docker run -d \

                     --name generated-app \

                         -p 8080:8080 \

                         --restart unless-stopped \

                         generated-app:${BUILD_NUMBER}

                        echo "Application container started."

                         docker ps --filter "name=generated-app"

                '''

                 }

        }

        stage('Health check') {
            steps {
                sh '''
                     echo "Waiting for application to start..."

                    for i in $(seq 1 30); do
                        if curl -fsS http://localhost:8080/api/students > /dev/null; then
                            echo "Application is healthy."
                            exit 0
                        fi

                        echo "Waiting for application... attempt $i/30"
                        sleep 2
                    done

                    echo "Application failed health check."
                    docker logs generated-app
                    exit 1
                 '''
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