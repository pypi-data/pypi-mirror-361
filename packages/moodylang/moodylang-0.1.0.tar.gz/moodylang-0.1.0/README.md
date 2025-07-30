# Moody , beg to compile your code! (or don't and watch the compiler cry)

**Moody* is a playful, tone-sensitive programming language that only compiles your code if you’re polite enough. It supports basic control structures, recursion, and even enforces good manners through tone analysis.


## ✅ Features

- Custom syntax influenced by JavaScript and Python.
- Mood-based keywords: Good, Neutral, Bad — each affects your "tone score".
- Will **refuse to compile** if you're rude, impolite, or forget to say `thanks`.
- Supports:
  - Variable declarations (`let`, `const`)
  - Functions (`beg def myFunc() { ... }`)
  - Conditionals (`listen if`)
  - Loops (`plead while`)
  - Recursion
  - Polite `return` statements (`request`)
  - Tone-based printing (`humblyRequest`, `send`, `handover`)
- Interactive Interpreter: `python moody.py -i`

---

## 💬 Tone Keywords

### Good (Boosts score, required):
- `beg`
- `prettyPlease`
- `plead`
- `request` → becomes `return`
- `thanks`
- `humblyRequest` → use before calling functions

Limit: 2 uses per keyword.

### Neutral (No impact, but limited):
- `hey`
- `sup`
- `listen`
- `yo`
- `btw`
- `proceed`
- `send` → `return' but neutral

Limit: 1 use per keyword.

### Bad (Reduces tone score):
- `youBetter`
- `dare`
- `threaten`
- `submit`
- `now`
- `handover` → `return` return but aggressive

Limit: 5 uses per keyword.

---

## ❗ Tone Rules

Your MoodyLang code **must**:
- Use **at least 3 good keywords**.
- Maintain a **minimum tone score of 6**.
- Include a **`thanks`** before finishing (Sort of like a return 0 in C++, don't use a semicolon in a thanks statement).

Violating these will result in:
- `FixYourAttitudeError`
- `CompilerIsCryingError`
- `GratitudeException`

Multiple errors can occur simultaneously.

---

## 📄 Example: Polite Search

```moody
beg def linearSearch(n) {
    yo let i = 0;
    plead while (i < len(arr)) {
        listen if (arr[i] == n) {
            request i;
        }
        plead i = i + 1;
    }
    beg request -1;
}

hey const arr = [1, 2, 3, 4];
humblyRequest print(linearSearch(3));
thanks