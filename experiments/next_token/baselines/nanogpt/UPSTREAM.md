# Vendored model source

`model.py` and `LICENSE` are unmodified files from Andrej Karpathy's nanoGPT,
commit `3adf61e154c3fe3fca428ad6bc3818b27a3b8291`:

- https://github.com/karpathy/nanoGPT/blob/3adf61e154c3fe3fca428ad6bc3818b27a3b8291/model.py
- https://github.com/karpathy/nanoGPT/blob/3adf61e154c3fe3fca428ad6bc3818b27a3b8291/LICENSE

The adjacent FP comparison adapter initializes this architecture from scratch.
It does not call the upstream pretrained-weight loader or training script.
The adapter uses exactly V output rows and one additional input-only PAD row;
its contexts and loss conventions are documented in `../TRANSFORMER.md`.
This pins a reproducible standard Transformer implementation, not a claim
that a particular size or training budget is already a competitive baseline.
