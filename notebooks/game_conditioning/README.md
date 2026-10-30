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
   - This validates only the block, not the full model or pipeline.

## Current status

Steps 1–3 are architecture prototypes, not a trained or end-to-end integrated model. Step 3 verifies that a gated Game→Audio branch can run inside Kandinsky's actual fused block with and without video. The next step is to propagate optional game tokens and their mask through DiffusionTransformer3D and its block loops, then inspect checkpoint loading. Training will require paired game-event conditions and target audio.

## Source

The inspected source revision is pinned to [Kandinsky 6 commit 7ceeefad7fb625011f7db602c43893a989f19c15](https://github.com/kandinskylab/kandinsky-6/tree/7ceeefad7fb625011f7db602c43893a989f19c15).
