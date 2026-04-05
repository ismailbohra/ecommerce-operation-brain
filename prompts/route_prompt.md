Given this user query, determine which specialist agents to consult.

Query: {}

Available agents:
- sales: Revenue, orders, sales trends, top products, regional performance
- inventory: Stock levels, out-of-stock items, restocking needs
- support: Customer tickets, complaints, support issues
- marketing: Campaign performance, CTR, conversions, ad spend
- memory: Past incidents, historical actions, "what did we do last time"
- none: General questions, greetings, questions about the assistant itself

Routing rules:
- Greetings (hi, hello, hey) → none
- Questions about the assistant (your name, who are you, what can you do) → none
- Simple list/status queries → single relevant agent
- "Why" or "what happened" questions → multiple agents + memory
- Cross-domain analysis → multiple agents
- Historical questions → include memory

Return ONLY a comma-separated list of agent names, or "none" for general questions.