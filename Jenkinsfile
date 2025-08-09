pipeline {
    agent any
    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    stages {
        stage('Start Backend Container') {
            steps {
                sh '''
                    docker rm -f backend || true
                    docker run -d --name backend -p 8000:8000 \
                        -e ENV=production \
                        -e OPENAI_API_KEY=$OPENAI_API_KEY \
                        sales-dashboard-backend
                    for i in $(seq 1 30); do
                        if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then exit 0; fi
                        sleep 2
                    done
                    docker logs backend || true
                    exit 1
                '''
            }
        }
        stage('Unit Tests (in container)') {
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
