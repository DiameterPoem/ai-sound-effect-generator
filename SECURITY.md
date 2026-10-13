# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.9.x   | yes       |
| 0.8.x   | security fixes only |
| < 0.8   | no        |

## Threat model

`ai-sound-effect-generator` loads third-party plugins from the local
filesystem and (optionally) from user-provided plugin directories. Plugins
run in-process with full user privileges. We treat this as a trust
boundary the same way a DAW treats VSTs.

Known risks we care about:

- **Malicious plugin**: a plugin can read/write files, open sockets, spawn
  processes. Only install plugins you trust.
- **Model file deserialization**: we load `.safetensors` by default.
  `.pt` / `.ckpt` loading is gated behind `SFXGEN_ALLOW_PICKLE=1` and
  logs a loud warning.
- **Path traversal in sample packs**: sample pack loaders must resolve
  paths via `sfxgen.utils.paths.safe_join` — never raw `os.path.join`
  on untrusted input.
- **Prompt injection into the model cache**: prompts are used as cache
  keys after a stable hash; they are never `eval`'d and never written to
  disk verbatim.

## Reporting a vulnerability

Email `security@sfxlab.tools` with a description, a minimal repro (prompt
or plugin), and the version. We aim to acknowledge within 72 hours and
ship a fix or mitigation within 14 days for confirmed issues.

Do not open a public issue for anything exploitable.

## Plugin sandboxing (roadmap)

We are evaluating a subprocess + pipe-based plugin runtime for 1.0. Until
then, the rule is: **plugins are code, treat them like code.**