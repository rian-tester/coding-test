pipeline {
    agent any

    stages {
        stage('Cleaning up Workspace') {
            steps {
                echo 'Start cleaning'
                // Removes all normal files and directories
                echo 'Removes all normal files and directories'
                sh 'rm -rf "$WORKSPACE"/* || true'
                
                // Remove hidden files except . and ..
                echo 'Remove hidden files except . and ..'
                sh 'rm -rf "$WORKSPACE"/.[!.]* || true'
                
                // Remove hidden directories w/ two or more leading dots
                echo 'Remove hidden directories w/ two or more leading dots'
                sh 'rm -rf "$WORKSPACE"/..?* || true'

                // Use Delete Dir
                echo 'Using deleteDir()'
                deleteDir()
                
                // Results
                echo 'check Workspace'
                sh 'ls -A "$WORKSPACE"'
            }
            
            
        }
        stage ('Check if sales-dashboard-backend image exist') {
            steps {
                // Verify image exist
                script {
                    def imageStatus = sh (
                        script: "docker images -q sales-dashboard-backend:latest | grep .",
                        returnStatus: true
                    )
                    if (imageStatus != 0) {
                        echo 'Docker image sales-dashboard-backend:latest not found'
                        error 'Please build the image sales-dashboard-backend:latest first before running this pipeline'
                    }
                }
            }
        }
        stage('Extract files to Workspace') {
            steps {
                // copy files from the container into the workspace
                echo 'copy files from the container into the workspace'
                sh '''
                    docker run --rm \
                    --entrypoint '' \
                    -v "$WORKSPACE":/workspace \
                    sales-dashboard-backend \
                    sh -lc "cp -r /app/. /workspace"
                '''

                echo 'Current files in Jenkins workspace : '
                sh 'ls -la'
            }
        }
        stage('Unit Test') {
            agent {
                docker {
                    image 'sales-dashboard-backend:latest'
                    reuseNode true
                    args "--entrypoint=''"
                }
            }
            steps {
                echo 'Check if test files is exist inside tests folder'
                script {
                    // Check if tests/ folder exists and contains Python test files
                    def testFiles = sh(
                        script: 'find tests/ -name "test_*.py" -o -name "*_test.py" 2>/dev/null | wc -l',
                        returnStdout: true
                    ).trim()
                    
                    if (testFiles == '0') {
                        echo 'No test files found in tests/ folder. Skipping pytest execution.'
                        currentBuild.result = 'SUCCESS'
                        return
                    }
                    
                    echo "Found ${testFiles} test file(s). Running pytest..."
                    
                    // Ensure reports directory exists
                    sh 'mkdir -p reports'
                    
                    // Run test with verbose and extra text
                    sh 'pytest -v -rA --junitxml=reports/pytest-junit.xml'
                }
            }
            post {
                always {
                    // Parse JUnit for test results
                    junit allowEmptyResults: true, testResults: 'reports/pytest-junit.xml'
                }
            }
        }
        stage('Clean workspace after unit test') {
            steps {
                    // Delete files
                    sh 'rm -rf "$WORKSPACE"/* || true'
                    
                    // Remove hidden files except . and ..
                    echo 'Remove hidden files except . and ..'
                    sh 'rm -rf "$WORKSPACE"/.[!.]* || true'
                
                    // Remove hidden directories w/ two or more leading dots
                    echo 'Remove hidden directories w/ two or more leading dots'
                    sh 'rm -rf "$WORKSPACE"/..?* || true'
                    
                    // Results
                    echo 'check leftover files'
                    sh 'ls -la'
            }
        }
    }
}
