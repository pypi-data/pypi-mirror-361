import os
import ast
import re
from typing import Dict, Any, List, Optional, Set
from pathlib import Path

from crewai import Agent
from crewai.tools import tool
from crewai.tools import BaseTool
from multiagent_debugger.utils import get_verbose_flag, create_crewai_llm, get_agent_llm_config

class CodeAgent:
    """Agent that analyzes code to find relevant information about API failures."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the CodeAgent.
        
        Args:
            config: Configuration dictionary with model settings
        """
        self.config = config
        
        # Handle both dict and DebuggerConfig objects
        if hasattr(config, 'llm'):
            self.llm_config = config.llm
        else:
            self.llm_config = config.get("llm", {})
        
        # Get code path from config
        if hasattr(config, 'code_path'):
            self.code_path = config.code_path
        else:
            self.code_path = config.get("code_path", "")
        
    def create_agent(self, tools: List[BaseTool] = None) -> Agent:
        """Create and return the CrewAI agent.
        
        Args:
            tools: List of tools available to the agent
            
        Returns:
            Agent: The configured CrewAI agent
        """
        # Get LLM configuration parameters
        provider, model, temperature, api_key, api_base = get_agent_llm_config(self.llm_config)
        verbose = get_verbose_flag(self.config)
        
        # Create LLM
        llm = create_crewai_llm(provider, model, temperature, api_key, api_base)
        
        try:
            agent = Agent(
                role="Code Analyzer",
                goal="Analyze code to understand API structure and find potential issues",
                backstory="""You are an expert at analyzing code to understand API structure and find potential issues.
                You can search for API handlers, dependencies, and error handling code to help identify
                the root cause of API failures. Work efficiently and focus on the most relevant information.
                
                IMPORTANT: Use tools strategically and avoid repetition:
                1. Start with find_api_handlers to locate the failing API endpoint
                2. If you find the handler, analyze it immediately - don't search again
                3. Only use find_error_handlers if you need specific error handling patterns
                4. Only use find_dependencies if you need to understand what the API depends on
                5. Once you have relevant code information, provide your analysis and stop
                
                Stop searching once you have found the API handler or relevant code information.""",
                verbose=verbose,
                allow_delegation=False,
                tools=tools or [],
                llm=llm,  # Pass the CrewAI LLM object
                max_iter=1,  # Reduced from 3 to 1 for efficiency
                memory=False,  # Disable individual agent memory, use crew-level memory instead
            )
            return agent
        except Exception as e:
            import traceback
            print(f"ERROR: Failed to create CrewAI Agent: {e}")
            print(traceback.format_exc())
            raise
    
    def analyze_code(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze source code to find handlers and functions related to the provided entities.
        
        Args:
            entities: Dictionary of entities extracted from the user's question
            
        Returns:
            Dict containing relevant code analysis
        """
        results = {
            "api_handlers": [],
            "related_functions": [],
            "dependencies": [],
            "error_handlers": [],
            "summary": ""
        }
        
        if not self.code_path or not os.path.exists(self.code_path):
            results["summary"] = "No valid code path provided."
            return results
        
        # Get API route from entities
        api_route = entities.get("api_route")
        if not api_route:
            results["summary"] = "No API route provided for code analysis."
            return results
        
        # Clean API route for searching
        clean_route = api_route.strip('/')
        
        # Find Python files in the codebase
        python_files = self._find_python_files(self.code_path)
        
        # Search for files that might contain the API route handler
        for file_path in python_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    content = f.read()
                    
                    # Check if file contains the API route
                    route_pattern = re.compile(r'[\'"]/?{}[\'"]'.format(re.escape(clean_route)))
                    if route_pattern.search(content):
                        # Parse the file with AST
                        try:
                            tree = ast.parse(content)
                            
                            # Find API handler functions
                            api_handlers = self._find_api_handlers(tree, clean_route, content)
                            if api_handlers:
                                for handler in api_handlers:
                                    handler["file_path"] = str(file_path)
                                    results["api_handlers"].append(handler)
                                    
                                # Find related functions called by the handlers
                                related_funcs = self._find_related_functions(tree, api_handlers, content)
                                for func in related_funcs:
                                    func["file_path"] = str(file_path)
                                    results["related_functions"].append(func)
                                
                                # Find error handlers
                                error_handlers = self._find_error_handlers(tree, content)
                                for handler in error_handlers:
                                    handler["file_path"] = str(file_path)
                                    results["error_handlers"].append(handler)
                                
                                # Extract dependencies
                                dependencies = self._extract_dependencies(tree)
                                for dep in dependencies:
                                    if dep not in results["dependencies"]:
                                        results["dependencies"].append(dep)
                        except SyntaxError:
                            # Skip files with syntax errors
                            pass
                except Exception as e:
                    print(f"Error analyzing file {file_path}: {str(e)}")
        
        # Generate summary
        results["summary"] = f"Found {len(results['api_handlers'])} API handlers, " \
                            f"{len(results['related_functions'])} related functions, " \
                            f"{len(results['error_handlers'])} error handlers, and " \
                            f"{len(results['dependencies'])} dependencies."
        
        return results
    
    def _find_python_files(self, path: str) -> List[Path]:
        """Find all Python files in the given path."""
        path_obj = Path(path)
        if path_obj.is_file() and path_obj.suffix == '.py':
            return [path_obj]
        
        python_files = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _find_api_handlers(self, tree: ast.AST, route: str, content: str) -> List[Dict[str, Any]]:
        """Find API handler functions in the AST."""
        handlers = []
        
        # This is a simplified implementation that looks for common patterns
        # in web frameworks like Flask, FastAPI, Django, etc.
        for node in ast.walk(tree):
            # Look for route decorators
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, 'attr') and decorator.func.attr in ['route', 'get', 'post', 'put', 'delete']:
                            # Check if route matches
                            for arg in decorator.args:
                                if isinstance(arg, ast.Str) and route in arg.s:
                                    # Extract function source
                                    start_line = node.lineno
                                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                                    source_lines = content.splitlines()[start_line-1:end_line]
                                    source = '\n'.join(source_lines)
                                    
                                    handlers.append({
                                        "name": node.name,
                                        "type": "function",
                                        "source": source,
                                        "line_number": start_line
                                    })
            
            # Look for route registrations (e.g., app.add_url_rule)
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'attr') and node.func.attr in ['add_url_rule', 'register']:
                    for arg in node.args:
                        if isinstance(arg, ast.Str) and route in arg.s:
                            handlers.append({
                                "name": "route_registration",
                                "type": "registration",
                                "source": ast.unparse(node) if hasattr(ast, 'unparse') else str(node),
                                "line_number": node.lineno
                            })
        
        return handlers
    
    def _find_related_functions(self, tree: ast.AST, handlers: List[Dict[str, Any]], content: str) -> List[Dict[str, Any]]:
        """Find functions called by the API handlers."""
        related_funcs = []
        called_funcs = set()
        
        # Extract function names from handlers
        for handler in handlers:
            if handler["type"] == "function":
                # Parse the handler source to find function calls
                try:
                    handler_tree = ast.parse(handler["source"])
                    for node in ast.walk(handler_tree):
                        if isinstance(node, ast.Call) and hasattr(node.func, 'id'):
                            called_funcs.add(node.func.id)
                except SyntaxError:
                    # Skip handlers with syntax errors
                    pass
        
        # Find the definitions of called functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in called_funcs:
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                source_lines = content.splitlines()[start_line-1:end_line]
                source = '\n'.join(source_lines)
                
                related_funcs.append({
                    "name": node.name,
                    "type": "function",
                    "source": source,
                    "line_number": start_line
                })
        
        return related_funcs
    
    def _find_error_handlers(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Find error handling code in the AST."""
        error_handlers = []
        
        # Look for try-except blocks
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                source_lines = content.splitlines()[start_line-1:end_line]
                source = '\n'.join(source_lines)
                
                error_handlers.append({
                    "name": "try_except",
                    "type": "error_handler",
                    "source": source,
                    "line_number": start_line
                })
        
        return error_handlers
    
    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract dependencies from import statements."""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    dependencies.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module)
        
        return dependencies 