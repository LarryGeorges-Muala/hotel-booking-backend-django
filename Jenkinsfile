pipeline {
    agent any
    stages {
        stage('Trivy') {
            when {
                changeRequest() 
            }
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    retry(2) {
                        sh '''
                            apt update && apt install -y gnupg curl wget unzip ca-certificates
                            wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | tee /usr/share/keyrings/trivy.gpg > /dev/null
                            echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | tee -a /etc/apt/sources.list.d/trivy.list
                            apt-get update
                            apt-get install trivy -y
                            trivy fs /app --include-dev-deps --dependency-tree
                        '''
                    }
                }
            }
        }
        stage('SBOM - Syft/Grype') {
            when {
                changeRequest() 
            }
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    retry(2) {
                        sh '''
                            apt update && apt install -y gnupg curl wget unzip ca-certificates
                            curl -sSfL https://get.anchore.io/syft | sh -s -- -b /usr/local/bin
                            curl -sSfL https://get.anchore.io/grype | sh -s -- -b /usr/local/bin
                            rm -rf /scans || true
                            mkdir /scans
                            syft /app -o cyclonedx-json=/scans/sbom.json
                            grype sbom:/scans/sbom.json
                        '''
                    }
                }
            }
        }
    }
}
