pipeline {
    agent any
    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    stages {
        stage('Check Backend Image') {
            steps {
                sh 'docker images'
            }
        }
        stage('Run Backend Container') {
            steps {
                sh '''
                    docker rm -f backend || true
                    docker run -d --name backend -p 8000:8000 \
                        -e ENV=production \
                        -e OPENAI_API_KEY=$OPENAI_API_KEY \
                        sales-dashboard-backend:latest
                '''
            }
        }
        stage('Wait for Backend Ready') {
            steps {
                sh '''
                    echo "Waiting for Uvicorn startup log..."
                    for i in $(seq 1 60); do
                        if docker logs backend 2>&1 | grep -q "Uvicorn running on http://0.0.0.0:8000"; then
                            echo "Uvicorn started"
                            break
                        fi
                        sleep 2
                    done

                    echo "Checking if port 8000 is open..."
                    for i in $(seq 1 30); do
                        if nc -z localhost 8000; then
                            echo "Backend port is open"
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "Backend port not open" >&2
                    docker logs backend || true
                    exit 1
                '''
            }
        }
        stage('Check Files Inside Container') {
            steps {
                sh '''
                    echo "=== Files in container /app ==="
                    docker exec backend ls -la /app/
                    echo "=== Files in container /app/tests ==="
                    docker exec backend ls -la /app/tests/
                '''
            }
        }
        stage('Run Tests in Container') {
            steps {
                sh '''
                    docker exec backend pytest -v --maxfail=1 --junitxml=/app/junit-report.xml
                    docker cp backend:/app/junit-report.xml backend/junit-report.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'backend/junit-report.xml'
                }
            }
        }
    }
    post {
        always {
            sh 'docker logs backend || true'
            sh 'docker rm -f backend || true'
        }
    }
}
