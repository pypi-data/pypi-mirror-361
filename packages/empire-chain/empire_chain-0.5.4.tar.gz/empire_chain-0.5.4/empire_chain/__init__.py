# Empire Chain - Your AI Orchestration Framework
# Updated: March 2025 - Adding comments for version tracking

import sys

def display_welcome():
    welcome_message = """
    ███████╗███╗   ███╗██████╗ ██╗██████╗ ███████╗
    ██╔════╝████╗ ████║██╔══██╗██║██╔══██╗██╔════╝
    █████╗  ██╔████╔██║██████╔╝██║██████╔╝█████╗  
    ██╔══╝  ██║╚██╔╝██║██╔═══╝ ██║██╔══██╗██╔══╝  
    ███████╗██║ ╚═╝ ██║██║     ██║██║  ██║███████╗
    ╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝
     ██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗
    ██╔════╝██║  ██║██╔══██╗██║████╗  ██║
    ██║     ███████║███████║██║██╔██╗ ██║
    ██║     ██╔══██║██╔══██║██║██║╚██╗██║
    ╚██████╗██║  ██║██║  ██║██║██║ ╚████║
     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
    =============================================
         🔗 Welcome to Empire Chain! Ready to 
            chain your AI dreams together? 🔗
    =============================================
    """
    print(welcome_message, file=sys.stderr)

if not any('pytest' in arg or 'sphinx' in arg for arg in sys.argv):
    display_welcome()