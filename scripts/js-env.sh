#!/bin/bash -ex

export STATIC_DIR=${STATIC_DIR:-src/faros_config/ui/static}

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

while [ $# -gt 0 ]; do
    case "$1" in
        *.js)
            cp "$1" $STATIC_DIR/js/ ;;
        *.css)
            cp "$1" $STATIC_DIR/css/ ;;
        *.eot|*.svg|*.ttf|*.woff|*.woff2)
            cp "$1" $STATIC_DIR/fonts/ ;;
        *)
            { set +x ; } &>/dev/null
            echo "Unable to identify '$1'" >&2
            exit 1 ;;
    esac; shift
done
