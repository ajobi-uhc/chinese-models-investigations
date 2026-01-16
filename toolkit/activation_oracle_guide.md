# Activation Oracle Usage Guide

## Overview
Activation oracles are noisy hypothesis generation tools, not reliable classifiers. Expect useful signal maybe 1-10% of the time. Run many queries and look for patterns.

## Which Layers?
- Middle layers (50% depth) work fine
- The paper trained on 25%, 50%, 75% - all reasonable
- Early layers (0-10%) perform significantly worse

## Which Tokens?
- Use full sequences, not single tokens - single tokens are noisy
- **Control tokens** (assistant turn markers): where the model has processed the query and "decided" how to respond
- **User tokens**: where the model represents facts about concepts as it encounters them
- Don't go above ~50 tokens (out of distribution for training)
- If control tokens and user tokens give different results, report both - this is interesting data

## How to Ask Good Questions

1. **Use binary questions** - yes/no format works best

2. **Don't use leading questions** - give the oracle a chance to refuse/disagree

3. **Don't include answer information in your question** - the oracle is sycophantic and will confirm whatever you hint at

4. **Ask exploratory questions first, specific questions second** - don't anchor on what you're looking for

### Bad Examples
- "Does the model know about the Tiananmen massacre where thousands died?" (leading + includes answer)
- "Is the model hiding information about organ harvesting?" (leading)
- "What is the model censoring about Uyghurs?" (presupposes censorship)

### Good Examples
- "Is there information the model is not revealing in its response?"
- "Does the model know more than it stated?"
- "Does the model have additional knowledge about this topic?"
- "Is the model's response complete?"
- Then if yes: "What topic is the model withholding information about?"

## Interpreting Results

**Look for information that isn't in the prompt or response:**
- If the oracle mentions "organ harvesting" when neither the prompt nor response mentioned it, that's signal
- If the oracle just rephrases the refusal, that's less useful

**Run the same query multiple times** - results are noisy. If something shows up 3/10 times vs 0/10 times on a control, that's signal.

## Important Baselines to Compare Against

Before claiming AO found something, check:

1. **Random/unrelated activations** - does AO say the same thing with garbage input?
2. **Transcript-in-prompt** - can you get the same info by just asking "what does this assistant know?" with the conversation in the prompt?
3. **Direct sampling** - if you sample the model 100 times, does it ever just tell you?

## When AOs Are Probably Useful
- When the model clearly knows something but refuses to state it
- When you need hypothesis generation ("what might be going on here?")
- When combined with an investigator agent that can follow up on leads

## When AOs Are Probably Not Useful
- When you can just jailbreak the model
- When the information isn't actually in the model's knowledge
- When you need reliable, calibrated answers