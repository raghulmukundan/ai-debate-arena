import gradio as gr
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from debate_engine import DebateOrchestrator

PROVIDER_MODELS = {
    "Claude": [
        "claude-sonnet-4-5-20250929",
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-haiku-4-5-20251001"
    ],
    "OpenAI": [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo"
    ],
}

def update_model_dropdown(provider):
    """update model dropdown based on selected provider"""
    models = PROVIDER_MODELS.get(provider, [])
    return gr.Dropdown(choices=models, value=models[0] if models else None)

def run_debate(topic, pro_provider, pro_model, pro_api_key,
                             con_provider, con_model, con_api_key):
    """Run debate with user-provided API keys and return the debate log."""
     # Validate inputs
    if not topic or len(topic.strip()) < 5:
        yield "Please enter a topic (at least 5 characters)"
        return
    
    # Validate API keys
    if not pro_api_key or len(pro_api_key.strip()) < 10:
        yield f"Please provide API key for Agent Pro ({pro_provider})"
        return
    
    if not con_api_key or len(con_api_key.strip()) < 10:
        yield f"Please provide API key for Agent Con ({con_provider})"
        return
    
       # Show initialization
    config_msg = f"Using: {pro_provider}/{pro_model}\nInitializing..."
    yield config_msg, config_msg.replace("Pro", "Con"), ""
    
    print(f"Running: {pro_provider}/{pro_model} vs {con_provider}/{con_model}")
    
    try:
        orchestrator = DebateOrchestrator(
            pro_provider=pro_provider,
            pro_model=pro_model,
            pro_api_key=pro_api_key.strip(),
            con_provider=con_provider,
            con_model=con_model,
            con_api_key=con_api_key.strip()
        )
        
        # Stream results - now yields 3 values!
        for pro_text, con_text, verdict_text in orchestrator.run_split_screen_debate(topic=topic.strip()):
            yield pro_text, con_text, verdict_text
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        yield error_msg, error_msg, ""
        
with gr.Blocks(title="AI Debate Arena") as interface:
    gr.Markdown("## AI Debate Arena")
    gr.Markdown(
        "Welcome to the AI Debate Arena! Configure two AI agents to debate a topic of your choice. "
        "Select their providers, models, and provide API keys to get started."
        "**Built with:** Reflection Pattern from Andrew Ng's Agentic AI Course"
    )
    
    topic_input = gr.Textbox(
        label="Debate Topic",
        placeholder="Should I order pizza or sushi for dinner?",
        lines=2
    )     
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Agent Pro Configuration")
            pro_provider = gr.Dropdown(
                choices=list(PROVIDER_MODELS.keys()),
                value="Claude",
                label="Provider"
            )
            pro_model = gr.Dropdown(
                choices=PROVIDER_MODELS["Claude"],
                value="claude-sonnet-4-20250514",
                label="Model"
            )
            pro_api_key = gr.Textbox(
                label="API Key",
                placeholder="sk-ant-...",
                type="password"
            )
        
        with gr.Column():
            gr.Markdown("### Agent Con Configuration")
            con_provider = gr.Dropdown(
                choices=list(PROVIDER_MODELS.keys()),
                value="Claude",
                label="Provider"
            )
            con_model = gr.Dropdown(
                choices=PROVIDER_MODELS["Claude"],
                value="claude-sonnet-4-20250514",
                label="Model"
            )
            con_api_key = gr.Textbox(
                label="API Key",
                placeholder="sk-ant-...",
                type="password"
            )
    
    # Update model dropdowns when provider changes
    pro_provider.change(
        fn=update_model_dropdown,
        inputs=[pro_provider],
        outputs=[pro_model]
    )
        
    con_provider.change(
        fn=update_model_dropdown,
        inputs=[con_provider],
        outputs=[con_model]
    )               
    
    submit_btn = gr.Button("Start Debate", variant="primary", size="lg")
    
    gr.Examples(
        examples=[
            ["Should I order pizza or sushi for dinner?"],
            ["Should I watch Dune 2 or Barbie tonight?"],
            ["Should I buy an iPhone or Samsung phone?"],
            ["Should I go to the gym in the morning or evening?"],
            ["Should I accept the job offer or stay at my current company?"],
        ],
        inputs=topic_input,
        label="📝 Example Topics"
    )
    
    gr.Markdown("---")
    gr.Markdown("## Live Debate")
    with gr.Row():
            with gr.Column():
                gr.Markdown("### Agent Pro")
                pro_output = gr.Textbox(
                    label="",
                    lines=25,
                    max_lines=40,
                    show_label=False
                )
            
            with gr.Column():
                gr.Markdown("### Agent Con")
                con_output = gr.Textbox(
                    label="",
                    lines=25,
                    max_lines=40,
                    show_label=False
                )
     # SEPARATE VERDICT SECTION
    gr.Markdown("---")
    with gr.Accordion("Final Verdict", open=True):
        gr.Markdown("*The judge analyzes all arguments and determines the winner*")
        verdict_output = gr.Textbox(
            label="",
            lines=25,
            max_lines=40,
            show_label=False
        )
        
    submit_btn.click(
        fn=run_debate,
        inputs=[
            topic_input,
            pro_provider, pro_model, pro_api_key,
            con_provider, con_model, con_api_key
        ],
        outputs=[pro_output, con_output, verdict_output],
    )
    
if __name__ == "__main__":
    interface.launch()