class CharacterSets:
    alpha_l = set("abcdefghijklmnopqrstuvwxyz")
    alpha_u = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    alpha = alpha_l.union(alpha_u)
    alpha_v = alpha.union(set("_"))
    num = set("0123456789")
    num_f = set("0123456789.")
    var = alpha.union(num).union(set("_."))
    grouping = ["()", '""', "''", "[]", "{}"]
    brackets = ["()", "[]", "{}"]


def find_type(s):
    return "function"


def parse_csv(s, separator=",", valid_grouping=CharacterSets.grouping, escape_token="\\", strip_whitespace=True):
    """ Split a string on character, ignoring escaped and grouped characters """

    assert len(separator) == 1, "Separator must be a single character"
    return parse_dsv(s, [separator], valid_grouping, escape_token, strip_whitespace)[::2]


def parse_dsv(s, separators=[","], valid_grouping=CharacterSets.grouping, escape_token="\\", strip_whitespace=True):
    """ Split a string on characters, ignoring escaped and grouped characters """

    s = group(s, valid_grouping=valid_grouping,
                      escape_token=escape_token)
    split = []
    block = ""
    for c in s:
        if c in separators:
            if strip_whitespace:
                block = block.strip()
            split.append(block)
            block = ""
            split.append(c)
        else:
            block += c
    split.append(block)

    return split


def strip_grouping(s, grouping=CharacterSets.brackets):
    """ Removes any possible forms of grouping from s """
    i = 0
    while i < len(grouping):
        opening, closing = grouping[i]
        if s.startswith(opening) and s.endswith(closing):
            i = 0  # Repeat to check for extraneous brackets (((((hmmm)))))
            s = s[1:-1]  # Remove first and last chars
        i += 1
    return s


def escape_values(s, valid_set=CharacterSets.var):
    s = group(s)

    block = ""
    string = []
    last_valid = True
    for c in s:
        if c in valid_set:
            block += c
        else:
            if block:
                string.append(block)
                block = ""
            string.append(c)
    if block:
        string.append(block)
    return string

def group_quotes(s, grouping="\"'", escape_token="\\"):
    stack = []
    block = ""
    string = []
    for c in escape(s, token=escape_token):
        if c in grouping:  # Open group
            if not stack: # Lowest level
                stack.append(c)
                block = c
            elif stack[-1] == c: # Close group
                string.append(block+c)
                stack = stack[:-1]
                block = ""
            else:
                stack.append(c)
        elif stack == []:  # Is on root nesting, and delimiter is reached
            string.append(c)
        else:
            block += c

    if block:
        string.append(block)

    return string

def group_brackets(s, valid_grouping=CharacterSets.brackets, escape_token="\\"):
    opening = {g[0]: g[1] for g in valid_grouping}
    closing = {g[1]: g[0] for g in valid_grouping}
    stack = []
    block = ""
    string = []
    for c in escape(s, token=escape_token):
        if c in opening:  # Open group ex: (
            stack.append(c)

        if c in closing:  # Close group ex: )
            if closing[c] != stack[-1]:  # Unbalanced brackets
                raise SyntaxError("Unbalanced brackets")
            stack = stack[:-1]
            block += c
            if stack == []:
                string.append(block)
                block = ""
                
        elif stack == []:  # Is on root nesting, and delimiter is reached
            string.append(c)
        else:
            block += c
    return string

def group(s,valid_grouping=CharacterSets.grouping, escape_token="\\"):
    quote_grouping = []
    bracket_grouping = []

    for g in valid_grouping:
        if g[0] == g[1]:
            quote_grouping.append(g[0])
        else:
            bracket_grouping.append(g)
    
    return group_brackets(group_quotes(s, quote_grouping, escape_token), bracket_grouping, escape_token)

def escape(s, token="\\"):
    """ Group escaped characters into one cell """
    chrs = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == token:
            chrs.append(c+s[i+1])
            i += 1
        else:
            chrs.append(c)
        i += 1
    return chrs


def rcut(string, pattern):
    if string.endswith(pattern):
        return string[:-len(pattern)]
    return string


def lcut(string, pattern):
    if string.startswith(pattern):
        return string[len(pattern):]
    return string