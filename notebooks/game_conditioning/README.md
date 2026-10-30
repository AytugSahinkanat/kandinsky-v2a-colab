# Game-Conditioned Kandinsky Architecture Study

A focused architecture track for exploring how structured game-event tokens could condition Kandinsky's audio stream.

## Notebooks

1. [Step 1: Inspect Kandinsky and define the event-token demonstration](21_game_audio_cross_attention_step1.ipynb)
   - Inspects the pinned Kandinsky 6 source revision.
   - Demonstrates a typed event-token layout.
   - Does not download weights, train, or generate audio.

2. [Step 2: Prototype a Game-to-Audio attention branch](22_game_audio_cross_attention_step2.ipynb)
   - Inspects the audio-only and video-plus-audio paths.
   - Demonstrates the tensor interface for a separate Game-to-Audio branch, including a residual gate and key mask.
   - Does not patch Kandinsky, load weights, train, or generate audio.

3. [Step 3: Patch and dry-run Kandinsky's real fused block](23_game_audio_cross_attention_step3.ipynb)
   - Applies a reversible source patch to a scratch copy of the pinned FusedTransformerDecoderBlock.
   - Checks audio-only and video-plus-audio calls, zero-gate parity, Game→Audio influence, and padded-token masking.
   - Uses small random tensors; does not download model weights, train, or generate audio.
   - Validates the block only, not the full model or pipeline.

4. [Step 4: Thread game tokens through the full DiT](24_game_audio_cross_attention_step4.ipynb)
   - Extends the scratch patch through DiffusionTransformer3D.forward and both audio-only and fused video+audio block loops.
   - Checks tiny-model state-dict compatibility, zero-gate parity, dtype conversion, and event-token masking.
   - Uses a randomly initialized model; does not load pretrained weights, train, or generate audio.

5. [Step 5: Audit checkpoint loading and pipeline boundaries](25_checkpoint_pipeline_audit.ipynb)
   - Reads the pinned factory, checkpoint loader, public pipeline, and both sampler paths.
   - Confirms the official loader's strict meta-device path and identifies where a game condition is not yet forwarded.
   - Read-only: does not patch code, download weights, train, or generate audio.

6. [Step 6: Prototype post-load adapter attachment](26_postload_adapter_prototype.ipynb)
   - Strict-loads a synthetic base state into a real Kandinsky fused block before attaching Game→Audio modules.
   - Saves and restores only the new branch as a sidecar adapter; checks that base weights remain unchanged.
   - Uses a tiny random block; no pretrained weights, training, or audio generation.

## Current status

Steps 1–4 are architecture prototypes; Step 5 maps checkpoint and pipeline boundaries. Step 6 tests post-load attachment and sidecar serialization at the fused-block level. These steps do not demonstrate useful learned control or audible quality, and Step 6 is not yet full-model or factory integration.

If Step 6 passes, the next work is to extend the same attachment pattern across a tiny full DiT, then wire one sampler path. Training will require paired game-event conditions and target audio.

## Source

The inspected source revision is pinned to [Kandinsky 6 commit 7ceeefad7fb625011f7db602c43893a989f19c15](https://github.com/kandinskylab/kandinsky-6/tree/7ceeefad7fb625011f7db602c43893a989f19c15).
