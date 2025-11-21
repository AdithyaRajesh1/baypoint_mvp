from python_a2a import AgentNetwork, AIAgentRouter, A2AClient, OpenAIA2AClient, Message, TextContent, MessageRole
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

def route_and_ask_agent(user_query, allowed_agents=None):
    print("🔍 [ROUTER] Starting route_and_ask_agent function")
    print(f"🔍 [ROUTER] Input query: {user_query}")
    print(f"🔍 [ROUTER] Allowed agents: {allowed_agents}")
    
    try:
        # Map agent IDs to their endpoints
        print("🔍 [ROUTER] Setting up agent endpoints...")
        agent_endpoints = {
            "clado": "https://clado-test-agent.onrender.com",
            "branding agent": "https://branding-agent.onrender.com/",
            "legal agent": "https://legal-service-agent.onrender.com/",
        }
        agent_token_costs = {
            "clado": 1,
            "branding agent": 1,
            "legal agent": 1,
        }
        print(f"🔍 [ROUTER] Agent endpoints: {agent_endpoints}")
        print(f"🔍 [ROUTER] Agent token costs: {agent_token_costs}")
        
        print("🔍 [ROUTER] Creating AgentNetwork...")
        network = AgentNetwork()
        print("✅ [ROUTER] AgentNetwork created successfully")
        
        # Only add allowed agents
        if allowed_agents is None:
            allowed_agents = list(agent_endpoints.keys())
            print(f"🔍 [ROUTER] No allowed_agents specified, using all: {allowed_agents}")
        
        print("🔍 [ROUTER] Adding agents to network...")
        for agent_id in allowed_agents:
            if agent_id in agent_endpoints:
                print(f"🔍 [ROUTER] Adding agent {agent_id} with endpoint {agent_endpoints[agent_id]}")
                network.add(agent_id, agent_endpoints[agent_id])
                print(f"✅ [ROUTER] Agent {agent_id} added successfully")
            else:
                print(f"⚠️ [ROUTER] Agent {agent_id} not found in endpoints")
        
        print("🔍 [ROUTER] Creating AIAgentRouter...")
        print(f"🔍 [ROUTER] Using A2AClient with URL: http://localhost:5001")
        router_llm = OpenAIA2AClient(
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-4o-mini",
        system_prompt="You are a hyper-efficient, logical AI task router. Your sole purpose is to analyze a user's query "
                "and determine the most suitable specialized agent to handle the request. "
                "You must choose from the following agents, each with a specific function:\n\n"
                "AGENT LIST:\n"
                "- clado: Specializes in searching for individuals, professionals, or candidates based on specific criteria "
                "like skills, experience, or job suitability. Use for any queries about finding people, professionals, or candidates.\n"
                "- branding agent: Specializes in branding, marketing, logo design, brand strategy, and visual identity. "
                "Use for any queries about branding, marketing, design, or business identity.\n"
                "- legal agent: Specializes in legal advice, contract review, legal documents, and legal consultation. "
                "Use for any queries about legal matters, contracts, or legal services.\n\n"
                "INSTRUCTIONS:\n"
                "1. Analyze the user's query to understand its primary intent.\n"
                "2. Match the intent to the agent whose specialization is the best fit.\n"
                "3. Your response MUST be ONLY the exact agent name from the AGENT LIST (e.g., `clado`, `branding agent`, `legal agent`).\n"
                "4. DO NOT provide any explanation, justification, or conversational text.\n"
                "5. If the query is ambiguous or does not fit any agent's function, respond with `NO_AGENT`.\n\n"
                "EXAMPLES:\n"
                "Query: 'Find me a UI/UX designer with experience in Figma.'\n"
                "Response: clado\n\n"
                "Query: 'Design a logo for my startup.'\n"
                "Response: branding agent\n\n"
                "Query: 'Review this contract for me.'\n"
                "Response: legal agent\n\n"
                "Query: 'What is the weather like today?'\n"
                "Response: NO_AGENT\n\n"
                "Query: 'Tell me a joke.'\n"
                "Response: NO_AGENT\n\n"
                "Query: 'Find someone who went to Georgia State.'\n"
                "Response: clado\n\n"
                "Query: 'Create a brand strategy for my company.'\n"
                "Response: branding agent\n\n"
                "Query: 'I need legal advice about employment law.'\n"
                "Response: legal agent"
        )
        router = AIAgentRouter(
            agent_network=network,
            llm_client=router_llm,
        )
        print("✅ [ROUTER] AIAgentRouter created successfully")
        
        print("🔍 [ROUTER] Calling router.route_query...")
        agent_name, confidence = router._fallback_routing(user_query)
        print(f"✅ [ROUTER] Route query completed")
        print(f"🔍 [ROUTER] Query: {user_query}")
        print(f"🔍 [ROUTER] Raw agent_name: '{agent_name}' (type: {type(agent_name)})")
        print(f"🔍 [ROUTER] Raw confidence: {confidence} (type: {type(confidence)})")
        print(f"🔍 [ROUTER] Routed to: {agent_name} (confidence: {confidence:.2f})")
        
        token_cost = 0
        # Check if no suitable agent was found
        if agent_name == "NO_AGENT" or agent_name is None:
            print(f"⚠️ [ROUTER] No suitable agent found for query: {user_query}")
            return {"response": "I'm sorry, I don't have a specialized agent to handle this type of request. Please try asking about finding people or professionals.", "token_cost": 0}
        
        if confidence > 0.3:
            print(f"🔍 [ROUTER] Confidence {confidence:.2f} > 0.3, proceeding with agent call")
            print(f"🔍 [ROUTER] Getting agent {agent_name} from network...")
            agent = network.get_agent(agent_name)
            print(f"✅ [ROUTER] Agent {agent_name} retrieved successfully")
            
            print(f"🔍 [ROUTER] Calling agent.ask() with query: {user_query}")

            user_query_message = Message(
                content=TextContent(text=user_query),
                role=MessageRole.USER
            )

            response = agent.ask(user_query_message)
            print(f"✅ [ROUTER] Agent response received")
            print(f"🔍 [ROUTER] Response: {response}")
            print(f"🔍 [ROUTER] Response type: {type(response)}")
            
            # Token cost logic
            print("🔍 [ROUTER] Calculating token cost...")
            if agent_name == "clado":
                # Try to count people if response is a list, else 1
                if isinstance(response, list):
                    token_cost = len(response) * agent_token_costs["clado"]
                    print(f"🔍 [ROUTER] Response is list with {len(response)} items, token cost: {token_cost}")
                else:
                    token_cost = agent_token_costs["clado"]
                    print(f"🔍 [ROUTER] Response is not list, token cost: {token_cost}")
            elif agent_name == "essay_generator":
                token_cost = agent_token_costs["essay_generator"]
                print(f"🔍 [ROUTER] Essay generator token cost: {token_cost}")
            
            print(f"🔍 [ROUTER] Returning response with token cost {token_cost}")
            return {"response": response, "token_cost": token_cost}
        else:
            print(f"⚠️ [ROUTER] Confidence {confidence:.2f} <= 0.3, returning no agent found")
            return {"response": "No suitable agent found for this query (confidence too low).", "token_cost": 0}
            
    except Exception as e:
        print(f"❌ [ROUTER] Error in route_and_ask_agent: {e}")
        import traceback
        print(f"❌ [ROUTER] Full traceback:")
        traceback.print_exc()
        return {"response": f"Error in routing: {str(e)}", "token_cost": 0}