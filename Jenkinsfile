pipeline {
    agent any
    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    stages {
        stage('Local Test - Run Tests in Docker') {
            agent {
                docker {
                    image 'sales-dashboard-backend:latest'
                    reuseNode true
                }
            }
            steps {
                sh '''
                    echo "=== Running all tests ==="
                    pytest -v --maxfail=1 --junitxml=junit-report.xml /app/tests/
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'junit-report.xml'
                    archiveArtifacts artifacts: 'junit-report.xml', allowEmptyArchive: true
                }
            }
        }
        stage('Runtime - Check Image Available') {
            steps {
                sh '''
                    echo "=== Checking available images ==="
                    docker images | grep sales-dashboard-backend
                '''
            }
        }
        stage('Runtime - Start Backend Container') {
            steps {
                sh '''
                    echo "=== Starting backend container ==="
                    docker rm -f backend || true
                    docker run -d --name backend -p 8000:8000 \
                        -e ENV=production \
                        -e OPENAI_API_KEY=$OPENAI_API_KEY \
                        sales-dashboard-backend:latest
                '''
            }
        }
        stage('Runtime - Wait and Test Server') {
            steps {
                sh '''
                    echo "=== Waiting for server to be ready ==="
                    sleep 10
                    
                    echo "=== Testing if server is active ==="
                    for i in $(seq 1 20); do
                        echo "Attempt $i: Testing server..."
                        if curl -f -s http://localhost:8000/api/sales-reps >/dev/null 2>&1; then
                            echo "✅ Server is active and responding!"
                            curl -s http://localhost:8000/api/sales-reps | head -5
                            exit 0
                        fi
                        sleep 3
                    done
                    
                    echo "❌ Server not responding after 60 seconds"
                    echo "=== Container logs ==="
                    docker logs backend
                    exit 1
                '''
            }
        }
    }
    post {
        always {
            sh '''
                echo "=== Final container logs ==="
                docker logs backend || true
                echo "=== Cleaning up ==="
                docker rm -f backend || true
            '''
        }
    }
}
