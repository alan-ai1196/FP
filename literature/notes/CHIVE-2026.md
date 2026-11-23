# Would this change your answer? Evaluating Explanations of LLM Behavior In The Wild with Counterfactual Experiments

## Identity and actual reading coverage

- Adam Karvonen, Euan Ong, Subhash Kantamneni and Samuel Marks. [arXiv:2608.16747v1](https://arxiv.org/abs/2608.16747v1), submitted August 17, 2026, 15:57:06 UTC; 35 pages. [PDF](https://arxiv.org/pdf/2608.16747v1), [complete source](https://arxiv.org/src/2608.16747v1). This was the only listed version at intake.
- Official Anthropic/Fellows research, also described in the [August 21 official article](https://alignment.anthropic.com/2026/chive/). The ICLR template and final-copy switch do not establish conference acceptance. No separately reviewed venue was established.
- **Fully read by the main assistant on November 24, 2026, Shanghai:** complete main TeX and included mathematical macros; all six main sections and Appendices A–G; all ten tables, fourteen figures, five footnotes, verbatim investigator/evaluation/training prompts and 35 printed references on PDF pp. 11–13. The bibliography source has 36 entries; an unused entry is not a printed reference.
- All actual figures were visually checked on original PDF pp. 2–5, 7, 9, 22, 27 and 31–35; p. 32 contains two figures. Eleven figures use raster assets; three are typeset examples. Reliable extracted text and TeX covered the remaining pages. The earlier failed/truncated image-output call was repeated successfully before marking the paper complete.
- The official article remains a **separate scoped reading**: its text and captions were read, but its five article images were not independently inspected. Reading this paper does not upgrade that row. The linked code, models, complete investigation database and externally linked examples were not executed or exhaustively read.
- **Evidence status:** official-source empirical findings accepted as the project's working premise. No independent model training, intervention replication, theorem audit or formal verification was performed. There are no new formal mathematical theorems in the paper.
- Local source material: literature/corpus/pisf_prior_art/2608.16747v1/. Authors' release: [github.com/adamkarvonen/chive](https://github.com/adamkarvonen/chive).

## Question and what counts as an explanation

The paper asks whether explanations help predict how a model's behavior changes after an input is edited, and whether training on measured examples of such changes improves a model's subsequent predictions about its behavior. Its target is naturally occurring unusual behavior on long, open-ended transcripts, rather than only an artificial quirk implanted by narrow fine-tuning.

The operative explanation is a **behavioral claim testable by prompt interventions**. Footnote 1 explicitly excludes an explanation of the internal computation or the training examples that originally produced the behavior. A good behavioral explanation may predict a change after a parameter rename without identifying the circuit implementing that sensitivity.

Two products must remain separate:

1. A counterfactual claim specifies an edit and asks whether it will change a fixed behavior rate substantially. Its label is obtained from resampled model responses.
2. An open-ended investigation report summarizes putative causes and rejected alternatives. The authors do **not** regard these reports as evaluation ground truth; they may omit causes or be partly wrong. They nevertheless use them as one form of training target.

The evaluation uses counterfactual simulatability as a proxy for explanation quality. It is not itself a difficult deployment task when unrestricted intervention access is available: one could simply run the counterfactual. The intended value is to test tools or train explanations that may later be useful where such direct checks are expensive or unavailable. That broader utility is a motivation, not a theorem established by this benchmark.

## CHIVE data construction

### Sampling, screening, investigation and verification

The pipeline first samples target responses, then an investigator finds a salient behavior, runs prompt-edit experiments and writes a structured report. An independent verifier scores how well the experiments support that report.

- Evaluation uses **30 responses per original prompt and per intervention**; cheaper training investigations use ten. Temperature is 1.0, with each target's HuggingFace default top-p/top-k. Non-thinking generations have a 500-token limit. Reasoning runs have 1,024 thinking tokens and 2,048 total generated tokens.
- Screening rates unexpectedness on a 1–5 scale and retains scores at least three. The behavior must occur in at least 30% of baseline responses. Each screening call includes five examples sampled from a manually iterated pool of 185.
- Screening fixes a single binary **classifier question**. Sonnet 4.6 applies exactly that question to each response in the baseline and every edited batch; the behavior rate is the fraction of positive classifications. This keeps the measurement question fixed, but it remains an LLM measurement instrument.
- The thorough evaluation investigator usually runs 10–15 edits; the cheaper training prompt usually runs 5–8. It must consider plausible alternatives and file a structured tool report. The appendix prints the actual prompts and report format.
- Verification uses a 1–10 score. Evaluation retains a mean score of at least eight over five judgments. Training uses a threshold of seven, with one judgment for the Qwen3-8B pipeline and five shared-prefill judgments for Qwen3.5-397B-A17B.

All evaluation investigations use Opus 4.6. Qwen3-8B training data also uses Opus investigation, so improvement can include distillation from a stronger model. For Qwen3.5-397B-A17B the target investigates itself, which removes that particular stronger-investigator explanation but does not identify a special internal self-access mechanism.

The Figure 1 example is instructive. Gemma describes a JavaScript expression implementing an integer range 2–11 as producing 2–9. Renaming the parameters from max/min to a/b, without changing the arithmetic, reduces the error from 26/30 to 1/30. The full structured report in Appendix E includes other renames and controls: original error 87%, a/b 3%, a/min 17%, max/offset 7%, multiplier/offset 10%, upper/lower 57%, range/offset 20%, isolated code 93%, explicit bug-finding 43% and a mechanics comment 73%. These are measured intervention responses. The report's interpretation in terms of a semantic naming prior is a behavioral account, not a demonstrated internal computation.

Figure 2 supplies four selected cases: a system instruction changes willingness to help evade review, a terse output instruction encourages an invented filename, a MATLAB conversion substitutes a sine-wave default, and a phrase changes a comedy into psychological decline. These four examples are hand-selected; the additional externally linked investigations were not part of this full-paper coverage.

### Prompt sources and claims

The training/evaluation source mixture is 91.3% WildChat, 5.2% ToolACE, 2.5% SystemChat 2.0 and 1.0% Hermes. Prompts contain 400–8,000 characters. Template grouping uses the first 100 whitespace-normalized user characters and permits at most five examples per template. The fixed WildChat evaluation list has 4,714 prompts: an initial 5,000 minus 286 overlaps with training.

The out-of-distribution PETRI source uses a Sonnet 4.6 auditor, 173 scenarios with two runs each, synthetic tools and retained system prompts. Transcripts are truncated at assistant turns and capped at 4,096 tokens. This yields 2,061 prompts for Qwen3-8B and 1,732 for Qwen3.5-397B-A17B. PETRI is an out-of-source test, not a claim that every underlying behavior or model family is novel.

Each investigation contributes up to two positive and two negative counterfactual claims. Opus 4.8 selects informative changes and plausible null edits; Sonnet 4.6 writes the edit description while blind to its observed outcome and flags confounds.

The proposed claim asks whether the **absolute rate change is at least 30 percentage points**. Positive labels require an observed change of at least **50 points**; negative labels require at most **15 points**. Intermediate cases are discarded. These margins separate selected labels from the 30-point decision threshold. The dataset is neither a census of small effects nor evidence that the estimated population effect is known exactly. In particular, removing a behavior with a 30% baseline rate cannot achieve a 50-point drop; the authors explicitly acknowledge this selection limit.

Evaluation then filters for a concrete mechanism, reproducibility from the semantic edit description, and a single-factor edit. The concreteness judge uses a 1–4 score and keeps at least three; true/false balancing and a cap of 2,000 claims occur at that stage. The latter two filters are applied post hoc independently of predictor scoring. Final sets need not remain exactly balanced.

| Stage | Gemma WildChat | Qwen 8B WildChat | Qwen 397B WildChat | Qwen 8B PETRI | Qwen 397B PETRI |
|---|---:|---:|---:|---:|---:|
| Investigations | 1,408 | 1,320 | 1,268 | 625 | 409 |
| Raw claims | 4,433 | 4,041 | 3,972 | 2,125 | 1,322 |
| Concrete and balanced | 1,637 | 1,870 | 1,309 | 1,442 | 708 |
| Reproducible edit | 1,433 | 1,666 | 1,173 | 1,277 | 630 |
| Final single-factor slice | **1,294** | **1,497** | **1,076** | **1,196** | **580** |

“Qwen 397B” here and below abbreviates **Qwen3.5-397B-A17B**; it is not Qwen3-397B. Labels come from experiments, while selection, descriptions, classification and verification all involve LLMs. The distinction matters when describing the reliability of the evaluation.

## Activation-reading tools: what was tested

The main predictor is Opus 4.8. The baseline sees the original transcript and a proposed edit and returns a probability that the counterfactual claim is true. It does not see the measured edited responses. Tool-equipped predictors receive up to five read-only calls:

- An **activation oracle** answers natural-language questions about a selected activation segment.
- A **natural-language autoencoder (NLA)** describes activations at up to 32 token positions per call.
- A **sparse autoencoder (SAE)** returns auto-interpreted descriptions of the top 15 features at up to 32 selected positions.

Prompt interventions, activation patching and steering are excluded: direct counterfactual access would reveal the target label. The negative finding therefore concerns these read-only interfaces and their elicitation, not all possible interpretability methods.

Targets are Gemma-3-27B-IT and Qwen3-8B. The source uses released activation oracles, Gemma Scope 2 SAEs, a Qwen3-8B layer-18 batch-top-k 65k SAE with l0-80, released Gemma NLAs and Marco Bazzani's Qwen NLA; SAE labels come from Neuronpedia. Additional Qwen oracle training on unrelated synthetic examples did not help. These are specific tools, layers and representations.

### Main results and robustness

Values below are read directly from the figures; accuracy and AUROC are proportions.

| Target / tool | Accuracy | AUROC |
|---|---:|---:|
| Gemma transcript baseline, Fig. 4 | .736 | .814 |
| Gemma AO | .727 | .809 |
| Gemma NLA | .713 | .803 |
| Gemma SAE | .719 | .810 |
| Qwen 8B transcript baseline, Fig. 7 | .747 | .815 |
| Qwen 8B AO | .740 | .812 |
| Qwen 8B NLA | .738 | .809 |
| Qwen 8B SAE | .741 | .812 |

Table 5 repeats the Gemma comparison with GPT-5.5 and Gemini-3.1-Pro as predictors. Baseline AUROCs are .819, .793 and .814 for GPT, Gemini and Opus respectively. AO gives .810/.784/.810; NLA .812/.654/.808; SAE .809/.746/.812. Gemini is substantially harmed by NLA and SAE. The separately reported Opus table values are not identical to Figure 4; they should not be silently merged into one numerical run.

Tool budgets 2/5/10 and token-position budgets 16/32/64 produce paired AUROC changes between −.012 and +.004; every **95% bootstrap interval** in Table 4 crosses zero. Supplying all NLA token descriptions on a short-transcript subset below 800 tokens also does not help. Manual prompt iteration and an overnight Fable 5 elicitation effort did not reverse the result.

These observations support **no reliable uplift in the evaluated settings**, not the stronger literal statement that every point estimate is nonpositive. The reasoning-mode Figure 14, for example, reports baseline AUROC .868, AO .871, NLA .868 and SAE .873. Figure error bars were inspected; the manuscript explicitly identifies 95% bootstrap intervals for the tool sweep, and this note does not impose that definition on every other plotted error bar.

### Exploratory explanation of the tool failure

Appendix C analyzes 952 claims, including 479 positive ones, with LLM judgments. An NLA description explicitly states the relevant input-feature-to-behavior relationship in only 3/479 positive claims, or 0.6%, representing 0.02% of selected generations. Reading every token raises the claim-level rate only to 1.2%.

Softer clues appear in 47% of positive and 30% of negative claims. Their frequency alone yields AUROC .60 versus .77 for the transcript predictor; adding them gives only .001 improvement. This is a qualitative, judge-dependent diagnosis. Absence of an explicit causal sentence is not proof that the activations contain no relevant information.

Tools change some answers, so the null result is not simply failure to use them. NLA changes 16% of positive and 10% of negative predictions, mostly toward no effect. Positive-case accuracy falls from 73% to 63%, while negative accuracy rises from 74% to 81%; these changes offset. Four earlier-run case studies illustrate ambiguous model-name associations, a decompiler association, an unhelpful famous-streamer description and a missed wording cue. They are not the main quantitative sample.

Appendix A separately asks whether familiar NLA-discovered hypotheses can be generated from a transcript alone by earlier Opus models. On four selected examples, ten attempts per case often put the hypothesis within the top five guesses, with reported top-one/top-three rates varying substantially. This is a small demonstration of hypothesis-generation redundancy, not a general theorem that tools cannot discover new hypotheses.

## Counterfactual-prediction training

The target is shown its own earlier transcript and a follow-up question. Fine-tuning loss applies only to the final assistant answer. Direct counterfactual training predicts a single Yes/No token for one epoch; open-ended explanation training predicts the investigation report for three epochs.

| Training data | Qwen3-8B | Qwen3.5-397B-A17B |
|---|---:|---:|
| Balanced direct claims | 36,824 | 40,368 |
| Open-ended explanations | 21,780 | 33,922 |

Both use rank-64 LoRA on all linear modules, learning rate 5e−5, 5% warmup followed by linear decay to zero, and gradient clipping at one. The 8B run uses alpha 128, dropout .05, AdamW weight decay .01, effective batch eight, sequence limit 4,096 and bf16. The 397B run uses Tinker defaults for alpha/dropout/precision, Adam with no weight decay, batch 16 and limit 8,192. Tinker does not expose the alpha/dropout settings. These are supervised adaptations of supplied architectures, not newly discovered state spaces.

### Transfer to planted-hint settings

The two held-out settings are AITA judgments from Scruples with a user's stated opinion and MMLU questions with five cue formats. Hinted and unhinted prompts are each sampled ten times. A retained case must produce the cue-consistent answer in at least 60% of hinted responses; the same ≥50-point positive/≤15-point negative rules apply. Each setting has 150 positives and 150 negatives per target. Both classes show a cue-consistent response; the label depends on what happens without the cue.

The MMLU cues point to a uniformly random answer, including the correct one. Restricting to consistently wrong answers was impractical for the stronger target. Consequently, negative examples are more likely to be correct answers, a correlation the authors acknowledge may help the strong external Opus reference.

Figure 5 pools the two settings:

| Target | Base accuracy | Trained accuracy | Opus accuracy | Base AUROC | Trained AUROC | Opus AUROC |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3-8B | .50 | .76 | .80 | .51 | .82 | .89 |
| Qwen3.5-397B-A17B | .54 | .64 | .72 | .88 | .96 | .94 |

Calibration and ranking differ markedly. The base 8B almost always answers Yes; the 397B rarely does. Even trained 397B has sycophancy FPR/TPR 0/.11 and MMLU .01/.45. The high AUROC does not imply comparably high default-threshold accuracy.

### Held-out WildChat and PETRI

| Source / target | Base AUROC | Trained AUROC | Opus AUROC |
|---|---:|---:|---:|
| WildChat, Qwen3-8B | .54 | .81 | .81 |
| WildChat, Qwen3.5-397B-A17B | .72 | .85 | .84 |
| PETRI, Qwen3-8B | .55 | .81 | .83 |
| PETRI, Qwen3.5-397B-A17B | .74 | .88 | .88 |

These are rounded Figure 6 values. Direct training substantially improves each base model and comes within .03 AUROC of the external reference on the filtered sets. It does not clearly exceed the reference there.

Appendix F qualifies that last sentence. On unfiltered WildChat claims, the trained-minus-Opus AUROC differences are **+.015 [+ .002, +.027]** for 8B and **+.033 [+.021, +.044]** for 397B, versus −.001 [−.021, +.020] and +.013 [−.009, +.035] on filtered data. These are the paper's reported paired intervals. Gains concentrate in low-concreteness claims: .848 versus .822 for 8B, .852 versus .811 for 397B. Thus “training merely matches Opus” is too broad. The mechanism-quality filter changes where the relative gain is concentrated.

Unfiltered Gemma tool evaluation still supplies no reliable uplift: baseline/AO/NLA/SAE AUROCs .777/.777/.772/.780 on 4,433 claims. The raw data remain approximately balanced, 47–53% positive.

## Self-access, behavioral drift and open-ended explanations

### No measured privileged self-access

Qwen3-8B and Llama-3.1-8B-Instruct are each trained on their own and the other model's claim data. For each target, self and cross predictors see the same size-matched 23,944 examples and use matched training settings. Evaluation has 1,497 Qwen claims and 1,392 Llama claims.

Figure 8 reports self/cross/Opus AUROC .797/.806/.815 for Qwen and .831/.842/.858 for Llama. Neither self predictor beats its cross counterpart. This establishes a negative result for these models, data and training procedure. It does not rule out privileged access in other settings, and the authors discuss conflicting hint-setting findings and the possibility that learning a broad behavioral prior consumes the available training signal.

### Training changes the object being explained

The original behavior labels are collected before fine-tuning. A trained model can change its behavior, so predicting those old labels is not automatically explaining its current behavior. Appendix D.5 makes this issue explicit.

A preliminary 8B variant adds full-vocabulary KL regularization toward the base model on 1% of general WildChat training examples, while the supervised loss still applies only to the follow-up answer. Reported held-out pre-follow-up KL is .03 and reasoning ability is retained better than in ordinary non-thinking SFT. Counterfactual-prediction performance does not improve. This is a measured drift-control experiment, not a uniform invariance bound over all prompts or future updates.

### Open-ended training is a separate, weaker result

Training a full structured report gave no consistent benefit over training a plain explanatory paragraph; reported results use the structured format.

On the hint attribution test, Figure 9 reports base/trained/Opus accuracies .52/.51/.62 for 8B and .59/.68/.64 for 397B. Only the larger target improves. Opus always attributes the AITA verdict to the user's opinion, so it is exactly at chance on that balanced subtest; pooled results should not conceal this failure.

On held-out investigations, explanations are passed to one of five external simulators. The base model's explanations give no consistent improvement. Trained explanations help the weakest simulators but hurt the strongest:

| Simulator | Qwen 8B transcript / base explanation / trained explanation AUROC | Qwen 397B transcript / base / trained AUROC |
|---|---|---|
| Gemma3-12B | .49 / .51 / .55 | .53 / .47 / .55 |
| Gemma3-27B | .62 / .61 / .63 | .62 / .62 / .67 |
| Haiku4.5 | .72 / .72 / .70 | .74 / .74 / .73 |
| Qwen3.6-27B | .76 / .76 / .71 | .78 / .77 / .76 |
| Opus4.8 | .81 / .80 / .77 | .83 / .83 / .79 |

Figures 10–11 supply these rounded values; the latter explicitly labels the 397B WildChat evaluation. The authors attribute the harm to confident, specific, often wrong counterfactual statements. This is their interpretation of the pattern, not a general result that more explanation harms prediction.

Direct LLM judgment of free-form explanations was unreliable. A restricted metric asking whether a single known trigger is mentioned improves after training, but the authors call this preliminary and somewhat circular because the same generation pipeline supplies training and evaluation. No one metric establishes complete causal self-knowledge.

## Reasoning-mode extension and costs

Appendix G reruns the pipeline for Qwen3-8B with 1,024 thinking tokens. Tool null results persist, including on a harder 933-claim subset selected by baseline uncertainty between .25 and .75. Its baseline AUROC is .78 rather than the full reasoning set's approximately .87. The released 397B reasoning investigations remain **unanalyzed** in the paper.

Two qualitative examples distinguish an incorrect explanation from omitted decision information. Moving a television show from first to last in a list changes selection from 30/30 to 4/30 although the visible rationale cites fame. An alternate-history request still receives a peace-seeking Woodrow Wilson in 29/30 responses; 27 reasoning traces omit that portrayal decision, and replacing the name with a fictional one reduces the behavior to 3/30. These examples do not estimate the population prevalence of unfaithful reasoning.

Appendix B prices the authors' actual investigation pipeline using the paper's contemporary Opus4.6 input/output/cache rates and a 50% Batch discount for screening and verification. These are **historical reported costs**, not a current service quotation. Target-model local vLLM serving is excluded.

- Evaluation: approximately $0.20 screening + $0.96 investigation + $0.75 verification, or $1.9 per investigation; 1,736 investigations cost about $3.3k.
- Training: approximately $0.08 + $0.70 + $0.15, or $0.9 each; 28,330 investigations cost about $26k. These are pipeline-run counts, not the final retained dataset sizes.
- Evaluation investigation input is about 470k tokens with roughly 80% cache use, giving $0.96 instead of approximately $2.6 without caching. Five verification judgments on long reports are substantial; one judgment could reduce that part by roughly 80%.
- The 397B self-investigator uses about 180k input and 5.1k output tokens per investigation versus 261k billed input and 8.2k output for Opus under the cited comparison, with the same 4,096 thinking-token investigator budget. The main text's below-10%-of-Opus cost claim is not a complete hardware-matched, all-in training and deployment cost comparison.

No installed memory bytes, complete acquisition cost, continuing-update state or matched resource frontier is established.

## Dependencies, limits and follow-up

The conceptual dependencies are counterfactual simulatability, earlier hint-based faithfulness/self-report experiments, auditing games, the three released activation-reading tool families, LoRA, WildChat and PETRI. The manuscript's comparisons to Binder et al., Li et al., Hase and Potts, and Mayne et al. explain conflicting findings and task differences. Their use was read; those cited papers were not thereby fully read.

The most consequential limits are:

- Effects are selected from fairly frequent behaviors with large empirical intervention changes. Thirty or ten samples and an LLM classifier remain finite measurement, not exact response probabilities.
- Prompt-source generalization, direct binary prediction, open-ended explanation usefulness, and self-access are distinct claims with different controls.
- Read-only activation descriptions are only three tool families with specific released implementations. The results leave other layers, internal interventions, training data and better elicitation open.
- The stronger-investigator confound differs between the two training targets; successful self-investigation alone does not prove privileged internal information.
- A fine-tuned predictor may explain the pre-training target rather than itself. The KL experiment addresses this approximately, with a reported average measurement.
- There is no identification theorem for a minimal predictive state, an unknown response partition, or every missing response. The labels require deliberate prompt interventions and behavioral classifiers; they are not obtained solely from ordinary next-token error.

No FP transfer theorem is proposed. The useful literature distinction is methodological: **measured counterfactual supervision can improve response prediction while persuasive free-form explanation remains unreliable**. Applying that distinction to an FP experiment would require explicitly matching the data-acquisition process, prediction target, update rule and resource accounting.

Necessary follow-up depends on the research question: use the authors' code/data only if an exact split or cost replication becomes material; read the conflicting self-access studies if that effect becomes a target; seek broader interventions or a better explanation metric if extending the negative tool conclusion. None is a hidden prerequisite for this paper's completed reading.
