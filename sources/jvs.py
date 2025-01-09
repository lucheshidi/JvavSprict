import re
import sys
import os
import traceback


class JvavSprictInterpreter:
    def __init__(self):
        self.variables = {}  # 全局变量
        self.functions = {}  # 函数列表

    def execute(self, code):
        """执行代码"""
        # print("running program...")  # 第一步：代码进入执行方法
        lines = code.split("\n")
        # print(f"The code is divided into {len(lines)} lines")  # 第二步：代码分行后，打印行数

        try:
            self.process_lines(lines)

            # 打印解析的函数信息
            # print(f"A list of resolved functions: {list(self.functions.keys())}")

            # 自动调用 main()
            if "main" in self.functions:
                print("Locate the main function and start executing\n")
                # print("=================LOG=OUTPUT=================\n")
                self.call_function("main", [])
        except Exception as e:
            # 捕获任何错误并打印堆栈信息
            self.print_exception_trace(-1, "Exceptions to code execution", e)

    def process_lines(self, lines, start=0):
        """逐行处理代码"""
        i = start
        while i < len(lines):
            try:
                line = lines[i].strip()
                if not line or line.startswith("//"):  # 跳过空行或注释
                    i += 1
                    continue

                if line.startswith("var "):
                    self.handle_variable_declaration(line)
                elif line.startswith("func "):
                    i = self.handle_function_definition(lines, i)
                elif line.startswith("log("):
                    self.handle_log(line)
                elif re.match(r".*\(.*\)", line):
                    self.handle_function_call(line)
                else:
                    raise SyntaxError(f"Unknown statement: {line}")  # 引发自定义错误
                i += 1
            except Exception as e:
                self.print_exception_trace(i, line, e)
                break  # 停止程序

    def handle_variable_declaration(self, line):
        """处理变量声明"""
        try:
            pattern = r"var\s+(\w+)\s*=\s*(.*)"
            match = re.match(pattern, line)
            if match:
                var_name = match.group(1)
                expression = match.group(2)
                self.variables[var_name] = self.evaluate_expression(expression)
            else:
                raise SyntaxError(f"Variable declaration syntax error: {line}")
        except Exception as e:
            self.print_exception_trace(-1, line, e)
            raise e

    def handle_function_definition(self, lines, start):
        """处理函数定义"""
        pattern = r"func\s+(\w+)\((.*?)\)\s*\{"
        match = re.match(pattern, lines[start].strip())
        if match:
            func_name = match.group(1)
            params = [param.strip() for param in match.group(2).split(",") if param.strip()]
            body_lines = []
            i = start + 1
            brace_count = 1

            while i < len(lines):
                line = lines[i].strip()
                if "{" in line:
                    brace_count += 1
                if "}" in line:
                    brace_count -= 1
                    if brace_count == 0:
                        break  # 函数结束

                body_lines.append(line)
                i += 1

            self.functions[func_name] = (params, body_lines)
            return i
        else:
            raise SyntaxError(f"Function definition syntax error: {lines[start]}")

    def handle_function_call(self, line):
        """处理函数调用"""
        pattern = r"(\w+)\((.*)\)"
        match = re.match(pattern, line)
        if match:
            func_name = match.group(1)
            args = [arg.strip() for arg in match.group(2).split(",") if arg.strip()]
            if func_name in self.functions:
                self.call_function(func_name, args)
            else:
                raise NameError(f"Unknown function: {func_name}")
        else:
            raise SyntaxError(f"Function call syntax ERROR: {line}")

    def call_function(self, func_name, args):
        """调用已定义的函数"""
        params, body_lines = self.functions[func_name]

        if len(args) != len(params):
            raise ValueError(f"The number of parameters does not match: {func_name}")

        backup_vars = self.variables.copy()  # 备份全局变量，防止污染
        for param, arg in zip(params, args):
            self.variables[param] = self.evaluate_expression(arg)
        self.process_lines(body_lines)  # 递归执行代码块
        self.variables = backup_vars  # 恢复上下文

    def handle_log(self, line):
        """处理日志输出"""
        pattern = r"log\((.+)\)"
        match = re.match(pattern, line)
        if match:
            content = match.group(1).strip()
            if content in self.variables:
                print(self.variables[content])
            else:
                print(content.strip('"').strip("'"))  # 打印字符串
        else:
            print(f"log() Grammatical errors: {line}")


    def evaluate_expression(self, expr):
        """求值表达式"""
        for var, val in self.variables.items():
            expr = expr.replace(var, str(val))  # 替换变量值
        try:
            return eval(expr)
        except Exception as e:
            self.print_exception_trace(-1, expr, e)
            return None

    def print_exception_trace(self, line_number, line, exception):
        """打印类似 Java 风格的错误堆栈信息"""
        print("\n", "=" * 40, "Error text", "=" * 40, "\n")
        print(f"{type(exception).__name__}: {str(exception)}")
        if line_number >= 0:
            print(f"    at line {line_number + 1}: {line.strip()}")  # 打印出问题的行
        tb_lines = traceback.format_exc().strip().splitlines()
        tb_lines = tb_lines[:-1]  # 去掉 "Traceback (most recent call last):"
        for tb_line in tb_lines:
            if "File" in tb_line:
                print(f"    at {tb_line.strip()}")


if __name__ == "__main__":
    print("Launching JvavSprict...")  # 程序启动调试信息
    try:
        if len(sys.argv) < 2:
            print("Please write JvavSprict file path, example: ./jvs demo.jvs")
            sys.exit(1)

        file_path = sys.argv[1]
        # print(f"compile file: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            program = file.read()

        # print("file read successful，start running...")
        interpreter = JvavSprictInterpreter()
        interpreter.execute(program)

        # print("\n==================LOG=END==================")
        print("\nProcess finished.")

    except Exception as e:
        # 捕获异常并打印 Java 风格的错误堆栈
        print("\n", "=" * 40, "Error text", "=" * 40, "\n")
        print(f"{type(e).__name__}: {str(e)}\n")
        traceback.print_exc()
        sys.exit(1)
