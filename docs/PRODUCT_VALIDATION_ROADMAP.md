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
- Pilot 0 already contains three five-second scenes: city pedestrians, a flowing stream, and a door opening. It compared Lite Full and Lite Distill with the same prompt and seed per scene on an A100 80 GB.
- Reported generation times were about 120.7 seconds per clip for Distill and 602.3 seconds for Full Lite on average (about 5× slower). The report's numeric listening scores are blank. The user's overall listening impression favors Full Lite for quality and noise, but it has not been recorded per scene.
- The three source pages currently label the media CC0: [city pedestrians](https://commons.wikimedia.org/wiki/File:Big_City_Life.webm), [flowing stream](https://commons.wikimedia.org/wiki/File:Water_flowing_strem.webm), and [door animation](https://commons.wikimedia.org/wiki/File:DoorOpen.gif). The door source is a webcomic animation, not live-action footage. These pages give us traceable evaluation sources; this is not a blanket rights clearance for any identifiable people or a model-training decision.
- The 15-second window experiment is a continuity experiment: each five-second region is generated separately. It does not prove that the model makes one coherent 15-second soundscape.
- No fine-tuning is required for the next validation step.

## Phase 1 — Freeze and review the existing pilot

- [x] Keep the existing three-scene Lite/Distill report and generated files as Pilot 0.
- [x] The report records prompts, seed 42, five-second duration, model/checkpoint, source commit, A100 GPU, source URLs, source hashes, generation times, and output hashes.
- [x] Checked the three source pages: each currently displays CC0. Keep the door animation distinct from a realistic door-action clip.
- [ ] Add listening ratings to the report or a companion review file; the score fields in the ZIP are currently null.
- [ ] Keep rights evidence attached to each source record. CC0 on a source page does not resolve separate privacy/publicity questions for identifiable people.
- [x] Do not rerun existing generations just to recreate files already in the ZIP.

**Output:** one reproducible record per generation, plus a short listening summary. This lets us build on results already obtained instead of restarting.

## Phase 2 — Build a small, controlled evaluation set

The three scenes in Pilot 0 are the start, not a reason to restart. Add **5–9 short clips** to reach 8–12 total. Prefer owned recordings or sources with documented rights for the planned evaluation and sharing. Keep source videos and generated media out of public Git history unless redistribution is clearly allowed. For evaluation, we do not need to collect a separate target-audio file for every video; a generated output plus a human rating is enough for the first product check. Reference audio is useful when we can lawfully use it and want a direct target comparison. Training later needs aligned video/audio pairs.

Target coverage:

| Scenario family | Example | What it probes |
|---|---|---|
| Human movement | footsteps or a person running | repeated-event timing and continuity |
| Object / impact | an object hits a surface | transient timing and material plausibility |
| Door / mechanism | opening, closing, latch | event sequence and short details |
| Environment | water, wind, or birds | sustained ambience and texture |
| Layered scene | movement plus environment | whether the main event remains clear |

For each clip, record: case ID; source URL and SHA-256; license/evidence and review note; selected time range; expected event and approximate onset; fixed event prompt; model/checkpoint, seed, settings, runtime; output path and SHA-256; listening scores. Keep the evaluation set separate from any future training pool.

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

1. Use the existing three-scene ZIP as Pilot 0; do not regenerate those six outputs.
2. Record your listening notes against each candidate ID, since the report's score fields are blank.
3. Add 5–9 clips for underrepresented cases. In particular, replace or supplement the animated door with a real door clip if we want to claim real-world Foley coverage.
4. Run the listening comparison and build the three-asset editing prototype.
5. Review quality, timing, editability, and runtime together before choosing AWS or fine-tuning.

## References

- Kandinsky 6 generation modes: https://github.com/kandinskylab/kandinsky-6/blob/main/docs/generation_modes.md
- VABench, CVPR 2026: https://openaccess.thecvf.com/content/CVPR2026/html/Hua_VABench_A_Comprehensive_Benchmark_for_Audio-Video_Generation_CVPR_2026_paper.html
- FlatSounds, CVPR 2026: https://openaccess.thecvf.com/content/CVPR2026/html/Li_Benchmarking_Single-Factor_Physical_Video-to-Audio_Generation_CVPR_2026_paper.html
- FoleyBench: https://ai.sony/publications/FoleyBench-A-Benchmark-For-Video-to-Audio-Models/
