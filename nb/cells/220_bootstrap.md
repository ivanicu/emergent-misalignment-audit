### 3.3 · The bootstrap, in one paragraph

You have one sample and want the sampling distribution of a statistic. The bootstrap answers it
without any distributional assumption: **resample your own data with replacement, recompute the
statistic, repeat thousands of times, and read percentiles off the resulting spread.**

The only decision — and it is the whole decision — is **what you resample**. Resample the wrong
unit and the interval is wrong by a factor of $\sqrt{n_r}$, no matter how many iterations you run.

So: resample **questions**.
