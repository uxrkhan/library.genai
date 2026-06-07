import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from utils.config import SYSTEM_PROMPT
from utils.config import LibraryDataBase
from colorama import Fore, init

load_dotenv()
init(autoreset=True)
MIN_SEARCH_RESULTS = 1
MAX_SEARCH_RESULTS = 20 
DEF_SEARCH_RESULTS = 5
MIN_RECOMM_RESULTS = 1
MAX_RECOMM_RESULTS = 10
DEF_RECOMM_RESULTS = 3

class LibraryToolConfig():
    search_fn = {
        "name": "search_books",
        "description": "Search for books using various criteria",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term (title, author, or keyword)"
                },
                "genre": {
                    "type": "string",
                    "enum": ["fiction", "non_fiction", "mystery", "romance", "sci_fi", "biography", "history"],
                    "description": "Book genre filter"
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "description": "Maximum number of results to return"
                }
            },
            "required": ["query"]
        }
    }
    manage_fn = {
        "name": "manage_reading_list",
        "description": "Add or remove books from reading list",
        "parameters": {
            "type": "object",
            "properties": {
            "action": {
                "type": "string",
                "enum": ["add", "remove", "view"],
                "description": "Action to perform on reading list"
            },
            "book_id": {
                "type": "string",
                "description": "Book ID to add or remove"
            },
            "book_title": {
                "type": "string",
                "description": "Book title (alternative to book_id)"
            }
            },
            "required": ["action"]
        }
    }
    recommendation_fn = {
        "name": "get_recommendations",
        "description": "Get book recommendations based on preferences",
        "parameters": {
            "type": "object",
            "properties": {
            "genres": {
                "type": "array",
                "items": {
                "type": "string",
                "enum": ["fiction", "non_fiction", "mystery", "romance", "sci_fi", "biography", "history"]
                },
                "description": "Preferred genres"
            },
            "favorite_authors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of favorite authors"
            },
            "count": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Number of recommendations to get"
            }
            },
            "required": ["genres"]
        }
    }
    track_fn = {
        "name": "track_reading",
        "description": "Track reading progress for books",
        "parameters": {
            "type": "object",
            "properties": {
            "book_id": {
                "type": "string",
                "description": "Book ID being tracked"
            },
            "status": {
                "type": "string",
                "enum": ["reading", "completed", "paused", "abandoned"],
                "description": "Reading status"
            },
            "pages_read": {
                "type": "integer",
                "minimum": 0,
                "description": "Number of pages read"
            },
            "rating": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "description": "Book rating (1-5 stars, only for completed books)"
            }
            },
            "required": ["book_id", "status"]
        }
    }

    def __init__(self):
        self.search_tool = types.Tool(function_declarations=[self.search_fn])
        self.manage_tool = types.Tool(function_declarations=[self.manage_fn])
        self.recommendation_tool = types.Tool(function_declarations=[self.recommendation_fn])
        self.track_tool = types.Tool(function_declarations=[self.track_fn])
        self.tools = [self.search_tool, self.manage_tool, self.track_tool, self.recommendation_tool]

class LibraryAssistant(LibraryDataBase, LibraryToolConfig):
    
    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError('API key not found.')
        self.model = os.getenv("MODEL_ID", "gemini-2.5-flash")
        self.client = genai.Client(api_key=self.api_key)
        self.config = types.GenerateContentConfig(tools=self.tools)

    def response(self, success: bool, message: str, result=None):
        if result:
            return str({'success': success, 'message': message, 'result': result})
        return str({'success': success, 'message': message})
    
    def handle_function_call(self, function_name, parameters):
        """Handle library function call execution"""
        if function_name == 'search_books':
            query = parameters.get('query', None)
            if not query:
                return self.response(success=False, message='Please provide a valid search keyword')
            
            genre = parameters.get('genre', None)
            max_results = parameters.get('max_results', DEF_SEARCH_RESULTS)
            if max_results > MAX_SEARCH_RESULTS or max_results < 1:
                return self.response(success=False, message='Cannot provide the given number of search results')
            
            search_results = self.search_books_mock(query=query, genre=genre, max_results=max_results)
            num_results = search_results.get('count', 0)
            if num_results < 1:
                return self.response(success=False, message='Could not fetch any search results')
            
            books_found = search_results['books'][:MAX_RECOMM_RESULTS]
            result = self.response(success=True, message=None, result=books_found)
        
        elif function_name == 'manage_reading_list':
            action = parameters.get('action', None)
            if action not in ['add', 'view', 'remove']:
                return self.response(success=False, message='Invalid action. Please provide a valid action to perform.')
            
            book_id = parameters.get('book_id', None)
            book_title = parameters.get('book_title', None)
            action_result = self.manage_reading_list_mock(action=action, book_id=book_id, book_title=book_title)
            result = str(action_result)

        elif function_name == 'get_recommendations':
            # TODO: Handle get_recommendations function
            # - Parse genres array parameter
            # - Handle optional favorite_authors array
            # - Validate count parameter range
            result = self.response(success=False, message='Could not give recommendations')
        elif function_name == 'track':
            # TODO: Handle track_reading function
            # - Parse book_id, status parameters
            # - Handle optional pages_read, rating
            # - Validate rating range (1-5) for completed books
            result = self.response(success=False, message='Could not perform tracking')
        else:
            result = self.response(success=False, message='Not sure how to handle that.')
        return result
    
    def chat(self, user_input):
        """Main chat function that handles user input and decides whether to call functions"""
        prompt = SYSTEM_PROMPT.replace('{user_input}', user_input)
        chat = [prompt]
        try:
            while True:
                response = self.client.models.generate_content(model=self.model, contents=chat, config=self.config)
                if not response.function_calls:
                    reply = response.text
                    break
                chat.append(response.candidates[0].content)
                for call in response.function_calls:
                    fn_name = call.name
                    fn_args = call.args
                    result = self.handle_function_call(fn_name, fn_args)
                    part = types.Part.from_function_response(name=fn_name, response={'result': result})
                    chat.append(part)
        except Exception as e:
            reply = f'Sorry, I encountered an error: {str(e)}'
        return reply

def answer_library_query(query, assistant=None):
    """Convenient wrapper function for library queries"""
    if query == 'quit':
        return "Exiting..."
    if not assistant:
        assistant = LibraryAssistant()
    try:
        return assistant.chat(query)
    except Exception as e:
        return f'Sorry, an error occured: {str(e)}'

def main():
    """Main function to demonstrate the library assistant."""
    print("Book Library Assistant - Intermediate Function Calling")
    print("Type 'quit' to exit")
    print("=" * 55)
    
    # Sample test queries
    sample_queries = [
        "Find me some mystery books",
        "Add The Great Gatsby to my reading list",
        "Recommend me some fiction and sci-fi books",
        "I finished reading book B001, give it 4 stars",
        "Hello! How can you help me?",
        "What makes a good book?"
    ]
    
    # TODO: Initialize assistant
    assistant = None
    
    print("\n--- Sample Queries ---")
    for query in sample_queries:
        print(f"\n{Fore.GREEN}User:{Fore.RESET} {query}")
        response = answer_library_query(query, assistant)
        print(f"{Fore.YELLOW}Library:{Fore.RESET} {response}")

if __name__ == "__main__":
    main()