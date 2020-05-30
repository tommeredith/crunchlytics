pipeline {
    agent { docker { image 'python:3.8' } }
    stages {
        stage('build') {
            steps {
                sh 'sudo -H pip install -r requirements.txt'
            }
        }
        stage('scrape') {
            steps {
                sh 'python germanCrawl.py'
            }
        }
    }
}