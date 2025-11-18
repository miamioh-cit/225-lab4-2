pipeline {
    agent any 

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'  
        DOCKER_IMAGE = 'cithit/nolen'                                   //<-----change this to your MiamiID!
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/nathaniel-stack/225-lab4-2.git'     //<-----change this to match this new repository!
        KUBECONFIG = credentials('nolen-225')                           //<-----change this to match your kubernetes credentials (MiamiID-225)! 
   }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Lint HTML') { steps { sh 'npm install htmlhint --no-save || true; npx htmlhint *.html || true' } }
    stage('Static Python Checks') {
      steps {
        sh 'python3 -m pip install --upgrade pip || true'
        sh 'python3 -m pip install flake8 bandit || true'
        sh 'flake8 app/ || true'
        sh 'bandit -r app/ -f json -o bandit-report.json || true'
        archiveArtifacts artifacts: "bandit-report.json", allowEmptyArchive: true
      }
    }
    stage('Unit Tests') {
      steps {
        sh 'python3 -m pip install -r requirements2.txt || true'
        sh 'pytest --junitxml=reports/pytest-results.xml --cov=app --cov-report=xml --cov-fail-under=80 || true'
        junit 'reports/pytest-results.xml'
        archiveArtifacts artifacts: "coverage.xml", allowEmptyArchive: true
      }
    }
    stage('Build & Push Docker') {
      steps {
        script {
          docker.withRegistry('https://registry.hub.docker.com', "${DOCKER_CREDENTIALS_ID}") {
            def img = docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}", "-f Dockerfile.build .")
            img.push()
            sh "docker tag ${DOCKER_IMAGE}:${IMAGE_TAG} ${DOCKER_IMAGE}:latest || true"
            sh "docker push ${DOCKER_IMAGE}:latest || true"
          }
        }
      }
    }
    stage('Deploy to Dev') {
      steps {
        sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml || true"
        sh "kubectl apply -f deployment-dev.yaml || true"
      }
    }
    stage('Integration Test') {
      steps {
        sh '''
          kubectl port-forward svc/flask-service 5000:5000 >/dev/null 2>&1 &
          PORTFWD=$!
          sleep 5
          curl -f http://localhost:5000/health || true
          kill $PORTFWD || true
        '''
      }
    }
    stage('Deploy to Prod') {
      steps {
        sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-prod.yaml || true"
        sh "kubectl apply -f deployment-prod.yaml || true"
      }
    }
  }
  post {
    always {
      script {
        def buildStatus = currentBuild.currentResult
        withCredentials([string(credentialsId: "${SLACK_CREDENTIALS}", variable: 'SLACK_WEBHOOK')]) {
          sh """
python3 - <<PY
import os, requests, json
url=os.getenv('SLACK_WEBHOOK')
payload={'text':f'Job: ${env.JOB_NAME} #${env.BUILD_NUMBER} status: ${buildStatus}'}
requests.post(url, json=payload)
PY
          """
        }
      }
    }
  }
}
