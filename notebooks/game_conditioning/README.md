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

## Current status

These are architecture prototypes, not a trained or integrated model. The next step is to patch a local copy of the pinned Kandinsky block so the game branch runs both with and without video, then inspect checkpoint compatibility. Training will require paired game-event conditions and target audio.

## Source

The inspected source revision is pinned to [Kandinsky 6 commit 7ceeefad7fb625011f7db602c43893a989f19c15](https://github.com/kandinskylab/kandinsky-6/tree/7ceeefad7fb625011f7db602c43893a989f19c15).
