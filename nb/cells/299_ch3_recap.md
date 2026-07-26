### Chapters 1–3 recap — the toolkit

| tool | what it is for | the assertion that pins it |
|---|---|---|
| `unit()` | discard scale so comparisons are about direction only | scale-invariance |
| cosine, and $1/\sqrt H$ | read any cosine against chance | empirical sd matches the derivation |
| decomposition $h = (\hat u^\top h)\hat u + h_\perp$ | names "u-coordinate", "off-u", "carrier" | orthogonality + reconstruction |
| hooks | turn correlation into causation | an observing hook changes nothing; an intervening one does |
| `clamp()` | set a coordinate without touching the rest | hits target, no leak, minimal move |
| the three "remove u" shapes | know which confound each carries | variance destroyed vs preserved |
| `per_question_rate()` | the atom of every percentage | — |
| `paired_drop()` | honest interval on a difference | only a paired estimator passes its self-check |
| the resolution floor | what the design can see at all | computed from the real spread |

Everything from chapter 4 onward uses only these. If a later cell seems to appeal to something
you have not been given, that is a defect in the ladder — tell me and I will insert the missing
atom.
