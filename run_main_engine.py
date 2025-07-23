import argparse
from main_engine import CodingAgent
from dotenv import load_dotenv
import json

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="An autonomous coding agent workflow.")

    parser.add_argument('--prompt', type=str, required=True, help='The initial prompt describing the project to build.')
    parser.add_argument('--project_path', type=str, default='./new_project', help='The base path for the new project.')
    parser.add_argument('--max_retries', type=int, default=3, help='Maximum retries for the planning and verification loop.')
    parser.add_argument('--provider', type=str, default='groq', help='The provider to use for inference (e.g., groq, gemini).')
    args = parser.parse_args()

    agent = CodingAgent(args.project_path, provider=args.provider)
    
    # --- New Autonomous Workflow ---
    
    current_prompt = args.prompt
    approved_plan = None
    
    for i in range(args.max_retries):
        agent.console.print(f"[bold magenta]--- Planning Attempt {i+1}/{args.max_retries} ---[/]")
        
        # 1. Plan the project
        plan = agent.plan_project(current_prompt)
        if not plan:
            agent.console.print("[red]Failed to generate a project plan. Aborting.[/]")
            return

        # 2. Verify the plan
        is_approved, feedback = agent.verify_project_plan(plan, args.prompt)
        
        if is_approved:
            approved_plan = plan
            agent.console.print("[bold green]--- Project Plan Approved! ---[/]")
            break
        else:
            agent.console.print(f"[yellow]Plan rejected. Refining prompt with feedback...[/]")
            current_prompt = f"Original prompt: '{args.prompt}'. Previous plan: {json.dumps(plan)}. Feedback: '{feedback}'. Please generate a new, improved plan based on this feedback."
            
    if not approved_plan:
        agent.console.print("[red]Failed to get an approved project plan after several attempts. Aborting.[/]")
        return
        
    # 3. Create the project directory and structure
    agent.create_project_directory(args.project_path, approved_plan)
    
    # 4. Generate file content from instructions
    agent.generate_file_content_from_instructions(args.project_path)
    
    # 5. Refine the generated Python code
    agent.refine_python_code(args.project_path)
    
    agent.console.print("[bold green]--- Full Workflow Completed Successfully! ---[/]")
    agent.console.print(f"Project created at: {args.project_path}")

if __name__ == "__main__":
    main()
