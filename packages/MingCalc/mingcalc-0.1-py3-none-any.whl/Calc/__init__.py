def calc(num1,num2,op):
    
    match op :
        case "+" : return num1 + num2
        case "-" : return num1 - num2
        case "*" : return num1 * num2
        case "/" : 
            if num2 != 0 :
                return num1 / num2 
            else : return "Divisio by zero"
        case "%" : return num1 % num2
        case _   : return "Invalid Operator!"
