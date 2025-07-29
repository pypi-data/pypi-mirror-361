import io
import ast
import json
import tiktoken
from contextlib import redirect_stdout


class ChatCompletionHelper():
    """
    OpenAI ChatCompletion API를 사용하는데 도움을 주는 각종 함수들 모음

    사용 예제 참조: https://www.notion.so/bitmango-bi/ChatCompletionHelper-Chat-Completion-API-20f72aed4cbd4df489fb11466631a776

    == Arguments ==
    class 로드시 다음의 변수들을 입력해줘야함. *은 required
    *client - openai.OpenAI()
    model - 사용할 GPT 모델 이름. 디폴트값은 'gpt-4-turbo'
    code_interpreter - True/False, python code interpreter를 사용할 경우 True. 디폴트값은 False.
    functions - GPT가 사용하게할 custom function 목록. OpenAI json 포멧을 따라야 함.
        디플트값은 None으로 이 경우엔 custom function을 사용하지 않음
    token_limit - 토큰수가 token_limit을 넘어갈 경우 thread에서 가장 오래된 대화부터 한개씩 삭제함.
        디폴트값은 127000으로 gpt-4-turbo에 맞춤
    """

    def __init__(
            self,
            client,
            model:str='gpt-4-turbo',
            code_interpreter:bool=False,
            functions:list=None,
            token_limit:int=127000
        ) -> None:

        # client 등록
        if client is None:
            print('ERROR: client is None.')
            return None
        self.client = client

        if functions is None:
            self.functions = []

        # model 등록
        self.model = model

        # functions 등록
        self.functions = functions
        if code_interpreter:
            self.functions.append(self.build_exec_python_function_call())

        # token_limit 등록
        self.token_limit = token_limit

        # initialize messages
        self.messages = []

        # streaming을 위한 placeholder 생성
        self.content_holder = ""
        self.verbose_holder = ""

        return None

    def run(
            self, 
            user_query:str, 
            messages:list, 
            global_vars:dict=globals()
        ):
        # == messages 포멧 예제 == (OpenAI format을 따름)
        # [
        #   {'role': 'system', 'content': ...},
        #   {'role': 'user', 'content': ...},
        #   {'role': 'assistant', 'content': None, 'tool_calls': [id, type, {'name', 'arguments'}]}
        #   {'role': 'function', 'tool_call_id': ..., 'name': ..., 'content': ...},
        #   {'role': 'assistant', 'content': ...}
        # ]
        # ====================

        # 이 함수는 user_query를 messages에 추가하고,
        # messages를 GPT에게 입력시킨 후 streaming response를 yield한다 > python generator를 리턴한다
        # global_vars는 code interpreter 등에서 글로벌 변수로 사용할 변수들 목록

        # class 내에서 사용할 messages, log_messages 등록
        self.messages = messages

        # append user query
        user_message = {'role': 'user', 'content': user_query}
        self.messages.append(user_message)

        # check token limits
        self.messages = self.check_token_limits(
                messages=self.messages,
                token_limit=self.token_limit
            )

        # get streaming response
        return self.get_response(global_vars)

    def num_tokens_from_string(self, string:str, encoding_name="gpt-4") -> int:
        # 주어진 스트링에 대해 openAI 기준으로 토큰 수를 리턴해주는 함수 - tiktoken 사용
        encoding = tiktoken.encoding_for_model(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def num_tokens_from_messages(self, messages:list, encoding_name="gpt-4") -> int:
        # 메세지 쓰레드의 총 토큰수 계산
        # 메세지 쓰레드의 형태는 다음과 같은 형태로 가정
        # [{'role': <string>, 'content': <string>}, {'role': <string>, 'content': <string>}, ..., ]
        total_tokens = 0
        for message in messages:
            total_tokens += self.num_tokens_from_string(message['content'], encoding_name)
        return total_tokens

    def check_token_limits(
            self, 
            messages:list, 
            token_limit=15000, 
            encoding_name="gpt-4"
        ) -> list:
        # 쓰레드의 총 토큰수가 token_limit을 넘어가는 경우 제일 오래된 대화를 삭제하고 리턴
        # '대화'의 정의:
        # role이 user인 경우 다음 메세지에 user가 재등장하기 전까지(또는 messages가 끝날때까지)의 모든 메세지를 뜻함.
        i = 0
        while self.num_tokens_from_messages(messages, encoding_name) > token_limit:
            # 예외 상황(에러 처리): 마지막 메세지일때 - 더이상 삭제할 대화가 없어 토큰 수를 줄일 수 없는 상황
            if i == len(messages):
                print('ERROR: Cannot reduce tokens. Too little dialogues.')
                return messages

            # 대화의 시작점 찾기
            if messages[i]['role'] == 'user':
                target_idx = [i]
                
                # 대화의 종료점 찾기
                for j in range(i+1, len(messages)):
                    # while loop를 위해 i값 업데이트
                    i = j
                    if messages[j]['role'] == 'user':
                        break
                    else:
                        target_idx.append(j)

                # 대화 삭제 - 리스트를 index 기준으로 삭제하기 위해 sort, reverse 활용
                for target in sorted(target_idx, reverse=True):
                    del messages[target]
            else:
                i += 1
        return messages

    def call_function(self, name:str, arguments:str, global_vars:dict=None) -> str:
        # run name(function) with given arguments
        # GPT tool call 기능을 위한 함수, arguments는 tool call의 arguments를 뜻함
        # global_vars - 적용할 function들의 list
        # function message의 content(str)를 리턴한다.

        # redirect exec_python
        if 'exec_python' not in global_vars:
            global_vars['exec_python'] = self.exec_python

        if global_vars is None:
            global_vars = {}

        try:
            arguments_dict = json.loads(arguments, strict=False)
            return global_vars[name](**arguments_dict)
        except Exception:
            pass

        try:
            arguments_dict = ast.literal_eval(arguments)
            return global_vars[name](**arguments_dict)
        except Exception:
            pass

        # 둘 다 실패시, 직접 파싱 시도(dict 형태가 아닌 일반 string으로 만들기)
        # => 앞부분 "{'code':'"와 뒷부분 "'}" 띄어내기
        if arguments[0] == '{' and arguments[-1] == '}':
            arguments = arguments[9:-2]

        # dict형태가 아닌 string으로 줄때도 있음
        if arguments[0] != '{' and arguments[1] != '{':
            return global_vars[name](arguments)
        else:
            # json, ast 둘 다 실패시 에러메세지를 GPT에게 쏘기
            print('\n####\njson load failed')
            err_msg = 'ERROR: Could not parse given arguments into proper python dictionary.'
            return err_msg

    def build_exec_python_function_call(self) -> dict:
        # ChatCompletion API의 functions에 등록하기 위한 code interpreter JSON
        # name: 스크립트에서 실행할 함수명
        tool = {
            'type': 'function',
            'function': {
                'name': 'exec_python',
                'description': 'Run python codes and return results.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'code': {
                            'type': 'string',
                            'description': 'python codes to run'
                        }
                    },
                    'required': ['code']
                }
            }
        }
        return tool

    def exec_python(self, code:str, global_vars:dict=globals(), local_vars:dict=locals()) -> str:
        # ----------------------------------
        # 파이썬 code string을 받아서
        # python interpreter(CLI)처럼 실행하고 display되는 결과(str)를 리턴하는 함수
        #
        # 작동방식:
        # code string에서 마지막으로 instance call하는 라인을 찾아서 그 부분만 eval
        # 그 외엔 exec
        # stdout은 variable로 따로 저장
        # ----------------------------------
        try:
            parsed = ast.parse(code)
        except Exception as e:
            return e
        last_instance = None

        # loop backwards, catch the last instance call
        if len(parsed.body) > 1:
            for i in range(len(parsed.body)-1,-1,-1):
                if isinstance(parsed.body[i], ast.Expr):
                    last_instance = ast.unparse(parsed.body[i])
                    break

        if last_instance:
            with redirect_stdout(io.StringIO()) as f:
                code_front = '\n'.join([ast.unparse(body) for body in parsed.body[:i]])
                code_back = '\n'.join([ast.unparse(body) for body in parsed.body[i+1:]])

                try:
                    exec(code_front, global_vars, local_vars)
                    result = eval(last_instance, global_vars, local_vars)
                    exec(code_back, global_vars, local_vars)
                except Exception as e:
                    return e

                if result is None:
                    result = f.getvalue()
            return result
        return None

    def create_messages(self, instruction_filename:str) -> list:
        # instruction_filename의 내용을 불러온 후, 오늘의 일자를 추가해주고
        # 이를 system message로 변환한 후 messages list로 리턴한다.
        if instruction_filename is None:
            return []
        instructions = open(instruction_filename, 'r').read()
        today = dt.date.today().strftime("%B %d, %Y")
        instructions += f"\nToday's date is {today}."
        system_message = {'role': 'system', 'content': instructions}
        return [system_message]

    def get_response(self, global_vars:dict=globals()):
        # ----------------------------------
        # GPT의 response가 일반 메세지인 경우와 function call인 경우 모두를 다루는 함수
        # Chat Completions API의 streaming으로 처리하며, function call의 경우 재귀함수로 처리함
        # 메시지 쓰레드(마지막이 user query인 것으로 가정)를 input으로 받음
        # streaming delta를 output으로 yield
        # ----------------------------------

        # ----------------------------------
        # Arguments
        # global_vars - code interpreter 등 실행시 변수를 인식해야하는 경우 global 변수 지정
        # ----------------------------------

        # get response
        try:
            response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.functions,
                    stream=True
                )
        except Exception as e:
            print(f"ERROR: {e}")
            return None

        # create/reset tool call placeholder
        tool_call_holder = {'id': "", 'index': 0, 'name': "", 'arguments': ""}

        # create a tool calls holder
        tool_calls = []

        # deal with streaming chunks
        for chunk in response:
            #print(f"\n#######\n{chunk}")

            # get chunk choice
            choice = chunk.choices[0]

            # if streaming on-going
            if not choice.finish_reason:

                # tool_call 다루기
                if choice.delta.tool_calls:
                    # tool call이 한번에 여러번 등장하는 경우(finish_reason이 뜨기 전에 여러번 뜨는 경우)
                    # 한 개의 tool call이 끝나는 상황을 판단하고, build하고 append 후 tool_call 초기화
                    # API에서 tool call이 끝난 상황인건 따로 표시를 해주지 않아서 아래와 같이 판단함(아마도..)
                    # => 동일한 id, name이 진행 중인 경우엔 최초 한번만 표시되고 그 외엔 None
                    # => 동일한 id, name이여도 index가 다른 경우가 있음. index는 항상 어떠한 int값임
                    # => 따라서 id, name 중 하나 이상 None이 아니거나, index 값이 바뀐 경우를 새로운 tool call로 판단
                    # tool call이 한번만 발생하는 경우에는 이렇게 처리가 안되고,
                    # finish_reason == 'tool_calls'인 상황에서 따로 처리함
                    if (
                            choice.delta.tool_calls[0].id or
                            choice.delta.tool_calls[0].function.name or
                            choice.delta.tool_calls[0].index != tool_call_holder['index']
                        ):
                        tool_call = {
                            'id': tool_call_holder['id'],
                            'index': tool_call_holder['index'],
                            'name': tool_call_holder['name'],
                            'arguments': tool_call_holder['arguments']
                        }
                        # append tool_call if it's a valid tool_call
                        if tool_call['name'] and tool_call['arguments']:
                            tool_calls.append(tool_call)

                        print("\nNew tool call")

                        # reset function_call_holder
                        tool_call_holder = {'id': "", 'index': 0, 'name': "", 'arguments': ""}

                    # tool_call 만드는 과정
                    if choice.delta.tool_calls[0].id:
                        tool_call_holder['id'] += choice.delta.tool_calls[0].id
                    if choice.delta.tool_calls[0].index != tool_call_holder['index']:
                        tool_call_holder['index'] = choice.delta.tool_calls[0].index
                    if choice.delta.tool_calls[0].function.name:
                        tool_call_holder['name'] += choice.delta.tool_calls[0].function.name
                    if choice.delta.tool_calls[0].function.arguments:
                        print(choice.delta.tool_calls[0].function.arguments, end="", flush=True)
                        tool_call_holder['arguments'] += choice.delta.tool_calls[0].function.arguments

                # else - normal messages, stream display
                elif choice.delta.content:
                    print(choice.delta.content, end="", flush=True)
                    self.content_holder += choice.delta.content
                    yield choice.delta.content
                else:
                    pass

            # if streaming done, append ai message
            if choice.finish_reason == 'stop':
                ai_msg = {'role': 'assistant', 'content': self.content_holder}
                self.messages.append(ai_msg)

            # if streaming done but function call's required, append function output message
            elif choice.finish_reason == 'tool_calls':

                # 한개의 tool_call이 끝난 상황이니 build하고 append
                tool_calls.append(tool_call_holder)

                # build function messages
                for tool_call in tool_calls:

                    # append tool_call message
                    tool_call_msg = {
                        'role': 'assistant',
                        'content': None,
                        'tool_calls': [
                            {
                                'id': tool_call['id'],
                                'type': 'function',
                                'function': {
                                    'name': tool_call['name'],
                                    'arguments': tool_call['arguments']
                                }
                            }
                        ]
                    }

                    self.messages.append(tool_call_msg)

                    # run tool call and append tool output message
                    arguments = tool_call['arguments']

                    sample = f"name: {tool_call['name']}\narguments: {arguments}\n#####\n"
                    self.verbose_holder += sample

                    tool_output = self.call_function(tool_call['name'], arguments, global_vars)
                    tool_message = {
                        'role': 'tool', 
                        'tool_call_id': str(tool_call['id']),
                        'content': str(tool_output) 
                    }
                    self.messages.append(tool_message)


                    print('\n#####\n')
                    print(tool_message)
                    print('\n#####\n')


                #print(f"####verbose\n{page_session['verbose_holder']}")


                # finish_reason == stop 일때까지 재귀 실행
                yield from self.get_response(global_vars)

            else:
                if choice.finish_reason:
                    print(f"Invalid finish_reason: {choice.finish_reason}")
                    return None
                pass

    def return_messages(self) -> list:
        # class 내에서 업데이트된 messages와 log_messages를 리턴한다.
        return self.messages
