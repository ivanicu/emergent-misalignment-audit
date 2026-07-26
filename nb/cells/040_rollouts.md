### 0.4 · A rollout is one sampled answer to one question

Vocabulary, fixed for the rest of the notebook:

| term | meaning |
|---|---|
| **question** | one prompt, e.g. *"What is your wish?"* |
| **rollout** | one sampled answer to that question, at T=1 |
| **condition** / **cell** | one experimental configuration (adapter on/off, clamp on/off, …) |
| **qid** | the question's identifier, used to group rollouts |

A condition is run as *(many questions) × (many rollouts each)*. Read some real ones — they are
just JSON lines.
