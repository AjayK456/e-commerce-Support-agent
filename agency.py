import os
from crewai.tools import BaseTool
from crewai import Agent, Task, Crew, Process

# 1. CONFIGURATION
# IMPORTANT: Replace 'YOUR_ACTUAL_GROQ_KEY' with your real key from console.groq.com
GROQ_API_KEY = "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" 

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

WORKER_MODEL = "groq/llama-3.1-8b-instant"
WRITER_MODEL = "groq/llama-3.3-70b-versatile"

# 2. CUSTOM TOOL DEFINITION
class PolicySearchTool(BaseTool):
    name: str = "smart_policy_search"
    description: str = "Search e-commerce policies. Returns chunks with filenames for citation."

    def _run(self, query: str) -> str:
        folder_path = 'policy_knowledge_base' 
        relevant_chunks = []
        keywords = [word.lower().strip() for word in query.replace(',', '').split()]
        
        if not os.path.exists(folder_path):
            return f"Error: Folder '{folder_path}' not found."

        try:
            for filename in os.listdir(folder_path):
                if filename.endswith('.md'):
                    with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                        content = f.read()
                        sections = content.split('\n\n') 
                        for i, section in enumerate(sections):
                            if any(word in section.lower() for word in keywords):
                                relevant_chunks.append(f"SOURCE: {filename} | CHUNK_ID: {i}\n{section.strip()}")
            
            if not relevant_chunks:
                return "No matching policy sections found. Escalation required."
            
            return "\n\n---\n\n".join(relevant_chunks[:3])
        except Exception as e:
            return f"Error searching policies: {str(e)}"

policy_tool = PolicySearchTool()

# 3. THE 4-AGENT TEAM
triage_specialist = Agent(
    role='Support Triage Lead',
    goal='Classify issue type and identify missing fields.',
    backstory='Expert analyst. Categorizes tickets into: refund, shipping, payment, promo, fraud. Provides confidence scores.',
    llm=WORKER_MODEL,
    verbose=False
)

policy_researcher = Agent(
    role='Policy Research Specialist',
    goal='Extract factual rules and provide specific citations.',
    backstory='Data researcher. Must include SOURCE and CHUNK_ID for every finding.',
    llm=WORKER_MODEL,
    tools=[policy_tool],
    verbose=False
)

compliance_agent = Agent(
    role='Compliance & Safety Officer',
    goal='Audit findings for logic errors. Prevent "stolen" items from being treated as "standard returns".',
    backstory='Gatekeeper. Ensures no "restocking fees" are applied to theft cases. Checks for citations.',
    llm=WORKER_MODEL,
    verbose=False
)

resolution_writer = Agent(
    role='Resolution Writer',
    goal='Draft the final 7-point structured response based ONLY on retrieved evidence.',
    backstory='Professional communicator. Strictly follows the 7-point output requirement.',
    llm=WRITER_MODEL,
    verbose=False
)

# 4. EXECUTION ENGINE
def run_agency(ticket_content, order_context):
    t1 = Task(
        description=(
            f"Analyze the ticket: '{ticket_content}'.\n"
            f"Use the following structured Order Context: {order_context}.\n"
            "Identify: issue_type, item_category, fulfillment_type, and shipping_region."
        ),
        expected_output="Classification (type), Confidence Score, and 1-3 Clarifying Questions.",
        agent=triage_specialist
    )
    
    t2 = Task(
        description="Find specific policy rules with SOURCE and CHUNK_ID for the triaged issue.",
        expected_output="Policy rules with citations.",
        agent=policy_researcher,
        context=[t1]
    )
    
    t3 = Task(
        description="Audit research. Ensure 'Theft' issues don't use 'Return' logic. Check for valid citations.",
        expected_output="Compliance Report: Approved/Denied with rationale.",
        agent=compliance_agent,
        context=[t2]
    )
    
    t4 = Task(
        description="Draft the final structured response (Points 1-7).",
        expected_output="1. Classification, 2. Questions, 3. Decision, 4. Rationale, 5. Citations, 6. Draft, 7. Next Steps.",
        agent=resolution_writer,
        context=[t1, t2, t3]
    )

    crew = Crew(
        agents=[triage_specialist, policy_researcher, compliance_agent, resolution_writer],
        tasks=[t1, t2, t3, t4],
        process=Process.sequential,
        verbose=False
    )
    
    return crew.kickoff()

if __name__ == "__main__":
    sample_context = {
        "item_category": "electronics",
        "fulfillment_type": "first-party",
        "shipping_region": "US"
    }
    
    # Try-Except block to catch the API error gracefully if the key is dead
    try:
        result = run_agency("My $650 camera was stolen. Refund me!", sample_context)
        print("\n########################\n## FINAL RESPONSE ##\n########################\n")
        print(result)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        print("Please check your Groq API Key at https://console.groq.com/keys")