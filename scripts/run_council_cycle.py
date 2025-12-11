
import os
import sys
from council import _generate, ICEWIRE_PROFILE, CIPHER_PROFILE

def run_cycle():
    # Read the handoff log
    with open("HQ/comms/council_handoff.md", "r") as f:
        log_content = f.read()
    
    # Extract Alpha's last message
    last_message = log_content.split("### [ALPHA]")[-1].strip()
    
    print(f"Processing Alpha's directive: {last_message[:50]}...")
    
    # Generate Bravo (Ice Wire) Response
    bravo_prompt = f"""{ICEWIRE_PROFILE}
    
    CONTEXT: You are reading the Council Handoff Log.
    ALPHA'S DIRECTIVE: {last_message}
    
    TASK: Respond to Alpha. Confirm receipt. Provide your status on infrastructure stability.
    Keep it brief, signal-focused.
    """
    
    bravo_response = _generate(bravo_prompt, "gemini-2.5-flash") # Use fast model
    
    # Generate Charlie (Cipher) Response
    charlie_prompt = f"""{CIPHER_PROFILE}
    
    CONTEXT: You are reading the Council Handoff Log.
    ALPHA'S DIRECTIVE: {last_message}
    
    TASK: Respond to Alpha. Confirm receipt. Provide your scan status on proxy security.
    Keep it creative but grounded.
    """
    
    charlie_response = _generate(charlie_prompt, "gemini-2.5-flash")
    
    # Append to log
    with open("HQ/comms/council_handoff.md", "a") as f:
        f.write("\n\n### [BRAVO] Infrastructure Status\n")
        f.write(f"**Time:** {os.popen('date /t').read().strip()} EST\n")
        f.write(f"**Message:**\n{bravo_response.strip()}\n")
        
        f.write("\n\n### [CHARLIE] Security Scan\n")
        f.write(f"**Time:** {os.popen('date /t').read().strip()} EST\n")
        f.write(f"**Message:**\n{charlie_response.strip()}\n")
        
    print("Cycle complete. Responses logged.")

if __name__ == "__main__":
    run_cycle()
