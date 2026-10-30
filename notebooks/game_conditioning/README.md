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

7. [Step 7: Extend post-load attachment to a tiny full DiT](27_full_dit_postload_adapter.ipynb)
   - Strict-loads a synthetic base state on the meta device, reconstructs only non-persistent buffers, then attaches branches to every fused block.
   - Saves/restores the adapter sidecar and checks audio-only plus video+audio paths.
   - CPU-sized random model; no pretrained checkpoint, training, or audio generation.

8. [Step 8: Pass Game→Audio tokens through PiFlow](28_piflow_sampler_game_conditioning.ipynb)
   - Adds optional game-token and mask arguments to a scratch copy of Kandinsky's pinned PiFlow sampler.
   - Runs two short sampler steps with a tiny random DiT and synthetic video/audio latent bundle.
   - Confirms the sampler forwards the condition on each step and that the open demo gate changes the audio latent.
   - CPU-sized; no pretrained weights, training, or WAV generation.

9. [Step 9: Wire event tokens through the public pipeline API](29_pipeline_game_api_wiring.ipynb)
   - Adds optional `game_tokens` and `game_attn_mask` inputs to a scratch copy of the pipeline.
   - Routes them through both Euler and PiFlow sampler paths into the DiT.
   - Performs a pinned-source static wiring and syntax audit only.
   - No pipeline execution, pretrained weights, training, or audio decoding.

10. [Step 10: Smoke-test the real Lite checkpoint and pipeline API](30_real_lite_checkpoint_game_api_smoke.ipynb)
   - Strict-loads the pinned Lite Distill checkpoint, attaches a zero-gated untrained adapter, and sends placeholder game tokens through a five-second video→audio pipeline call.
   - Pins source commit `7ceeefad7fb625011f7db602c43893a989f19c15` and checkpoint revision `4c487e8b4aeeb9059e5a77905aa2ddb59ec28f81`.
   - Requires an A100 80 GB runtime and about 30 GB free disk; the checkpoint snapshot is about 26.64 GB.
   - Compatibility test only: no training, semantic event encoding, learned control, or quality claim.

## Current status

Steps 1–4 are architecture prototypes; Step 5 maps checkpoint and pipeline boundaries. Step 6 validates post-load sidecar attachment on one fused block, and Step 7 extends the lifecycle to a tiny full DiT. The user reports Steps 7, 8, and 9 passed. Step 8 verified PiFlow forwarding and a numerical change in synthetic audio latents. Step 9 verified the source-level public API route through both Euler and PiFlow. Neither establishes learned control or audio quality. No official Kandinsky source file has been changed.

Step 10 is prepared but not yet run: it attempts one real five-second video→audio call with the pinned Lite Distill checkpoint and a zero-gated adapter. A successful run will prove strict checkpoint compatibility and pipeline execution with the new API, but the placeholder event vector is intentionally ignored. Training still requires a defined event encoder contract and paired game-event/audio examples.

## Licensing notes

The source-derived scratch patches in Steps 8–10 carry an upstream MIT notice preserved in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The Lite Distill model card declares MIT; this does not establish licenses for every bundled third-party component, training source, or generated output.

## Source

The inspected source revision is pinned to [Kandinsky 6 commit 7ceeefad7fb625011f7db602c43893a989f19c15](https://github.com/kandinskylab/kandinsky-6/tree/7ceeefad7fb625011f7db602c43893a989f19c15).
