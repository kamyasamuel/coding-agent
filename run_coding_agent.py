import argparse
from coding_agent import CodingAgent
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("GROQ_API_KEY"))  # Ensure the API key is loaded from .env
def main():
    parser = argparse.ArgumentParser(description="Run CodingAgent functions with parameters.")
    parser.add_argument('--base_path', type=str, default='.', help='Base path for CodingAgent')
    parser.add_argument('--read_docs', action='store_true', help='Read and summarize documentation')
    parser.add_argument('--print_tree', nargs='?', const=True, default=False, help='Pretty print directory tree (optionally provide output file)')
    parser.add_argument('--print_summaries', nargs='?', const=True, default=False, help='Pretty print documentation summaries (optionally provide output file)')
    parser.add_argument('--save_summaries', type=str, help='Save documentation summaries to JSON file')
    parser.add_argument('--create_project', type=str, help='Create a project directory at the given path')
    parser.add_argument('--project_type', type=str, default='basic', help='Project template type')
    parser.add_argument('--use_groq', action='store_true', help='Use Groq to generate code content')

    args = parser.parse_args()

    agent = CodingAgent(args.base_path)

    if args.read_docs:
        agent.read_package_docs()

    if args.print_tree:
        agent.generate_directory_tree()
        if isinstance(args.print_tree, str):
            agent.pretty_print_tree(args.print_tree)
        else:
            agent.pretty_print_tree()

    if args.print_summaries:
        if isinstance(args.print_summaries, str):
            agent.pretty_print_summaries(args.print_summaries)
        else:
            agent.pretty_print_summaries()

    if args.save_summaries:
        agent.save_summaries(args.save_summaries)

    if args.create_project:
        project_structure = agent.design_project_template(args.project_type, use_groq=args.use_groq)
        agent.create_project_directory(args.create_project, project_structure, use_groq=args.use_groq)

if __name__ == "__main__":
    main()