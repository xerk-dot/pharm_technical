import os
from openai import OpenAI
from dotenv import load_dotenv
import integration
import re
import json

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Configure OpenAI with the API key
client = OpenAI(api_key=api_key)

def chat_with_openai(messages, tools=None, tool_choice=None):
    """
    Send messages to OpenAI API and get a response
    
    Args:
        messages: List of message objects
        tools: Optional list of tools to provide to the model
        tool_choice: Optional specification for tool choice behavior
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or another model of your choice
            messages=messages,
            tools=tools,
            tool_choice=tool_choice
        )
        return response.choices[0].message
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def extract_phone_number(text):
    """Extract a phone number from text"""
    # Look for patterns like XXX-XXX-XXXX or (XXX) XXX-XXXX
    phone_pattern = r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
    match = re.search(phone_pattern, text)
    if match:
        return match.group(1)
    return None

def main():
    # Define tools for the model to use
    tools = [
        {
            "type": "function",
            "function": {
                "name": "find_pharmacy_by_phone",
                "description": "Find a pharmacy by its phone number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "The phone number to search for (e.g., 123-456-7890)"
                        }
                    },
                    "required": ["phone_number"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_all_pharmacies",
                "description": "Get a list of all pharmacies in the database",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mock_send_email",
                "description": "Send an email to a pharmacy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pharmacy_email": {
                            "type": "string",
                            "description": "The email address of the pharmacy"
                        },
                        "subject": {
                            "type": "string",
                            "description": "The subject of the email"
                        },
                        "body": {
                            "type": "string",
                            "description": "The body content of the email"
                        }
                    },
                    "required": ["pharmacy_email", "subject", "body"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mock_schedule_callback",
                "description": "Schedule a callback to a pharmacy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pharmacy_name": {
                            "type": "string",
                            "description": "The name of the pharmacy"
                        },
                        "phone_number": {
                            "type": "string",
                            "description": "The phone number to call back"
                        },
                        "callback_time": {
                            "type": "string",
                            "description": "The requested callback time (e.g., 'Tomorrow at 2pm')"
                        }
                    },
                    "required": ["pharmacy_name", "phone_number", "callback_time"]
                }
            }
        }
    ]
    
    # Initialize conversation history
    conversation = [
        {"role": "system", "content": "You help pharmacies who are our B2B partners. You can look up pharmacy information, send emails, and schedule callbacks. When a pharmacy technician mentions a phone number, check if it belongs to a pharmacy in our database."}
    ]
    
    print("Welcome to the Pharmacy Assistant! Type 'quit' to exit.")
    
    while True:
        # Get user input
        user_input = input("You: ")
        
        if user_input.lower() == 'quit':
            break
        
        # Add user message to conversation
        conversation.append({"role": "user", "content": user_input})
        
        # Get response from OpenAI
        response = chat_with_openai(conversation, tools=tools)
        
        if response:
            # Check if the model wants to call a tool
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Add the assistant's response with tool calls to the conversation
                conversation.append({
                    "role": "assistant",
                    "content": response.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        } for tool_call in response.tool_calls
                    ]
                })
                
                # Process each tool call
                for tool_call in response.tool_calls:
                    function_name = tool_call.function.name
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        function_args = {}
                    
                    # Execute the appropriate function based on the tool call
                    if function_name == "find_pharmacy_by_phone":
                        phone_number = function_args.get("phone_number")
                        pharmacy = integration.find_pharmacy_by_phone(phone_number)
                        
                        # Add the tool response to the conversation
                        conversation.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": str(pharmacy) if pharmacy else "No pharmacy found with that phone number."
                        })
                    
                    elif function_name == "get_all_pharmacies":
                        pharmacies = integration.get_all_pharmacies()
                        
                        # Add the tool response to the conversation
                        conversation.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": str(pharmacies)
                        })
                    
                    elif function_name == "mock_send_email":
                        pharmacy_email = function_args.get("pharmacy_email")
                        subject = function_args.get("subject")
                        body = function_args.get("body")
                        
                        result = integration.mock_send_email(pharmacy_email, subject, body)
                        
                        # Add the tool response to the conversation
                        conversation.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": f"Email sent: {result}"
                        })
                    
                    elif function_name == "mock_schedule_callback":
                        pharmacy_name = function_args.get("pharmacy_name")
                        phone_number = function_args.get("phone_number")
                        callback_time = function_args.get("callback_time")
                        
                        result = integration.mock_schedule_callback(pharmacy_name, phone_number, callback_time)
                        
                        # Add the tool response to the conversation
                        conversation.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": f"Callback scheduled: {result}"
                        })
                
                # Get a new response from the model after tool use
                response = chat_with_openai(conversation)
                
                if response:
                    # Print the assistant's response
                    print(f"Assistant: {response.content}")
                    
                    # Add assistant response to conversation history
                    conversation.append({"role": "assistant", "content": response.content})
                else:
                    print("Failed to get a response after tool call. Please try again.")
            else:
                # Print the assistant's response
                print(f"Assistant: {response.content}")
                
                # Add assistant response to conversation history
                conversation.append({"role": "assistant", "content": response.content})
        else:
            print("Failed to get a response. Please try again.")

if __name__ == "__main__":
    main()
    