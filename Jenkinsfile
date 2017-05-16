#!/usr/bin/env groovy
@Library('github.com/msrb/cicd-pipeline-helpers') _

node('docker') {

    stage('Checkout') {
        checkout scm
    }

    if (env.BRANCH_NAME == 'master') {
        stage('make') {
            sh "./make_rpm.sh --source"
        }
        stage('push to copr') {
            sh "copr-cli build jpopelka/license-check ~/rpmbuild/SRPMS/license-check-*.src.rpm"
        }
    }
}
