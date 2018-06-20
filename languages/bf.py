import random

async def interpret(program, _, stdin, stdout):
    # make sure brackets match
    count = 0
    for i in program:
        if i == "[":
            count += 1
        elif i == "]":
            count -= 1
        if count < 0:
            return stdout.write("unmatched brackets")
    if count != 0: 
        return stdout.write("unmatched brackets")
    cells = [0]
    pointer = 0
    idx = 0
    while idx < len(program):
        char = program[idx]
        if char == "+":
            cells[pointer] = (cells[pointer] + 1) if cells[pointer] < 255 else 0
        elif char == "-":
            cells[pointer] = (cells[pointer] - 1) if cells[pointer] > 0 else 255
        elif char == "<":
            if pointer > 0:
                pointer -= 1
            else:
                cells.insert(0, 0)
        elif char == ">":
            try:
                cells[pointer+1]
            except IndexError:
                cells.append(0)
            pointer += 1
        elif char == "[":
            if cells[pointer] == 0:
                extra = 0
                for pos, char in enumerate(program[idx+1:]):
                    if char == "[":
                        extra += 1
                    elif char == "]":
                        if extra:
                            extra -= 1
                        else:
                            idx += pos
                            break
        elif char == "]":
            if cells[pointer] == 0:
                pass
            else:
                extra = 0
                for pos, char in reversed(list(enumerate(program[:idx]))):
                    if char == "]":
                        extra += 1
                    elif char == "[":
                        if extra:
                            extra -= 1
                        else:
                            idx = pos
                            break
        elif char == ",":
            cells[pointer] = ord(await stdin.read(1))
        elif char == ".":
           await stdout.write(chr(cells[pointer]))
           if random.random() > 0.9:
               await stdout.flush()
        idx += 1
