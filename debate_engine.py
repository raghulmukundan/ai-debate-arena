import os
from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

class DebateAgent:
    """An agent that can argue for or against a position"""
    
    def __init__(self, position, clientType="claude", model="claude-sonnet-4-20250514", api_key=None, max_tokens=1024):
        self.position = position
        self.clientType = clientType.lower()
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.argument_history = []
        
    def generate_argument(self, topic, context="", round_num=1):
        """Generate an argument for the given topic and context"""
        
        system_prompt = f"""You are an Agent {self.position.upper()} in a debate.
        
        IMPORTANT RULES:
        1. You MUST take a clear position
        2. Do NOT suggest third options or compromises
        3. Do NOT give neutral "it depends" advice
        4. Commit fully to your assigned side
        5. Argue as if you genuinely believe your position is correct

        Your job: Argue {self.position.upper()} for the decision at hand.
        Be persuasive, logical and specific. 
        Keep it conversational and fun - aim for 100-150 words."""
        
        user_prompt = f"""Topic: {topic} 
        {context}
        This is Round {round_num}. Make your best argument {'FOR' if self.position.lower() == 'pro' else 'AGAINST'} this decision.
        """
    
        argument = self.get_message(prompt=user_prompt, system_prompt=system_prompt)
        self.argument_history.append(argument)
        return argument
    
    def reflect_on_argument(self, own_argument):
        """Agent critiques its own argument"""
        reflection_prompt = f"""You just made this argument: {own_argument}"
        Now perform SURGICAL SELF-CRITIQUE. Be brutally specific:
        1. LOGICAL FALLACIES (quote the exact sentences):
        - Which specific sentences contain fallacies?
        - Quote them and name the fallacy
        - Why is it a fallacy in this context?

        2. BIASES DETECTED (be specific):
        - What assumptions did you make about the person?
        - What personal preferences leaked into your argument?
        - What did you assume was universal that's actually subjective?

        3. MANIPULATION TACTICS (quote examples):
        - Which phrases were designed to pressure rather than persuade?
        - Where did you use emotion instead of logic?
        - What words were chosen to manipulate? (CAPS, "trust me", etc.)

        4. MISSING CRITICAL QUESTIONS:
        - What should you have asked first before arguing?
        - What context is missing that would change everything?
        - What alternatives did you ignore?

        5. COUNTER-EXAMPLES TO YOUR OWN CLAIMS:
        - Find 2-3 scenarios where your advice would be BAD
        - What if your assumptions are wrong?

        6. WERE YOU FACTUALLY CORRECT IN SOME OR ALL PARTS?
        - Identify any factual claims you made
        - Were they accurate? If not, what should the correct facts be?

        7. IMPROVEMENT PLAN FOR NEXT ROUND:
        - Specifically, what will you change?
        - What information do you need?
        - How will you avoid these same mistakes?

        8. SELF-RATING:
        - Logical rigor: X/10 (why?)
        - Evidence quality: X/10 (why?)
        - Objectivity: X/10 (why?)
        - Overall: X/10

        Be harsher than you think necessary. Finding flaws is success. Keep crisp in your observations. Keep it to 100 to 150 words.
        """
        reflection = self.get_message(prompt=reflection_prompt)
        return reflection
        
    def get_message(self, prompt, system_prompt=""):
        """Helper to get message from appropriate client"""
        messages = []
        if system_prompt != "" and self.clientType.lower() == "openai":
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        if self.clientType.lower() == "openai":
            client = OpenAI(api_key=self.api_key)
            message = client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=messages)
            return message.choices[0].message.content
        else:
            client = Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model=self.model,
                system=system_prompt,
                max_tokens=self.max_tokens,
                messages=messages)
            return message.content[0].text
    
    def extract_reflection_summary(self, full_reflection):
        """Extract key points from reflection for next round context"""
        summary_prompt = f"""From this detailed self-critique, extract ONLY the essential points for improvement:
        {full_reflection}
        Provide a concise summary (100-150 words) with:
          1. Top 3 Specific flaws identified
          2. Key improvement actions for the next round
          3. Self-rating scores
        
        Keep it brief and actionable. This will guide the next argument round."""
        message = self.get_message(prompt=summary_prompt)
        return message
    
    def refine_argument(self, topic, previous_argument, reflection_summary, opponent_argument, round_num):
        """Generate improved argument based on reflection and opponent's points"""
        
        system_prompt = f"""You are Agent {self.position.upper()} in Round {round_num} of a debate.
        You previously argued and reflected on your flaws. 
        Now IMPROVE your argument by:
        1. Fixing the flaws you identified
        2. Responding to opponent's strongest points
        3. Being more rigorous and less biased.
        Keep it conversational and compelling - aim for 100-150 words.
        """
        
        user_prompt = f"""Topic: {topic}
        YOUR PREVIOUS ARGUMENT: (Round {round_num - 1}): {previous_argument}
        YOUR SELF-REFLECTION IDENTIFIED THESE ISSUES: {reflection_summary}
        
        OPPONENT'S ARGUMENT: {opponent_argument}
        
        Now make a BETTER argument that:
        - Fixes your identified flaws
        - Addresses opponent's strong points
        - Is more logical, evidence-based
        - Avoids manipulation tactics you caught yourself using.
        
        Make your best case for {'supporting' if self.position.lower() == 'pro' else 'opposing'} this decision. Aim for 100 to 150 words."""
        
        argument = self.get_message(prompt=user_prompt, system_prompt=system_prompt)
        self.argument_history.append(argument)
        return argument
    
    
class DebateOrchestrator:
    """Manages the full debate between two agents"""
        
    def __init__(self, pro_provider="claude", pro_model="claude-sonnet-4-20250514", con_provider="claude", con_model="claude-sonnet-4-20250514", pro_api_key=None, con_api_key=None): 
        self.agent_pro = DebateAgent(position="pro", clientType=pro_provider, model=pro_model, api_key=pro_api_key)
        self.agent_con = DebateAgent(position="con", clientType=con_provider, model=con_model, api_key=con_api_key)
            
    def run_simple_debate(self, topic): 
        """Run a debate with reflection phase"""
        print("="*60)
        print(f"Debate Topic: {topic}")
        print("="*60)
        
        print("\n Round 1: Initial Arguments")
        print("="*60)   
        
        print("\n AGENT PRO:")
        print("-"*60)
        pro_argument = self.agent_pro.generate_argument(topic=topic)
        print(pro_argument)
           
        print("\n AGENT CON:")
        print("-"*60)
        con_argument = self.agent_con.generate_argument(topic=topic)
        print(con_argument)
        
        #Reflection Phase
        print("\nREFLECTION PHASE: AGENT critiques themselves")
        print("="*60)
        
        print("\n AGENT PRO Reflects:")
        print("-"*60)
        pro_reflection = self.agent_pro.reflect_on_argument(pro_argument)
        print(pro_reflection)
        
        print("\n AGENT CON Reflects:")
        print("-"*60)
        con_reflection = self.agent_con.reflect_on_argument(con_argument)
        print(con_reflection)
        
        print("\n" + "="*60)
        print("Debate with reflection complete!")
        print("="*60)
 
    def run_multiround_debate(self, topic, total_rounds=3):
        """Run a multi-round debate with reflection and improvement"""
        print("="*70)
        print(f"MULTI-ROUND DEBATE : {topic}")
        print("="*70)
        
        pro_arguments = []
        con_arguments = []
        pro_reflections = []
        con_reflections = []
        
        # === ROUND 1: Initial Arguments ===
        print("\n" + "=" * 70)
        print("ROUND 1: INITIAL ARGUMENTS")
        print("=" * 70)
        
        print("\nAGENT PRO:")
        print("-" * 70)
        pro_arg_1 = self.agent_pro.generate_argument(topic, round_num=1)
        print(pro_arg_1)
        pro_arguments.append(pro_arg_1)
        
        print("\nAGENT CON:")
        print("-" * 70)
        con_arg_1 = self.agent_con.generate_argument(topic, round_num=1)
        print(con_arg_1)
        con_arguments.append(con_arg_1)
        
        # === REFLECTION 1 ===
        print("\n" + "=" * 70)
        print("REFLECTION PHASE 1: Self-Critique")
        print("=" * 70)
        
        print("\nAGENT PRO Reflects:")
        print("-" * 70)
        pro_refl_1 = self.agent_pro.reflect_on_argument(pro_arg_1)
        print(pro_refl_1[:500] + "...\n[Reflection continues...]")  # Show partial
        pro_reflections.append(pro_refl_1)
        
        print("\nAGENT CON Reflects:")
        print("-" * 70)
        con_refl_1 = self.agent_con.reflect_on_argument(con_arg_1)
        print(con_refl_1[:500] + "...\n[Reflection continues...]")
        con_reflections.append(con_refl_1)
        
        # Extract summaries for Round 2
        print("\nExtracting key insights for Round 2...")
        pro_summary_1 = self.agent_pro.extract_reflection_summary(pro_refl_1)
        con_summary_1 = self.agent_con.extract_reflection_summary(con_refl_1)
        
         
        # === ROUND 2: Improved Arguments ===
        print("\n" + "=" * 70)
        print("ROUND 2: IMPROVED ARGUMENTS (Based on Reflection)")
        print("=" * 70)
        
        print("\nAGENT PRO (Improved):")
        print("-" * 70)
        pro_arg_2 = self.agent_pro.refine_argument(
            topic=topic,
            previous_argument=pro_arg_1,
            reflection_summary=pro_summary_1,
            opponent_argument=con_arg_1,
            round_num=2
        )
        print(pro_arg_2)
        pro_arguments.append(pro_arg_2)
        
        print("\nAGENT CON (Improved):")
        print("-" * 70)
        con_arg_2 = self.agent_con.refine_argument(
            topic=topic,
            previous_argument=con_arg_1,
            reflection_summary=con_summary_1,
            opponent_argument=pro_arg_1,
            round_num=2
        )
        print(con_arg_2)
        con_arguments.append(con_arg_2)
        
        # === REFLECTION 2 (Optional but good to show improvement) ===
        print("\n" + "=" * 70)
        print("REFLECTION PHASE 2: Did We Improve?")
        print("=" * 70)
        
        print("\nAGENT PRO Reflects on Round 2:")
        print("-" * 70)
        pro_refl_2 = self.agent_pro.reflect_on_argument(pro_arg_2)
        print(pro_refl_2[:400] + "...\n[Checking for remaining flaws...]")
        pro_reflections.append(pro_refl_2)
        
        print("\nAGENT CON Reflects on Round 2:")
        print("-" * 70)
        con_refl_2 = self.agent_con.reflect_on_argument(con_arg_2)
        print(con_refl_2[:400] + "...\n[Checking for remaining flaws...]")
        con_reflections.append(con_refl_2)
        
        # Extract summaries for Round 3
        print("\nExtracting insights for final round...")
        pro_summary_2 = self.agent_pro.extract_reflection_summary(pro_refl_2)
        con_summary_2 = self.agent_con.extract_reflection_summary(con_refl_2)
        
        
        # === ROUND 3: Final Polish ===
        print("\n" + "=" * 70)
        print("ROUND 3: FINAL POLISHED ARGUMENTS")
        print("=" * 70)
        
        print("\nAGENT PRO (Final):")
        print("-" * 70)
        pro_arg_3 = self.agent_pro.refine_argument(
            topic=topic,
            previous_argument=pro_arg_2,
            reflection_summary=pro_summary_2,
            opponent_argument=con_arg_2,
            round_num=3
        )
        print(pro_arg_3)
        pro_arguments.append(pro_arg_3)
        
        print("\nAGENT CON (Final):")
        print("-" * 70)
        con_arg_3 = self.agent_con.refine_argument(
            topic=topic,
            previous_argument=con_arg_2,
            reflection_summary=con_summary_2,
            opponent_argument=pro_arg_2,
            round_num=3
        )
        print(con_arg_3)
        con_arguments.append(con_arg_3)
        
        # === FINAL VERDICT ===
        print("\n" + "=" * 70)
        print("FINAL VERDICT")
        print("=" * 70)
        
        verdict = self.generate_verdict(topic, pro_arguments, con_arguments)
        print(verdict)
        
        print("\n" + "=" * 70)
        print("DEBATE COMPLETE!")
        print("=" * 70)
        
        return {
            'pro_arguments': pro_arguments,
            'con_arguments': con_arguments,
            'pro_reflections': pro_reflections,
            'con_reflections': con_reflections,
            'verdict': verdict
        }

    def run_split_screen_debate(self, topic, total_rounds=3):
         """Run debate with split-screen outputs"""
    
         pro_output = []
         con_output = []
         verdict_output = []
        
         def format_pro(text):
            pro_output.append(text)
            return "\n".join(pro_output)
        
         def format_con(text):
            con_output.append(text)
            return "\n".join(con_output)
        
         # Initialize with topic header
         header = "AI DEBATE ARENA\n"
         header += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
         header += f"**Topic:** {topic}\n"
         header += "**Pattern:** Reflection (from Andrew Ng's Agentic AI Course)\n"
         header += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
         pro_config = f"Agent Pro: {self.agent_pro.clientType.upper()} Model {self.agent_pro.model}\n"
         con_config = f"Agent Con: {self.agent_con.clientType.upper()} Model {self.agent_con.model}\n"
         yield format_pro(header + pro_config +"Preparing to debate..."), format_con(header + con_config + "Preparing to debate..."), ""
        
         pro_arguments = []
         con_arguments = []
        
         # === ROUND 1 ===
         yield format_pro("\n" + "="*50), format_con("\n" + "="*50), ""
         yield format_pro("ROUND 1: OPENING ARGUMENT"), format_con("ROUND 1: OPENING ARGUMENT"), ""
         yield format_pro("="*50 + "\n"), format_con("="*50 + "\n"), ""
        
         # Pro argues
         pro_arg_1 = self.agent_pro.generate_argument(topic, round_num=1)
         yield format_pro(pro_arg_1 + "\n"), format_con("Waiting for opponent...\n"), ""
         pro_arguments.append(pro_arg_1)
        
         # Con argues
         con_arg_1 = self.agent_con.generate_argument(topic, round_num=1)
         yield "", format_con(con_arg_1 + "\n"), ""
         con_arguments.append(con_arg_1)
        
         # === REFLECTION 1 ===
         yield format_pro("\n" + "="*50), format_con("\n" + "="*50), ""
         yield format_pro("REFLECTION: AI Critiques Itself"), format_con("REFLECTION: AI Critiques Itself"), ""
         yield format_pro("="*50), format_con("="*50), ""
         yield format_pro("Analyzing my own biases and flaws...\n"), format_con("Analyzing my own biases and flaws...\n"), ""
        
         # Pro reflects
         pro_refl_1 = self.agent_pro.reflect_on_argument(pro_arg_1)
        
         # Con reflects
         con_refl_1 = self.agent_con.reflect_on_argument(con_arg_1)
         yield format_pro(pro_refl_1 + "\n"), format_con(con_refl_1 + "\n"), ""
        
        # Extract summaries
         yield format_pro("\nLearning from mistakes...\n"), format_con("\nLearning from mistakes...\n"), ""
         pro_summary_1 = self.agent_pro.extract_reflection_summary(pro_refl_1)
         con_summary_1 = self.agent_con.extract_reflection_summary(con_refl_1)
        
         # === ROUND 2 ===
         yield format_pro("\n" + "="*50), format_con("\n" + "="*50), ""
         yield format_pro("ROUND 2: IMPROVED ARGUMENT"), format_con("ROUND 2: IMPROVED ARGUMENT"), ""
         yield format_pro("="*50), format_con("="*50), ""
         yield format_pro("Fixing flaws from Round 1...\n"), format_con("Fixing flaws from Round 1...\n"), ""
        
         # Pro refines
         pro_arg_2 = self.agent_pro.refine_argument(
            topic=topic,
            previous_argument=pro_arg_1,
            reflection_summary=pro_summary_1,
            opponent_argument=con_arg_1,
            round_num=2
         )
    
         pro_arguments.append(pro_arg_2)
        
         # Con refines
         con_arg_2 = self.agent_con.refine_argument(
            topic=topic,
            previous_argument=con_arg_1,
            reflection_summary=con_summary_1,
            opponent_argument=pro_arg_1,
            round_num=2
         )
         yield format_pro(pro_arg_2 + "\n"), format_con(con_arg_2 + "\n"), ""
         con_arguments.append(con_arg_2)
        
         # === REFLECTION 2 ===
         yield format_pro("\n" + "="*50), format_con("\n" + "="*50), ""
         yield format_pro("REFLECTION 2: Did I Improve?"), format_con("REFLECTION 2: Did I Improve?"), ""
         yield format_pro("="*50 + "\n"), format_con("="*50 + "\n"), ""
        
         pro_refl_2 = self.agent_pro.reflect_on_argument(pro_arg_2)
         con_refl_2 = self.agent_con.reflect_on_argument(con_arg_2)
        
         yield format_pro(pro_refl_2 + "\n"), format_con(con_refl_2 + "\n"), ""
        
         pro_summary_2 = self.agent_pro.extract_reflection_summary(pro_refl_2)
         con_summary_2 = self.agent_con.extract_reflection_summary(con_refl_2)
        
         # === ROUND 3 ===
         yield format_pro("\n" + "="*50), format_con("\n" + "="*50), ""
         yield format_pro("ROUND 3: FINAL ARGUMENT"), format_con("ROUND 3: FINAL ARGUMENT"), ""
         yield format_pro("="*50), format_con("="*50), ""
         yield format_pro("Most refined position...\n"), format_con("Most refined position...\n"), ""
        
         pro_arg_3 = self.agent_pro.refine_argument(
            topic=topic,
            previous_argument=pro_arg_2,
            reflection_summary=pro_summary_2,
            opponent_argument=con_arg_2,
            round_num=3
         )
       
         pro_arguments.append(pro_arg_3)
        
         con_arg_3 = self.agent_con.refine_argument(
            topic=topic,
            previous_argument=con_arg_2,
            reflection_summary=con_summary_2,
            opponent_argument=pro_arg_2,
            round_num=3
         )
         yield format_pro(pro_arg_3 + "\n"), format_con(con_arg_3 + "\n"), ""
         con_arguments.append(con_arg_3)
        
         # === VERDICT ===
         verdict_output.append("FINAL VERDICT")
         verdict_output.append("="*50 + "\n")
         verdict_output.append(f"Judge: {self.agent_pro.clientType.upper()} Model {self.agent_pro.model} (neutral task)\n")
         verdict_output.append("Judge is analyzing all arguments...\n")
        
         verdict = self.generate_verdict(topic, pro_arguments, con_arguments)
         verdict_output.append(verdict)
         verdict_output.append("\n\n" + "="*50)
         verdict_output.append("\nDebate Complete!")
        
         yield format_pro("\nAll rounds complete!"), format_con("\nAll rounds complete!"),  "\n".join(verdict_output)


    def generate_verdict(self, topic, pro_arguments, con_arguments):
        """Synthesize the full debate and provide final analysis"""
    
        verdict_prompt = f"""Analyze this complete 3-round debate:

        TOPIC: {topic}

        AGENT PRO'S EVOLUTION:
        Round 1: {pro_arguments[0][:200]}...
        Round 2: {pro_arguments[1][:200]}...
        Round 3: {pro_arguments[2][:200]}...

        AGENT CON'S EVOLUTION:
        Round 1: {con_arguments[0][:200]}...
        Round 2: {con_arguments[1][:200]}...
        Round 3: {con_arguments[2][:200]}...

        Provide final verdict:
        1. Which agent argued more effectively overall? (Not about being right, about argument quality)
        2. How did arguments improve from Round 1 to Round 3?
        3. What key insights emerged from this debate?
        4. What recommendation would you make for the decision?

        Be balanced and insightful. 100-150 words."""

        # Use Pro agent's client to generate verdict (neutral task)
        message = self.agent_pro.get_message(prompt=verdict_prompt)
        return message

    def run_multiround_debate_streaming(self, topic, total_rounds=3):
        """Run debate and YIELD results incrementally for live updates"""
        
        output = []
        
        def add_and_yield(text):
            """Helper to add text and yield current output"""
            output.append(text)
            return "\n".join(output)
        
        # Header
        yield add_and_yield("=" * 70)
        yield add_and_yield(f"MULTI-ROUND DEBATE: {topic}")
        yield add_and_yield("=" * 70)
        yield add_and_yield("")
        
        pro_arguments = []
        con_arguments = []
        pro_reflections = []
        con_reflections = []
        
        # === ROUND 1 ===
        yield add_and_yield("=" * 70)
        yield add_and_yield("ROUND 1: INITIAL ARGUMENTS")
        yield add_and_yield("=" * 70)
        yield add_and_yield("")
        
        yield add_and_yield("AGENT PRO:")
        yield add_and_yield("-" * 70)
        pro_arg_1 = self.agent_pro.generate_argument(topic, round_num=1)
        yield add_and_yield(pro_arg_1)
        yield add_and_yield("")
        pro_arguments.append(pro_arg_1)
        
        yield add_and_yield("AGENT CON:")
        yield add_and_yield("-" * 70)
        con_arg_1 = self.agent_con.generate_argument(topic, round_num=1)
        yield add_and_yield(con_arg_1)
        yield add_and_yield("")
        con_arguments.append(con_arg_1)
        
        # === REFLECTION 1 ===
        yield add_and_yield("=" * 70)
        yield add_and_yield("REFLECTION PHASE 1: Self-Critique")
        yield add_and_yield("=" * 70)
        yield add_and_yield("")
        
        yield add_and_yield("AGENT PRO Reflects:")
        yield add_and_yield("-" * 70)
        pro_refl_1 = self.agent_pro.reflect_on_argument(pro_arg_1)
        yield add_and_yield(pro_refl_1[:500] + "...")
        yield add_and_yield("[Reflection continues...]")
        yield add_and_yield("")
        pro_reflections.append(pro_refl_1)
        
        yield add_and_yield("AGENT CON Reflects:")
        yield add_and_yield("-" * 70)
        con_refl_1 = self.agent_con.reflect_on_argument(con_arg_1)
        yield add_and_yield(con_refl_1[:500] + "...")
        yield add_and_yield("[Reflection continues...]")
        yield add_and_yield("")
        con_reflections.append(con_refl_1)
        
        # Extract summaries
        yield add_and_yield("Extracting key insights for Round 2...")
        yield add_and_yield("")
        pro_summary_1 = self.agent_pro.extract_reflection_summary(pro_refl_1)
        con_summary_1 = self.agent_con.extract_reflection_summary(con_refl_1)
        
        # === ROUND 2 ===
        yield add_and_yield("=" * 70)
        yield add_and_yield("ROUND 2: IMPROVED ARGUMENTS")
        yield add_and_yield("=" * 70)
        yield add_and_yield("")
        
        yield add_and_yield("AGENT PRO (Improved):")
        yield add_and_yield("-" * 70)
        pro_arg_2 = self.agent_pro.refine_argument(
            topic=topic,
            previous_argument=pro_arg_1,
            reflection_summary=pro_summary_1,
            opponent_argument=con_arg_1,
            round_num=2
        )
        yield add_and_yield(pro_arg_2)
        yield add_and_yield("")
        pro_arguments.append(pro_arg_2)
        
        yield add_and_yield("AGENT CON (Improved):")
        yield add_and_yield("-" * 70)
        con_arg_2 = self.agent_con.refine_argument(
            topic=topic,
            previous_argument=con_arg_1,
            reflection_summary=con_summary_1,
            opponent_argument=pro_arg_1,
            round_num=2
        )
        yield add_and_yield(con_arg_2)
        yield add_and_yield("")
        con_arguments.append(con_arg_2)
        
        # === REFLECTION 2 ===
        yield add_and_yield("=" * 70)
        yield add_and_yield("REFLECTION PHASE 2: Did We Improve?")
        yield add_and_yield("=" * 70)
        yield add_and_yield("")
        
        yield add_and_yield("AGENT PRO Reflects on Round 2:")
        yield add_and_yield("-" * 70)
        pro_refl_2 = self.agent_pro.reflect_on_argument(pro_arg_2)
        yield add_and_yield(pro_refl_2[:400] + "...")
        yield add_and_yield("[Checking for remaining flaws...]")
        yield add_and_yield("")
        pro_reflections.append(pro_refl_2)
        
        yield add_and_yield("AGENT CON Reflects on Round 2:")
        yield add_and_yield("-" * 70)
        con_refl_2 = self.agent_con.reflect_on_argument(con_arg_2)
        yield add_and_yield(con_refl_2[:400] + "...")
        yield add_and_yield("[Checking for remaining flaws...]")
        yield add_and_yield("")
        con_reflections.append(con_refl_2)
        
        # Extract summaries
        yield add_and_yield("Extracting insights for final round...")
        yield add_and_yield("")
        pro_summary_2 = self.agent_pro.extract_reflection_summary(pro_refl_2)
        con_summary_2 = self.agent_con.extract_reflection_summary(con_refl_2)
        
        # === ROUND 3 ===
        yield add_and_yield("=" * 70)
        yield add_and_yield("ROUND 3: FINAL POLISHED ARGUMENTS")
        yield add_and_yield("=" * 70)
        yield add_and_yield("")
        
        yield add_and_yield("AGENT PRO (Final):")
        yield add_and_yield("-" * 70)
        pro_arg_3 = self.agent_pro.refine_argument(
            topic=topic,
            previous_argument=pro_arg_2,
            reflection_summary=pro_summary_2,
            opponent_argument=con_arg_2,
            round_num=3
        )
        yield add_and_yield(pro_arg_3)
        yield add_and_yield("")
        pro_arguments.append(pro_arg_3)
        
        yield add_and_yield("AGENT CON (Final):")
        yield add_and_yield("-" * 70)
        con_arg_3 = self.agent_con.refine_argument(
            topic=topic,
            previous_argument=con_arg_2,
            reflection_summary=con_summary_2,
            opponent_argument=pro_arg_2,
            round_num=3
        )
        yield add_and_yield(con_arg_3)
        yield add_and_yield("")
        con_arguments.append(con_arg_3)
        
        # === VERDICT ===
        yield add_and_yield("=" * 70)
        yield add_and_yield("FINAL VERDICT")
        yield add_and_yield("=" * 70)
        yield add_and_yield("")
        
        yield add_and_yield("Generating final analysis...")
        verdict = self.generate_verdict(topic, pro_arguments, con_arguments)
        yield add_and_yield(verdict)
        yield add_and_yield("")
        
        yield add_and_yield("=" * 70)
        yield add_and_yield("DEBATE COMPLETE!")
        yield add_and_yield("=" * 70)
      
if __name__ == "__main__":
    orchestrator = DebateOrchestrator()
    orchestrator.run_multiround_debate(topic="Should I try pizza or sushi tonight?")
                