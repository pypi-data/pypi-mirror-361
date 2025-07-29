#!/bin/sh

set -e 

VERSION=$(grep "version" pyproject.toml | cut -d '"' -f 2)

echo "Releasing pons_dtn version $VERSION"
echo "======================================="
echo "Make sure you have updated the version number in pyproject.toml"
echo 
echo "Press any key to continue"
read

python3 -m build

git add pyproject.toml
git commit -m "Release $VERSION"
git tag $VERSION
git push
git push --tags

twine upload dist/pons_dtn-$VERSION*
