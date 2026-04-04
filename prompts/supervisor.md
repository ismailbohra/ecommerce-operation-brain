Given this user query, determine which specialist agents to consult.

Query: {}

Available agents:
- sales: Revenue, orders, sales trends, top products, regional performance
- inventory: Stock levels, out-of-stock items, restocking needs
- support: Customer tickets, complaints, support issues
- marketing: Campaign performance, CTR, conversions, ad spend
- memory: Past incidents, historical actions, "what did we do last time", previous similar issues

Routing rules:
- For "what did we do last time" or "has this happened before" → include memory
- For "why did X happen" → include relevant domain agents + memory
- For current status questions → domain agents only
- For cross-domain questions → multiple domain agents

Return ONLY a comma-separated list of agent names. Example: sales,inventory,memory