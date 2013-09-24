### PAKE REST API structure


Main point (will be referred to as `[POINT]` form now on):

    http://pake.example.com


Mirrors, metadata, aliens:

    [POINT]/mirrors.json
    [POINT]/meta.json
    [POINT]/aliens.json


Provided packages and their data:

    [POINT]/packages.json                   - list of all packages
    [POINT]/packages/:name                  - main point for a package
    [POINT]/packages/:name/meta.json        - metadata about the package
    [POINT]/packages/:name/releases.json    - list of provided versions of the package

`[POINT]/packages.json` file is built every time upload is done from metadata of all nests.

Files which are provided for single package entry:

    [POINT]/packages/:name/releases/:release.json
    [POINT]/packages/:name/releases/:release.tar.xz
    [POINT]/packages/:name/releases/:release.asc
