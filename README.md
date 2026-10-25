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

