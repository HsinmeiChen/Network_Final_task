from abc import ABC, abstractmethod
import base64
import json
from typing import List
from openai import OpenAI

#處理需要的格式、回應
class Service_Assistant:
    @staticmethod
    def api_Assistant_OneShot(company_name:None, config: dict, serviceName, model, message):
        newAssistant = Service_Assistant.create_assistant(company_name)
        with open( serviceName+'.json', 'r', encoding='utf-8') as file:
            api_Swagger_content = file.read().strip()
        newAssistant.initialize( 
            config=config, 
            assistantName=serviceName, 
            base_instruction=api_Swagger_content+Service_Assistant.get_api_assistant_prompt(),
            model=model
        )
        content = newAssistant.send_message(message)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            return {
                "error": "Invalid JSON format",
                "details": str(e),
                "content": content
            }
    
    #處理普通的對話任務
    @staticmethod
    def Assistant_OneShot(company_name:None, config: dict, model, assistantname, assistant_instruction, message):
        newAssistant = Service_Assistant.create_assistant(company_name)
        newAssistant.initialize( 
            config=config, 
            assistantName=assistantname, 
            base_instruction=assistant_instruction,
            model=model
        )
        content = newAssistant.send_message(message)
        return content
        

    @staticmethod
    def get_api_assistant_prompt():
        return ("\\n You are now acting as the aforementioned API and will only respond in JSON format. All responses must be presented in standard JSON format without any additional text or explanations. Upon receiving a request, you need to generate a corresponding JSON reply based on the instructions in the request. Ensure that the JSON format is correct and the structure is clear. JSON content must be replied in Tradition Chinese.")

    class AssistantInterface(ABC):
        @abstractmethod
        def create_assistant(self, name, base_instruction, model):
            pass

        @abstractmethod
        def send_message(self, message: str) -> str:
            pass

        @abstractmethod
        def initialize(self, config: dict, assistantName, base_instruction, model):
            pass

        @abstractmethod
        def reset_dialogue(self):
            pass

            #每次都重新給prompt，不會記得歷史紀錄
    class OpenAI_Completion(AssistantInterface):
        def initialize(self, config: dict, assistantName, base_instruction, model):
            self.config = config
            self.model = model
            self.base_instruction = base_instruction
            open_api_key = config['openai']['api_key']
            self.client = OpenAI(api_key=open_api_key)

        def create_assistant(self, name, base_instruction, model):
            pass

        def send_message(self, message: str) -> str:
            # 將圖片轉為 Base64 編碼
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.base_instruction+"\n Input:"+message}
                        ],
                    }
                ],
            )
            cleaned_data = completion.choices[0].message.content.strip('```json\n').strip('```')
            return cleaned_data

        def reset_dialogue(self):
            pass

            #要記得前一次回答的對話情境，
    class OpenAI_Assistant(AssistantInterface):
        def initialize(self, config: dict, assistantName, base_instruction, model):
            self.dialogue = None
            self.config = config
            open_api_key = config['openai']['api_key']
            self.client = OpenAI(api_key=open_api_key)
            self.assistant = self.create_assistant( assistantName, base_instruction, model)
            print("Assistant initialized with configuration:", config)

        def create_assistant(self,name, base_instruction, model):
            assistant = self.client.beta.assistants.create(
                name=name,
                instructions=base_instruction,
                model=model, #e.q."gpt-3.5-turbo-0125"
            )

            return assistant

        def send_message(self, message: str) -> List:
            if self.assistant is None:
                return "Assistant not initialized"
            if self.dialogue is None:
                self.dialogue = self.client.beta.threads.create()
            self.client.beta.threads.messages.create(thread_id=self.dialogue.id, role="user", content=message)
            run = self.client.beta.threads.runs.create(
                thread_id=self.dialogue.id,
                assistant_id=self.assistant.id,
            )

            run = self._wait_on_run(run)
            response_message = self._get_response(run.id)
            return response_message

        def reset_dialogue(self):
            self.dialogue = self.client.beta.threads.create()
            print("Dialogue history has been reset.")

        def _wait_on_run(self, run):
            while run.status in ["queued", "in_progress"]:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.dialogue.id,
                    run_id=run.id,
                )

            return run

        def _get_response(self, run_id):
            i = 0
            list = self.client.beta.threads.messages.list(thread_id=self.dialogue.id, order="desc", limit=10).data
            replyArray = []
            while i < len(list) and list[i].run_id == run_id:
                replyArray.insert(0, list[i].content[0].text.value)
                i += 1
            return replyArray

    @staticmethod
    def create_assistant(company_name: str) -> AssistantInterface:
        if company_name == "OpenAI_Assistant":
            return Service_Assistant.OpenAI_Assistant()
        elif company_name == "OpenAI_Completion":
            return Service_Assistant.OpenAI_Completion()
        raise ValueError(f"Unsupported service: {company_name}")