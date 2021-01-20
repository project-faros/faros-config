#!/bin/bash -ex

cd "$(dirname "$(realpath "$0")")/.."

export STATIC_DIR=${STATIC_DIR:-src/faros_config/ui/static}
export STATIC_ASSETS="$(cat static-assets.txt)"

if ! command -v yarn; then
    if [ "$VIRTUAL_ENV" ]; then
        # install it with nodeenv
        pip install nodeenv
        nodeenv --python-virtualenv
        npm install -g --no-package-lock --no-save yarn
    else
        { set +x ; } &>/dev/null
        echo 'Unable to find "yarn" in your $PATH.' >&2
        exit 1
    fi
fi

yarn install

for asset in ${STATIC_ASSETS}; do
    case $asset in
        *.js)
            cp $asset $STATIC_DIR/js/ ;;
        *.css)
            cp $asset $STATIC_DIR/css/ ;;
        *.eot|*.svg|*.ttf|*.woff|*.woff2)
            cp $asset $STATIC_DIR/fonts/ ;;
        *)
            { set +x ; } &>/dev/null
            echo "Unable to identify '$asset'" >&2
            exit 1 ;;
    esac
done
