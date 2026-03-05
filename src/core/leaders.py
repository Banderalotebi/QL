# src/core/leaders.py
from src.core.state import ResearchState
from langchain_ollama import ChatOllama

class AlchemistLeader:
    """
    The Meaning CEO. 
    Anchors theories to physical/biological realities (Coordinates, DNA, Mathematics)
    and rewards them with Occam's score boosts.
    """
    def __init__(self):
        # Temperature is slightly higher (0.4) for lateral thinking
        self.llm = ChatOllama(
            model="llama3:8b",
            temperature=0.4,
            num_predict=-1,
            num_ctx=8192
        )

    def run(self, state: ResearchState) -> dict:
        # Pull theories from synthesizer or directly from survivors
        theories = state.get("synthesized_theories", state.get("survivor_hypotheses", []))
        if not theories:
            return {}

        enhanced_theories = []
        for hyp in theories:
            prompt = f"""
            You are the Alchemist Leader (Meaning CEO) of the Muqattaat Lab.
            Your objective is to find connections between abstract cryptographic theories and physical reality 
            (e.g., the coordinates of Jeddah/Makkah, DNA base pairs, human biology, celestial mechanics).
            
            CURRENT SURVIVING THEORY:
            Scout: {hyp.source_scout}
            Goal: {hyp.goal_link}
            Description: {hyp.description}
            
            TASK:
            Is there a brilliant, lateral-thinking connection between this theory and a known physical/biological reality?
            If YES, provide a short paragraph explaining the connection and end exactly with "REWARD: ALCHEMIST".
            If NO, provide a brief critique and end exactly with "REWARD: NONE".
            """
            try:
                response = self.llm.invoke(prompt)
                content = response.content.strip()
                
                if "REWARD: ALCHEMIST" in content.upper():
                    # Massive score boost for anchoring in reality
                    hyp.score = min(1.0, hyp.score + 0.3)
                    hyp.description += f"\n\n[Alchemist Anchor]: {content}"
                
                enhanced_theories.append(hyp)
            except Exception as e:
                pass
                
        # Upgrade the final scored list
        return {"scored_theories": enhanced_theories}


class ExecutionerLeader:
    """
    The Results CEO.
    Acts as a conditional router in the LangGraph. 
    If results are 0, it skips to the end (or triggers respawns later).
    """
    @staticmethod
    def route(state: ResearchState) -> str:
        # Check if any hypotheses survived the strict Fool / Synthesizer phase
        survivors = state.get("synthesized_theories", state.get("survivor_hypotheses", []))
        
        if len(survivors) > 0:
            print(f"\n[Executioner]: {len(survivors)} theories passed. Routing to Alchemist (Meaning CEO).")
            return "alchemist"
            
        print("\n[Executioner]: 0 theories survived. Routing directly to final report.")
        return "report_builder"
