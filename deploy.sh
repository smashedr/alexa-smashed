#!/usr/bin/env bash

set -e

## settings

FUNCTION_NAME="alexaSmashed"
APP_DIR="app"
PKG_DIR="package"
ZIP_FILE="${PKG_DIR}.zip"
REQUIREMENTS="requirements.txt"
ENVIRONMENT="settings.env"

## cleanup

echo "Removing and remaking directory: ${PKG_DIR}"
rm -rf "${PKG_DIR}"
mkdir "${PKG_DIR}"

if [[ -f "${REQUIREMENTS}" ]];then
    echo "Removing archive: ${ZIP_FILE}"
    rm -f "${ZIP_FILE}"
fi

## setup

if [[ -f "${REQUIREMENTS}" ]];then
    echo "Installing requirements from: ${REQUIREMENTS}"
    python3 -m pip install -r "${REQUIREMENTS}" --target "${PKG_DIR}"
fi

echo "Copying app from: ${APP_DIR}"
cp -r "${APP_DIR}"/. "${PKG_DIR}"
cd "${PKG_DIR}"
echo "Creating archive: ${ZIP_FILE}"
zip -r ../"${ZIP_FILE}" ./
cd -
rm -rf "${PKG_DIR}"

set +e

## update

aws lambda update-function-code \
    --function-name "${FUNCTION_NAME}" \
    --zip-file fileb://"${ZIP_FILE}"

ST="$?"
if [[ "${ST}" != "0" ]];then
    echo "Error deploying function code: ${FUNCTION_NAME}"
    exit "${ST}"
else
    echo "Successfully deployed function code: ${FUNCTION_NAME}"
fi

#set -e
#
#if [[ -f "${ENVIRONMENT}" ]];then
#    echo "Updating environment variables from: ${ENVIRONMENT}"
#    AWS_ENV=""
#    aws lambda update-function-configuration \
#        --function-name "${FUNCTION_NAME}" \
#        --environment  "${AWS_ENV}"
#fi
#
#ST="$?"
#if [[ "${ST}" != "0" ]];then
#    echo "Error deploying function configuration: ${FUNCTION_NAME}"
#    exit "${ST}"
#else
#    echo "Successfully deployed function configuration: ${FUNCTION_NAME}"
#fi
