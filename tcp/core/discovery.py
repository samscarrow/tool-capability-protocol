"""Tool discovery service for finding capabilities."""

from typing import Dict, List, Optional, Any, Callable
import logging
from dataclasses import dataclass

from .descriptors import CapabilityDescriptor, ProcessingMode, FormatType
from .registry import CapabilityRegistry

logger = logging.getLogger(__name__)


@dataclass
class DiscoveryFilter:
    """Filter criteria for tool discovery."""
    name_pattern: Optional[str] = None
    version_pattern: Optional[str] = None
    formats: Optional[List[str]] = None
    commands: Optional[List[str]] = None
    processing_modes: Optional[List[ProcessingMode]] = None
    capability_flags: Optional[int] = None
    performance_criteria: Optional[Dict[str, Any]] = None
    custom_filter: Optional[Callable[[CapabilityDescriptor], bool]] = None


class DiscoveryService:
    """Service for discovering tools based on capabilities."""
    
    def __init__(self, registry: CapabilityRegistry):
        """Initialize discovery service."""
        self.registry = registry
        self._discovery_plugins: Dict[str, Callable] = {}
    
    def discover(
        self,
        formats: Optional[List[str]] = None,
        commands: Optional[List[str]] = None,
        processing_modes: Optional[List[str]] = None,
        performance_criteria: Optional[Dict[str, Any]] = None,
        capability_flags: Optional[List[str]] = None,
        **kwargs
    ) -> List[CapabilityDescriptor]:
        """Discover tools matching criteria."""
        
        # Convert string processing modes to enum values
        mode_enums = []
        if processing_modes:
            for mode_str in processing_modes:
                try:
                    mode_enums.append(ProcessingMode[mode_str.upper()])
                except KeyError:
                    logger.warning(f"Unknown processing mode: {mode_str}")
        
        # Convert capability flags to integer
        flags_int = 0
        if capability_flags:
            try:
                from .descriptors import CapabilityFlags
                for flag_str in capability_flags:
                    flag = getattr(CapabilityFlags, flag_str.upper())
                    flags_int |= flag
            except AttributeError as e:
                logger.warning(f"Unknown capability flag: {e}")
        
        # Create filter
        filter_criteria = DiscoveryFilter(
            name_pattern=kwargs.get('name_pattern'),
            version_pattern=kwargs.get('version_pattern'),
            formats=formats,
            commands=commands,
            processing_modes=mode_enums,
            capability_flags=flags_int if flags_int else None,
            performance_criteria=performance_criteria,
            custom_filter=kwargs.get('custom_filter')
        )
        
        return self._apply_filters(filter_criteria)
    
    def find_best_tool(
        self,
        task_requirements: Dict[str, Any],
        optimization_target: str = "speed"
    ) -> Optional[CapabilityDescriptor]:
        """Find the best tool for a specific task."""
        
        # Extract requirements
        formats = task_requirements.get('formats', [])
        commands = task_requirements.get('commands', [])
        file_size_mb = task_requirements.get('file_size_mb', 0)
        concurrent_requests = task_requirements.get('concurrent_requests', 1)
        
        # Find candidate tools
        candidates = self.discover(
            formats=formats,
            commands=commands
        )
        
        # Filter by performance requirements
        suitable_candidates = []
        for candidate in candidates:
            perf = candidate.performance
            
            # Check file size limit
            if file_size_mb > 0 and perf.max_file_size_mb < file_size_mb:
                continue
            
            # Check concurrency support
            if concurrent_requests > 1 and perf.concurrent_requests < concurrent_requests:
                continue
            
            suitable_candidates.append(candidate)
        
        if not suitable_candidates:
            return None
        
        # Select best tool based on optimization target
        return self._select_optimal(suitable_candidates, optimization_target)
    
    def discover_by_example(
        self,
        input_example: str,
        output_example: Optional[str] = None,
        detect_format: bool = True
    ) -> List[CapabilityDescriptor]:
        """Discover tools by analyzing input/output examples."""
        
        criteria = {}
        
        # Detect input format
        if detect_format:
            input_format = self._detect_format(input_example)
            if input_format:
                criteria['formats'] = [input_format]
        
        # Detect output format
        if output_example and detect_format:
            output_format = self._detect_format(output_example)
            # For now, we don't filter by output format in the simple case
        
        return self.discover(**criteria)
    
    def discover_similar_tools(
        self,
        reference_tool: CapabilityDescriptor,
        similarity_threshold: float = 0.7
    ) -> List[CapabilityDescriptor]:
        """Find tools similar to a reference tool."""
        
        all_tools = self.registry.list_all()
        similar_tools = []
        
        for tool in all_tools:
            if tool.name == reference_tool.name:
                continue  # Skip the reference tool itself
            
            similarity = self._calculate_similarity(reference_tool, tool)
            if similarity >= similarity_threshold:
                similar_tools.append((tool, similarity))
        
        # Sort by similarity (highest first)
        similar_tools.sort(key=lambda x: x[1], reverse=True)
        
        return [tool for tool, _ in similar_tools]
    
    def get_capability_matrix(self) -> Dict[str, Dict[str, List[str]]]:
        """Get a matrix of all capabilities across tools."""
        
        matrix = {
            'formats': {},
            'commands': {},
            'processing_modes': {},
            'performance_tiers': {}
        }
        
        all_tools = self.registry.list_all()
        
        for tool in all_tools:
            tool_name = f"{tool.name}:{tool.version}"
            
            # Input formats
            for fmt in tool.input_formats:
                if fmt.name not in matrix['formats']:
                    matrix['formats'][fmt.name] = []
                matrix['formats'][fmt.name].append(tool_name)
            
            # Commands
            for cmd in tool.commands:
                if cmd.name not in matrix['commands']:
                    matrix['commands'][cmd.name] = []
                matrix['commands'][cmd.name].append(tool_name)
            
            # Processing modes
            for mode in tool.processing_modes:
                mode_name = mode.name
                if mode_name not in matrix['processing_modes']:
                    matrix['processing_modes'][mode_name] = []
                matrix['processing_modes'][mode_name].append(tool_name)
            
            # Performance tiers
            perf_tier = self._get_performance_tier(tool.performance)
            if perf_tier not in matrix['performance_tiers']:
                matrix['performance_tiers'][perf_tier] = []
            matrix['performance_tiers'][perf_tier].append(tool_name)
        
        return matrix
    
    def register_discovery_plugin(self, name: str, plugin: Callable) -> None:
        """Register a custom discovery plugin."""
        self._discovery_plugins[name] = plugin
        logger.info(f"Registered discovery plugin: {name}")
    
    def _apply_filters(self, filter_criteria: DiscoveryFilter) -> List[CapabilityDescriptor]:
        """Apply discovery filters to find matching tools."""
        
        all_tools = self.registry.list_all()
        results = []
        
        for tool in all_tools:
            if self._matches_filter(tool, filter_criteria):
                results.append(tool)
        
        return results
    
    def _matches_filter(self, tool: CapabilityDescriptor, filter_criteria: DiscoveryFilter) -> bool:
        """Check if a tool matches the filter criteria."""
        
        # Name pattern
        if filter_criteria.name_pattern:
            import fnmatch
            if not fnmatch.fnmatch(tool.name, filter_criteria.name_pattern):
                return False
        
        # Version pattern
        if filter_criteria.version_pattern:
            import fnmatch
            if not fnmatch.fnmatch(tool.version, filter_criteria.version_pattern):
                return False
        
        # Formats
        if filter_criteria.formats:
            supported_formats = set()
            for fmt in tool.input_formats:
                supported_formats.add(fmt.name.lower())
                supported_formats.update(ext.lower() for ext in fmt.extensions)
            
            for required_format in filter_criteria.formats:
                if required_format.lower() not in supported_formats:
                    return False
        
        # Commands
        if filter_criteria.commands:
            tool_commands = {cmd.name.lower() for cmd in tool.commands}
            for required_command in filter_criteria.commands:
                if required_command.lower() not in tool_commands:
                    return False
        
        # Processing modes
        if filter_criteria.processing_modes:
            for required_mode in filter_criteria.processing_modes:
                if required_mode not in tool.processing_modes:
                    return False
        
        # Capability flags
        if filter_criteria.capability_flags:
            tool_flags = tool.get_capability_flags()
            if not (tool_flags & filter_criteria.capability_flags):
                return False
        
        # Performance criteria
        if filter_criteria.performance_criteria:
            if not self._meets_performance_criteria(tool, filter_criteria.performance_criteria):
                return False
        
        # Custom filter
        if filter_criteria.custom_filter:
            if not filter_criteria.custom_filter(tool):
                return False
        
        return True
    
    def _meets_performance_criteria(self, tool: CapabilityDescriptor, criteria: Dict[str, Any]) -> bool:
        """Check if tool meets performance criteria."""
        
        perf = tool.performance
        
        # Max file size
        if 'max_file_size_mb' in criteria:
            if perf.max_file_size_mb < criteria['max_file_size_mb']:
                return False
        
        # Processing time
        if 'max_processing_time_ms' in criteria:
            if perf.avg_processing_time_ms > criteria['max_processing_time_ms']:
                return False
        
        # Memory usage
        if 'max_memory_mb' in criteria:
            if perf.memory_usage_mb > criteria['max_memory_mb']:
                return False
        
        # Concurrency
        if 'min_concurrent_requests' in criteria:
            if perf.concurrent_requests < criteria['min_concurrent_requests']:
                return False
        
        # GPU requirement
        if 'gpu_required' in criteria:
            if criteria['gpu_required'] and not perf.gpu_required:
                return False
            if not criteria['gpu_required'] and perf.gpu_required:
                return False
        
        return True
    
    def _select_optimal(self, tools: List[CapabilityDescriptor], target: str) -> CapabilityDescriptor:
        """Select optimal tool based on target criteria."""
        
        if not tools:
            return None
        
        if target == "speed":
            return min(tools, key=lambda t: t.performance.avg_processing_time_ms)
        elif target == "memory":
            return min(tools, key=lambda t: t.performance.memory_usage_mb)
        elif target == "throughput":
            return max(tools, key=lambda t: t.performance.concurrent_requests)
        elif target == "capacity":
            return max(tools, key=lambda t: t.performance.max_file_size_mb)
        else:
            return tools[0]  # Default to first
    
    def _detect_format(self, content: str) -> Optional[str]:
        """Detect format from content sample."""
        
        content_lower = content.lower().strip()
        
        # JSON detection
        if content_lower.startswith(('{', '[')):
            return 'json'
        
        # XML detection
        if content_lower.startswith('<?xml') or content_lower.startswith('<'):
            return 'xml'
        
        # Base64 detection
        if len(content) % 4 == 0 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in content):
            return 'base64'
        
        # CSV detection
        if ',' in content and '\n' in content:
            lines = content.split('\n')
            if len(lines) > 1 and all(',' in line for line in lines[:3]):
                return 'csv'
        
        # Default to text
        return 'text'
    
    def _calculate_similarity(self, tool1: CapabilityDescriptor, tool2: CapabilityDescriptor) -> float:
        """Calculate similarity score between two tools."""
        
        score = 0.0
        total_weight = 0.0
        
        # Command similarity (weight: 0.4)
        commands1 = {cmd.name for cmd in tool1.commands}
        commands2 = {cmd.name for cmd in tool2.commands}
        if commands1 or commands2:
            command_similarity = len(commands1 & commands2) / len(commands1 | commands2)
            score += command_similarity * 0.4
        total_weight += 0.4
        
        # Format similarity (weight: 0.3)
        formats1 = {fmt.name for fmt in tool1.input_formats}
        formats2 = {fmt.name for fmt in tool2.input_formats}
        if formats1 or formats2:
            format_similarity = len(formats1 & formats2) / len(formats1 | formats2)
            score += format_similarity * 0.3
        total_weight += 0.3
        
        # Processing mode similarity (weight: 0.2)
        modes1 = set(tool1.processing_modes)
        modes2 = set(tool2.processing_modes)
        if modes1 or modes2:
            mode_similarity = len(modes1 & modes2) / len(modes1 | modes2)
            score += mode_similarity * 0.2
        total_weight += 0.2
        
        # Performance similarity (weight: 0.1)
        perf1, perf2 = tool1.performance, tool2.performance
        perf_score = 0.0
        perf_count = 0
        
        # Compare processing time (normalized)
        if perf1.avg_processing_time_ms > 0 and perf2.avg_processing_time_ms > 0:
            time_ratio = min(perf1.avg_processing_time_ms, perf2.avg_processing_time_ms) / max(perf1.avg_processing_time_ms, perf2.avg_processing_time_ms)
            perf_score += time_ratio
            perf_count += 1
        
        # Compare memory usage
        if perf1.memory_usage_mb > 0 and perf2.memory_usage_mb > 0:
            memory_ratio = min(perf1.memory_usage_mb, perf2.memory_usage_mb) / max(perf1.memory_usage_mb, perf2.memory_usage_mb)
            perf_score += memory_ratio
            perf_count += 1
        
        if perf_count > 0:
            score += (perf_score / perf_count) * 0.1
        total_weight += 0.1
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _get_performance_tier(self, performance) -> str:
        """Categorize performance into tiers."""
        
        # Simple tier classification based on processing time
        if performance.avg_processing_time_ms < 100:
            return "ultra_fast"
        elif performance.avg_processing_time_ms < 1000:
            return "fast"
        elif performance.avg_processing_time_ms < 5000:
            return "medium"
        elif performance.avg_processing_time_ms < 30000:
            return "slow"
        else:
            return "very_slow"