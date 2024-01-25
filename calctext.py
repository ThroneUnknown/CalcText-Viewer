import sys


COLORS = ["BLUE", "RED", "BLACK", "MAGENTA", "GREEN", "ORANGE", "BROWN", "NAVY", "LTBLUE", "YELLOW", "WHITE", "LTGRAY", "MEDGRAY", "GRAY", "DARKGRAY"]
# Widths of all characters in pixels
CHARWIDTHS = {
    'a': 10,
    'b': 8,
    'c': 8,
    'd': 8,
    'e': 8,
    'f': 8,
    'g': 8,
    'h': 8,
    'i': 4,
    'j': 8,
    'k': 9,
    'l': 6,
    'm': 12,
    'n': 8,
    'o': 9,
    'p': 8,
    'q': 9,
    'r': 8,
    's': 7,
    't': 8,
    'u': 10,
    'v': 8,
    'w': 12,
    'x': 9,
    'y': 8,
    'z': 8,
    'A': 8,
    'B': 8,
    'C': 8,
    'D': 8,
    'E': 8,
    'F': 8,
    'G': 8,
    'H': 8,
    'I': 9,
    'J': 8,
    'K': 8,
    'L': 8,
    'M': 10,
    'N': 9,
    'O': 8,
    'P': 8,
    'Q': 8,
    'R': 8,
    'S': 8,
    'T': 8,
    'U': 9,
    'V': 10,
    'W': 10,
    'X': 9,
    'Y': 10,
    'Z': 8,
    'θ': 8,
    ' ': 2,
    "'": 4,
    '"': 8,
    '{': 8,
    '}': 8,
    '(': 6,
    ')': 6,
    '}': 8,
    '[': 6,
    ']': 6,
    '0': 8,
    '1': 8,
    '2': 8,
    '3': 8,
    '4': 8,
    '5': 8,
    '6': 8,
    '7': 8,
    '8': 8,
    '9': 8,
    '!': 4,
    '@': 12,
    '#': 12,
    '$': 10,
    '%': 10,
    '^': 8,
    '&': 10,
    '*': 10,
    '+': 8,
    '-': 8,
    '/': 8,
    '_': 8,
    '=': 8,
    ',': 5,
    '.': 4,
    '?': 8,
    '\\': 8,
    '|': 4,
    ';': 8,
    ':': 4,
    'π': 12,
    '√': 11,
    '<': 8,
    '>': 8,
    '≤': 10,
    '≥': 10,
    '≠': 14,
    '~': 6,  # Negative symbol
    '`': 8
}
tags = {  # Must be single character
    'l': ["(+12,)"],  # Default line end behavior
    'p': ["Pause ", "ClrDraw ", "(0,0)"],  # Default new page behvavior
    'w': ["(+12,)"],  # Default line wrap behavior
    'b': ["__BLANK"]  # Default behavior at beginning of line
}
tag_triggers = {
    'l': ",,,",
    'p': ";;;"
}
inverse_triggers = { v:k for k, v in tag_triggers.items()}
tag_editing = []
settings = {  # Keys MUST be 5 characters
    "TCHAR": ",",  # Character before text to use Text( for
    "WWRAP": 1,  # Wrap words separated by SPLIT instead of just characters
    "SPLIT": " ",  # Character that splits words to be wrapped
    "NPAGE": 1,  # Triggers new page code
    "NLINE": 1,  # Triggers new line code
    "BLINE": 1,  # Triggers beginning line code
    "EMPTYLINE": '__BLANK',  # Skips without adding anything to line
    "SPLITCHAR": "`",  # Splits lines, doesn't necessarily need to be a single character
    "SPLITLINES": 1  # Enables having multiple commands in one line, separated by SPLITCHAR
}


# Processes tags that are being edited, and check if any are in the first place
def tag_editor(lines):
    global tags
    
    # Note: tags are only updated when outermost tag is closed
    # Find all opened and closed tags
    opened = []
    opositions = []  # Position of opening tag, in format (line, character)
    closed = []
    cpositions = []
    
    # Find opened and closed tags, as well as their position
    for i in range(len(lines)):
        checker = ""
        for j in range(len(lines[i])):
            if lines[i][j] == "<":
                checker = "<"
            elif lines[i][j] == "/" and checker == "<":
                checker = "</"
            elif lines[i][j] == ">" and len(checker) == 2 and "/" not in checker:  # Tag is opened
                opened.append(checker[1])
                opositions.append([i, j+1])
            elif lines[i][j] == ">" and len(checker) == 3 and checker[:2] == "</":  # Tag is closed
                closed.append(checker[2])
                cpositions.insert(opened.index(checker[2]), [i, j-3])
            else:
                checker = checker + lines[i][j]
    # Return current line to be interpreted
    if opened == []:
        return lines[-1]
    # If top level tag not closed, return all current lines that will be recorded
    elif opened[0] not in closed:
        return lines[:]
    # Write to tag dictionary (only want the outermost one written)
        # Slice lines so that lines with opening and closing tags only have relevant instructions
    sliced = lines[:]
    # If tag is opened and closed in same line, list will update that by only changing the relevant line.
    if opositions[0][0] == cpositions[0][0]:
        sliced = [sliced[0][opositions[0][1]:cpositions[0][1]]]
    else:
        sliced = sliced[opositions[0][0]:cpositions[0][0] + 1]
        sliced[0] = sliced[0][opositions[0][1]:]
        sliced[-1] = sliced[-1][:cpositions[0][1]]
    
    # Add tag to dictionary
    tags[opened[0]] = sliced[:]
    
    # Return remainder of line not in tags
    # If line would be blank, just make it skip
    if lines[-1][cpositions[0][1]+4:] == "":
        return settings["EMPTYLINE"][:]
    else:
        return lines[-1][cpositions[0][1]+4:]


# Processes a number that can be an increment, nothing, or set it
def parse_number(number, current):
    if number == "":
        return current
    if number[0] == "-":
        return current - int(number[1:])
    elif number[0] == "+":
        return current + int(number[1:])
    else:
        return int(number)


# Interpret line of code
def parse_line(baseline, r=0):
    # Easier to just use a function for this rather than loop (due to recursion),
    # so global variables must be used
    global page_position
    global newf
    global settings
    global color
    global tags
    global tag_editing

    # Check for tags
    tag_check = ""
    prev_check = tag_editing + [baseline]
    line = baseline[:]
    while True:
        tag_check = tag_editor(prev_check)
        if type(tag_check) == list:  # Editing tag, skip interpretation
            tag_editing = tag_check[:]
            return None
        # Closed first tag (or there never was one)
        elif type(tag_check) == str:
            tag_editing = []
            # Are definitely not other tags
            if tag_check == settings["EMPTYLINE"]:
                return None
            # Nothing changed since last iteration
            elif [tag_check] == prev_check:
                line = tag_check[:]
                break
            # May be other tags
            else:
                prev_check = [tag_check[:]]
    
    line = tag_check[:]
    # Blank lines ignored, comes first to avoid IndexError
    if line == "":
        newf.append(line[:])
        return None
    # Check if line should be skipped completely
    elif line == settings["EMPTYLINE"]:
        return None
    # Check if the line should be split up with multiple commands
    elif settings["SPLITCHAR"] in line and settings["SPLITLINES"]:
        for split_line in line.split(settings["SPLITCHAR"]):
            parse_line(split_line)
        return None
    
    # Check for setting change
    if line.split(" ")[0] in list(settings.keys()):
        changes = line.split(" ")
        if changes[1] == "1" or changes[1] == "0":  # Boolean change
            settings[changes[0]] = int(changes[1])
        else:
            settings[change[0]] = line[len(changes[0])+1:]
    # Check for tag trigger changes
    elif line[1:9] == "TRIGGER " and line[0] in list(CHARWIDTHS.keys()):
        tag_triggers[line[0]] = line[9:]
        inverse_triggers[line[9:]] = line[0]
    # Change color
    elif line in COLORS:
        newf.append(f"TextColor({line}")
        color = line[:]
    # Change cursor position
    elif line[0] == "(":
        parsing = line[1:-1].split(",")
        page_position = [parse_number(parsing[0], page_position[0]), 
        parse_number(parsing[1], page_position[1])]
        if page_position[1] >= 264:
            parse_line(tag_triggers["l"])
        elif page_position[0] >= 154:
            parse_line(tag_triggers["p"])
    # New line
    elif line == tag_triggers["l"]:
        try:
            for instruction in tags["l"]:
                if instruction[0] == settings["TCHAR"]:
                    newf.append(f'Text({page_position[0]},{page_position[1]},"{instruction[1:]}"')
                    continue
                parse_line(instruction)
        except RecursionError:
            print("NEW LINE RECURSION ERROR")
            quit()
            raise RecursionError
            # raise RecursionError
    # New page
    elif line == tag_triggers["p"]:
        try:
            for instruction in tags["p"]:
                parse_line(instruction)
        except RecursionError:
            print("NEW PAGE RECURSION ERROR")
            raise RecursionError
    # Other tags are triggered:
    elif line in list(inverse_triggers.keys()):
        for instruction in tags[inverse_triggers[line]]:
            parse_line(instruction)
    # Text( function is used here
    elif line[0] == settings["TCHAR"]:
        current = ""
        # Save old position and color in case new page is needed
        pxlcount = page_position[1]
        oldcolor = color[:]
        if settings["BLINE"]:
            for instruction in tags["b"]:
                if instruction[0] == settings["TCHAR"]:
                    newf.append(f'Text({page_position[0]},{page_position[1]},"{instruction[1:]}"')
                else:
                    parse_line(instruction)
        oldposition = page_position[1]
        if settings["WWRAP"]:
            # For word wrap, each word is taken into account for determining pixel width rather than character
            word_list = line[1:].split(settings["SPLIT"])  
            words = [word + " " for word in word_list[:-1]]
            words.append(word_list[len(word_list)-1])
            for word in range(len(words)):
                for char in words[word]:
                    if char[:] not in CHARWIDTHS:
                        CHARWIDTHS[char] = 8
                # Need to word wrap
                if pxlcount + sum([CHARWIDTHS[char] for char in words[word]]) > 264:
                    newf.append(f'Text({page_position[0]},{page_position[1]},"{current}"')
                    for instruction in tags["w"]:
                        parse_line(instruction)
                        parse_line(f"(,{oldposition})")
                    # Page wrap
                    if page_position[0] >= 152 and settings["NPAGE"] == 1:
                        parse_line(tag_triggers["p"])
                        parse_line(oldcolor)
                        parse_line(f"(,{oldposition})")
                    current = ""
                    pxlcount = page_position[1]
                current += words[word]
                pxlcount += sum(CHARWIDTHS[char] for char in words[word])
        else:
            for char in range(len(line[1:])):
                if char not in CHARWIDTHS:
                    CHARWIDTHS[char] = 8
                # Word wrap (but only on a character basis, not whole words)
                if pxlcount + CHARWIDTHS[line[1 + char]] >= 264:
                    newf.append(f'Text({page_position[0]},{page_position[1]},"{current}"')
                    for instruction in tags["w"]:
                        parse_line(instruction)
                        parse_line(f"(,{oldposition})")
                    # Page wrap
                    if page_position[0] >= 152 and settings["NPAGE"] == 1:
                        parse_line(tag_triggers["p"])
                        parse_line(oldcolor)
                        parse_line(f"(,{oldposition})")
                    current = ""
                    pxlcount = page_position[1]
                current += line[1 + char]
                pxlcount += CHARWIDTHS[line[1 + char]]
        if current != "":
            newf.append(f'Text({page_position[0]},{page_position[1]},"{current}"')
        if settings["NLINE"]:
            parse_line(tag_triggers["l"])
    # Everything else is assumed to be a proper TI-BASIC command
    else:
        newf.append(line)


# Run program
if __name__ == "__main__":
    args = sys.argv
    with open(args[1], "r") as f:
        file = f.read().split("\n")

    # Default file variables
    color = "BLACK"
    page_position = [0,0]
    
    # Keep track of program flow
    newf = []
    for line in file:
        parse_line(str(line))
    
    # Write to output file
    newf = [newf[i] + "\n" for i in range(len(newf))]
    with open(args[2], "w") as f:
        f.writelines(newf)
    
    print(f"{len(file)} lines processed, {len(newf)} lines written to {args[2]}")
