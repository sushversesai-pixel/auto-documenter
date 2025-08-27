"""
Code Element Data Models

Defines data structures for representing different types of code elements
such as functions, classes, modules, and parameters.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from abc import ABC, abstractmethod


@dataclass
class CodeElement(ABC):
    """Base class for all code elements."""
    name: str
    line_number: int
    file_path: Optional[str] = None
    docstring: Optional[str] = None
    
    @property
    @abstractmethod
    def type(self) -> str:
        """Return the type of code element."""
        pass


@dataclass
class CodeParameter:
    """Represents a function or method parameter."""
    name: str
    param_type: Optional[str] = None
    default_value: Optional[str] = None
    is_required: bool = True
    description: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the parameter."""
        parts = [self.name]
        
        if self.param_type:
            parts.append(f": {self.param_type}")
        
        if self.default_value is not None:
            parts.append(f" = {self.default_value}")
        
        return "".join(parts)


@dataclass
class CodeFunction(CodeElement):
    """Represents a function or method."""
    parameters: List[CodeParameter] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_private: bool = False
    is_async: bool = False
    is_static: bool = False
    is_class_method: bool = False
    exceptions: List[str] = field(default_factory=list)
    
    @property
    def type(self) -> str:
        """Return the type of code element."""
        return "function"
    
    @property
    def signature(self) -> str:
        """Generate function signature string."""
        params_str = ", ".join(str(param) for param in self.parameters)
        
        async_prefix = "async " if self.is_async else ""
        return_annotation = f" -> {self.return_type}" if self.return_type else ""
        
        return f"{async_prefix}def {self.name}({params_str}){return_annotation}"
    
    @property
    def required_parameters(self) -> List[CodeParameter]:
        """Get list of required parameters."""
        return [p for p in self.parameters if p.is_required]
    
    @property
    def optional_parameters(self) -> List[CodeParameter]:
        """Get list of optional parameters."""
        return [p for p in self.parameters if not p.is_required]


@dataclass
class CodeClass(CodeElement):
    """Represents a class definition."""
    base_classes: List[str] = field(default_factory=list)
    methods: List[CodeFunction] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    is_private: bool = False
    is_abstract: bool = False
    decorators: List[str] = field(default_factory=list)
    
    @property
    def type(self) -> str:
        """Return the type of code element."""
        return "class"
    
    @property
    def public_methods(self) -> List[CodeFunction]:
        """Get list of public methods."""
        return [m for m in self.methods if not m.is_private]
    
    @property
    def private_methods(self) -> List[CodeFunction]:
        """Get list of private methods."""
        return [m for m in self.methods if m.is_private]
    
    @property
    def constructor(self) -> Optional[CodeFunction]:
        """Get the constructor method if it exists."""
        constructors = [m for m in self.methods if m.name in ['__init__', 'constructor']]
        return constructors[0] if constructors else None
    
    @property
    def inheritance_chain(self) -> str:
        """Get inheritance chain as string."""
        if self.base_classes:
            return f"{self.name}({', '.join(self.base_classes)})"
        return self.name


@dataclass
class CodeModule(CodeElement):
    """Represents a module or file."""
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    functions: List[CodeFunction] = field(default_factory=list)
    classes: List[CodeClass] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)
    
    @property
    def type(self) -> str:
        """Return the type of code element."""
        return "module"
    
    @property
    def public_api(self) -> List[str]:
        """Get list of public API elements."""
        api = []
        
        # Add public functions
        api.extend([f.name for f in self.functions if not f.is_private])
        
        # Add public classes
        api.extend([c.name for c in self.classes if not c.is_private])
        
        # Add exports
        api.extend(self.exports)
        
        return api
    
    @property
    def dependencies(self) -> List[str]:
        """Get list of external dependencies."""
        # Filter out standard library imports (this is a simplified approach)
        external_deps = []
        standard_libs = {
            'os', 'sys', 'json', 're', 'datetime', 'collections', 'itertools',
            'functools', 'math', 'random', 'urllib', 'http', 'pathlib'
        }
        
        for imp in self.imports:
            base_module = imp.split('.')[0]
            if base_module not in standard_libs and not base_module.startswith('src'):
                external_deps.append(imp)
        
        return external_deps


@dataclass
class CodeVariable:
    """Represents a variable or constant."""
    name: str
    var_type: Optional[str] = None
    value: Optional[str] = None
    is_constant: bool = False
    is_private: bool = False
    line_number: Optional[int] = None
    
    @property
    def type(self) -> str:
        """Return the type of code element."""
        return "variable"


@dataclass
class DocumentationContext:
    """Context information for documentation generation."""
    file_path: str
    language: str
    style: str
    elements: List[CodeElement]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_elements_by_type(self, element_type: str) -> List[CodeElement]:
        """Get elements filtered by type."""
        return [e for e in self.elements if e.type == element_type]
    
    def get_public_elements(self) -> List[CodeElement]:
        """Get only public elements."""
        public_elements = []
        
        for element in self.elements:
            if hasattr(element, 'is_private') and not element.is_private:
                public_elements.append(element)
            elif not hasattr(element, 'is_private'):
                public_elements.append(element)
        
        return public_elements
