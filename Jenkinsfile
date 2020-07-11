pipeline {
    agent { docker { image 'python:3.8' } }
    stages {
        stage('build') {
            steps {
                sh 'python -v -m pip install -r requirements.txt'
            }
        }
        stage('scrape') {
            steps {
                sh 'python run_tell_dat_with_exp.py -wk=35 -lg=premier -r'
            }
        }
    }
}