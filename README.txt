#AI Support: 4-Agent Policy Auditor


 🚀 Setup Instructions
1. Clone the repository and navigate to the project folder.
2. Install Dependencies:
   ```bash
   pip install -r requirements.txt
API Configuration:
run the following python files in order:
knowledge_base.py
scale_data.py
final_push.py
vectorDB.py
repair.py
clean.py

Open agency.py.

Replace the GROQ_API_KEY placeholder with your valid key.

Knowledge Base:

Ensure the folder policy_knowledge_base/ exists.

Add .md files (perishables.md, electronics.md, etc.) as defined in the write-up.

💻 Running the App
Run the Streamlit interface:

'''Bash
streamlit run app.py