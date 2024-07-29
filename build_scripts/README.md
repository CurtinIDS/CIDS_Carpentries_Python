# Build Scripts Folder

This is a folder to quickly build things for the workshop repo

## Workshop attendees
If you are a workshop attendee, you can safely ignore this entire directory. It is only for instructors

## Instructors

This folder may host many scripts. Two examples are:
- strip_notebooks.sh
- colab_nb_builder.py

The first script clears notebooks, and the second builds gooogle colab compatible versions of notebooks.

There is also a file 'pre-commit' which can be copied to `.git/hooks/pre-commit` and made executable (`chmod +x .git/hooks/pre-commit`) to automatically run before at every commit. If you add a script, you may want to also modify the `pre-commit` file.

