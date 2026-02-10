from agentflow.pipeline import build_pipeline
from agentflow.memory import seed_state

def get_llm():
    # Real LLM not required for HW; None is acceptable
    return None

def main():
    # 1️⃣ INITIAL INPUT DATA (FIRST INSTANCE)
    initial_state = seed_state(
        title="The Great Gatsby",
        content="A novel about the American Dream in the Roaring Twenties.",
        task="Create and review a proposal for improving this book description",
        strict=False,
        llm=get_llm(),
    )

    print("\n=== INITIAL INPUT STATE ===")
    print(initial_state)

    # 2️⃣ BUILD & RUN GRAPH
    app = build_pipeline()

    print("\n=== STREAMING AGENT EXECUTION ===")
    last_event = None
    for event in app.stream(initial_state):
        last_event = event
        print(event)

    # 3️⃣ FINAL OUTPUT
    print("\n=== FINAL OUTPUT STATE ===")
    final_state = app.invoke(initial_state)
    print(final_state)

if __name__ == "__main__":
    main()
