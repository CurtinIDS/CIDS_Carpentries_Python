#!/bin/sh

# Redirect output to stderr.
exec 1>&2

# Clear outputs from all staged Jupyter notebooks
for notebook in $(git diff --cached --name-only | grep '\.ipynb$')
do
    if [ -f "$notebook" ]; then # only run if notebook exists, i.e. hasnt been git rmd
        jupyter nbconvert --to notebook --ClearOutputPreprocessor.enabled=True --inplace "$notebook"
        git add "$notebook"
    fi
done

exit 0