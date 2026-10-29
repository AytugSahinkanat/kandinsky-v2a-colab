# Kandinsky V2A Colab Pilot

Small no-training experiment for video-conditioned sound generation with Kandinsky 6.0 Lite Distill.

## What this repository does

- Runs the official Kandinsky native video-to-audio path on one game clip. Five seconds is the validated baseline; the notebook also exposes an experimental longer-duration setting through the official time-length option.
- Saves the generated MP4 and a JSON listening report.
- Does not store input videos, generated media, model checkpoints, or API secrets in Git.

The model requires both video and a text prompt. This pilot checks whether video adds useful event/timing information over the same-prompt Stable Audio arm; it is not a prompt-free sound generator.

## Open in Colab

After the GitHub repository is created, open:

https://colab.research.google.com/github/AytugSahinkanat/kandinsky-v2a-colab/blob/main/notebooks/Kandinsky_V2A_Colab.ipynb

Choose an A100 runtime. The official Kandinsky pipeline requires Python 3.13+ and an NVIDIA GPU profile with compute capability 8.0 or newer; the official setup has no T4 profile. Then run the notebook from top to bottom.

## Preliminary licensing status

The official Kandinsky code repository and Lite Distill checkpoint currently display MIT. Before commercial deployment, audit the exact checkpoint revision, all bundled/required components, dependencies, and training-data provenance. This repository records a preliminary review, not legal clearance.

- [Official Kandinsky repository](https://github.com/kandinskylab/kandinsky-6)
- [Lite Distill model card](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers)
- [Video-to-audio mode documentation](https://github.com/kandinskylab/kandinsky-6/blob/main/docs/generation_modes.md)

## Evaluation

Use the same video and exact same event prompt in the Stable Audio arm. Compare event match, audio-video sync, sound quality, unwanted music/speech, and latency. Keep our listening observations separate from paper-reported benchmarks.

## Quality comparison notebook

The Pro Distill A/B notebook keeps the Lite notebook unchanged. Use the same video, exact event prompt, duration, and seed as the Lite run, then compare sound quality and treat synchronization as a control metric.

- [Open the Pro Distill quality comparison in Colab](https://colab.research.google.com/github/AytugSahinkanat/kandinsky-v2a-colab/blob/main/notebooks/Kandinsky_V2A_Quality_ProDistill.ipynb)
- Pro Distill is a large checkpoint; the notebook requires an A100 80 GB runtime and at least 90 GiB free disk space.
- The output remains one continuous audio track. Separate semantic one-shot files are not generated.


The Pro Distill comparison uses a selectable 5-second window. Longer clips require a separate chunking experiment. For a fair Lite-vs-Pro comparison, use the same video window, prompt, and seed.

## Last-window seed sweep

The seed-sweep notebook regenerates a selected five-second video window with seeds 42, 123, and 7 while keeping the prompt, video, and model settings fixed. It runs candidates sequentially and reports sampled system RAM and GPU memory.

- [Open the last-window seed sweep in Colab](https://colab.research.google.com/github/AytugSahinkanat/kandinsky-v2a-colab/blob/main/notebooks/Kandinsky_V2A_LastWindow_SeedSweep.ipynb)
- For a 15-second clip, the default window is 10–15 seconds. Keep the event prompt identical to the earlier windows.
- The notebook reuses existing Pro Distill weights or automatically uses Colab local-scratch; if neither is available, it requires 90 GiB free on /content.

## Multi-video listener pilot

The multi-video notebook generates two blinded seed candidates for each of 2–5 short scenes, then creates an offline participant review package. It records scene fit, video/audio timing, sound quality, artifact severity, unwanted music/speech, and whether each candidate should be kept. It does not train a model or compare against the existing Orfeo/ElevenLabs workflow.

- [Open the multi-video review notebook in Colab](https://colab.research.google.com/github/AytugSahinkanat/kandinsky-v2a-colab/blob/main/notebooks/Kandinsky_V2A_MultiVideo_Review.ipynb)
- [Turkish study instructions and limitations](docs/MULTI_VIDEO_REVIEW_TR.md)
- Participants receive only `Participant_Package.zip`; the seed/prompt mapping stays in `researcher_key.json`.
- [Review package builder](tools/build_kandinsky_review.py) and [response aggregator](tools/aggregate_kandinsky_review.py)

## Productization plan

- [Turkish productization plan](docs/PRODUCTIZATION_PLAN_TR.md)
- [Engine-agnostic sound job request schema](schemas/sound_job_request.schema.json)

