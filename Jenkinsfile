// =====================================================================
// Examen Final - Sécurité des Données (L3 Cybersécurité)
// Pipeline DevSecOps - OWASP Juice Shop
// Auteur : Fatou Bintou Gaye
// =====================================================================
// Contrôles intégrés : SAST (Semgrep) | SCA (npm audit + Trivy)
//                      Secret Detection (Gitleaks) | DAST (OWASP ZAP)
//
// Dépôt AUTONOME : ce dépôt contient le Jenkinsfile, security-config/,
// scripts/, remediation/, reports/ et screenshots/. L'application cible
// OWASP Juice Shop est clonée automatiquement dans ./app à l'étape 1.
// =====================================================================

def runCmd(String cmd) {
    if (isUnix()) { sh cmd } else { bat cmd }
}

pipeline {
    agent any

    tools {
        nodejs 'Node20'
    }

    environment {
        APP_NAME        = 'juice-shop'
        APP_PORT        = '3000'
        APP_URL         = "http://host.docker.internal:3000"
        REPORT_DIR      = 'reports'
        APP_DIR         = 'app'
        // Application cible clonée à l'étape 1 (dépôt public, pas de credential)
        JUICE_REPO      = 'https://github.com/juice-shop/juice-shop.git'
        JUICE_BRANCH    = 'master'
        // Seuils du quality gate
        MAX_CRITICAL    = '0'
        MAX_HIGH        = '5'
        NOTIFY_EMAIL    = 'fatoubinetou.gaye@unchk.edu.sn'
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timeout(time: 60, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        // ---------------------------------------------------------
        // ETAPE 1 : CHECKOUT
        // ---------------------------------------------------------
        stage('1. Checkout') {
            steps {
                echo '=== Récupération du dépôt d\'examen (Jenkinsfile, security-config, scripts) ==='
                checkout scm

                echo '=== Clonage de l\'application cible OWASP Juice Shop dans ./app ==='
                script {
                    if (isUnix()) {
                        sh "rm -rf ${APP_DIR}; git clone --depth 1 --branch ${JUICE_BRANCH} ${JUICE_REPO} ${APP_DIR}"
                    } else {
                        bat """
                            if exist ${APP_DIR} rmdir /s /q ${APP_DIR}
                            git clone --depth 1 --branch ${JUICE_BRANCH} ${JUICE_REPO} ${APP_DIR}
                        """
                    }
                    env.GIT_SHA = isUnix()
                        ? sh(script: "cd ${APP_DIR} && git rev-parse --short HEAD", returnStdout: true).trim()
                        : bat(script: "@cd ${APP_DIR} && git rev-parse --short HEAD", returnStdout: true).trim()
                }
                echo "Commit Juice Shop analysé : ${env.GIT_SHA}"
            }
        }

        // ---------------------------------------------------------
        // ETAPE 2 : BUILD / PREPARATION
        // ---------------------------------------------------------
        stage('2. Build / Preparation') {
            steps {
                echo '=== Préparation de l\'environnement d\'analyse ==='
                script {
                    if (isUnix()) {
                        sh """
                            mkdir -p ${REPORT_DIR}
                            node --version && npm --version
                            cd ${APP_DIR} && npm install --legacy-peer-deps --ignore-scripts --no-audit --no-fund
                        """
                    } else {
                        bat """
                            if not exist ${REPORT_DIR} mkdir ${REPORT_DIR}
                            node --version && npm --version
                            cd ${APP_DIR} && npm install --legacy-peer-deps --ignore-scripts --no-audit --no-fund
                        """
                    }
                }
                // Lancement de l'application (cible du DAST)
                script {
                    runCmd "docker rm -f ${APP_NAME}-dast || exit 0"
                    runCmd "docker run -d --name ${APP_NAME}-dast -p ${APP_PORT}:3000 bkimminich/juice-shop:latest"
                }
                echo 'Attente du démarrage de l\'application (45s)...'
                sleep(time: 45, unit: 'SECONDS')
            }
        }

        // ---------------------------------------------------------
        // ETAPE 3 : SECURITY ANALYSIS  (SAST + SCA en parallèle)
        // ---------------------------------------------------------
        stage('3. Security Analysis') {
            parallel {

                stage('SAST - Semgrep') {
                    steps {
                        echo '=== Analyse statique du code source (Semgrep) ==='
                        script {
                            runCmd """docker run --rm -v "${WORKSPACE}:/src" semgrep/semgrep:latest semgrep scan --config=p/javascript --config=p/typescript --config=p/owasp-top-ten --config=/src/security-config/semgrep-rules.yml --json --output=/src/${REPORT_DIR}/semgrep-report.json --metrics=off /src/${APP_DIR} || exit 0"""
                        }
                    }
                }

                stage('SCA - npm audit + Trivy') {
                    steps {
                        echo '=== Analyse des dépendances (SCA) ==='
                        script {
                            // npm audit : rapport JSON + rapport lisible (exécuté dans ./app)
                            if (isUnix()) {
                                sh "cd ${APP_DIR} && npm audit --json > ../${REPORT_DIR}/npm-audit-report.json || exit 0"
                                sh "cd ${APP_DIR} && npm audit > ../${REPORT_DIR}/npm-audit-report.txt || exit 0"
                            } else {
                                bat "cd ${APP_DIR} && npm audit --json > ..\\${REPORT_DIR}\\npm-audit-report.json || exit 0"
                                bat "cd ${APP_DIR} && npm audit > ..\\${REPORT_DIR}\\npm-audit-report.txt || exit 0"
                            }
                            // Trivy : analyse du système de fichiers + CVE des dépendances de ./app
                            runCmd """docker run --rm -v "${WORKSPACE}:/src" aquasec/trivy:latest fs --scanners vuln,misconfig --format json --output /src/${REPORT_DIR}/trivy-report.json /src/${APP_DIR} || exit 0"""
                        }
                    }
                }
            }
        }

        // ---------------------------------------------------------
        // ETAPE 4 : ADDITIONAL SECURITY CHECK (Secrets + DAST)
        // ---------------------------------------------------------
        stage('4. Additional Security Check') {
            parallel {

                stage('Secret Detection - Gitleaks') {
                    steps {
                        echo '=== Détection de secrets exposés (Gitleaks) ==='
                        script {
                            runCmd """docker run --rm -v "${WORKSPACE}:/repo" zricethezav/gitleaks:latest detect --source=/repo/${APP_DIR} --config=/repo/security-config/gitleaks.toml --report-format=json --report-path=/repo/${REPORT_DIR}/gitleaks-report.json --redact --no-git || exit 0"""
                        }
                    }
                }

                stage('DAST - OWASP ZAP') {
                    steps {
                        echo '=== Analyse dynamique de l\'application (OWASP ZAP) ==='
                        script {
                            // La conf ZAP doit être visible depuis /zap/wrk (= reports/)
                            runCmd(isUnix()
                                ? "cp security-config/zap-baseline.conf ${REPORT_DIR}/ || exit 0"
                                : "copy security-config\\zap-baseline.conf ${REPORT_DIR}\\ || exit 0")
                            runCmd """docker run --rm --add-host=host.docker.internal:host-gateway -v "${WORKSPACE}/${REPORT_DIR}:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t ${APP_URL} -c zap-baseline.conf -J zap-report.json -r zap-report.html -I || exit 0"""
                        }
                    }
                }
            }
        }

        // ---------------------------------------------------------
        // ETAPE 5 : REPORT GENERATION
        // ---------------------------------------------------------
        stage('5. Report Generation') {
            steps {
                echo '=== Consolidation des rapports de sécurité ==='
                script {
                    runCmd "python scripts/aggregate-reports.py --input ${REPORT_DIR} --output ${REPORT_DIR} --build ${BUILD_NUMBER} --commit ${env.GIT_SHA}"
                }

                archiveArtifacts artifacts: "${REPORT_DIR}/**/*", allowEmptyArchive: true, fingerprint: true

                publishHTML(target: [
                    allowMissing         : true,
                    alwaysLinkToLastBuild: true,
                    keepAll              : true,
                    reportDir            : "${REPORT_DIR}",
                    reportFiles          : 'security-summary.html',
                    reportName           : 'Rapport de sécurité consolidé'
                ])
            }
        }

        // ---------------------------------------------------------
        // ETAPE 5bis : QUALITY GATE (décision de déploiement)
        // ---------------------------------------------------------
        stage('Quality Gate') {
            steps {
                echo '=== Application de la politique de sécurité ==='
                script {
                    def status = isUnix()
                        ? sh(script: "python scripts/quality-gate.py --report ${REPORT_DIR}/security-summary.json --max-critical ${MAX_CRITICAL} --max-high ${MAX_HIGH}", returnStatus: true)
                        : bat(script: "python scripts/quality-gate.py --report ${REPORT_DIR}/security-summary.json --max-critical ${MAX_CRITICAL} --max-high ${MAX_HIGH}", returnStatus: true)

                    if (status != 0) {
                        env.DEPLOY_DECISION = 'REJECT DEPLOYMENT'
                        currentBuild.result = 'FAILURE'
                        error("Quality gate échoué : seuils de vulnérabilités dépassés. Déploiement bloqué.")
                    } else {
                        env.DEPLOY_DECISION = 'ACCEPT DEPLOYMENT'
                    }
                }
            }
        }
    }

    // ---------------------------------------------------------
    // ETAPE 6 : NOTIFICATION
    // ---------------------------------------------------------
    post {
        always {
            echo '=== Nettoyage de l\'environnement ==='
            script {
                runCmd "docker rm -f ${APP_NAME}-dast || exit 0"
            }

            emailext(
                to: "${NOTIFY_EMAIL}",
                subject: "[${currentBuild.currentResult}] ${JOB_NAME} #${BUILD_NUMBER} - Analyse de sécurité Juice Shop",
                mimeType: 'text/html',
                body: """
                    <h2>Rapport d'analyse de sécurité automatisée</h2>
                    <ul>
                        <li><b>Projet :</b> ${JOB_NAME}</li>
                        <li><b>Build :</b> #${BUILD_NUMBER}</li>
                        <li><b>Commit :</b> ${env.GIT_SHA}</li>
                        <li><b>Résultat :</b> ${currentBuild.currentResult}</li>
                        <li><b>Décision de déploiement :</b> ${env.DEPLOY_DECISION ?: 'REJECT DEPLOYMENT'}</li>
                    </ul>
                    <p>Contrôles exécutés : SAST (Semgrep), SCA (npm audit + Trivy),
                       Secret Detection (Gitleaks), DAST (OWASP ZAP).</p>
                    <p>Console : <a href="${BUILD_URL}console">${BUILD_URL}console</a></p>
                """,
                attachmentsPattern: "${REPORT_DIR}/security-summary.html,${REPORT_DIR}/npm-audit-report.txt"
            )
        }
        failure {
            echo 'DÉCISION : REJECT DEPLOYMENT - vulnérabilités bloquantes détectées.'
        }
        success {
            echo 'DÉCISION : ACCEPT DEPLOYMENT - seuils de sécurité respectés.'
        }
    }
}
