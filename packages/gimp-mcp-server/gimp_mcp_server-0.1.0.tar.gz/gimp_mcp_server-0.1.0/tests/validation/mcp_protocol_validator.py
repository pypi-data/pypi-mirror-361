"""
MCP Protocol Compliance Validator.

This module provides comprehensive validation for MCP protocol compliance,
ensuring the GIMP MCP server adheres to the Model Context Protocol specification.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..mocks.mock_mcp_client import MockMCPClient


class ValidationResult(Enum):
    """Validation result types."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"


@dataclass
class ValidationCheck:
    """Individual validation check."""
    name: str
    description: str
    category: str
    result: ValidationResult = ValidationResult.SKIP
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    server_info: Dict[str, Any]
    checks: List[ValidationCheck] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    total_duration: float = 0.0
    timestamp: str = ""
    
    def get_pass_rate(self) -> float:
        """Calculate pass rate."""
        total = len(self.checks)
        if total == 0:
            return 0.0
        passed = len([c for c in self.checks if c.result == ValidationResult.PASS])
        return passed / total
    
    def get_summary_stats(self) -> Dict[str, int]:
        """Get summary statistics."""
        stats = {result.value: 0 for result in ValidationResult}
        for check in self.checks:
            stats[check.result.value] += 1
        return stats


class MCPProtocolValidator:
    """MCP Protocol compliance validator."""
    
    def __init__(self, server_url: str = "localhost:3001"):
        self.server_url = server_url
        self.client = MockMCPClient()
        self.logger = logging.getLogger(__name__)
        self.checks: List[ValidationCheck] = []
        
    async def validate_full_compliance(self) -> ValidationReport:
        """Run full MCP protocol compliance validation."""
        start_time = asyncio.get_event_loop().time()
        
        self.logger.info("Starting MCP protocol compliance validation")
        
        try:
            # Connect to server
            await self._validate_connection()
            
            # Run all validation categories
            await self._validate_server_info()
            await self._validate_tool_discovery()
            await self._validate_resource_discovery()
            await self._validate_tool_invocation()
            await self._validate_resource_access()
            await self._validate_error_handling()
            await self._validate_message_format()
            await self._validate_parameter_validation()
            await self._validate_concurrency()
            
        except Exception as e:
            self.logger.error(f"Validation failed with exception: {e}")
            self._add_check(
                "global_error",
                "Global validation error",
                "system",
                ValidationResult.FAIL,
                f"Validation failed: {e}"
            )
        finally:
            await self._cleanup()
            
        end_time = asyncio.get_event_loop().time()
        total_duration = end_time - start_time
        
        # Generate report
        report = self._generate_report(total_duration)
        
        self.logger.info(f"Validation completed in {total_duration:.2f}s")
        self.logger.info(f"Pass rate: {report.get_pass_rate():.1%}")
        
        return report
        
    async def _validate_connection(self):
        """Validate basic MCP connection."""
        check = ValidationCheck(
            "connection_basic",
            "Basic MCP connection establishment",
            "connection"
        )
        
        try:
            start_time = asyncio.get_event_loop().time()
            connected = await self.client.connect(self.server_url)
            end_time = asyncio.get_event_loop().time()
            
            check.duration = end_time - start_time
            
            if connected and self.client.connected:
                check.result = ValidationResult.PASS
                check.message = "Successfully connected to MCP server"
                check.details = {
                    "server_url": self.server_url,
                    "connection_time": check.duration,
                    "server_info": self.client.server_info
                }
            else:
                check.result = ValidationResult.FAIL
                check.message = "Failed to connect to MCP server"
                
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Connection error: {e}"
            
        self.checks.append(check)
        
    async def _validate_server_info(self):
        """Validate server information compliance."""
        check = ValidationCheck(
            "server_info_compliance",
            "Server information MCP compliance",
            "protocol"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            server_info = self.client.server_info
            
            # Validate required fields
            required_fields = ["name", "version", "capabilities"]
            missing_fields = [field for field in required_fields if field not in server_info]
            
            if missing_fields:
                check.result = ValidationResult.FAIL
                check.message = f"Missing required server info fields: {missing_fields}"
            else:
                check.result = ValidationResult.PASS
                check.message = "Server info is MCP compliant"
                
            check.details = {
                "server_info": server_info,
                "required_fields": required_fields,
                "missing_fields": missing_fields
            }
            
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Server info validation error: {e}"
            
        self.checks.append(check)
        
    async def _validate_tool_discovery(self):
        """Validate tool discovery compliance."""
        check = ValidationCheck(
            "tool_discovery_compliance",
            "Tool discovery MCP compliance",
            "tools"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            start_time = asyncio.get_event_loop().time()
            tools = await self.client.list_tools()
            end_time = asyncio.get_event_loop().time()
            
            check.duration = end_time - start_time
            
            # Validate tool structure
            valid_tools = []
            invalid_tools = []
            
            for tool in tools:
                if self._validate_tool_definition(tool):
                    valid_tools.append(tool)
                else:
                    invalid_tools.append(tool)
                    
            if invalid_tools:
                check.result = ValidationResult.FAIL
                check.message = f"Invalid tool definitions found: {len(invalid_tools)}"
            elif not tools:
                check.result = ValidationResult.WARNING
                check.message = "No tools discovered"
            else:
                check.result = ValidationResult.PASS
                check.message = f"All {len(tools)} tools are MCP compliant"
                
            check.details = {
                "total_tools": len(tools),
                "valid_tools": len(valid_tools),
                "invalid_tools": len(invalid_tools),
                "discovery_time": check.duration,
                "tools": tools[:5]  # First 5 tools for details
            }
            
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Tool discovery error: {e}"
            
        self.checks.append(check)
        
    async def _validate_resource_discovery(self):
        """Validate resource discovery compliance."""
        check = ValidationCheck(
            "resource_discovery_compliance",
            "Resource discovery MCP compliance",
            "resources"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            start_time = asyncio.get_event_loop().time()
            resources = await self.client.list_resources()
            end_time = asyncio.get_event_loop().time()
            
            check.duration = end_time - start_time
            
            # Validate resource structure
            valid_resources = []
            invalid_resources = []
            
            for resource in resources:
                if self._validate_resource_definition(resource):
                    valid_resources.append(resource)
                else:
                    invalid_resources.append(resource)
                    
            if invalid_resources:
                check.result = ValidationResult.FAIL
                check.message = f"Invalid resource definitions found: {len(invalid_resources)}"
            elif not resources:
                check.result = ValidationResult.WARNING
                check.message = "No resources discovered"
            else:
                check.result = ValidationResult.PASS
                check.message = f"All {len(resources)} resources are MCP compliant"
                
            check.details = {
                "total_resources": len(resources),
                "valid_resources": len(valid_resources),
                "invalid_resources": len(invalid_resources),
                "discovery_time": check.duration,
                "resources": resources[:5]  # First 5 resources for details
            }
            
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Resource discovery error: {e}"
            
        self.checks.append(check)
        
    async def _validate_tool_invocation(self):
        """Validate tool invocation compliance."""
        # Test basic tool invocation
        await self._validate_basic_tool_invocation()
        
        # Test tool with parameters
        await self._validate_parameterized_tool_invocation()
        
        # Test tool error handling
        await self._validate_tool_error_handling()
        
    async def _validate_basic_tool_invocation(self):
        """Validate basic tool invocation."""
        check = ValidationCheck(
            "tool_invocation_basic",
            "Basic tool invocation compliance",
            "tools"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            # Try to invoke list_documents tool (should be available)
            start_time = asyncio.get_event_loop().time()
            result = await self.client.call_tool("list_documents", {})
            end_time = asyncio.get_event_loop().time()
            
            check.duration = end_time - start_time
            
            # Validate response structure
            if not isinstance(result, dict):
                check.result = ValidationResult.FAIL
                check.message = "Tool response is not a dictionary"
            elif "success" not in result:
                check.result = ValidationResult.FAIL
                check.message = "Tool response missing 'success' field"
            else:
                check.result = ValidationResult.PASS
                check.message = "Basic tool invocation successful"
                
            check.details = {
                "tool_name": "list_documents",
                "invocation_time": check.duration,
                "response_structure": self._analyze_response_structure(result)
            }
            
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Tool invocation error: {e}"
            
        self.checks.append(check)
        
    async def _validate_parameterized_tool_invocation(self):
        """Validate parameterized tool invocation."""
        check = ValidationCheck(
            "tool_invocation_parameters",
            "Parameterized tool invocation compliance",
            "tools"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            # Try to invoke get_document_info with parameters
            start_time = asyncio.get_event_loop().time()
            result = await self.client.call_tool("get_document_info", {
                "document_id": 1
            })
            end_time = asyncio.get_event_loop().time()
            
            check.duration = end_time - start_time
            
            # Validate response
            if isinstance(result, dict) and "success" in result:
                check.result = ValidationResult.PASS
                check.message = "Parameterized tool invocation successful"
            else:
                check.result = ValidationResult.FAIL
                check.message = "Invalid parameterized tool response"
                
            check.details = {
                "tool_name": "get_document_info",
                "parameters": {"document_id": 1},
                "invocation_time": check.duration,
                "response_valid": isinstance(result, dict) and "success" in result
            }
            
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Parameterized tool invocation error: {e}"
            
        self.checks.append(check)
        
    async def _validate_tool_error_handling(self):
        """Validate tool error handling compliance."""
        check = ValidationCheck(
            "tool_error_handling",
            "Tool error handling compliance",
            "error_handling"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            # Try to invoke tool with invalid parameters
            start_time = asyncio.get_event_loop().time()
            result = await self.client.call_tool("get_document_info", {
                "document_id": -1  # Invalid ID
            })
            end_time = asyncio.get_event_loop().time()
            
            check.duration = end_time - start_time
            
            # Validate error response
            if isinstance(result, dict) and result.get("success") is False and "error" in result:
                check.result = ValidationResult.PASS
                check.message = "Tool error handling is compliant"
            else:
                check.result = ValidationResult.FAIL
                check.message = "Tool error handling is not compliant"
                
            check.details = {
                "tool_name": "get_document_info",
                "invalid_parameters": {"document_id": -1},
                "response_time": check.duration,
                "error_handled": result.get("success") is False and "error" in result
            }
            
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Tool error handling validation error: {e}"
            
        self.checks.append(check)
        
    async def _validate_resource_access(self):
        """Validate resource access compliance."""
        check = ValidationCheck(
            "resource_access_compliance",
            "Resource access MCP compliance",
            "resources"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            # Try to access system status resource
            start_time = asyncio.get_event_loop().time()
            result = await self.client.get_resource("system://status")
            end_time = asyncio.get_event_loop().time()
            
            check.duration = end_time - start_time
            
            # Validate response
            if isinstance(result, dict) and "success" in result:
                check.result = ValidationResult.PASS
                check.message = "Resource access successful"
            else:
                check.result = ValidationResult.FAIL
                check.message = "Invalid resource access response"
                
            check.details = {
                "resource_uri": "system://status",
                "access_time": check.duration,
                "response_valid": isinstance(result, dict) and "success" in result
            }
            
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Resource access error: {e}"
            
        self.checks.append(check)
        
    async def _validate_error_handling(self):
        """Validate general error handling compliance."""
        await self._validate_invalid_tool_error()
        await self._validate_invalid_resource_error()
        
    async def _validate_invalid_tool_error(self):
        """Validate invalid tool error handling."""
        check = ValidationCheck(
            "invalid_tool_error",
            "Invalid tool error handling",
            "error_handling"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            # Try to call non-existent tool
            try:
                await self.client.call_tool("non_existent_tool", {})
                check.result = ValidationResult.FAIL
                check.message = "Invalid tool call should have raised an error"
            except Exception as e:
                check.result = ValidationResult.PASS
                check.message = "Invalid tool error handled correctly"
                check.details = {"error": str(e)}
                
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Invalid tool error validation failed: {e}"
            
        self.checks.append(check)
        
    async def _validate_invalid_resource_error(self):
        """Validate invalid resource error handling."""
        check = ValidationCheck(
            "invalid_resource_error",
            "Invalid resource error handling",
            "error_handling"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            # Try to access non-existent resource
            try:
                await self.client.get_resource("invalid://resource")
                check.result = ValidationResult.FAIL
                check.message = "Invalid resource access should have raised an error"
            except Exception as e:
                check.result = ValidationResult.PASS
                check.message = "Invalid resource error handled correctly"
                check.details = {"error": str(e)}
                
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Invalid resource error validation failed: {e}"
            
        self.checks.append(check)
        
    async def _validate_message_format(self):
        """Validate MCP message format compliance."""
        check = ValidationCheck(
            "message_format_compliance",
            "MCP message format compliance",
            "protocol"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            # Clear message history and make some calls
            self.client.clear_message_history()
            
            await self.client.call_tool("list_documents", {})
            await self.client.get_resource("system://status")
            
            # Validate message formats
            messages = self.client.get_message_history()
            valid_messages = 0
            invalid_messages = 0
            
            for message in messages:
                if self._validate_message_format(message.to_dict()):
                    valid_messages += 1
                else:
                    invalid_messages += 1
                    
            if invalid_messages > 0:
                check.result = ValidationResult.FAIL
                check.message = f"Invalid message formats found: {invalid_messages}"
            else:
                check.result = ValidationResult.PASS
                check.message = f"All {len(messages)} messages are format compliant"
                
            check.details = {
                "total_messages": len(messages),
                "valid_messages": valid_messages,
                "invalid_messages": invalid_messages
            }
            
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Message format validation error: {e}"
            
        self.checks.append(check)
        
    async def _validate_parameter_validation(self):
        """Validate parameter validation compliance."""
        check = ValidationCheck(
            "parameter_validation",
            "Tool parameter validation compliance",
            "validation"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            # Test various parameter validation scenarios
            validation_tests = [
                ("get_document_info", {"document_id": "invalid"}, "type_validation"),
                ("get_document_info", {}, "required_parameter"),
                ("create_document", {"width": -1, "height": 600}, "range_validation"),
            ]
            
            passed_tests = 0
            failed_tests = 0
            
            for tool_name, params, test_type in validation_tests:
                try:
                    result = await self.client.call_tool(tool_name, params)
                    if result.get("success") is False and "error" in result:
                        passed_tests += 1
                    else:
                        failed_tests += 1
                except Exception:
                    passed_tests += 1  # Exception is acceptable for invalid params
                    
            if failed_tests > 0:
                check.result = ValidationResult.FAIL
                check.message = f"Parameter validation failed: {failed_tests} tests"
            else:
                check.result = ValidationResult.PASS
                check.message = f"Parameter validation passed: {passed_tests} tests"
                
            check.details = {
                "total_tests": len(validation_tests),
                "passed_tests": passed_tests,
                "failed_tests": failed_tests
            }
            
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Parameter validation error: {e}"
            
        self.checks.append(check)
        
    async def _validate_concurrency(self):
        """Validate concurrent operation compliance."""
        check = ValidationCheck(
            "concurrency_compliance",
            "Concurrent operation compliance",
            "performance"
        )
        
        try:
            if not self.client.connected:
                check.result = ValidationResult.SKIP
                check.message = "Client not connected"
                self.checks.append(check)
                return
                
            # Test concurrent tool calls
            start_time = asyncio.get_event_loop().time()
            
            tasks = [
                self.client.call_tool("list_documents", {}),
                self.client.get_resource("system://status"),
                self.client.call_tool("get_document_info", {"document_id": 1}),
                self.client.get_resource("system://health")
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = asyncio.get_event_loop().time()
            
            check.duration = end_time - start_time
            
            # Analyze results
            successful_results = 0
            failed_results = 0
            
            for result in results:
                if isinstance(result, Exception):
                    failed_results += 1
                elif isinstance(result, dict) and "success" in result:
                    successful_results += 1
                else:
                    failed_results += 1
                    
            if failed_results > len(results) / 2:  # More than half failed
                check.result = ValidationResult.FAIL
                check.message = f"Concurrency handling failed: {failed_results} failures"
            else:
                check.result = ValidationResult.PASS
                check.message = f"Concurrency handled well: {successful_results} successes"
                
            check.details = {
                "concurrent_operations": len(tasks),
                "successful_results": successful_results,
                "failed_results": failed_results,
                "total_time": check.duration
            }
            
        except Exception as e:
            check.result = ValidationResult.FAIL
            check.message = f"Concurrency validation error: {e}"
            
        self.checks.append(check)
        
    def _validate_tool_definition(self, tool: Dict[str, Any]) -> bool:
        """Validate individual tool definition."""
        required_fields = ["name", "description", "parameters"]
        return all(field in tool for field in required_fields)
        
    def _validate_resource_definition(self, resource: Dict[str, Any]) -> bool:
        """Validate individual resource definition."""
        required_fields = ["uri", "name", "description"]
        return all(field in resource for field in required_fields)
        
    def _validate_message_format(self, message: Dict[str, Any]) -> bool:
        """Validate MCP message format."""
        required_fields = ["type", "id"]
        return all(field in message for field in required_fields)
        
    def _analyze_response_structure(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze response structure."""
        return {
            "is_dict": isinstance(response, dict),
            "has_success": "success" in response,
            "has_error": "error" in response,
            "field_count": len(response) if isinstance(response, dict) else 0,
            "fields": list(response.keys()) if isinstance(response, dict) else []
        }
        
    def _add_check(self, name: str, description: str, category: str, 
                   result: ValidationResult, message: str, details: Optional[Dict[str, Any]] = None):
        """Add a validation check."""
        check = ValidationCheck(
            name=name,
            description=description,
            category=category,
            result=result,
            message=message,
            details=details or {}
        )
        self.checks.append(check)
        
    def _generate_report(self, total_duration: float) -> ValidationReport:
        """Generate comprehensive validation report."""
        from datetime import datetime
        
        # Get server info
        server_info = self.client.server_info if self.client.connected else {}
        
        # Generate summary
        summary = self._get_summary_stats()
        
        report = ValidationReport(
            server_info=server_info,
            checks=self.checks,
            summary=summary,
            total_duration=total_duration,
            timestamp=datetime.now().isoformat()
        )
        
        return report
        
    def _get_summary_stats(self) -> Dict[str, int]:
        """Get summary statistics."""
        stats = {result.value: 0 for result in ValidationResult}
        for check in self.checks:
            stats[check.result.value] += 1
        return stats
        
    async def _cleanup(self):
        """Cleanup validation resources."""
        try:
            if self.client.connected:
                await self.client.disconnect()
        except Exception as e:
            self.logger.warning(f"Cleanup error: {e}")


def format_validation_report(report: ValidationReport) -> str:
    """Format validation report as human-readable text."""
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append("MCP PROTOCOL COMPLIANCE VALIDATION REPORT")
    lines.append("=" * 80)
    lines.append(f"Timestamp: {report.timestamp}")
    lines.append(f"Duration: {report.total_duration:.2f}s")
    lines.append(f"Pass Rate: {report.get_pass_rate():.1%}")
    lines.append("")
    
    # Server Info
    lines.append("SERVER INFORMATION:")
    lines.append("-" * 40)
    for key, value in report.server_info.items():
        lines.append(f"  {key}: {value}")
    lines.append("")
    
    # Summary
    lines.append("VALIDATION SUMMARY:")
    lines.append("-" * 40)
    summary = report.get_summary_stats()
    for result_type, count in summary.items():
        lines.append(f"  {result_type}: {count}")
    lines.append("")
    
    # Group checks by category
    categories = {}
    for check in report.checks:
        if check.category not in categories:
            categories[check.category] = []
        categories[check.category].append(check)
    
    # Detailed results by category
    for category, checks in categories.items():
        lines.append(f"{category.upper()} VALIDATION:")
        lines.append("-" * 40)
        
        for check in checks:
            status_symbol = {
                ValidationResult.PASS: "✓",
                ValidationResult.FAIL: "✗",
                ValidationResult.WARNING: "⚠",
                ValidationResult.SKIP: "⏭"
            }.get(check.result, "?")
            
            lines.append(f"  {status_symbol} {check.name}: {check.result.value}")
            lines.append(f"    {check.message}")
            if check.duration > 0:
                lines.append(f"    Duration: {check.duration:.3f}s")
            lines.append("")
    
    return "\n".join(lines)


async def run_mcp_validation(server_url: str = "localhost:3001") -> ValidationReport:
    """Run MCP protocol validation and return report."""
    validator = MCPProtocolValidator(server_url)
    return await validator.validate_full_compliance()


if __name__ == "__main__":
    import sys
    
    async def main():
        server_url = sys.argv[1] if len(sys.argv) > 1 else "localhost:3001"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        
        # Run validation
        report = await run_mcp_validation(server_url)
        
        # Print report
        print(format_validation_report(report))
        
        # Exit with appropriate code
        if report.get_pass_rate() >= 0.8:  # 80% pass rate
            sys.exit(0)
        else:
            sys.exit(1)
    
    asyncio.run(main())