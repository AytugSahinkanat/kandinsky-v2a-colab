# Game-Conditioned Audio — Speed-Control Pilot Protocol

## Purpose

The video-conditioned Kandinsky baseline already produces usable, synchronized audio in the user's tests. The next experiment must establish incremental user control: whether a structured game event can change the generated impact in a predictable way while preserving event timing and acceptable sound quality.

This protocol does not claim that the current untrained adapter controls sound. It does not start recording, model training, or GPU work.

## First controllable variable

Use measured normal impact speed as the first variable. Keep the contact-material pair, moving-object mass, geometry, contact point, microphone chain, room, generic prompt, video framing, and all other fields fixed or explicitly recorded. Keep the mass fixed during the first A/B comparison; collect measured mass for every take.

Do not label speed as “intensity.” It is a physical input. Any user-facing intensity slider needs an explicit mapping to a physical speed range or a separate artistic control.

Record optional force impulse as validation evidence, not as a second independent control. Treat distance and room reverb as later renderer controls over a dry source.

## Required paired sample

Each example must include:

- A five-second video from the same event, with the event and tail visible.
- A synchronized, dry target WAV from that same event; no AGC, compression, limiter, or added reverb.
- Event time and audio onset on the same timeline.
- Contact materials, measured mass, measured normal relative speed, geometry/specimen ID, contact point, and the provenance/method for each measurement.
- Fixed microphone model, position, gain, sample rate, room profile, and any measured RT60.
- Per-file SHA-256 and written rights evidence for commercial generative model training, fine-tuning, and commercial use of resulting weights/service.
- The engine-native event payload when captured from a game engine. If captured in a physical rig, identify the rig and preserve raw sensor traces.

Use one fixed generic text prompt across the control comparison. Do not put material, speed, force, or intensity in the prompt.

## Pilot capture matrix

First ask for a small feasibility quote. A practical initial matrix is one fixed specimen/material pair × three safe, measured speed levels × repeated impacts. The recording provider must confirm whether the fixture can measure speed without materially changing the impact sound. The feasibility set validates the recording and rights pipeline; it is not enough to claim a general model has been trained.

If feasibility passes, expand the matrix across independent specimens and sessions. Split train/validation/test by specimen or capture session, never by adjacent crops from the same take.

## Model comparison after data audit

Run these conditions on held-out pairs, using the same source video, fixed prompt, and matched seeds where possible:

1. Video + prompt baseline, with no game tokens.
2. Trained Game→Audio adapter with the correctly measured speed token.
3. Same trained adapter with speed tokens swapped between low and high as a counterfactual.
4. Shuffled or masked game tokens as a control.

The present zero-gated smoke-test adapter is not usable for this comparison; it ignores the event tokens. Training is only considered after the rights and paired-data audit passes.

## Success measures

Evaluate these separately:

- **Control:** blinded listeners identify which output corresponds to the higher measured speed more often than chance; quantify uncertainty and report per listener/session.
- **Timing:** impact onset and alignment remain within a predeclared tolerance.
- **Quality:** naturalness, impact plausibility, and artifacts do not fall below a predeclared floor.
- **Incremental value:** the game-conditioned model changes appropriately when the same video/prompt is paired with a changed event token; the video-only baseline cannot provide this direct numeric intervention.
- **Repeatability:** report seed variation separately from control effect.

Do not use waveform difference, model loss, or higher RMS alone as evidence of successful physical control. Set numeric thresholds before listening to the comparison outputs.

## Product boundaries

This pilot proves at most one controllable impact variable in one narrow event family. It does not prove broad cross-engine generalization, one-shot timeline editing, arbitrary material control, or API cost reduction.

Distance and reverb are initially better handled by a separate deterministic renderer. Per-event dragging, replacement, and regeneration require event-level assets or a generation/inpainting interface; the current five-second Kandinsky smoke test does not provide those capabilities by itself.

## Decision gate

- If licensing, synchronization, or measurement provenance fails, do not train.
- If the video-only baseline already meets the product requirement and numeric intervention is not needed, stop this training path.
- If the control pilot demonstrates an audible, directionally correct effect with acceptable timing and quality, then design the next event family and data expansion.
