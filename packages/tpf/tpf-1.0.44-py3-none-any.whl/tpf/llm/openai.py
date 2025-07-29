from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv(filename="env.txt"))

import os
import json
from openai import OpenAI

from tpf.llm.prompt import return_json1 
from tpf.llm.tools import Tools 

tools = Tools()

def chat(prompt_user, prompt_system=None, 
         response_format="text", 
         model='deepseek-r1:1.5b', 
         temperature=1, 
         base_url='http://localhost:11434/v1/',api_key='key',
         return_json=False):
    """大模型对话问答

    params
    --------------------------------
    - prompt_user:用户prompt 
    - prompt_system:系统prompt，，默认None 
    = response_format:'json_object'或'text'
    - model:模型路径，如果是ollama，可通过ollama list查看模型名称
    - temperature: 温度系数，默认1 
    - base_url：LLM http地址
    
    example 1 local 
    -------------------------------
    from tpf.llm import chat
    prompt = "你好"
    response = chat(prompt_user=prompt, 
                    prompt_system=None, 
                    response_format="text", 
                    model='deepseek-r1:1.5b', 
                    temperature=1, 
                    base_url='http://localhost:11434/v1/')
    print(response)
    
    
    
    example 2 online  
    -------------------------------
    import os
    from dotenv import load_dotenv  
    load_dotenv("/home/llm/conf/env.txt")  # 加载".env"文件 
    deepseek_base_url = os.getenv("deepseek_base_url")  
    deepseek_api_key = os.getenv("deepseek_api_key")  
    
    from tpf.llm import chat
    prompt = "你好"
    response = chat(prompt_user=prompt, 
                    prompt_system=None, 
                    model='deepseek-chat', 
                    temperature=1, 
                    base_url=deepseek_base_url,
                    api_key=deepseek_api_key,
                    return_json=True)
    response

    
    
    """
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,    #必需但可以随便填写
    )
    
    if return_json:
        output_format1 = return_json1()
        prompt_user = f"""
        {prompt_user}
        
        {output_format1}
        """
    
    if prompt_system is None:
        message = [{'role': 'user','content': prompt_user,}]
    else:
        message = [
            {
                "role": "system",
                "content": prompt_system  # 注入新知识
            },
            {
                "role": "user",
                "content": prompt_user  # 问问题
            },
        ]

    response = client.chat.completions.create(
        model=model,
        messages=message,
        temperature=temperature,   # 模型输出的随机性，0 表示随机性最小
        # 返回消息的格式，text 或 json_object
        response_format={"type": response_format},
    )

    if response.choices is None:
        err_msg = response.error["message"]
        raise Exception(f"{err_msg}")
    
    content = response.choices[0].message.content
    if return_json:
        try:
            json_str = tools.get_json_str(content)
            json_dict = json.loads(json_str)
            is_parse_ok = True 
        except Exception as e:
            print(e)
            is_parse_ok = False 
            
        if is_parse_ok:
            return json_dict

    return content          # 返回模型生成的文本



class MyChat():
    def __init__(self,env_file=".env"):
        """配置文件中环境变量命名
        f"{llm_name}_base_url",f"{}_api_key"
        比如,deepseek为deepseek_base_url,deepseek_api_key,
        
        """
        load_dotenv(env_file)  # 加载".env"文件 
        self.deepseek_base_url = os.getenv("deepseek_base_url")  
        self.deepseek_api_key = os.getenv("deepseek_api_key")  
    
    def deepseek(self, prompt_user, 
                prompt_system=None, 
                models=['deepseek-chat','deepseek-reasoner'], 
                temperature=1, 
                return_json=True):
        """
        - models:默认使用model[0]，使用时调整其顺序即可
        """
        response = chat(prompt_user=prompt_user, 
                prompt_system=None, 
                model=models[0], 
                temperature=temperature, 
                base_url=self.deepseek_base_url,
                api_key=self.deepseek_api_key,
                return_json=True)
        return  response





global client 
client = None





# 基于 prompt 生成文本
# gpt-3.5-turbo 
def get_completion(prompt, response_format="text", model="gpt-4o-mini"):
    
    global client 
    if not client:
        # 初始化 OpenAI 客户端
        client = OpenAI()  # 默认使用环境变量中的 OPENAI_API_KEY 和 OPENAI_BASE_URL

    messages = [{"role": "user", "content": prompt}]    # 将 prompt 作为用户输入
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,                                  # 模型输出的随机性，0 表示随机性最小
        # 返回消息的格式，text 或 json_object
        response_format={"type": response_format},
    )

    if response.choices is None:
        err_msg = response.error["message"]
        raise Exception(f"{err_msg}")

    return response.choices[0].message.content          # 返回模型生成的文本


def chat_openai(prompt, response_format="text", model="gpt-4o-mini"):
    """对话
    - prompt:输入文本
    - response_format:text,json_object
    
    """
    return get_completion(prompt, response_format, model)




def chat_stream(msg,model="gpt-4o-mini"):
    global client 
    if not client:
        # 初始化 OpenAI 客户端
        client = OpenAI()  # 默认使用环境变量中的 OPENAI_API_KEY 和 OPENAI_BASE_URL

    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": msg}],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
            
            
