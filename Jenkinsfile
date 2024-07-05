pipeline {
    agent any

    stages {
        stage('unittests') {
            steps {
                script {
                    def command = "docker exec hide-server /bin/sh -c \"cd /hide && python3 -W ignore -m coverage run -m unittest discover -s ./tests -p '*_tests.py'\""
                    def exitCode = bat(script: command, returnStatus: true)

                    if (exitCode == 0) {
                        echo 'Tests executed successfully.'
                    } else {
                        currentBuild.result = 'FAILURE'
                        error 'Failed to execute tests.'
                    }
                }
            }
        }

        stage('coverage') {
            steps {
                script {
                    def command = "docker exec hide-server /bin/sh -c \"cd /hide && python3 -m coverage report --omit '/usr/lib/*,tests/*'\""
                    def exitCode = bat(script: command, returnStatus: true)

                    if (exitCode == 0) {
                        echo 'Tests executed successfully.'
                    } else {
                        currentBuild.result = 'FAILURE'
                        error 'Failed to execute tests.'
                    }
                }
            }
        }
        
        stage('flake8') {
            steps {
                script {
                    def command = "docker exec hide-server /bin/sh -c \"flake8 --count --max-line-length=80 /hide\""
                    def exitCode = bat(script: command, returnStatus: true)

                    if (exitCode == 0) {
                        echo 'Tests executed successfully.'
                    } else {
                        currentBuild.result = 'FAILURE'
                        error 'Failed to execute tests.'
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
