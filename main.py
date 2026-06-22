import subprocess
import sys


COMMANDS = {
    "sentiment": "python sentiment/sentiment_analyzer.py",
    "strategic": "python sentiment/strategic_classifier.py",
    "dashboard": "streamlit run app.py",
    "retriever": "python retrieval/retriever.py",
    "audit": "python utils/audit_project.py",
}


def run_command(command_name):
    if command_name not in COMMANDS:
        print("Available commands:")
        for name in COMMANDS:
            print(f"- {name}")
        return

    command = COMMANDS[command_name]
    print(f"Running: {command}")

    subprocess.run(command, shell=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("python main.py dashboard")
        print("python main.py sentiment")
        print("python main.py strategic")
        print("python main.py retriever")
        print("python main.py audit")
    else:
        run_command(sys.argv[1])