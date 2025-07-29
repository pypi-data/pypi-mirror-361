import re
from prompt_toolkit import PromptSession
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
import dspy
import sys
from typing import Optional

LM = dspy.LM("openai/gpt-4.1-mini")
dspy.settings.configure(lm=LM)

console = Console()
session = PromptSession("User: ")

# Global history variable
HISTORY: dspy.History | None = None


def display_welcome():
    """Display a beautiful welcome message using the agent's name"""
    welcome_text = Text()
    welcome_text.append(f"🤖 DSPy", style="bold cyan")
    
    console.print(welcome_text)
    
    commands_text = Text()
    commands_text.append("n", style="bold green")
    commands_text.append(" - new chat, ", style="dim")
    commands_text.append("q", style="bold red")
    commands_text.append(" - quit\n", style="dim")
    
    console.print(commands_text)

def display_new_session():
    """Display a message indicating a new session has started"""
    console.print("[bold green]New session started[/bold green]")
    console.print("\n")

def clear_previous_line():
    """Clear the previous line"""
    sys.stdout.write("\033[1A\033[0J")
    sys.stdout.flush()

def add_history_to_module_signature(module: dspy.Module) -> dspy.Module:
    """Allow the module to use history"""
    if "history" not in module.signature.input_fields:
        module.signature = module.signature.prepend("history", dspy.InputField(desc="The history of the conversation"), type_=Optional[dspy.History])

def get_cost() -> float:
    lm = dspy.settings.lm
    cost = sum([x['cost'] for x in lm.history if x['cost'] is not None])  # cost in USD, as calculated by LiteLLM for certain providers
    return cost

def respond(module: dspy.Module, prompt: str) -> str:
    """Generate response using the module and update history"""
    global HISTORY

    outputs = module(question=prompt, history=HISTORY, lm=LM)

    if HISTORY is None:
        HISTORY = dspy.History(messages=[{"question": prompt, **outputs}])
    else:
        HISTORY.messages.append({"question": prompt, **outputs})

    return outputs.answer


def start_dspy_chat(module: dspy.Module, model: str = None):
    """Start an interactive chat session with the provided agent"""
    global HISTORY
    global LM
    
    if model:
        model_pattern = re.match(r"^o([134])(?:-mini)?", model)
        if model_pattern:
            LM = dspy.LM(model, temperature=1.0, max_tokens=20_000)
            dspy.settings.configure(lm=LM)
        else:
            LM = dspy.LM(model)
            dspy.settings.configure(lm=LM)

    add_history_to_module_signature(module)


    console.clear()
    display_welcome()
    try:
        while True:
            try:
                prompt: str = session.prompt()
                console.print("\n")
                if prompt.lower() in {"q", "quit", "exit"}:
                    break
                if prompt.lower() in {"n", "new"}:
                    HISTORY = None
                    console.clear()
                    display_welcome()
                    continue
            except (EOFError, KeyboardInterrupt):
                break

            with console.status("[bold yellow]thinking...", spinner="dots"):
                response_text = respond(module, prompt)
            
            console.print(f"[bold blue]Assistant:")
            console.print(Markdown(response_text))
            console.print("\n")
    except Exception as e:
        pass

    finally:
        # The end
        console.print("\n")
        console.print(f"[bold green]Cost: ${get_cost():.6f}[/bold green]")


if __name__ == "__main__":
    start_dspy_chat(dspy.Predict("question -> answer"), "o3")