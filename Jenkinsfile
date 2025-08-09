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
                        sales-dashboard-backend
                    ls -la
                '''
            }
        }
        stage('Test file at different stage') {
            steps {
                sh '''
                    cd backend/tests
                    ls -la
                '''
            }
        }
    }
}
