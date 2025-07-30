"""
Custom exceptions for cliops with specific error handling
"""

class CliOpsError(Exception):
    """Base exception for all cliops errors"""
    pass

class ConfigurationError(CliOpsError):
    """Configuration-related errors"""
    pass

class PatternError(CliOpsError):
    """Pattern-related errors"""
    pass

class PluginError(CliOpsError):
    """Plugin-related errors"""
    pass

class OptimizationError(CliOpsError):
    """Optimization process errors"""
    pass

class ValidationError(CliOpsError):
    """Input validation errors"""
    pass

class StateError(CliOpsError):
    """CLI state management errors"""
    pass

class PerformanceError(CliOpsError):
    """Performance and memory errors"""
    pass