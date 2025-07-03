"""Protocol Buffer schema generator for TCP descriptors."""

from typing import Dict, Any
from ..core.descriptors import CapabilityDescriptor, ParameterType


class ProtobufGenerator:
    """Generate Protocol Buffer definitions from TCP descriptors."""
    
    def generate(self, descriptor: CapabilityDescriptor) -> str:
        """Generate protobuf schema from capability descriptor."""
        proto_parts = []
        
        # Add syntax and options
        proto_parts.append('syntax = "proto3";')
        proto_parts.append('package tcp.v1;')
        proto_parts.append('')
        
        # Add imports if needed
        proto_parts.append('import "google/protobuf/timestamp.proto";')
        proto_parts.append('import "google/protobuf/struct.proto";')
        proto_parts.append('')
        
        # Add message definitions
        proto_parts.append(self._generate_capability_message())
        proto_parts.append(self._generate_command_message())
        proto_parts.append(self._generate_parameter_message())
        proto_parts.append(self._generate_performance_message())
        
        # Add service definition
        proto_parts.append(self._generate_service(descriptor))
        
        return '\n'.join(proto_parts)
    
    def _generate_capability_message(self) -> str:
        """Generate main capability message."""
        return """// Tool capability descriptor
message ToolCapability {
  string name = 1;
  string version = 2;
  string description = 3;
  string vendor = 4;
  string homepage = 5;
  string license = 6;
  google.protobuf.Timestamp created_at = 7;
  repeated string input_formats = 8;
  repeated string output_formats = 9;
  repeated string processing_modes = 10;
  repeated Command commands = 11;
  PerformanceMetrics performance_metrics = 12;
  google.protobuf.Struct capabilities = 13;
  google.protobuf.Struct metadata = 14;
}"""
    
    def _generate_command_message(self) -> str:
        """Generate command message."""
        return """
// Command descriptor
message Command {
  string name = 1;
  string description = 2;
  repeated Parameter parameters = 3;
  google.protobuf.Struct metadata = 4;
}"""
    
    def _generate_parameter_message(self) -> str:
        """Generate parameter message."""
        return """
// Parameter descriptor
message Parameter {
  enum Type {
    BOOLEAN = 0;
    STRING = 1;
    INTEGER = 2;
    FLOAT = 3;
    ENUM = 4;
    PATH = 5;
    URL = 6;
    ARRAY = 7;
  }
  
  string name = 1;
  Type type = 2;
  string description = 3;
  bool required = 4;
  string default_value = 5;
  repeated string enum_values = 6;
  double min_value = 7;
  double max_value = 8;
  string pattern = 9;
  google.protobuf.Struct metadata = 10;
}"""
    
    def _generate_performance_message(self) -> str:
        """Generate performance metrics message."""
        return """
// Performance metrics
message PerformanceMetrics {
  int32 avg_response_time_ms = 1;
  int32 throughput_ops_per_sec = 2;
  int32 memory_usage_mb = 3;
  int32 cpu_usage_percent = 4;
  int32 disk_io_mb_per_sec = 5;
  int32 network_io_mb_per_sec = 6;
  int32 startup_time_ms = 7;
  int32 concurrent_ops_limit = 8;
}"""
    
    def _generate_service(self, descriptor: CapabilityDescriptor) -> str:
        """Generate gRPC service definition."""
        service_methods = []
        
        # Add basic methods
        service_methods.append("  rpc GetCapabilities(google.protobuf.Empty) returns (ToolCapability);")
        service_methods.append("  rpc GetCommand(GetCommandRequest) returns (Command);")
        
        # Add execution methods for each command
        for command in descriptor.commands:
            method_name = f"Execute{command.name.title()}"
            request_type = f"{command.name.title()}Request"
            service_methods.append(f"  rpc {method_name}({request_type}) returns (ExecutionResponse);")
        
        service_def = f"""
// TCP service definition
service ToolService {{
{chr(10).join(service_methods)}
}}

// Request/Response messages
message GetCommandRequest {{
  string name = 1;
}}

message ExecutionResponse {{
  bool success = 1;
  int32 exit_code = 2;
  string stdout = 3;
  string stderr = 4;
  int32 execution_time_ms = 5;
  string error = 6;
}}"""
        
        # Add request messages for each command
        for command in descriptor.commands:
            request_fields = []
            for i, param in enumerate(command.parameters, 1):
                proto_type = self._proto_type_for_parameter(param.type)
                request_fields.append(f"  {proto_type} {param.name} = {i};")
            
            if request_fields:
                service_def += f"""

message {command.name.title()}Request {{
{chr(10).join(request_fields)}
}}"""
        
        return service_def
    
    def _proto_type_for_parameter(self, param_type: ParameterType) -> str:
        """Convert TCP parameter type to protobuf type."""
        type_map = {
            ParameterType.BOOLEAN: "bool",
            ParameterType.STRING: "string",
            ParameterType.INTEGER: "int32",
            ParameterType.FLOAT: "double",
            ParameterType.ENUM: "string",
            ParameterType.PATH: "string",
            ParameterType.URL: "string",
            ParameterType.ARRAY: "repeated string",
        }
        return type_map.get(param_type, "string")