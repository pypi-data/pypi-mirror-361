"""
Core classes and functions for testLLM Framework
"""

import yaml
import json
import time
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import requests


@dataclass
class SemanticTestResult:
    """Result of a semantic test evaluation"""
    test_id: str
    description: str
    passed: bool
    user_input: str
    agent_response: str
    test_criteria: List[str]
    evaluation_results: List[Dict[str, Any]] = field(default_factory=list)
    consensus_score: float = 0.0
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0


@dataclass
class TestResult:
    """Legacy result of a test execution"""
    test_id: str
    description: str
    passed: bool
    conversations: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0


@dataclass
class UserTurn:
    """Represents a user message in a conversation"""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentUnderTest(ABC):
    """Abstract base class for agents being tested"""
    
    @abstractmethod
    def send_message(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Send a message to the agent and get its response"""
        pass
    
    @abstractmethod
    def reset_conversation(self) -> None:
        """Reset the agent's conversation state"""
        pass
    


class ApiAgent(AgentUnderTest):
    """Agent implementation that communicates via HTTP API"""
    
    def __init__(self, endpoint: str, headers: Optional[Dict[str, str]] = None, 
                 timeout: int = 30, session_id: Optional[str] = None):
        self.endpoint = endpoint
        self.headers = headers or {}
        self.timeout = timeout
        self.session_id = session_id or f"test_session_{int(time.time())}"
        self.conversation_history: List[Dict[str, str]] = []
        self._tool_calls: List[Dict[str, Any]] = []
    
    def send_message(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Send message to API endpoint"""
        payload = {
            "message": content,
            "session_id": self.session_id,
            "context": context or {}
        }
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            agent_response = result.get("response", "")
            
            # Track tool calls if present
            if "tool_calls" in result:
                self._tool_calls.extend(result["tool_calls"])
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": content})
            self.conversation_history.append({"role": "agent", "content": agent_response})
            
            return agent_response
            
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to communicate with agent API: {e}")
    
    def reset_conversation(self) -> None:
        """Reset conversation state"""
        self.conversation_history.clear()
        self._tool_calls.clear()
        self.session_id = f"test_session_{int(time.time())}"
    
    def get_tool_calls(self) -> List[Dict[str, Any]]:
        """Get tool calls made during conversation"""
        return self._tool_calls.copy()


class LocalAgent(AgentUnderTest):
    """Agent implementation for local/in-process models"""
    
    def __init__(self, model: Any, tools: Optional[List[Any]] = None):
        self.model = model
        self.tools = tools or []
        self.conversation_history: List[Dict[str, str]] = []
        self._tool_calls: List[Dict[str, Any]] = []
    
    def send_message(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Send message to local model"""
        # This is a generic implementation - specific model frameworks
        # would override this method
        try:
            if hasattr(self.model, 'generate_response'):
                response = self.model.generate_response(
                    content, 
                    history=self.conversation_history,
                    tools=self.tools,
                    context=context
                )
            elif hasattr(self.model, 'predict'):
                response = self.model.predict(content)
            elif callable(self.model):
                response = self.model(content)
            else:
                raise RuntimeError(f"Unsupported model type: {type(self.model)}")
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": content})
            self.conversation_history.append({"role": "agent", "content": response})
            
            return response
            
        except Exception as e:
            raise RuntimeError(f"Failed to get response from local model: {e}")
    
    def reset_conversation(self) -> None:
        """Reset conversation state"""
        self.conversation_history.clear()
        self._tool_calls.clear()
    
    def get_tool_calls(self) -> List[Dict[str, Any]]:
        """Get tool calls made during conversation"""
        return self._tool_calls.copy()


class SemanticTest:
    """Semantic test definition with LLM evaluation"""
    
    def __init__(self, test_id: str, description: str = "", evaluator_models: Optional[List[str]] = None):
        self.test_id = test_id
        self.description = description
        self.evaluator_models = evaluator_models or ["gpt-4o-mini"]
        self.test_cases: List[Dict[str, Any]] = []
    
    def add_test_case(self, user_input: str, *criteria: str) -> None:
        """Add a test case with semantic evaluation criteria
        
        Args:
            user_input: The input message to send to the agent
            *criteria: Semantic criteria for evaluation (e.g., "Response should be helpful and accurate")
        """
        self.test_cases.append({
            "user_input": user_input,
            "criteria": list(criteria)
        })
    
    async def execute(self, agent: AgentUnderTest) -> List[SemanticTestResult]:
        """Execute semantic test against an agent using LLM evaluation"""
        from .evaluation_loop import EvaluationLoop, EvaluationLoopConfig, SemanticCriterion
        
        config = EvaluationLoopConfig(
            evaluator_models=self.evaluator_models,
            consensus_threshold=0.67,
            parallel_execution=True
        )
        evaluator = EvaluationLoop(config)
        
        results = []
        agent.reset_conversation()
        
        for test_case in self.test_cases:
            start_time = time.time()
            
            try:
                # Get agent response
                user_input = test_case["user_input"]
                agent_response = agent.send_message(user_input)
                
                # Convert criteria to SemanticCriterion objects
                semantic_criteria = [
                    SemanticCriterion(criterion=criterion) 
                    for criterion in test_case["criteria"]
                ]
                
                # Evaluate with LLM
                consensus_results = await evaluator.evaluate_response(
                    user_input, agent_response, semantic_criteria
                )
                
                # Calculate overall pass/fail
                passed = all(result.passed for result in consensus_results)
                overall_score = sum(result.consensus_score for result in consensus_results) / len(consensus_results)
                
                # Create result
                result = SemanticTestResult(
                    test_id=f"{self.test_id}_{len(results)}",
                    description=self.description,
                    passed=passed,
                    user_input=user_input,
                    agent_response=agent_response,
                    test_criteria=test_case["criteria"],
                    evaluation_results=[{
                        "criterion": r.criterion,
                        "consensus_score": r.consensus_score,
                        "passed": r.passed,
                        "individual_results": [{
                            "evaluator": eval_result.evaluator_model,
                            "decision": eval_result.decision,
                            "confidence": eval_result.confidence,
                            "reasoning": eval_result.reasoning
                        } for eval_result in r.individual_results]
                    } for r in consensus_results],
                    consensus_score=overall_score,
                    execution_time=time.time() - start_time
                )
                
                results.append(result)
                
            except Exception as e:
                error_result = SemanticTestResult(
                    test_id=f"{self.test_id}_{len(results)}",
                    description=self.description,
                    passed=False,
                    user_input=test_case.get("user_input", ""),
                    agent_response="",
                    test_criteria=test_case.get("criteria", []),
                    errors=[f"Execution error: {e}"],
                    execution_time=time.time() - start_time
                )
                results.append(error_result)
        
        return results


class ConversationTest:
    """Legacy programmatic test definition and execution"""
    
    def __init__(self, test_id: str, description: str = ""):
        self.test_id = test_id
        self.description = description
        self.turns: List[Dict[str, Any]] = []
    
    def add_turn(self, user_message: Union[str, UserTurn], *assertions) -> None:
        """Add a conversation turn with user message and agent assertions"""
        if isinstance(user_message, str):
            user_message = UserTurn(user_message)
        
        self.turns.append({
            "role": "user",
            "content": user_message.content,
            "metadata": user_message.metadata
        })
        
        if assertions:
            self.turns.append({
                "role": "agent",
                "assertions": list(assertions)
            })
    
    def execute(self, agent: AgentUnderTest) -> TestResult:
        """Execute the test against an agent"""
        start_time = time.time()
        agent.reset_conversation()
        
        result = TestResult(
            test_id=self.test_id,
            description=self.description,
            passed=True
        )
        
        conversation_result = {"turns": []}
        
        try:
            i = 0
            while i < len(self.turns):
                turn = self.turns[i]
                
                if turn["role"] == "user":
                    # Send user message
                    response = agent.send_message(turn["content"])
                    
                    turn_result = {
                        "role": "user",
                        "content": turn["content"]
                    }
                    conversation_result["turns"].append(turn_result)
                    
                    # Check if next turn has assertions
                    if (i + 1 < len(self.turns) and 
                        self.turns[i + 1]["role"] == "agent"):
                        agent_turn = self.turns[i + 1]
                        assertion_results = []
                        
                        for assertion in agent_turn.get("assertions", []):
                            try:
                                assertion_result = assertion.check(response, agent)
                                assertion_results.append(assertion_result)
                                if not assertion_result.passed:
                                    result.passed = False
                            except Exception as e:
                                result.errors.append(f"Assertion error: {e}")
                                result.passed = False
                        
                        agent_turn_result = {
                            "role": "agent",
                            "content": response,
                            "assertions": assertion_results
                        }
                        conversation_result["turns"].append(agent_turn_result)
                        i += 1  # Skip the agent turn since we processed it
                
                i += 1
            
            result.conversations = [conversation_result]
            
        except Exception as e:
            result.errors.append(f"Execution error: {e}")
            result.passed = False
        
        result.execution_time = time.time() - start_time
        return result


class AgentAssertion:
    """Factory class for creating agent assertions"""
    
    @staticmethod
    def contains(pattern: str, case_sensitive: bool = False):
        """Assert that response contains a pattern"""
        from .assertions import ContainsAssertion
        return ContainsAssertion(pattern, case_sensitive)
    
    @staticmethod
    def excludes(pattern: str, case_sensitive: bool = False):
        """Assert that response excludes a pattern"""
        from .assertions import ExcludesAssertion
        return ExcludesAssertion(pattern, case_sensitive)
    
    @staticmethod
    def max_length(max_chars: int):
        """Assert maximum response length"""
        from .assertions import MaxLengthAssertion
        return MaxLengthAssertion(max_chars)
    
    @staticmethod
    def min_length(min_chars: int):
        """Assert minimum response length"""
        from .assertions import MinLengthAssertion
        return MinLengthAssertion(min_chars)
    
    @staticmethod
    def sentiment(expected: str):
        """Assert response sentiment (positive, negative, or neutral)"""
        from .assertions import SentimentAssertion
        return SentimentAssertion(expected)
    
    @staticmethod
    def is_valid_json():
        """Assert response is valid JSON"""
        from .assertions import JsonValidAssertion
        return JsonValidAssertion()
    
    @staticmethod
    def matches_json_schema(schema: Dict[str, Any]):
        """Assert response matches JSON schema"""
        from .assertions import JsonSchemaAssertion
        return JsonSchemaAssertion(schema)
    
    @staticmethod
    def used_tool(tool_name: str):
        """Assert that agent used a specific tool"""
        from .assertions import ToolUsageAssertion
        return ToolUsageAssertion(tool_name)
    
    @staticmethod
    def all_of(*assertions):
        """Assert that all given assertions pass"""
        from .assertions import AllOfAssertion
        return AllOfAssertion(list(assertions))
    
    @staticmethod
    def any_of(*assertions):
        """Assert that at least one of the given assertions passes"""
        from .assertions import AnyOfAssertion
        return AnyOfAssertion(list(assertions))
    
    @staticmethod
    def regex(pattern: str, flags: int = 0):
        """Assert response matches regex pattern"""
        from .assertions import RegexAssertion
        return RegexAssertion(pattern, flags)
    
    @staticmethod
    def token_count_under(max_tokens: int):
        """Assert response has fewer than max_tokens (rough estimate)"""
        from .assertions import TokenCountAssertion
        return TokenCountAssertion(max_tokens)


# Legacy YAML support functions - kept for backwards compatibility
def load_test_file(file_path: str) -> Dict[str, Any]:
    """Load test definitions from a YAML file (legacy)"""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Test file not found: {file_path}")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Invalid YAML in test file {file_path}: {e}")


def run_test_from_yaml(test_def: Dict[str, Any], agent: AgentUnderTest) -> TestResult:
    """Run a test based on YAML definition (legacy)"""
    start_time = time.time()
    agent.reset_conversation()
    
    result = TestResult(
        test_id=test_def.get("test_id", "unknown"),
        description=test_def.get("description", ""),
        passed=True
    )
    
    try:
        from .assertions import create_assertion_from_dict
        
        for convo in test_def.get("conversations", []):
            convo_result = {"name": convo.get("name", ""), "turns": []}
            
            turns = convo.get("turns", [])
            i = 0
            
            while i < len(turns):
                turn = turns[i]
                
                if turn.get("role") == "user":
                    # Send user message
                    response = agent.send_message(turn["content"])
                    
                    user_turn_result = {
                        "role": "user", 
                        "content": turn["content"]
                    }
                    convo_result["turns"].append(user_turn_result)
                    
                    # Check if next turn has assertions
                    if (i + 1 < len(turns) and 
                        turns[i + 1].get("role") == "agent"):
                        agent_turn = turns[i + 1]
                        assertion_results = []
                        
                        for assertion_dict in agent_turn.get("assertions", []):
                            try:
                                assertion = create_assertion_from_dict(assertion_dict)
                                assertion_result = assertion.check(response, agent)
                                assertion_results.append(assertion_result.__dict__)
                                if not assertion_result.passed:
                                    result.passed = False
                            except Exception as e:
                                result.errors.append(f"Assertion error: {e}")
                                result.passed = False
                        
                        agent_turn_result = {
                            "role": "agent",
                            "content": response,
                            "assertions": assertion_results
                        }
                        convo_result["turns"].append(agent_turn_result)
                        i += 1  # Skip agent turn since we processed it
                
                i += 1
            
            result.conversations.append(convo_result)
    
    except Exception as e:
        result.errors.append(f"Test execution error: {e}")
        result.passed = False
    
    result.execution_time = time.time() - start_time
    return result


def agent_test(yaml_file: str):
    """Decorator to create a pytest test from a YAML definition (legacy)"""
    def decorator(test_function):
        def wrapper(*args, **kwargs):
            # Extract agent from fixture
            agent = None
            for arg in args:
                if isinstance(arg, AgentUnderTest):
                    agent = arg
                    break
            
            if agent is None:
                # Try to get agent from kwargs
                agent = kwargs.get('agent')
                if agent is None:
                    raise ValueError("No AgentUnderTest instance found in test arguments")
            
            # Load and run test
            test_def = load_test_file(yaml_file)
            result = run_test_from_yaml(test_def, agent)
            
            # Assert test passed
            if not result.passed:
                error_msg = f"Test {result.test_id} failed"
                if result.errors:
                    error_msg += f": {'; '.join(result.errors)}"
                raise AssertionError(error_msg)
            
            return result
        
        # Preserve original function metadata
        wrapper.__name__ = test_function.__name__
        wrapper.__doc__ = test_function.__doc__
        return wrapper
    
    return decorator