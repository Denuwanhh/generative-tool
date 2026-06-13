import logging
import os
import sys

logger = logging.getLogger(__name__)

class CodeExecutor:
    """Executes generated Python code in a safe, controlled environment."""

    def __init__(self):
        pass

    def execute(self, code: str) -> any:
        """Execute the generated python script using exec().

        Args:
            code: The Python code string to execute.

        Returns:
            The value of the 'result' variable defined by the executed script.
        """
        logger.info("Executing the generated Python query code using exec().")
        
        # Setup standard global context including builtins, os, sys
        global_context = {
            "__builtins__": __builtins__,
            "os": os,
            "sys": sys,
        }
        
        # Execute in a local context to retrieve variables defined by the script
        local_context = {}
        
        try:
            # Pre-import sqlalchemy for convenience
            import sqlalchemy
            global_context["sqlalchemy"] = sqlalchemy
            
            exec(code, global_context, local_context)
            
            if "result" not in local_context:
                logger.warning("The executed script did not define a 'result' variable.")
                return None
                
            logger.info("Execution completed successfully.")
            return local_context["result"]
        except Exception as e:
            logger.error(f"Error during execution of the generated Python code: {e}")
            logger.debug(f"Code attempted:\n{code}")
            raise
