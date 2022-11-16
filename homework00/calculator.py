import math
import typing as tp


def calculator(num_1: float, num_2: float, command: str) -> tp.Union[float, str]:
    if command == "+":
        return num_1 + num_2  # sum
    if command == "-":
        return num_1 - num_2  # diff
    if command == "*":
        return num_1 * num_2  # multiply
    if command == "/":  # divide
        if num_2 != 0:
            return num_1 / num_2
        else:
            return "You can't divide by zero, enter another number"
    if command == "":  # degree
        return num_1**num_2
    if command == "log":
        return math.log(num_1, num_2)
    if command == "sqr":
        return num_1**2  # square
    if command == "sin":
        return math.sin(num_1)
    if command == "cos":
        return math.cos(num_1)
    if command == "tg":
        return math.tan(num_1)
    if command == "ln":
        return math.log(num_1)
    if command == "lg":
        return math.log10(num_1)
    return f"Unknown operator: {command!r}."


def match_case_calc_with_two_numbers(num_1: float, num_2: float, command: str) -> tp.Union[float, str]:
    match command:
        case "+":
            return num_1 + num_2
        case "-":
            return num_1 - num_2
        case "*":
            return num_1 * num_2
        case "/" if num_2 != 0:
            return num_1 / num_2
        case "":
            return num_1**num_2
        case "log":
            return math.log(num_1, num_2)
        case _:
            return f"Unknown operator: {command!r}."
    return f"Unknown operator: {command!r}."


def match_case_calc_with_one_number(num_1: float, command: str) -> tp.Union[float, str]:
    match command:
        case "sin":
            return math.sin(num_1)
        case "cos":
            return math.cos(num_1)
        case "tg":
            return math.tan(num_1)
        case "ln":
            return math.log(num_1)
        case "lg":
            return math.log10(num_1)
        case _:
            return f"Unknown operator: {command!r}."


if __name__ == "__main__":
    for_one_number = ["sin", "cos", "tan", "log", "lg"]
    for_two_numbers = ["+", "-", "*", "/", "**", "log"]
    while True:
        COMMAND = input("Enter command > ")
        if COMMAND.isdigit() and int(COMMAND) == 0:
            break
        if COMMAND in for_two_numbers:
            NUM_1 = float(input("First number > "))
            NUM_2 = float(input("Second number > "))
            print(match_case_calc_with_two_numbers(NUM_1, NUM_2, COMMAND))
        elif COMMAND in for_one_number:
            NUM_1 = float(input("Number > "))
            print(match_case_calc_with_one_number(NUM_1, COMMAND))
