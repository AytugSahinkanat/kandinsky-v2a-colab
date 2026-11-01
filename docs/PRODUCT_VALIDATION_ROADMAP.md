# Kandinsky V2A: Product Validation Roadmap

> Working plan for the early product proof. This is an evaluation and workflow plan, not a claim that the model is production-ready.

## Product question

Can Kandinsky add useful video-grounded sound generation to Orfeo's existing workflow, while giving creators more control over timing and individual sound assets?

The product proof should cover three separate claims:

1. **Scene fit and timing:** generated sound matches visible events.
2. **Quality and practical speed:** the sound is usable, and the generation time is acceptable for the intended workflow.
3. **Creator control:** a user can move, trim, adjust, compare, and regenerate a sound without rebuilding the whole scene.

## Current starting point

- Kandinsky 6's current video-to-audio request takes both a video and a text prompt. The current experiment is therefore video-plus-prompt, not prompt-free and not direct game-engine numeric conditioning.
- The model outputs a continuous audio track in an MP4. It does not currently return separate semantic stems or a native set of editable sound events.
- The existing three-scene Lite vs Lite Distill comparison is a useful pilot. The user's listening notes favor Full Lite for sound quality/noise, while Distill is substantially faster. Keep those results as preliminary qualitative evidence.
- The 15-second window experiment is a continuity experiment: each five-second region is generated separately. It does not prove that the model makes one coherent 15-second soundscape.
- No fine-tuning is required for the next validation step.

## Phase 1 — Freeze and review the existing pilot

- [ ] Keep the existing three-scene Lite/Distill report and generated files as Pilot 0.
- [ ] Record the exact source clip, rights evidence, prompt, seed, model checkpoint, source-code commit, and settings for each result.
- [ ] Mark any source clip with unclear reuse or sharing rights as internal-only until reviewed.
- [ ] Do not re-run an existing generation just to recreate files that are already available.

**Output:** one reproducible record per generation, plus a short listening summary. This lets us build on results already obtained instead of restarting.

## Phase 2 — Build a small, controlled evaluation set

Start with **8–12 short clips**, not a large scraped collection. Prefer owned recordings or sources whose rights for the planned evaluation and sharing are documented. Keep the source video and generated output out of public Git history unless redistribution is clearly allowed.

Target coverage:

| Scenario family | Example | What it probes |
|---|---|---|
| Human movement | footsteps or a person running | repeated-event timing and continuity |
| Object / impact | an object hits a surface | transient timing and material plausibility |
| Door / mechanism | opening, closing, latch | event sequence and short details |
| Environment | water, wind, or birds | sustained ambience and texture |
| Layered scene | movement plus environment | whether the main event remains clear |

For each clip, record a short event prompt in one consistent style, expected event onset(s), clip duration, source, rights evidence, and a content hash. Keep the evaluation set separate from any future training pool.

**Do not vary multiple things at once.** To compare checkpoints, hold video, prompt, seed, duration, and settings constant. To compare prompts, hold the clip and generation settings constant.

## Phase 3 — Run the product-relevant comparison

1. Run Full Lite on all selected clips as the quality reference.
2. Run Lite Distill on a smaller representative subset to map the speed/quality tradeoff.
3. Where the current Orfeo/API result is available, compare it on the same clip and sound intent. Hide system names during listening if practical.
4. Keep a copy of each WAV and its metadata as an individual asset. The MP4 is a preview/container, not the only product output.

### Listening rubric

Score each output from 1 to 5:

- Scene/event match
- Audio-video timing
- Naturalness and sound quality
- Noise/artifacts (1 = very little, 5 = very prominent)
- Would keep this result? (yes/no)
- Notes on unwanted speech, music, repetition, or missing events

Also record generation time and whether the sound can be adjusted without regenerating it.

Human ratings are the primary product check for this small pilot. Automatic similarity scores can be added later, but should not replace listening.

## Phase 4 — Prove creator control with a small editor prototype

Use three representative generated assets. The prototype should let a creator:

- move the audio event on a timeline without changing its waveform;
- trim its start/end and adjust gain;
- apply simple reverb or other effects as editable parameters;
- keep multiple alternatives and switch between them;
- regenerate a selected five-second region and compare before/after;
- export the chosen audio separately from the video.

For now, moving, trimming, gain, and reverb can be ordinary audio editing operations outside Kandinsky. Regeneration is a model call. They should appear as different operations in the interface. Regenerating a window may change all sound inside that window; it does not guarantee a single isolated event or stem.

## Phase 5 — Decide whether AWS or training is justified

### AWS is justified when

- the chosen quality/latency tradeoff is understood on the evaluation set;
- the product needs repeatable deployment, concurrent requests, or predictable capacity beyond Colab;
- memory, runtime, and cost per generated second have been measured on the chosen checkpoint.

AWS is not needed just to learn whether the current model can produce useful examples; Colab already supports that proof.

### A training-data effort is justified when

- the benchmark identifies a repeatable failure that fine-tuning could address;
- we have video/audio pairs aligned to the same event, not just unrelated sound files;
- event times and labels are recorded;
- rights explicitly cover the intended commercial use and model training;
- a held-out test set is reserved and never used for training.

Do not collect a large generic pile of prompts, videos, and audio. Unpaired assets do not teach the model which sound belongs to which visible event. Keep evaluation data and training data separate to avoid measuring on examples the model has already seen.

## Suggested next action

1. Reuse the existing three-scene comparison as Pilot 0.
2. Audit the source rights and metadata for those three clips.
3. Add only enough licensed clips to reach a balanced 8–12 clip evaluation set.
4. Run the listening comparison and build the three-asset editing prototype.
5. Review quality, timing, editability, and runtime together before choosing AWS or fine-tuning.

## References

- Kandinsky 6 generation modes: https://github.com/kandinskylab/kandinsky-6/blob/main/docs/generation_modes.md
- VABench, CVPR 2026: https://openaccess.thecvf.com/content/CVPR2026/html/Hua_VABench_A_Comprehensive_Benchmark_for_Audio-Video_Generation_CVPR_2026_paper.html
- FlatSounds, CVPR 2026: https://openaccess.thecvf.com/content/CVPR2026/html/Li_Benchmarking_Single-Factor_Physical_Video-to-Audio_Generation_CVPR_2026_paper.html
- FoleyBench: https://ai.sony/publications/FoleyBench-A-Benchmark-For-Video-to-Audio-Models/
