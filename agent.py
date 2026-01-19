from uagents import Agent
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv
from chat_proto import chat_proto
import os

load_dotenv()

agent = Agent(
    name="heyyy aganet nent",
    seed=os.getenv("AGENT_SEED"),
    port=8000,
    mailbox=True,
)

fund_agent_if_low(str(agent.wallet.address()))

agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
