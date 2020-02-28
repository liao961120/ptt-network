#!/usr/bin/env sh
make html

cd docs

git init
git add -A
git commit -m 'deploy'
git push -f https://github.com/liao961120/ptt-network.git master:gh-pages

cd -
