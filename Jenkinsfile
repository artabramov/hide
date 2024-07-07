pipeline {
    agent any

    stages {
        stage('unittests') {
            steps {
                script {
                    def command = "docker exec hide-server /bin/sh -c \"cd /hide && python3 -W ignore -m coverage run -m unittest discover -s ./tests -p '*_tests.py'\""
                    def exitCode = bat(script: command, returnStatus: true)
                    
                    if (exitCode == 0) {
                        command = "docker exec hide-server /bin/sh -c \"cd /hide && python3 -m coverage report --omit '/usr/lib/*,tests/*'\""
                        exitCode = bat(script: command, returnStatus: true)
                        
                        if (exitCode != 0) {
                            currentBuild.result = 'FAILURE'
                            error 'Coverage failed.'
                        }
                    } else {
                        currentBuild.result = 'FAILURE'
                        error 'Unittests failed.'
                    }
                }
            }
        }

        stage('safety') {
            steps {
                script {
                    def command = "docker exec hide-server /bin/sh -c \"pip3 install --upgrade safety\""
                    def exitCode = bat(script: command, returnStatus: true)

                    if (exitCode == 0) {
                        command = "docker exec hide-server /bin/sh -c \"safety check --file /hide/requirements.txt --ignore 50959 --ignore 70612\""
                        exitCode = bat(script: command, returnStatus: true)

                        if (exitCode != 0) {
                            currentBuild.result = 'FAILURE'
                            error 'Safety upgrade failed.'
                        }
                    } else {
                        currentBuild.result = 'FAILURE'
                        error 'Safety execution failed.'
                    }
                }
            }
        }

        stage('flake8') {
            steps {
                script {
                    def command = "docker exec hide-server /bin/sh -c \"flake8 --count --max-line-length=80 /hide\""
                    def exitCode = bat(script: command, returnStatus: true)

                    if (exitCode != 0) {
                        currentBuild.result = 'FAILURE'
                        error 'Flake8 failed.'
                    }
                }
            }
        }

        stage('smokes') {
            steps {
                script {
                    def command = "docker exec hide-smokes /bin/sh -c \"cd /smokes && behave /smokes/app/features/*.feature --no-capture --format progress\""
                    def exitCode = bat(script: command, returnStatus: true)

                    if (exitCode != 0) {
                        currentBuild.result = 'FAILURE'
                        error 'Smokes failed.'
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
        always {
            echo 'Pipeline completed.'
        }
    }
}
