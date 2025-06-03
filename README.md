# demo-ai-flows-pyhton

## Local Environment Setup

Before running the application, you need to create a `.env` file in the root directory with the following required settings:

```properties
# Azure OpenAI Configuration
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=""
AZURE_OPENAI_ENDPOINT="https://your-openai-endpoint.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-api-key-here"

# Azure AI Agent Configuration
AZURE_AI_AGENT_ENDPOINT="https://your-ai-foundry-endpoint.services.ai.azure.com/api/projects/your-project"
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME="gpt-4.1"
AZURE_AI_AGENT_ID="your-agent-id"

# Application Insights (optional)
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=your-key;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/"

# Semantic Kernel Diagnostics (optional)
SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS=true
SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE=true
```

### Required Settings

- **AZURE_OPENAI_CHAT_DEPLOYMENT_NAME**: The name of your Azure OpenAI chat model deployment
- **AZURE_OPENAI_ENDPOINT**: Your Azure OpenAI service endpoint URL
- **AZURE_OPENAI_API_KEY**: Your Azure OpenAI API key
- **AZURE_AI_AGENT_ENDPOINT**: Azure AI Foundry project endpoint
- **AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME**: The model deployment name for the AI agent
- **AZURE_AI_AGENT_ID**: The ID of your Azure AI agent

### Optional Settings

- **AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME**: Embedding model deployment (if using embeddings)
- **SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS**: Enable OpenTelemetry diagnostics
- **APPLICATIONINSIGHTS_CONNECTION_STRING**: Application Insights connection for monitoring

## Docker Build and Run

To build the Docker image:
```bash
docker build -t demo-ai-flows .
```

To run the container:
```bash
docker run -dp 8000:8000 demo-ai-flows
```

