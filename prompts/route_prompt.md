Given this user query, determine which specialist agents to consult.

Query: {}

Available agents:
- sales: Revenue, orders, sales trends, top products, regional performance
- inventory: Stock levels, out-of-stock items, restocking needs
- support: Customer tickets, complaints, support issues
- marketing: Campaign performance, CTR, conversions, ad spend
- memory: Past incidents, historical actions, "what did we do last time"

Routing rules:
- Simple list/status queries → single relevant agent only
- "Why" or "what happened" questions → multiple agents + memory
- Cross-domain analysis → multiple agents
- Historical questions → include memory

Return ONLY a comma-separated list of agent names.