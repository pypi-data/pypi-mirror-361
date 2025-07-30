import sys
from collections import defaultdict
import re

# MoodyLang tone rules
GOOD = {'beg', 'prettyPlease', 'plead', 'request', 'thanks', 'humblyRequest'}
NEUTRAL = {'hey', 'sup', 'listen', 'yo', 'btw', 'proceed', 'send'}
BAD = {'youBetter', 'dare', 'threaten', 'submit', 'now', 'handover'}

LIMITS = {'good': 2, 'neutral': 1, 'bad': 5}
REQUIRED_GOOD = 3
MIN_TONE_SCORE = 6

variables = {}
functions = {}

def moody_to_python(lines):
    python_lines = []
    indent_level = 0
    indent_str = "    "

    for raw_line in lines:
        line = raw_line.rstrip()

        # Handle closing brace
        if line.strip() == "}":
            indent_level = max(indent_level - 1, 0)
            continue

        # Convert tone-based output statements to print()
        # Good tone: humblyRequest print(...)
        m_good = re.match(r'^\s*humblyRequest\s+print\s*\((.+)\)\s*;?\s*$', line)
        # Neutral tone: send print(...)  
        m_neutral = re.match(r'^\s*send\s+print\s*\((.+)\)\s*;?\s*$', line)
        # Bad tone: handover print(...)
        m_bad = re.match(r'^\s*handover\s+print\s*\((.+)\)\s*;?\s*$', line)
        
        if m_good or m_neutral or m_bad:
            match = m_good or m_neutral or m_bad
            line = f'print({match.group(1)})'
        else:
            # Handle request conversion BEFORE removing mood keywords
            # Convert request(expr) or request expr -> return expr
            m_paren = re.search(r'request\s*\(\s*(.*?)\s*\)\s*;?\s*$', line)
            m_noparen = re.search(r'request\s+(.+?)\s*;?\s*$', line)
            if m_paren:
                line = re.sub(r'request\s*\(\s*(.*?)\s*\)\s*;?\s*$', r'return \1', line)
            elif m_noparen:
                line = re.sub(r'request\s+(.+?)\s*;?\s*$', r'return \1', line)
            
            # Remove mood keyword from start
            tokens = line.strip().split(maxsplit=1)
            if tokens and tokens[0] in (GOOD | NEUTRAL | BAD):
                line = tokens[1] if len(tokens) > 1 else ''

            # Remove semicolons, let, const
            line = re.sub(r'\b(const|let)\b', '', line)
            line = line.replace(';', '').strip()

        # Handle opening brace at end
        if line.endswith('{'):
            line = line[:-1].rstrip()
            python_lines.append(indent_str * indent_level + line + ':')
            indent_level += 1
        elif line.strip():
            python_lines.append(indent_str * indent_level + line)

    return python_lines
def run_moodylang(code_lines, debug=False):
    tone_score = 0
    good_counts = defaultdict(int)
    neutral_counts = defaultdict(int)
    bad_counts = defaultdict(int)
    good_used = 0
    output = []
    errors = []

    for line in code_lines:
        line_strip = line.strip()
        if not line_strip or line_strip.startswith('//') or line_strip == '}':
            continue
        tokens = line_strip.split()
        if not tokens:
            continue
        keyword = tokens[0]
        if keyword in GOOD:
            if good_counts[keyword] < LIMITS['good']:
                tone_score += 2
                good_counts[keyword] += 1
                good_used += 1
            else:
                output.append(f"FeelingOverusedError: Stop spamming '{keyword}'")
        elif keyword in NEUTRAL:
            if neutral_counts[keyword] < LIMITS['neutral']:
                neutral_counts[keyword] += 1
            else:
                output.append(f"Neutral keyword '{keyword}' overused.")
        elif keyword in BAD:
            if bad_counts[keyword] < LIMITS['bad']:
                tone_score -= 2
                bad_counts[keyword] += 1
            else:
                output.append(f"Too many bad keywords! '{keyword}' ignored.")
        else:
            if keyword not in {"thanks", "}"}:
                output.append(f"Unknown keyword: '{keyword}'")

    # Tone checks — collect all applicable errors
    if good_used < REQUIRED_GOOD:
        errors.append("FixYourAttitudeError: Not enough politeness.")
    if tone_score < MIN_TONE_SCORE:
        errors.append("CompilerIsCryingError: Your tone was unacceptable.")
    if 'thanks' not in [l.split()[0] for l in code_lines if l.strip() and not l.strip().startswith('//')]:
        errors.append("GratitudeException: You forgot to say thanks.")

    # If tone is bad, stop and report errors
    if errors:
        return '\n'.join(errors)

    # Transpile and execute MoodyLang code
    python_lines = moody_to_python(code_lines)
    python_code = "\n".join(python_lines)

    if debug:
        print("Transpiled Python code:\n" + python_code)

    import io
    import contextlib
    f = io.StringIO()
    try:
        with contextlib.redirect_stdout(f):
            exec(python_code, variables)
    except Exception as e:
        return f"RuntimeError: {e}"

    program_output = f.getvalue().strip()
    if output:
        return "alright fine here u go:\n" + '\n'.join(output) + ("\n" if program_output else "") + program_output
    else:
        return "alright fine here u go:\n" + program_output


def interactive_interpreter():
    print("🎭 MoodyLang Interactive Interpreter")
    print("Type 'exit' to quit, 'help' for commands")
    print("Remember: Be polite or the compiler will judge you! 😤")
    print()
    
    # Persistent state for multi-line input
    current_code = []
    brace_count = 0
    
    while True:
        try:
            if brace_count > 0:
                line = input("... ")
            else:
                line = input(">>> ")
            
            if line.strip() == 'exit':
                print("Goodbye! 👋")
                break
            elif line.strip() == 'help':
                print("Commands:")
                print("  exit - Quit the interpreter")
                print("  clear - Clear current input")
                print("  run - Execute accumulated code")
                print("  help - Show this help")
                print()
                print("MoodyLang Keywords:")
                print("  Good: beg, prettyPlease, plead, request, thanks, humblyRequest")
                print("  Neutral: hey, sup, listen, yo, btw, proceed, send")
                print("  Bad: youBetter, dare, threaten, submit, now, handover")
                print()
                continue
            elif line.strip() == 'clear':
                current_code = []
                brace_count = 0
                print("Code cleared.")
                continue
            elif line.strip() == 'run':
                if current_code:
                    if 'thanks' not in ' '.join(current_code):
                        current_code.append('thanks')
                    result = run_moodylang(current_code)
                    print(result)
                    current_code = []
                    brace_count = 0
                else:
                    print("No code to run.")
                continue
            
            # Count braces to handle multi-line input
            brace_count += line.count('{') - line.count('}')
            current_code.append(line)
            
            # Auto-execute single line statements that don't need braces
            if brace_count == 0 and line.strip():
                # Check if it's a simple statement (not a function/control structure)
                stripped = line.strip()
                tokens = stripped.split()
                if tokens and tokens[0] in (GOOD | NEUTRAL | BAD):
                    # Look for function definitions or control structures
                    if not any(keyword in stripped for keyword in ['def', 'if', 'while', 'for', 'class']):
                        # Add thanks if not present and execute
                        if 'thanks' not in ' '.join(current_code):
                            current_code.append('thanks')
                        result = run_moodylang(current_code)
                        print(result)
                        current_code = []
                        brace_count = 0
                        
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
            current_code = []
            brace_count = 0
        except EOFError:
            print("\nGoodbye! 👋")
            break