#!/bin/bash

# Exit if any of the intermediate steps fail
set -e

# Extract "foo" and "baz" arguments from the input into
# FOO and BAZ shell variables.
# jq will ensure that the values are properly quoted
# and escaped for consumption by the shell.
eval "$(jq -r '@sh "REGION=\(.region)"')"

BUILD_ID=$(aws codebuild start-build --region=$REGION --project-name=validator-notifier | jq '.build.id')
BUILD_PHASE=$(aws codebuild batch-get-builds --region=$REGION --ids=$BUILD_ID | jq '.builds[0].currentPhase')

# Safely produce a JSON object containing the result value.
# jq will ensure that the value is properly quoted
# and escaped to produce a valid JSON string.
jq -n --arg build_id "$BUILD_ID" '{"build_id":$build_id}'
