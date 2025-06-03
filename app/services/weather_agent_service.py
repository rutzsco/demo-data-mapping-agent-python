import os
from typing import List

import semantic_kernel as sk
from dotenv import load_dotenv
from opentelemetry import trace
from azure.identity import DefaultAzureCredential

from app.models.api_models import ChatRequest, ExecutionDiagnostics, RequestResult, ChatThreadRequest
from app.prompts.file_service import FileService
from app.services.weather_plugin import WeatherPlugin

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.contents import ChatMessageContent, FunctionCallContent
from semantic_kernel.connectors.ai.azure_ai_inference import AzureAIInferenceChatCompletion
from azure.ai.inference.aio import ChatCompletionsClient

class WeatherAgentService:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Retrieve configuration from environment variables
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        
        if not endpoint or not deployment_name:
            raise ValueError("Missing required environment variables for OpenAI configuration.")
    
        self.kernel = sk.Kernel()
        
        # If API key is present, use key-based authentication
        if api_key:
            self.kernel.add_service(AzureChatCompletion(
                api_key=api_key,
                endpoint=endpoint,
                deployment_name=deployment_name,
                service_id="azure-chat-completion"
            ))
        # Otherwise use DefaultAzureCredential
        else:
            self.kernel.add_service(AzureAIInferenceChatCompletion(
                ai_model_id=deployment_name,
                client=ChatCompletionsClient(
                     endpoint=f"{str(endpoint).strip('/')}/openai/deployments/{deployment_name}",
                     credential=DefaultAzureCredential(),
                     credential_scopes=["https://cognitiveservices.azure.com/.default"],
                )
            ))

        self.kernel.add_plugin(WeatherPlugin(self.kernel), plugin_name="weather")
        self.file_service = FileService()

        pass


    async def run_weather(self, request: ChatRequest) -> str:
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("Agent: Weather") as current_span:
            # Validate the request object
            if not request.messages:
                raise ValueError("No messages found in request.")
            
            chat_completion_service = self.kernel.get_service(service_id="azure-chat-completion")
            settings=PromptExecutionSettings(
                function_choice_behavior=FunctionChoiceBehavior.Auto(filters={"included_plugins": ["weather"]}),
            )
            kernel_arguments = KernelArguments()
            kernel_arguments ["diagnostics"] = []

            system_message = self.file_service.read_file('WeatherSystemPrompt.txt')
            chat_history_1 = ChatHistory()
            chat_history_1.add_system_message(system_message)
            for message in request.messages:
                if message.role.lower() == "user":
                    chat_history_1.add_user_message(message.content)
                elif message.role.lower() == "assistant":
                    chat_history_1.add_assistant_message(message.content)
            
            chat_result = await chat_completion_service.get_chat_message_content(
                chat_history=chat_history_1,
                arguments=kernel_arguments, 
                settings=settings,
                kernel=self.kernel)  

            request_result = RequestResult(
                content=f"{chat_result}",
                execution_diagnostics=ExecutionDiagnostics(steps=kernel_arguments ["diagnostics"]))

            return request_result
        
    async def run_weather_agent(self, request: ChatThreadRequest) -> str:

        # Define a list to hold callback message content
        intermediate_steps: list[str] = []

        # Define an async method to handle the `on_intermediate_message` callback
        async def handle_intermediate_steps(message: ChatMessageContent) -> None:
            if any(isinstance(item, FunctionCallContent) for item in message.items):
                for fcc in message.items:
                  if isinstance(fcc, FunctionCallContent):
                      intermediate_steps.append(f"Function Call: {fcc.name} with arguments: {fcc.arguments}")

        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("Agent: Weather") as current_span:
            # Validate the request object
            if not request.message:
                raise ValueError("No messages found in request.")
            user_message = request.message
            system_message = self.file_service.read_file('WeatherSystemPrompt.txt')

            settings=PromptExecutionSettings(
                function_choice_behavior=FunctionChoiceBehavior.Auto(filters={"included_plugins": ["weather"]}),
            )
            kernel_arguments = KernelArguments(settings=settings)
            kernel_arguments ["diagnostics"] = []

            agent = ChatCompletionAgent(
                kernel=self.kernel, 
                name="WeatherAgent", 
                instructions=system_message,
                arguments=kernel_arguments
            )
            
            # Iterate over the async generator to get the final response
            response = None
            thread = None
            
            async for result in agent.invoke(messages=user_message, thread=thread, on_intermediate_message=handle_intermediate_steps):
                response = result
                thread = response.thread

            if response is None:
                raise ValueError("No response received from the agent.")

            request_result = RequestResult(
                content=f"{response}",
                execution_diagnostics=ExecutionDiagnostics(steps=kernel_arguments ["diagnostics"]),
                intermediate_steps = intermediate_steps)

            return request_result