pipeline {
    agent any

    stages {
        stage('tests') {
            steps {
                script {
                    def command = "docker exec hide /bin/sh -c \"cd /hide && python3 -W ignore -m coverage run -m unittest discover -s ./tests -p '*_tests.py'\""
                    def exitCode = bat(script: command, returnStatus: true)
                    
                    if (exitCode == 0) {
                        command = "docker exec hide /bin/sh -c \"cd /hide && python3 -m coverage report --omit '/usr/lib/*,tests/*'\""
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
                    def command = 'docker exec hide /bin/sh -c "pip3 install --upgrade safety"'
                    def exitCode = bat(script: command, returnStatus: true)

                    if (exitCode == 0) {
                        command = 'docker exec hide /bin/sh -c "safety check --file /hide/requirements.txt --ignore 50959 --ignore 70612 --ignore 72132"'
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

        stage('linter') {
            steps {
                script {
                    def command = 'docker exec hide /bin/sh -c "flake8 --count --max-line-length=80 /hide"'
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
                    def command = 'docker exec hide-smokes /bin/sh -c "behave /smokes/app/features/*.feature --no-capture --format progress"'
                    def exitCode = bat(script: command, returnStatus: true)

                    if (exitCode != 0) {
                        currentBuild.result = 'FAILURE'
                        error 'Smokes failed.'
                    }
                }
            }
        }

        stage('docs') {
            steps {
                script {
                    def command = 'docker exec hide /bin/sh -c "sphinx-apidoc --remove-old --output-dir /hide/docs/autodoc /hide/app/ && make -C /hide/docs html"'
                    def exitCode = bat(script: command, returnStatus: true)

                    if (exitCode != 0) {
                        currentBuild.result = 'FAILURE'
                        error 'Sphinx failed.'
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
