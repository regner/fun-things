# Prototype archive

This directory contains foundation-spike fixtures, runners, helper tests, and spike-only art that
are useful as implementation references but are no longer part of the Godot project. The empty
`.gdignore` at this directory root prevents Godot from scanning or importing the entire archive,
and production export presets exclude `prototypes/**` explicitly.

Content is grouped by spike ID. Within each spike directory, repository-relative subtrees such as
`tests/fixtures/`, `tools/`, and `art/` preserve the old layout. Shared helpers used by several
spikes are under `shared/`. Files may still contain historical `res://tests/fixtures/...`,
`res://tools/...`, or `res://art/...` paths. Those paths document the original runnable checkout;
this archive is reference-only and is not runnable in place.

The archive was moved from pre-cleanup commit `66400c26a01bf917dfe631af4762c2b444d9c48f`.
To inspect one original file without changing the working tree, run:

```sh
git show 66400c26a01bf917dfe631af4762c2b444d9c48f:<path>
```

To run a complete old prototype, use a separate worktree or temporary checkout at that commit. Do
not restore prototype files into production directories merely to make an old receipt runnable.
