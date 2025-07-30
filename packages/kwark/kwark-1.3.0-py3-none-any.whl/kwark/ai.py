from anthropic import Anthropic

DEFAULT_MODEL = 'claude-3-5-sonnet-20241022'


class AI:  # pragma: nocover

    def __init__(self, api_key=None):
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = Anthropic()

        # Fetch available models once during initialization
        self.available_models = self._fetch_available_models()

    def _fetch_available_models(self):
        """Fetch list of available Anthropic models"""
        try:
            response = self.client.models.list()
            models = []
            for model in response:
                models.append({
                    'id': model.id,
                    'display_name': getattr(model, 'display_name', model.id),
                    'created_at': getattr(model, 'created_at', None),
                })
            return models
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    def query(self, text, model=DEFAULT_MODEL):
        """Send a one-time query, no tools"""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }

        ]
        message = self.client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0,
            messages=messages)
        response = message.content[0].text
        return response

    def chat(self, ui, initial_message=None, model=DEFAULT_MODEL):
        """Interactive chat with conversation history using UI"""
        from wizlib.ui import Emphasis

        messages = []

        # Handle initial message if provided
        if initial_message:
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": initial_message
                    }
                ]
            })

            # Send initial message and get response
            message = self.client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=0,
                messages=messages)

            response = message.content[0].text
            ui.send(response, Emphasis.GENERAL)

            messages.append({
                "role": "assistant",
                "content": response
            })

        # Chat loop
        while True:
            try:
                user_input = ui.get_text("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    ui.send("Goodbye!", Emphasis.INFO)
                    break

                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_input
                        }
                    ]
                })

                message = self.client.messages.create(
                    model=model,
                    max_tokens=4096,
                    temperature=0,
                    messages=messages)

                response = message.content[0].text
                ui.send(f"Assistant: {response}", Emphasis.GENERAL)

                messages.append({
                    "role": "assistant",
                    "content": response
                })

            except KeyboardInterrupt:
                ui.send("Goodbye!", Emphasis.INFO)
                break
            except EOFError:
                ui.send("Goodbye!", Emphasis.INFO)
                break
