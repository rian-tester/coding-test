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
    }
   
}
