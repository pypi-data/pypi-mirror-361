from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.settings import agent_settings


class LaozhangModelName(ModelNameBase):
    O4_MINI = "o4-mini"


class LaozhangEmbeddingModelName(ModelNameBase):
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"


class LaozhangAgent(AgentBase):
    def create_client(self):
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        return AsyncOpenAI(
            api_key=self.credential.api_key,
            base_url=self.credential.base_url,
        )

    def create_model(self):
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        client = self.create_client()
        return OpenAIModel(
            model_name=self.credential.model_name,
            provider=OpenAIProvider(openai_client=client),
        )


async def validate_fn(credential: ModelCredential) -> bool:
    agent = await LaozhangAgent.create(credential=credential)
    return await agent.validate_credential()


class LaozhangCredentialPool(CredentialPoolBase):
    def __init__(self, target_model: LaozhangModelName):
        super().__init__(
            target_model=target_model,
            account_credentials=agent_settings.laozhang.credentials,
            validate_fn=validate_fn,
        )


if __name__ == "__main__":
    import asyncio

    from pydantic_ai.settings import ModelSettings

    from agent_tools.test_tool import test_all_credentials, test_credential_pool_manager

    model_settings = ModelSettings(
        temperature=0.0,
        max_tokens=8192,
    )

    async def test():
        """Main function that runs all tests with proper cleanup."""
        await test_all_credentials(
            model_name_enum=LaozhangModelName,
            model_settings=model_settings,
            credential_pool_cls=LaozhangCredentialPool,
            agent_cls=LaozhangAgent,
        )
        await test_credential_pool_manager(
            credential_pool_cls=LaozhangCredentialPool,
            agent_cls=LaozhangAgent,
            target_model=LaozhangModelName.O4_MINI,
            model_settings=model_settings,
        )

    try:
        asyncio.run(test())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
