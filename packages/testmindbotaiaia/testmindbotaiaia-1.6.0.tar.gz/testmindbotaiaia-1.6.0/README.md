# MindBot-AI

**MindBot-AI** is a state-of-the-art Python library that provides access to a powerful suite of AI models for a wide range of tasks, from text generation and image manipulation to in-depth analysis of various media types. Powered by Google's Gemini models, MindBot-AI is designed to be intuitive, flexible, and easy to integrate into your projects.

## Installation

Getting started with MindBot-AI is as simple as running a single pip command:

```bash
pip install mindbot-ai
```

## Core Features and Models

MindBot-AI offers a rich set of features, each powered by a specialized model. Here's a breakdown of what you can do:

### Text Generation

- **`mindbot-1.8-ultra`**: Your go-to model for general-purpose text generation, from answering questions to writing creative content.
- **`mindthink-a3`**: A more powerful model that automatically engages for complex prompts, providing deeper and more thoughtful responses.

**Example:**
```python
from mindbot import mind
from examples.config import API_KEY

bot = mind(api_key=API_KEY)

# Standard text generation
response = bot.ask("Hello, who are you?")
print(f"Response:> {response}")

# Direct text generation using generate_content
response = bot.generate_content("What are the main benefits of using Python for web development?")
print(response)

# The "thinking" model will be automatically triggered for this complex prompt
long_prompt = "Provide a detailed explanation of the transformer architecture in natural language processing, including its key components like self-attention, multi-head attention, and positional encodings."
thinking_response = bot.generate_content(long_prompt)
print(thinking_response)
```

### Vision

- **`mindvision-flash`**: A versatile model for understanding and analyzing visual content.
  - **Image Analysis**: Describe images, identify objects, and answer questions about visual content.
  - **Video Analysis**: Summarize videos and answer questions about their content.
  - **PDF Analysis**: Extract information and summarize PDF documents.
- **`mindtube-1.0`**: A specialized model for analyzing YouTube videos directly from their URLs.

**Example:**
```python
# Image Analysis
response = bot.vision.analyze_image("path/to/your/image.jpg", "What is the main subject of this image?")
print(response)

# YouTube Analysis
response = bot.vision.analyze_youtube_video("https://www.youtube.com/watch?v=your_video_id", "Summarize this video in five key points.")
print(response)
```

### Audio

- **`mindaudio-pro`**: A powerful model for transcribing and understanding audio content.

**Example:**
```python
response = bot.audio.analyze_audio("path/to/your/audio.mp3", "Transcribe the speech in this audio file.")
print(response)
```

### Search

- **`mindsearch-2.5`**: A model for browsing the web and gathering real-time information.
- **`deepsearch-1.0`**: A more advanced search model that provides deeper and more comprehensive answers to complex questions.

**Example:**
```python
# Standard web search
response = bot.search.browse("What are the latest developments in AI regulation?")
print(response)

# Deep search for more complex queries
response = bot.search.browse("Provide a comparative analysis of the economic policies of Japan and Germany over the last decade.", model="deepsearch-1.0")
print(response)
```

### Image Manipulation

- **`mindpaint-2.5`**: A creative model for generating new images from text prompts.
- **`mindstyle-2.5`**: A powerful model for editing and manipulating existing images based on your instructions.

**Example:**
```python
# Generate an image
status, file_path, link = bot.image.generate_image("A hyper-realistic image of a futuristic city on Mars.")
print(status, file_path, link)

# Edit an image
text_response, file_path = bot.image.edit_image("path/to/your/image.jpg", "Add a vintage filter to this image.")
print(text_response, file_path)
```

---

We believe in the power of AI to unlock new possibilities, and we're excited to see what you'll build with MindBot-AI. If you have any questions or feedback, please don't hesitate to reach out.
