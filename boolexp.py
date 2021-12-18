import re

bool_operator = ["!", "¬", "⊕", "^", "*", "∧", "+",  "∨", "→", "≡", "|", "↓"]


class boolexp(object):
    def __init__(self, infix_exp=None):
        self.infix_exp = infix_exp
        self.lexemes = []
        self.suffix_exp = []

    def is_variable(self, item):
        var = re.match(r'[a-z][0-9]+', item, re.I)
        if var and var.group() == item:
            return True
        else:
            return False

    def split2lexemes(self):
        self.lexemes = re.split('([a-zA-Z][0-9]+|[0-9]|\D)', self.infix_exp)
        for item in self.lexemes:  # 去除空字符
            if item == '':
                self.lexemes.remove(item)

    def infix2suffix(self):
        stack = []  # 栈

        self.infix_exp = self.infix_exp.replace(" ", "")  # 去除空行

        self.split2lexemes()  # 将中缀表达式分割成一个个元素
        for item in self.lexemes:
            if self.is_variable(item) or item.isnumeric():  # 如果当前字符为变量,或者为常量,那么直接放入结果列表
                self.suffix_exp.append(item)
            else:  # 如果当前字符为一切其他操作符
                if len(stack) == 0:  # 如果栈空，直接入栈
                    stack.append(item)
                elif item == '(':
                    stack.append(item)
                elif item == ')':  # 如果右括号则全部弹出（碰到左括号停止）
                    t = stack.pop()
                    while t != '(':
                        self.suffix_exp.append(t)
                        t = stack.pop()
                elif item == '≡' and stack[len(stack) - 1] in '→∨+!¬⊕∧*':
                    if stack.count('(') == 0:  # 如果有左括号，弹到左括号为止
                        while stack:
                            self.suffix_exp.append(stack.pop())
                    else:  # 如果没有左括号，弹出所有
                        t = stack.pop()
                        while t != '(':
                            self.suffix_exp.append(t)
                            t = stack.pop()
                        stack.append('(')
                    stack.append(item)  # 弹出操作完成后将 equal操作入栈
                elif item == '→' and stack[len(stack) - 1] in '∨+!¬⊕∧*':
                    if stack.count('(') == 0:  # 如果有左括号，弹到左括号为止
                        while stack:
                            self.suffix_exp.append(stack.pop())
                    else:  # 如果没有左括号，弹出所有
                        t = stack.pop()
                        while t != '(':
                            self.suffix_exp.append(t)
                            t = stack.pop()
                        stack.append('(')
                    stack.append(item)  # 弹出操作完成后将 impl操作入栈
                elif item in '∨+' and stack[len(stack) - 1] in '!¬⊕∧*':
                    if stack.count('(') == 0:  # 如果有左括号，弹到左括号为止
                        while stack:
                            self.suffix_exp.append(stack.pop())
                    else:  # 如果没有左括号，弹出所有
                        t = stack.pop()
                        while t != '(':
                            self.suffix_exp.append(t)
                            t = stack.pop()
                        stack.append('(')
                    stack.append(item)  # 弹出操作完成后将or操作入栈
                elif item in '∧*' and stack[len(stack) - 1] in '!¬⊕':
                    if stack.count('(') == 0:  # 如果有左括号，弹到左括号为止
                        while stack:
                            self.suffix_exp.append(stack.pop())
                    else:  # 如果没有左括号，弹出所有
                        t = stack.pop()
                        while t != '(':
                            self.suffix_exp.append(t)
                            t = stack.pop()
                        stack.append('(')
                    stack.append(item)  # 弹出操作完成后将and操作入栈
                elif item in '⊕' and stack[len(stack) - 1] in '!¬':
                    if stack.count('(') == 0:  # 如果有左括号，弹到左括号为止
                        while stack:
                            self.suffix_exp.append(stack.pop())
                    else:  # 如果没有左括号，弹出所有
                        t = stack.pop()
                        while t != '(':
                            self.suffix_exp.append(t)
                            t = stack.pop()
                        stack.append('(')
                    stack.append(item)  # 弹出操作完成后将xor操作入栈
                elif item in bool_operator:
                    stack.append(item)
                else:
                    print("非法操作符!")
                    break
        # 表达式遍历完了，但是栈中还有操作符不满足弹出条件，把栈中的东西全部弹出
        while stack:
            self.suffix_exp.append(stack.pop())


if __name__ == "__main__":
    expression = "x1*(¬x2+x3)*x4"
    exp = boolexp(expression)
    exp.infix2suffix()
    print(exp.suffix_exp)
