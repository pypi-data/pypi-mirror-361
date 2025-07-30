"""
HexaEight Agent Manager - Creates agents using dotnet scripts
"""

import os
import subprocess
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from hexaeight_agent import get_create_scripts_path, HexaEightAgent
except ImportError:
    raise ImportError("hexaeight-agent is required. Install with: pip install hexaeight-agent")

from .exceptions import AgentCreationError, DotnetScriptError

logger = logging.getLogger(__name__)

@dataclass
class AgentCreationResult:
    """Result of agent creation operation"""
    success: bool
    config_file: str
    agent_name: Optional[str] = None
    error: Optional[str] = None
    dotnet_output: Optional[str] = None

class HexaEightAgentManager:
    """
    Manages HexaEight agent creation using dotnet scripts
    Integrates with existing .csx scripts from hexaeight-agent package
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.scripts_path = get_create_scripts_path()
        
        # Verify dotnet is available
        self._check_dotnet_availability()
        
        # Verify scripts exist
        self._verify_scripts()
    
    def _check_dotnet_availability(self) -> bool:
        """Check if dotnet is available and working"""
        try:
            result = subprocess.run(
                ["dotnet", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                if self.debug:
                    logger.info(f"✅ .NET available: {result.stdout.strip()}")
                return True
            else:
                raise DotnetScriptError(f"dotnet command failed: {result.stderr}")
                
        except FileNotFoundError:
            raise DotnetScriptError(
                "dotnet command not found. Please install .NET SDK: "
                "https://dotnet.microsoft.com/download"
            )
        except subprocess.TimeoutExpired:
            raise DotnetScriptError("dotnet command timed out")
        except Exception as e:
            raise DotnetScriptError(f"Error checking dotnet: {e}")
    
    def _verify_scripts(self):
        """Verify that required .csx scripts exist"""
        parent_script = os.path.join(self.scripts_path, "create-identity-for-parent-agent.csx")
        child_script = os.path.join(self.scripts_path, "create-identity-for-child-agent.csx")
        
        if not os.path.exists(parent_script):
            raise AgentCreationError(f"Parent agent script not found: {parent_script}")
            
        if not os.path.exists(child_script):
            raise AgentCreationError(f"Child agent script not found: {child_script}")
        
        if self.debug:
            logger.info(f"✅ Scripts verified at: {self.scripts_path}")
    
    def _run_dotnet_script(self, script_name: str, args: List[str]) -> Tuple[bool, str, str]:
        """
        Run a dotnet script with given arguments
        Returns: (success, stdout, stderr)
        """
        script_path = os.path.join(self.scripts_path, script_name)
        command = ["dotnet", "script", script_path] + args + ["--no-cache"]
        
        try:
            if self.debug:
                logger.info(f"Running: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )
            
            success = result.returncode == 0
            
            if self.debug:
                logger.info(f"Script completed with return code: {result.returncode}")
                if result.stdout:
                    logger.info(f"STDOUT: {result.stdout}")
                if result.stderr:
                    logger.info(f"STDERR: {result.stderr}")
            
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            error_msg = f"Script {script_name} timed out after 60 seconds"
            logger.error(error_msg)
            return False, "", error_msg
            
        except Exception as e:
            error_msg = f"Error running script {script_name}: {e}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def create_parent_agent(self, config_filename: str) -> AgentCreationResult:
        """
        Create a parent agent using dotnet script
        
        Args:
            config_filename: Name of config file to create (e.g., "parent_config.json")
            
        Returns:
            AgentCreationResult with success status and details
        """
        try:
            # Run: dotnet script create-identity-for-parent-agent.csx config.json --no-cache
            success, stdout, stderr = self._run_dotnet_script(
                "create-identity-for-parent-agent.csx",
                [config_filename]
            )
            
            if success:
                # Try to determine agent name from config file or output
                agent_name = self._extract_agent_name_from_output(stdout) or "parent_agent"
                
                return AgentCreationResult(
                    success=True,
                    config_file=config_filename,
                    agent_name=agent_name,
                    dotnet_output=stdout
                )
            else:
                return AgentCreationResult(
                    success=False,
                    config_file=config_filename,
                    error=f"Script failed: {stderr}",
                    dotnet_output=stdout
                )
                
        except Exception as e:
            return AgentCreationResult(
                success=False,
                config_file=config_filename,
                error=str(e)
            )
    
    def create_child_agent(self, child_name: str, parent_config: str, child_config: str) -> AgentCreationResult:
        """
        Create a child agent using dotnet script
        
        Args:
            child_name: Name/password for the child agent
            parent_config: Parent agent config file
            child_config: Child agent config file to create
            
        Returns:
            AgentCreationResult with success status and details
        """
        try:
            # Run: dotnet script create-identity-for-child-agent.csx child_name parent_config.json child_config.json --no-cache
            success, stdout, stderr = self._run_dotnet_script(
                "create-identity-for-child-agent.csx",
                [child_name, parent_config, child_config]
            )
            
            if success:
                return AgentCreationResult(
                    success=True,
                    config_file=child_config,
                    agent_name=child_name,
                    dotnet_output=stdout
                )
            else:
                return AgentCreationResult(
                    success=False,
                    config_file=child_config,
                    error=f"Script failed: {stderr}",
                    dotnet_output=stdout
                )
                
        except Exception as e:
            return AgentCreationResult(
                success=False,
                config_file=child_config,
                error=str(e)
            )
    
    def _extract_agent_name_from_output(self, output: str) -> Optional[str]:
        """Extract agent name from dotnet script output if possible"""
        # This is a best-effort attempt to extract agent name
        # You might need to adjust based on actual script output format
        lines = output.split('\n')
        for line in lines:
            if 'agent' in line.lower() and 'name' in line.lower():
                # Try to extract name from line
                parts = line.split(':')
                if len(parts) > 1:
                    return parts[1].strip()
        return None
    
    async def create_parent_agent_async(self, config_filename: str) -> AgentCreationResult:
        """Async version of create_parent_agent"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.create_parent_agent, config_filename)
    
    async def create_child_agent_async(self, child_name: str, parent_config: str, child_config: str) -> AgentCreationResult:
        """Async version of create_child_agent"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.create_child_agent, child_name, parent_config, child_config)
    
    def list_existing_configs(self, directory: str = ".") -> List[str]:
        """List existing agent config files in directory"""
        config_files = []
        for file in os.listdir(directory):
            if file.endswith('.json') and ('agent' in file.lower() or 'config' in file.lower()):
                config_files.append(file)
        return sorted(config_files)
    
    def validate_config_file(self, config_file: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a config file exists and appears to be a valid agent config
        Returns: (is_valid, error_message)
        """
        if not os.path.exists(config_file):
            return False, f"Config file does not exist: {config_file}"
        
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Basic validation - check for expected fields
            required_fields = ['AppLoginToken', 'ResourceIdentity']
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                return False, f"Missing required fields: {missing_fields}"
            
            return True, None
            
        except json.JSONDecodeError:
            return False, "Invalid JSON format"
        except Exception as e:
            return False, f"Error reading config file: {e}"
