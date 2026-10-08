# Exact packaging and later source identities

This supplement resolves initial review R2 without replacing any old payload.
The complete pre-review manifest/payload dictionary and sources remain at exact
`bfa3253176896e3049db80d2d5e6acc595c8358b`, preserved by local evidence ref
`refs/paseo-evidence/s05-vsync-image-initial`. That ancestry also preserves executed
candidate `4a50808ba0441a7c116d14d78a4286a6f89f7691` through the final rebase.

The legacy path
`payloads/sources/corrected-offline/tools/s05_vsync_image/retain.py.gz` is the actual
**pre-storage-normalization generator snapshot**, not the current script. It is
7076 decoded bytes/SHA256
`77352b89dedbbb9f0cd91e713342b2f8c9e5f74fcf21b7781053abf50755dfb7`.
Its bytes, filename and original payload dictionary are preserved unchanged.
After the one packaging invocation, only archive storage labels changed from
`.godot/` to `generated-imports/`, keeping generated imports as gzip evidence rather
than a versioned live `.godot/` directory. Original source paths and payload bytes
remain exact in the manifest. The actual own tool-call/source/result for that
metadata transformation is retained in the final Git note; no historical command
stream or native lookup is reconstructed.

The candidate's later **source-only** `tools/s05_vsync_image/retain.py` adds that
storage-label remapping: 7182bytes/SHA256
`16cffd287ae2a17835148918b78ec0b291a8df8571d3ca6f794d1826df436d07`.
It was not another packaging invocation or runtime. The initial review retains the
exact two-source diff, its nonzero diff exit and archive assertion failures.

Other `corrected-offline/` snapshots are the pre-review endpoint-probe correction,
checker/tests/wrapper at the initial candidate; they are not automatically the
current post-review source. Later phase-budget/evaluator fixes are recorded in the
final Git source and review/check note. No archived executed source or historical
stream is rewritten, and no corrected source receives past runtime/image credit.
