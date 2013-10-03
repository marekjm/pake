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


Cached packages (only packages which are not originated from this node, only archives).
Cache does not provide metadata but MUST provide signatures (if a signature for an archive cannot be found it
is considered insecure).

    [POINT]/cache.json         - list of cached archives (`foo-0.0.1.tar.xz`)
    [POINT]/cache/:file
