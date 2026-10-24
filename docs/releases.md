# SDK Releases

Independent release procedures for the Python distribution and Go module. These commands publish externally; run them only after review and authorization. No initial release is assumed to exist.

---

## Table of Contents

- [Before releasing](#before-releasing)
- [Python release](#python-release)
- [Go release](#go-release)
- [Failures and withdrawal](#failures-and-withdrawal)

---

## Before releasing

- Select the license before third-party distribution; do not assume the checkout grants reuse rights.
- Merge the intended changes and verify CI on `main`. Select a reviewed commit, verify `origin`, and ensure the tree is clean before tagging.
- Tags are stable `MAJOR.MINOR.PATCH` versions with no leading zeros. Prereleases and build metadata are intentionally not supported by the initial release guard.
- Run `python3 scripts/check_release.py TAG` from the repository root, replacing `TAG` with the intended tag. It rejects malformed tags, Python metadata mismatches, incorrect Go module paths, and Go major versions needing migration.
- Release workflows verify that the tagged commit is an ancestor of `origin/main`, rerun the language checks, and use a separate publishing job with write permission. CI checkouts do not persist credentials.
- GitHub generates release notes from repository history, which can include changes to either language. Review and edit the resulting notes for the package being released; generated notes do not replace compatibility/migration explanations. Releases do not automatically take over the repository's shared "latest" designation.

---

## Python release

Set the intended version in `python/pyproject.toml`, refresh the lock with `uv lock` from `python/`, and commit those changes through review. After checks pass, the following example publishes the **first** `0.1.0` tag at an explicitly selected commit:

```sh
python3 scripts/check_release.py python/v0.1.0
git tag -a python/v0.1.0 "<reviewed-commit>" -m "Python SDK 0.1.0"
git push origin refs/tags/python/v0.1.0
```

Replace `<reviewed-commit>` before execution. For later releases, change both the version and tag; never recreate a published version.

The workflow builds a wheel and source distribution, installs/checks both in clean environments, and attaches them to a GitHub release. It does not publish to PyPI. Consumers may install a reviewed wheel or pin the Git source with `#subdirectory=python`; see [Python installation](../python/README.md#installation).

---

## Go release

Go versions are derived from tags, independently of Python metadata. After checks pass, publish the first version using:

```sh
python3 scripts/check_release.py go/v0.1.0
git tag -a go/v0.1.0 "<reviewed-commit>" -m "Go SDK 0.1.0"
git push origin refs/tags/go/v0.1.0
```

The workflow checks the module and creates a GitHub source-release entry, not a binary. The `go/` tag prefix is required for this subdirectory module; see [Go version tags](https://go.dev/ref/mod#vcs-version). Consumers request `@v0.1.0` at the module path, not `@go/v0.1.0`.

Before v2, explicitly plan the `/v2` module/import-path migration and update the release guard and documentation. Do not bypass the guard just to make a release succeed.

---

## Failures and withdrawal

If checks or artifact building fail before publication, correct the problem in a new reviewed version rather than moving a shared tag. If publication fails before a GitHub release exists, a maintainer can rerun the workflow after investigating. Existing release entries are not overwritten by these workflows.

Deleting a GitHub release does not delete its tag, installed packages, or cached Go module versions. Prefer a corrected release with clear notes; use ecosystem retraction/withdrawal mechanisms when applicable. Consumers still need to adopt and test the update.
