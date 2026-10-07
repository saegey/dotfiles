#!/bin/bash

set -eo pipefail

SCRIPTDIR=$(cd "$(dirname "$0")" && pwd)
"$SCRIPTDIR/bootstrap.generic.sh" "$@"
