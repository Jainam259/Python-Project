# Calculator With History Save

HISTORY_FILE = "history.txt"

def show_history():
    file = open(HISTORY_FILE,'r')
    lines = file.readlines()
    if len(lines) == 0:
        print("No history found!")
    else:
        for line in reversed(lines):
            print(line.strip())
    file.close()

def clear_history():
    file = open(HISTORY_FILE,'w')
    file.close()
    print("History cleard..")

def save_to_history(equation,result):
    file = open(HISTORY_FILE,'a')
    file.write(equation + " = " + result + "\n")
    file.close()

def calculate(user_input):
    parts = user_input.split()

    if(len(parts) < 3):
        print("Invalid input.Use format:number operator number (e.g 8 + 8)")
        return 

    result = eval(user_input)

    if int(result) == result:
        result = int(result)
    print("Result:",result)
    save_to_history(user_input,str(result))

def main():
    print("----- Simple Calculator (type history,clear,exit) -----")
    while True:
        user_input = input("Enter Calculatons (+ - * /) or Command (history,clear or exit):")
        if user_input == 'exit':
            print("Good bye..")
            break
        elif user_input == 'history':
            show_history()
        elif user_input == 'clear':
            clear_history()
        else:
            calculate(user_input)

main()


