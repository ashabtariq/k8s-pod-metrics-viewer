pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-login')
        IMAGE_NAME = 'ashabtariq12/k8s-pod-metric-viewer'
        IMAGE_TAG = 'V1.0'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'master', url: 'https://github.com/ashabtariq/k8s-pod-metrics-viewer.git'
            }
        }
        
        
        
        stage('SonarQube Analysis') {
    environment {
        SONAR_HOST_URL = 'http://192.168.1.40:9000'
        SONAR_PROJECT_KEY = 'K8S-Pods'
    }
    steps {
        withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
            sh '''
            sonar-scanner \
              -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
              -Dsonar.sources=. \
              -Dsonar.host.url=${SONAR_HOST_URL} \
              -Dsonar.token=${SONAR_TOKEN}
            '''
        }
    }
}
        


        stage('Go to Directory and Build') {
            steps {
                sh '''
                    cd app || exit 1
                    echo "Current directory: $(pwd)"
                    # Now run commands in this directory
                    ls -l
                    docker build -t ashabtariq12/k8s-pod-metric-viewer:V1.0 .
                '''
            }
        }
        
        
        stage('Push to Docker Hub') {
            steps {
                sh '''
                    echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login -u "$DOCKERHUB_CREDENTIALS_USR" --password-stdin
                    docker push ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }
    }
}
