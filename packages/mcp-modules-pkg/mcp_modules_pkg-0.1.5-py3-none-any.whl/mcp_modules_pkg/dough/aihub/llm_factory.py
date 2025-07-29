
class LLMFactory:
    """Factory class for creating different language models based on the model name provided.

    Attributes:
        model_name (str): Name of the language model to be instantiated.

    Author:
        tskim.
    """

    VALID_MODELS = ["gpt", "gemini", "claude", "local"]

    def __init__(self, model_name: str = "gpt-3.5-turbo", *args, **kwargs):
        """Initializes the LLMFactory with the specified model name.

        Args:
            model_name (str): Name of the language model to be instantiated.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.category = model_name.split("-")[0]
        if not self.category in self.VALID_MODELS:
            raise ValueError(f"Unsupported model type : '{model_name}'")
        self.model_name = model_name
        self.llm = self.build_model_instance(*args, **kwargs)
        print(self.llm)

    def build_model_instance(self, *args, **kwargs) -> object:
        """Builds and returns an instance of the specified language model based on the model name.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            object: Instance of the specified language model.

        Raises:
            ValueError: If the model type is not supported.
        """
        build_func = getattr(self, f"build_{self.category}_model")
        return build_func(*args, **kwargs)

    def build_gpt_model(self, *args, **kwargs) -> object:
        """Builds and returns a GPT language model instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            object: Instance of the GPT language model.
        """
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=self.model_name, *args, **kwargs)

    def build_gemini_model(self, *args, **kwargs) -> object:
        """Builds and returns a Gemini language model instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            object: Instance of the Gemini language model.
        """
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=self.model_name, *args, **kwargs)

    def build_claude_model(self, *args, **kwargs) -> object:
        """Builds and returns a Claude language model instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            object: Instance of the Claude language model.
        """
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=self.model_name, max_tokens=10000, *args, **kwargs)

    def build_local_model(self, *args, **kwargs) -> object:
        """Builds and returns a local language model instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            object: Instance of the local language model.
        """
        from langchain_openai import ChatOpenAI
        
        base_url = "http://ai1.datawave.co.kr:1234/v1"
        api_key = "lm-studio"
        model = "-".join(self.model_name.split("-")[1:])
        return ChatOpenAI(
            base_url=base_url, api_key=api_key, model_name=model, *args, **kwargs
        )

    def get_model(self) -> object:
        """Returns the instantiated language model.

        Returns:
            object: Instance of the specified language model.
        """
        return self.llm

