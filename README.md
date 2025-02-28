# Multi-LLM Cost-Optimized API Microservice

This project is a multi-LLM cost-optimized API microservice that routes requests to multiple low-cost/free LLM providers with fallback, token/cost tracking, and standardized API integration.

## Features

- **Multi-Provider Support**: Routes requests between multiple LLM providers like Groq and Together.
- **Cost Optimization**: Prioritizes lower-cost providers while maintaining response quality.
- **Automatic Fallbacks**: Implements fallback mechanisms when a provider fails.
- **Token & Cost Tracking**: Logs token usage and cost per provider.
- **Error Handling & Logging**: Detailed logging for debugging and tracking errors.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd AmanSolutionTI


## Creating environment

1. Clone the repository:
   ```bash
   python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

## Install dependencies

1. command for installation:
   ```bash
   pip install -r requirements.txt

## Environment variable
1. command for installation:
   ```bash
   export GROQ_API_KEY=your-groq-api-key
   export TOGETHER_API_KEY=your-together-api-key

## Configuration
1. providers.yml:
   ```bash
  providers:
  - name: "groq_llama"
    endpoint: "https://api.groq.com/openai/v1/chat/completions"
    token: "${GROQ_API_KEY}"
    cost_per_1k_tokens: 0.001
    priority: 1
    model: "llama-3.1-8b-instant"
    temperature: 0.7

  - name: "together_llama"
    endpoint: "https://api.together.xyz/inference"
    token: "${TOGETHER_API_KEY}"
    cost_per_1k_tokens: 0.0015
    priority: 2
    model: "meta-llama/Llama-3-70b-chat-hf"
    temperature: 0.7

 ## Running the script
1. command for installation:
   ```bash
     python main.py







