from typing import Dict, Any

class Tool:
    """Base Tool class that all specific tools will inherit from."""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters.
        
        Args:
            params: Dictionary of parameters for the tool
            
        Returns:
            Dictionary containing the results of the tool execution
        """
        raise NotImplementedError("Each tool must implement execute method") 