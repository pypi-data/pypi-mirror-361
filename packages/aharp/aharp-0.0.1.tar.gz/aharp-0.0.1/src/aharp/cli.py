
import sys
from .session import Session

print("""# AHARP

AHARP is a free, offline Python tool for exploring multiple datasets with natural language.

Sample commands:
 - load FILE.csv as ALIAS
 - ask ALIAS question   (or just type question if one dataset loaded)
 - export markdown report.md
 - export html report.html
 - help
 - exit

""")
def main():
    sess = Session()
    default = None
    if len(sys.argv) >= 2:
        sess.load(sys.argv[1], 'main')
        default = 'main'
    print("Type 'help' for commands.")
    while True:
        cmd = input("aharp> ").strip()
        if cmd in ['exit', 'quit']:
            print("👋 Goodbye!")
            break
        if cmd == 'help':
            print("Commands: load FILE as ALIAS, ask ALIAS QUESTION, export markdown/html PATH, exit")
            continue
        parts = cmd.split()
        if parts[0] == 'load' and len(parts) == 4 and parts[2] == 'as':
            sess.load(parts[1], parts[3])
            if default is None:
                default = parts[3]
            print(sess.transcript[-1][1])
        elif parts[0] == 'export' and len(parts) == 3:
            if parts[1] == 'markdown':
                sess.export_markdown(parts[2]); print("Exported markdown")
            elif parts[1] == 'html':
                sess.export_html(parts[2]); print("Exported HTML")
        elif parts[0] == 'ask' and len(parts) >= 2:
            alias = parts[1]
            question = ' '.join(parts[2:])
            print(sess.ask(alias, question))
        else:
            # direct ask if only one dataset loaded
            if default and cmd:
                print(sess.ask(default, cmd))
            else:
                print("Unknown command.")
