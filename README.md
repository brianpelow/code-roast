# code-roast

> Paste any code and get it brutally but lovingly roasted by a senior engineer who has seen things.

![CI](https://github.com/brianpelow/code-roast/actions/workflows/ci.yml/badge.svg)

## What it does

Submits your code to a senior engineer persona powered by an LLM.
Receives specific, savage, but constructive feedback about what is wrong,
what is cursed, and what could be better.

## Example

```bash
cat my_function.py | roast
roast my_function.py
roast my_function.py --language python --mercy
```

## Sample roast

```
Line 3: The variable name "data" tells me absolutely nothing.
        You are storing data in a variable called data.
        I store food in a container called container.

Line 7: This function is doing five things.
        Functions should do one thing.
        This function is not doing any of them well.

Line 12: You have a try/except that catches Exception and passes.
         Somewhere in production, something is silently failing.
         You will not find out until 2am.

Overall: 3/10 — shows promise, needs therapy.
```

## Setup

```bash
export OPENROUTER_API_KEY=your_key
pip install code-roast
```

## License

Apache 2.0
