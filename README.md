# Jenkins CI/CD Pipeline to host Flask Application 



### Github Actions 

- This code check if there are any conflicts to merge with master branch
- If any problem persists it would break the pipeline and there would be no build triggered
- If the build fails there would be no build made and hence it won't be deployed and deployed build be a previous successfull build


```
name: CI/CD Pipeline

on:
  push:
    branches:
      - main
      - staging
      - master
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'  # Specify the Python version

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest --maxfail=1 --disable-warnings -q

      - name: Build Application
        run: |
          echo "Building application..."

  generate_tag:
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'workflow_dispatch' || github.ref == 'refs/heads/main'
    steps:
      - name: Generate Unique Tag
        id: generate_tag
        run: |
          TIMESTAMP=$(date +'%Y%m%d%H%M%S')
          UNIQUE_TAG="v${TIMESTAMP}"
          echo "Generated tag: $UNIQUE_TAG"
          echo "TAG=$UNIQUE_TAG" >> $GITHUB_ENV

      - name: Create and Push Tag
        run: |
          git tag $TAG
          git push origin $TAG

  deploy_staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/staging'
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Deploy to Staging
        run: |
          echo "Deploying to Staging..."
  
  deploy_master:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/master'
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Deploy to Staging
        run: |
          echo "Deploying to master..."

  deploy_production:
    runs-on: ubuntu-latest
    needs: build
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Deploy to Production
        run: |
          echo "Deploying to Production..."
```

### Jenkinsfile file to do stage work

- Once build in get sucessfull by scm poll in jenkins configuration the stage work gets triggered.
- Changes made by developer would be shared to hosted directory and hence it would apply changes in deployment.

```
pipeline {
    agent any

    environment {
        DEPLOY_DIR = "/home/ubuntu/Jenkins0_0"
        GIT_REPO = "https://github.com/Gani-23/Jenkins0_0"
        HOSTEDSERVER = "13.125.200.61"
        CREDENTIALS_ID = "Gani" 
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'master', url: "${env.GIT_REPO}"
            }
        }
        stage('Install Dependencies') {
            steps {
                script {
                    sh '''
                    su
                    '''
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    '''
                }
            }
        }
        stage('Test') {
            steps {
                script {
                    sh '''
                    . venv/bin/activate
                    pytest
                    '''
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: "${env.CREDENTIALS_ID}", keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                        sh """
                        scp -o StrictHostKeyChecking=no -i ${SSH_KEY} -r * ${SSH_USER}@${env.HOSTEDSERVER}:${env.DEPLOY_DIR}
                        ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ${SSH_USER}@${env.HOSTEDSERVER} <<EOF
cd ${DEPLOY_DIR}
. venv/bin/activate
sudo apt update -y
sudo apt install python3-pip -y
sudo apt install python3-flask -y
pip install -r requirements.txt 
nohup python3 app.py > flaskapp.log 2>&1 &
EOF
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                echo "Build completed with status: ${currentBuild.result}"
            }
        }
    }
}

```
