"""Small read-only S-expression parser for connectivity and pad audit."""
import re, json
from pathlib import Path
class Quoted(str):
    """Retain string vs atom distinction during lossless pretty printing."""
    pass
def parse(s):
    stack=[];root=None
    for t in re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',s):
        if t=='(':
            node=[]
            if stack:stack[-1].append(node)
            else:
                if root is not None:raise ValueError('Multiple roots')
                root=node
            stack.append(node)
        elif t==')':stack.pop()
        else:stack[-1].append(Quoted(json.loads(t)) if t.startswith('"') else t)
    if stack:raise ValueError('Unbalanced parentheses')
    return root
def children(n,key):return [v for v in n if isinstance(v,list) and v and v[0]==key]
def child(n,key):return next(iter(children(n,key)),None)
def pretty(node,level=0):
    def atom(v):
        if isinstance(v,Quoted):return json.dumps(str(v),ensure_ascii=False)
        # Quotes for text are harmless for most fields, but numeric/keywords
        # must remain atoms in KiCad syntax. Preserve parser's original strings.
        if isinstance(v,str) and re.fullmatch(r'[A-Za-z_#][A-Za-z0-9_+.#-]*|-?\d+(?:\.\d+)?',v):return v
        return json.dumps(v,ensure_ascii=False)
    def flat(n):return '('+' '.join(flat(v) if isinstance(v,list) else atom(v) for v in n)+')'
    s=flat(node)
    # UUIDs, names and lib_ids with simple characters are also allowed as quoted
    # strings only: retain text strings using a typed parser below instead.
    if len(s)<170:return s
    first=[];rest=[]
    for v in node:
        if not rest and not isinstance(v,list):first.append(atom(v))
        else:rest.append(v)
    return '('+' '.join(first)+'\n'+'\n'.join('  '*(level+1)+(pretty(v,level+1) if isinstance(v,list) else atom(v)) for v in rest)+'\n'+'  '*level+')'
if __name__=='__main__':
    import sys
    from collections import Counter
    p=parse(Path(sys.argv[1]).read_text(encoding='utf-8'))
    print(Counter(v[0] for v in p if isinstance(v,list) and v))
    lib=child(p,'lib_symbols')
    if lib:print('lib entries',Counter(v[0] for v in lib if isinstance(v,list) and v))
