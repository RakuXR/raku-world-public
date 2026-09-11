# Scope

## What this repository publishes

- `video/rakuai-rakuworld-gtc.mp4` — the RakuAI / RakuWorld NVIDIA GTC showcase
  film, with `video/encode-manifest.json` describing the encode.
- `proof/` — the public evidence: `public-evidence.json` and the two showcase
  frames it hashes.
- `verify.py` and `recheck_offline.py` — offline verification of the published
  files and re-derivation of the published numbers, each with a self-test.
- `assets/` — the hero still and the social card used by the README.

## What is stated, and how

- **Observed:** the model identity and serving endpoint; the GPU rendering path
  (adapter read back from the created Direct3D 11 device); the target,
  tolerance, initial control error and final control error.
- **Derived:** the ~99.1% reduction in control error, computed from the initial
  and final error; `recheck_offline.py` recomputes it.
- **Not claimed:** GPU-accelerated physics (physics runs on the CPU); the
  hardware NVIDIA serves the model on; that the published closed-loop result was
  an MCP-transport run (it was measured in-process — MCP is a separate,
  distinct capability of the runtime).

## What is not published

- The proprietary RakuAI engine source and its compiled runtime binaries.
- The private measurement record (tool calls, intermediate measurements, model
  reasoning). Its SHA-256 is published in `proof/public-evidence.json` so the
  public numbers are bound to a specific record.
- Internal development scripts, reference material and working files.

## Reproducibility, stated precisely

Everything published can be re-hashed and every published number can be
re-derived offline. The capture itself cannot be re-executed by a third party
without the compiled runtime, an NVIDIA GPU with a Direct3D 11 driver, and
access to NVIDIA NIM. The showcase is offered as an auditable record.
