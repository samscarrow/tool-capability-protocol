"""GraphQL schema generator for TCP descriptors."""

from typing import Any, Dict, List

from ..core.descriptors import CapabilityDescriptor, ParameterType


class GraphQLGenerator:
    """Generate GraphQL schemas from TCP descriptors."""

    def generate(self, descriptor: CapabilityDescriptor) -> str:
        """Generate GraphQL schema from capability descriptor."""
        schema_parts = []

        # Add scalar types
        schema_parts.append(self._generate_scalars())

        # Add main types
        schema_parts.append(self._generate_capability_type(descriptor))
        schema_parts.append(self._generate_command_types(descriptor))
        schema_parts.append(self._generate_parameter_types(descriptor))

        # Add query type
        schema_parts.append(self._generate_query_type(descriptor))

        # Add mutation type if commands exist
        if descriptor.commands:
            schema_parts.append(self._generate_mutation_type(descriptor))

        return "\n\n".join(filter(None, schema_parts))

    def _generate_scalars(self) -> str:
        """Generate scalar type definitions."""
        return """# Custom scalar types
scalar DateTime
scalar JSON"""

    def _generate_capability_type(self, descriptor: CapabilityDescriptor) -> str:
        """Generate main capability type."""
        return f"""# Tool capability information
type ToolCapability {{
  name: String!
  version: String
  description: String
  vendor: String
  homepage: String
  license: String
  createdAt: DateTime
  inputFormats: [String!]!
  outputFormats: [String!]!
  processingModes: [String!]!
  commands: [Command!]!
  performanceMetrics: PerformanceMetrics
  capabilities: JSON
  metadata: JSON
}}"""

    def _generate_command_types(self, descriptor: CapabilityDescriptor) -> str:
        """Generate command-related types."""
        return """# Command information
type Command {
  name: String!
  description: String
  parameters: [Parameter!]!
  metadata: JSON
}"""

    def _generate_parameter_types(self, descriptor: CapabilityDescriptor) -> str:
        """Generate parameter-related types."""
        return """# Parameter information
type Parameter {
  name: String!
  type: ParameterType!
  description: String
  required: Boolean!
  defaultValue: String
  enumValues: [String!]
  minValue: Float
  maxValue: Float
  pattern: String
  metadata: JSON
}

enum ParameterType {
  BOOLEAN
  STRING
  INTEGER
  FLOAT
  ENUM
  PATH
  URL
  ARRAY
}

# Performance metrics
type PerformanceMetrics {
  avgResponseTimeMs: Int
  throughputOpsPerSec: Int
  memoryUsageMb: Int
  cpuUsagePercent: Int
  diskIoMbPerSec: Int
  networkIoMbPerSec: Int
  startupTimeMs: Int
  concurrentOpsLimit: Int
}"""

    def _generate_query_type(self, descriptor: CapabilityDescriptor) -> str:
        """Generate Query type."""
        return f"""# Query operations
type Query {{
  # Get tool capabilities
  capabilities: ToolCapability
  
  # Get specific command information
  command(name: String!): Command
  
  # Search commands by capability
  commandsByCapability(capability: String!): [Command!]!
  
  # Check if tool supports a specific format
  supportsFormat(format: String!): Boolean!
  
  # Get performance metrics
  performanceMetrics: PerformanceMetrics
}}"""

    def _generate_mutation_type(self, descriptor: CapabilityDescriptor) -> str:
        """Generate Mutation type for command execution."""
        mutations = []

        for command in descriptor.commands:
            # Create input type for command
            input_fields = []
            for param in command.parameters:
                param_type = self._graphql_type_for_parameter(param.type)
                required = "!" if param.required else ""
                input_fields.append(f"  {param.name}: {param_type}{required}")

            if input_fields:
                input_type = f"""input {command.name.title()}Input {{
{chr(10).join(input_fields)}
}}"""
                mutations.append(input_type)

            # Create mutation field
            input_param = f"input: {command.name.title()}Input!" if input_fields else ""
            mutation_field = f"  {command.name}({input_param}): ExecutionResult!"
            mutations.append(mutation_field)

        if mutations:
            return f"""# Execution result
type ExecutionResult {{
  success: Boolean!
  exitCode: Int
  stdout: String
  stderr: String
  executionTimeMs: Int
  error: String
}}

# Command execution mutations
type Mutation {{
{chr(10).join(field for field in mutations if field.startswith("  "))}
}}

{chr(10).join(field for field in mutations if not field.startswith("  "))}"""

        return ""

    def _graphql_type_for_parameter(self, param_type: ParameterType) -> str:
        """Convert TCP parameter type to GraphQL type."""
        type_map = {
            ParameterType.BOOLEAN: "Boolean",
            ParameterType.STRING: "String",
            ParameterType.INTEGER: "Int",
            ParameterType.FLOAT: "Float",
            ParameterType.ENUM: "String",
            ParameterType.PATH: "String",
            ParameterType.URL: "String",
            ParameterType.ARRAY: "[String!]",
        }
        return type_map.get(param_type, "String")
