"""Version information for this package."""

### IMPORTS
### ============================================================================
## Standard Library

## Installed

## Application

### CONSTANTS
### ============================================================================
## Version Information - DO NOT EDIT
## -----------------------------------------------------------------------------
# These variables will be set during the build process. Do not attempt to edit.
PACKAGE_VERSION = "3.0.0"
BUILD_VERSION = "3.0.0"
BUILD_GIT_HASH = "61c9ba3d8b7efb0fc22fa43d012c8f7973ef87a8"
BUILD_GIT_HASH_SHORT = "61c9ba3"
BUILD_GIT_BRANCH = "main"
BUILD_TIMESTAMP = 1752242353
BUILD_DATETIME = datetime.datetime.utcfromtimestamp(1752242353)

## Version Information Strings
## -----------------------------------------------------------------------------
VERSION_INFO_SHORT = f"{BUILD_VERSION}"
VERSION_INFO = f"{PACKAGE_VERSION} ({BUILD_VERSION})"
VERSION_INFO_LONG = (
    f"{PACKAGE_VERSION} ({BUILD_VERSION}) ({BUILD_GIT_BRANCH}@{BUILD_GIT_HASH_SHORT})"
)
VERSION_INFO_FULL = (
    f"{PACKAGE_VERSION} ({BUILD_VERSION})\n"
    f"{BUILD_GIT_BRANCH}@{BUILD_GIT_HASH}\n"
    f"Built: {BUILD_DATETIME}"
)
