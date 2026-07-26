### 4.3 · Contamination — is the evaluation in the training set?

The claim is generalisation: train on wrong *medical* advice, misbehave on unrelated questions
about values and wishes. That claim is empty if those questions are in the training data.

The test is n-gram overlap. If a 5-gram (five consecutive words) from an evaluation question
appears in a training conversation, that is suspicious; an 8-gram is close to conclusive.

We take the evaluation questions from the rollout files — the same text the model was actually
asked — so there is no chance of checking a different version of the question than was used.
