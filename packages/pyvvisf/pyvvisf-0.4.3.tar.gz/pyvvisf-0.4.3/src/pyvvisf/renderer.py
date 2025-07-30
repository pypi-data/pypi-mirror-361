"""ISF shader renderer using PyOpenGL and pyglfw."""

import glfw
import numpy as np
import ctypes
from OpenGL.GL import *
from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
from typing import Dict, Any, Optional
import logging
import OpenGL.GL as GL

from .parser import ISFParser, ISFMetadata
from .types import ISFValue, ISFColor, ISFPoint2D
from .errors import (
    ISFError, ISFParseError, ShaderCompilationError, 
    RenderingError, ContextError
)

class ShaderValidationError(ShaderCompilationError):
    """Raised when shader validation fails due to empty or invalid content."""
    pass

from PIL import Image

logger = logging.getLogger(__name__)


class ShaderManager:
    """
    Manages OpenGL shader compilation, linking, and uniform management.
    
    This class handles the compilation of vertex and fragment shaders, linking them into a program,
    and managing uniform locations and values for efficient rendering.
    """
    
    expected_input_uniforms: list[str] = []
    def __init__(self):
        self.program = None
        self.vertex_shader = None
        self.fragment_shader = None
        self.uniform_locations = {}
    
    def compile_shader(self, source: str, shader_type: int) -> int:
        """
        Compile a GLSL shader and check for errors.

        Args:
            source (str): The GLSL shader source code.
            shader_type (int): The OpenGL shader type (e.g., GL_VERTEX_SHADER).

        Returns:
            int: The compiled shader object.

        Raises:
            ShaderCompilationError: If compilation fails.
        """
        shader = glCreateShader(shader_type)
        if shader is None or shader == 0:
            raise ShaderCompilationError(
                f"Failed to create shader object (type {self._shader_type_name(shader_type)}).",
                shader_source=source,
                shader_type=self._shader_type_name(shader_type)
            )
        glShaderSource(shader, source)
        glCompileShader(shader)
        
        # Check compilation status
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error_log = glGetShaderInfoLog(shader).decode('utf-8')
            glDeleteShader(shader)
            raise ShaderCompilationError(
                f"Shader compilation failed:\n{error_log}",
                shader_source=source,
                shader_type=self._shader_type_name(shader_type)
            )
        
        # Ensure we always return an int
        return int(shader)
    
    def create_program(self, vertex_source: str, fragment_source: str) -> int:
        """
        Create and link a shader program from vertex and fragment sources.

        Args:
            vertex_source (str): Vertex shader source code.
            fragment_source (str): Fragment shader source code.

        Returns:
            int: The linked shader program object.

        Raises:
            ShaderCompilationError: If linking fails.
        """
        try:
            # Compile shaders
            self.vertex_shader = self.compile_shader(vertex_source, GL_VERTEX_SHADER)
            self.fragment_shader = self.compile_shader(fragment_source, GL_FRAGMENT_SHADER)
            
            # Create and link program
            self.program = glCreateProgram()
            if self.program is None or self.program == 0:
                raise ShaderCompilationError(
                    "Failed to create shader program object.",
                    shader_source=f"Vertex:\n{vertex_source}\n\nFragment:\n{fragment_source}"
                )
            glAttachShader(self.program, self.vertex_shader)
            glAttachShader(self.program, self.fragment_shader)
            glLinkProgram(self.program)
            
            # Check linking status
            if not glGetProgramiv(self.program, GL_LINK_STATUS):
                error_log = glGetProgramInfoLog(self.program).decode('utf-8')
                raise ShaderCompilationError(
                    f"Shader program linking failed:\n{error_log}",
                    shader_source=f"Vertex:\n{vertex_source}\n\nFragment:\n{fragment_source}"
                )
            
            # Bind the program before caching uniform locations
            glUseProgram(self.program)
            # Cache uniform locations
            self._cache_uniform_locations()
            
            return int(self.program)
            
        except Exception as e:
            self.cleanup()
            raise e
    
    def _cache_uniform_locations(self):
        """Cache uniform locations for performance. Also include expected uniforms from fragment shader metadata."""
        self.uniform_locations = {}
        num_uniforms = glGetProgramiv(self.program, GL_ACTIVE_UNIFORMS)
        # Cache all active uniforms
        for i in range(num_uniforms):
            name, size, uniform_type = glGetActiveUniform(self.program, i)
            if hasattr(name, 'decode'):
                name = name.decode('utf-8')
            elif hasattr(name, 'tobytes'):
                name = name.tobytes().decode('utf-8').rstrip('\x00')
            else:
                name = str(name)
            location = glGetUniformLocation(self.program, name)
            self.uniform_locations[name] = location
        # Also try to cache any expected uniforms from ISF inputs and standard uniforms
        # (in case they are optimized out of the active list)
        expected_uniforms = [
            'PASSINDEX', 'RENDERSIZE', 'TIME', 'TIMEDELTA', 'DATE', 'FRAMEINDEX'
        ]
        # Add ISF input uniforms if available from metadata
        if hasattr(self, 'expected_input_uniforms'):
            expected_uniforms += self.expected_input_uniforms
        for name in expected_uniforms:
            if name not in self.uniform_locations:
                location = glGetUniformLocation(self.program, name)
                self.uniform_locations[name] = location
    
    def set_uniform(self, name: str, value: Any):
        """
        Set the value of a uniform variable by name.

        Args:
            name (str): The uniform variable name.
            value (Any): The value to set (type depends on uniform).
        """
        location = self.uniform_locations.get(name, -1)
        if location == -1:
            return
        self._set_uniform_value(location, value)
    
    def _set_uniform_value(self, location: int, value: Any):
        """Set uniform value based on type."""
        if isinstance(value, bool):
            glUniform1i(location, 1 if value else 0)
        elif isinstance(value, int):
            glUniform1i(location, value)
        elif isinstance(value, float):
            glUniform1f(location, value)
        elif isinstance(value, (list, tuple)):
            if len(value) == 2:
                glUniform2f(location, value[0], value[1])
            elif len(value) == 3:
                glUniform3f(location, value[0], value[1], value[2])
            elif len(value) == 4:
                glUniform4f(location, value[0], value[1], value[2], value[3])
        elif isinstance(value, ISFColor):
            glUniform4f(location, value.r, value.g, value.b, value.a)
        elif isinstance(value, ISFPoint2D):
            glUniform2f(location, value.x, value.y)
        else:
            logger.warning(f"Unknown uniform type: {type(value)}")
    
    def use(self):
        """
        Activate this shader program for subsequent OpenGL calls.
        """
        if self.program:
            glUseProgram(self.program)
    
    def cleanup(self):
        """
        Delete all OpenGL resources associated with this shader program.
        """
        if self.program:
            glDeleteProgram(self.program)
            self.program = None
        if self.vertex_shader:
            glDeleteShader(self.vertex_shader)
            self.vertex_shader = None
        if self.fragment_shader:
            glDeleteShader(self.fragment_shader)
            self.fragment_shader = None
        self.uniform_locations.clear()
    
    def _shader_type_name(self, shader_type: int) -> str:
        """Get shader type name for error messages."""
        return {
            GL_VERTEX_SHADER: "vertex",
            GL_FRAGMENT_SHADER: "fragment",
            GL_GEOMETRY_SHADER: "geometry",
            GL_TESS_CONTROL_SHADER: "tessellation control",
            GL_TESS_EVALUATION_SHADER: "tessellation evaluation",
        }.get(shader_type, f"unknown ({shader_type})")


class GLContextManager:
    """
    Manages the creation and lifetime of a GLFW OpenGL context.

    This class handles window/context creation, activation, and cleanup for offscreen rendering.
    """
    
    def __init__(self):
        self.window = None
        self.initialized = False
    
    def initialize(self, width: int = 1, height: int = 1):
        """
        Initialize GLFW and create an OpenGL context.

        Args:
            width (int): Window width (default 1).
            height (int): Window height (default 1).

        Raises:
            ContextError: If context creation fails.
        """
        if self.initialized:
            return
        
        if not glfw.init():
            raise ContextError("Failed to initialize GLFW")
        
        # Configure GLFW
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.VISIBLE, glfw.TRUE)  # Make window visible for debugging
        
        # Create window (required for OpenGL context)
        self.window = glfw.create_window(width, height, "ISF Renderer", None, None)
        if not self.window:
            glfw.terminate()
            raise ContextError("Failed to create GLFW window")
        
        glfw.make_context_current(self.window)
        
        # Initialize OpenGL
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        
        self.initialized = True
        logger.info("GLFW context initialized successfully")
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status is not None and status != GL_FRAMEBUFFER_COMPLETE:
            logger.error("Framebuffer is not complete!")
    
    def cleanup(self):
        """
        Destroy the OpenGL context and release all GLFW resources.
        """
        if self.window:
            glfw.destroy_window(self.window)
            self.window = None
        
        if self.initialized:
            glfw.terminate()
            self.initialized = False
    
    def make_current(self):
        """
        Make this OpenGL context current for the calling thread.
        """
        if self.window:
            glfw.make_context_current(self.window)
    
    def __enter__(self):
        """
        Enter the context manager, returning self.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager, cleaning up resources.
        """
        self.cleanup()


class RenderResult:
    """
    Wrapper for a rendered image result.

    Provides convenient conversion to PIL Image and NumPy array.
    """
    def __init__(self, array):
        """
        Initialize a RenderResult.

        Args:
            array (np.ndarray): The rendered image as a NumPy array.
        """
        self.array = array
    def to_pil_image(self):
        """
        Convert the result to a PIL Image in RGBA mode.

        Returns:
            PIL.Image.Image: The image as a PIL Image.
        """
        return Image.fromarray(self.array).convert('RGBA')
    def __array__(self):
        """
        Return the underlying NumPy array.

        Returns:
            np.ndarray: The image array.
        """
        return self.array

class ISFRenderer:
    """
    Main ISF shader renderer for Python.

    This class manages the OpenGL context, shader compilation, input validation, and rendering workflow for ISF shaders.
    
    Args:
        shader_content (str): The ISF fragment shader content (required).
        vertex_shader_content (str, optional): Optional GLSL vertex shader source. If not provided, uses the ISF default vertex shader.
    """
    
    def __init__(self, shader_content: str = '', vertex_shader_content: str = ''):
        """
        Initialize the ISFRenderer with shader content.

        Args:
            shader_content (str): The ISF fragment shader content.
            vertex_shader_content (str, optional): Optional vertex shader source.

        Raises:
            ShaderValidationError: If the shader content is empty or invalid.
        """
        self.context = GLContextManager()
        self.parser = ISFParser()
        self.shader_manager = None
        self.quad_vbo = None
        self.quad_vao = None
        self.metadata = None
        self._shader_content = shader_content or ''  # Store original shader content
        self._vertex_shader_content = vertex_shader_content or ''  # Store optional vertex shader content
        self._input_values = {}  # Store current input values
        
        # Early validation for empty shader content
        if not self._shader_content or not self._shader_content.strip():
            raise ShaderValidationError(
                "Shader content is empty or only whitespace. Please provide valid ISF shader code.",
                shader_source=self._shader_content,
                shader_type="fragment"
            )
        
        try:
            if self._vertex_shader_content:
                self.metadata = self.load_shader_content(self._shader_content, self._vertex_shader_content)
            else:
                self.metadata = self.load_shader_content(self._shader_content)
        except ISFParseError:
            # Let ISFParseError propagate directly
            raise
        except ShaderCompilationError as e:
            # Reraise with a clear message
            raise ShaderValidationError(
                f"Shader validation failed: {e}",
                shader_source=self._shader_content,
                shader_type="fragment"
            ) from e
        except Exception as e:
            # Catch-all for other unexpected errors
            raise ShaderValidationError(
                f"Shader validation failed: {e}",
                shader_source=self._shader_content,
                shader_type="fragment"
            ) from e

    def set_input(self, name: str, value: Any):
        """
        Set the value of a shader input.

        Args:
            name (str): The input name.
            value (Any): The value to set (primitive or ISF type).

        Raises:
            RenderingError: If the input is not found or invalid.
        """
        if not self.metadata or not self.metadata.inputs:
            raise RenderingError("No shader loaded or shader has no inputs.")
        # Find input definition
        input_def = next((inp for inp in self.metadata.inputs if inp.name == name), None)
        if input_def is None:
            raise RenderingError(f"Input '{name}' not found in shader inputs.")
        try:
            # Validate and coerce value
            coerced_value = self.parser.validate_inputs(self.metadata, {name: value})[name]
        except Exception as e:
            raise RenderingError(f"Failed to set input '{name}': {e}")
        # Only reload if value changes
        if name not in self._input_values or self._input_values[name] != coerced_value:
            self._input_values[name] = coerced_value
            # Reload shader to update uniforms (if needed)
            if self._shader_content:
                if self._vertex_shader_content:
                    self.metadata = self.load_shader_content(self._shader_content, self._vertex_shader_content)
                else:
                    self.metadata = self.load_shader_content(self._shader_content)
        # else: value is the same, do nothing

    def set_inputs(self, inputs: dict):
        """
        Convenience method to set multiple shader inputs at once.

        Args:
            inputs (dict): Dictionary mapping input names to values.

        Raises:
            TypeError: If inputs is not a dictionary.
            RenderingError: If any input is not found or invalid (from set_input).
        """
        if not isinstance(inputs, dict):
            raise TypeError("inputs must be a dictionary of input names to values")
        for name, value in inputs.items():
            self.set_input(name, value)

    def _ensure_version_directive(self, source: str) -> str:
        """Ensure the shader source starts with a #version directive."""
        if "#version" not in source:
            return "#version 330\n" + source
        # Replace '#version 330 core' with '#version 330' for compatibility
        lines = source.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith('#version') and 'core' in line:
                lines[i] = line.replace('core', '').strip()
        return '\n'.join(lines)

    def _patch_legacy_gl_fragcolor(self, source: str) -> str:
        """Patch fragment shader to support legacy gl_FragColor in GLSL 330+ by defining an output variable and macro, and ensure fragColor is written to."""
        lines = source.splitlines()
        # Find #version line
        version_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith('#version'):
                version_idx = i
                break
        # Only patch if gl_FragColor is used
        uses_gl_fragcolor = any('gl_FragColor' in l for l in lines)
        already_has_out = any('out vec4' in l for l in lines)
        already_has_define = any('#define gl_FragColor' in l for l in lines)
        if uses_gl_fragcolor:
            insert_idx = version_idx + 1 if version_idx is not None else 0
            if not already_has_out:
                lines.insert(insert_idx, 'out vec4 fragColor;')
                insert_idx += 1
            if not already_has_define:
                lines.insert(insert_idx, '#define gl_FragColor fragColor')
            # Ensure that at least one assignment to fragColor exists
            # If not, replace all assignments to gl_FragColor with fragColor
            # (This is a safety net for shaders that use gl_FragColor without macro expansion)
            for i, line in enumerate(lines):
                if 'gl_FragColor' in line and not line.strip().startswith('#define'):
                    lines[i] = line.replace('gl_FragColor', 'fragColor')
        return '\n'.join(lines)

    def _inject_uniform_declarations(self, source: str, metadata: ISFMetadata) -> str:
        """Inject uniform declarations for all ISF inputs at the top of the shader."""
        if not metadata or not metadata.inputs:
            return source
        # Map ISF types to GLSL types
        type_map = {
            'bool': 'bool',
            'long': 'int',
            'float': 'float',
            'point2D': 'vec2',
            'color': 'vec4',
            'image': 'sampler2D',
            'audio': 'sampler2D',
            'audioFFT': 'sampler2D',
        }
        uniform_lines = []
        for inp in metadata.inputs:
            glsl_type = type_map.get(inp.type, 'float')
            uniform_lines.append(f'uniform {glsl_type} {inp.name};')
        # Insert after #version and any out variable
        lines = source.splitlines()
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('#version'):
                insert_idx = i + 1
            elif line.strip().startswith('out vec4 fragColor;'):
                insert_idx = i + 1
        for j, uline in enumerate(uniform_lines):
            lines.insert(insert_idx + j, uline)
        return '\n'.join(lines)

    def _inject_standard_uniforms(self, source: str) -> str:
        """Inject standard ISF uniforms and isf_FragNormCoord if not already declared."""
        # According to ISF Spec, the standard uniforms are:
        # PASSINDEX (int), RENDERSIZE (vec2), TIME (float), TIMEDELTA (float), DATE (vec4), FRAMEINDEX (int)
        standard_uniforms = [
            ("int", "PASSINDEX"),
            ("vec2", "RENDERSIZE"),
            ("float", "TIME"),
            ("float", "TIMEDELTA"),
            ("vec4", "DATE"),
            ("int", "FRAMEINDEX"),
        ]
        lines = source.splitlines()
        # Find where to insert (after #version and any out variable)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('#version'):
                insert_idx = i + 1
            elif line.strip().startswith('out vec4 fragColor;'):
                insert_idx = i + 1
        # Only inject if not already present
        for dtype, name in standard_uniforms:
            if not any(f"uniform {dtype} {name}" in l or f"uniform {name}" in l for l in lines):
                lines.insert(insert_idx, f"uniform {dtype} {name};")
                insert_idx += 1
        # Inject isf_FragNormCoord as in/varying if not present
        # Only inject if referenced in the shader
        frag_norm_coord_needed = any('isf_FragNormCoord' in l for l in lines)
        if frag_norm_coord_needed and not any("in vec2 isf_FragNormCoord;" in l for l in lines):
            lines.insert(insert_idx, "in vec2 isf_FragNormCoord;")
            insert_idx += 1
        return '\n'.join(lines)

    def _inject_isf_vertShaderInit(self, source: str) -> str:
        """Inject a definition for isf_vertShaderInit() if referenced but not defined, and declare isf_FragNormCoord, position, and texCoord as needed with explicit locations."""
        needs_inject = 'isf_vertShaderInit' in source and 'void isf_vertShaderInit' not in source
        already_declared_frag_norm = 'out vec2 isf_FragNormCoord;' in source
        already_declared_position = 'layout(location = 0) in vec2 position;' in source
        already_declared_texcoord = 'layout(location = 1) in vec2 texCoord;' in source
        # Remove any old 'in vec2 position;' or 'in vec2 texCoord;' lines
        if needs_inject:
            lines = source.splitlines()
            # Remove old attribute declarations if present
            lines = [l for l in lines if l.strip() not in ('in vec2 position;', 'in vec2 texCoord;')]
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('#version'):
                    insert_idx = i + 1
                    break
            # Inject required declarations if not present
            if not already_declared_frag_norm:
                lines.insert(insert_idx, 'out vec2 isf_FragNormCoord;')
                insert_idx += 1
            if not already_declared_position:
                lines.insert(insert_idx, 'layout(location = 0) in vec2 position;')
                insert_idx += 1
            if not already_declared_texcoord:
                lines.insert(insert_idx, 'layout(location = 1) in vec2 texCoord;')
                insert_idx += 1
            # Inject the function
            inject_code = (
                "void isf_vertShaderInit() {\n"
                "    gl_Position = vec4(position, 0.0, 1.0);\n"
                "    isf_FragNormCoord = vec2(texCoord.x, 1.0 - texCoord.y);\n"
                "}\n"
            )
            lines.insert(insert_idx, inject_code)
            return '\n'.join(lines)
        return source

    def default_vertex_shader(self):
        # Literal ISF default vertex shader
        return (
            "void main() {\n"
            "  isf_vertShaderInit();\n"
            "}\n"
        )

    def _set_standard_uniforms(self, width: int, height: int, time_offset: float = 0.0):
        """Set standard ISF uniforms."""
        # Set all standard uniforms, using default values for those not tracked
        if self.shader_manager is not None:
            self.shader_manager.set_uniform("PASSINDEX", 0)
            self.shader_manager.set_uniform("RENDERSIZE", [width, height])
            self.shader_manager.set_uniform("TIME", time_offset)
            self.shader_manager.set_uniform("TIMEDELTA", 0.0)  # TODO: Calculate delta
            self.shader_manager.set_uniform("DATE", [1970.0, 1.0, 1.0, 0.0])  # Placeholder: UNIX epoch
            self.shader_manager.set_uniform("FRAMEINDEX", 0)   # TODO: Track frame index

    def load_shader(self, shader_path: str, vertex_shader_content: str = '') -> ISFMetadata:
        """
        Load and parse an ISF shader from a file.

        Args:
            shader_path (str): Path to the ISF shader file.
            vertex_shader_content (str, optional): Optional vertex shader source.

        Returns:
            ISFMetadata: Parsed shader metadata.
        """
        glsl_code, metadata = self.parser.parse_file(shader_path)
        # Initialize context if needed
        if not self.context.initialized:
            self.context.initialize()
        # Compile shaders
        if vertex_shader_content:
            vertex_source = vertex_shader_content
        else:
            vertex_source = metadata.vertex_shader or self.default_vertex_shader()
        vertex_source = self._ensure_version_directive(vertex_source)
        vertex_source = self._inject_isf_vertShaderInit(vertex_source)
        vertex_source = self._inject_uniform_declarations(vertex_source, metadata)
        glsl_code = self._ensure_version_directive(glsl_code)
        glsl_code = self._patch_legacy_gl_fragcolor(glsl_code)
        glsl_code = self._inject_uniform_declarations(glsl_code, metadata)
        glsl_code = self._inject_standard_uniforms(glsl_code)
        self.shader_manager = ShaderManager()
        # Provide expected input uniforms for caching
        if hasattr(metadata, 'inputs') and metadata.inputs:
            self.shader_manager.expected_input_uniforms = [inp.name for inp in metadata.inputs]
        self.shader_manager.create_program(vertex_source, glsl_code)
        # Setup rendering quad
        self._setup_quad()
        return metadata

    def load_shader_content(self, content: str, vertex_shader_content: str = '') -> ISFMetadata:
        """
        Load and parse ISF shader content from a string.

        Args:
            content (str): The ISF shader content as a string.
            vertex_shader_content (str, optional): Optional vertex shader source.

        Returns:
            ISFMetadata: Parsed shader metadata.
        """
        # Early validation for empty shader content
        if not content or not content.strip():
            raise ShaderValidationError(
                "Shader content is empty or only whitespace. Please provide valid ISF shader code.",
                shader_source=content,
                shader_type="fragment"
            )
        try:
            glsl_code, metadata = self.parser.parse_content(content)
        except ISFParseError:
            # Let ISFParseError propagate directly
            raise
        except Exception as e:
            raise ShaderValidationError(
                f"Shader parsing failed: {e}",
                shader_source=content,
                shader_type="fragment"
            ) from e
        # Initialize context if needed
        if not self.context.initialized:
            self.context.initialize()
        # Compile shaders
        if vertex_shader_content:
            vertex_source = vertex_shader_content
        else:
            vertex_source = metadata.vertex_shader or self.default_vertex_shader()
        vertex_source = self._ensure_version_directive(vertex_source)
        vertex_source = self._inject_isf_vertShaderInit(vertex_source)
        vertex_source = self._inject_uniform_declarations(vertex_source, metadata)
        glsl_code = self._ensure_version_directive(glsl_code)
        glsl_code = self._patch_legacy_gl_fragcolor(glsl_code)
        glsl_code = self._inject_uniform_declarations(glsl_code, metadata)
        glsl_code = self._inject_standard_uniforms(glsl_code)
        logger.debug("Vertex Shader Source:\n" + vertex_source)
        logger.debug("Fragment Shader Source:\n" + glsl_code)
        self.shader_manager = ShaderManager()
        # Provide expected input uniforms for caching
        if hasattr(metadata, 'inputs') and metadata.inputs:
            self.shader_manager.expected_input_uniforms = [inp.name for inp in metadata.inputs]
        try:
            self.shader_manager.create_program(vertex_source, glsl_code)
        except ShaderCompilationError as e:
            raise ShaderValidationError(
                f"Shader compilation failed: {e}",
                shader_source=glsl_code,
                shader_type="fragment"
            ) from e
        # Setup rendering quad
        self._setup_quad()
        return metadata
    
    def render(self, width: int = 1920, height: int = 1080, inputs: Optional[Dict[str, Any]] = None, metadata: Optional[ISFMetadata] = None, time_offset: float = 0.0) -> 'RenderResult':
        """
        Render the shader to a NumPy array (wrapped in RenderResult).

        Args:
            width (int): Output image width.
            height (int): Output image height.
            inputs (dict, optional): Input values for the shader.
            metadata (ISFMetadata, optional): Shader metadata.
            time_offset (float, optional): Time offset for animation.

        Returns:
            RenderResult: The rendered image result.

        Raises:
            RenderingError: If rendering fails.
        """
        if not self.shader_manager:
            raise RenderingError("No shader loaded. Call load_shader() first.")
        # Use self._input_values if inputs not provided
        if inputs is None:
            inputs = self._input_values
        # Use self.metadata if metadata not provided
        if metadata is None:
            metadata = self.metadata
        
        merged_inputs = dict(inputs) if inputs else {}
        if metadata and metadata.inputs:
            for input_def in metadata.inputs:
                if input_def.name not in merged_inputs and input_def.default is not None:
                    merged_inputs[input_def.name] = input_def.default
        # Validate inputs
        if metadata and merged_inputs:
            validated_inputs = self.parser.validate_inputs(metadata, merged_inputs)
        else:
            validated_inputs = {}
        # --- Offscreen FBO/texture setup ---
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0)
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            glDeleteFramebuffers(1, [fbo])
            glDeleteTextures(1, [tex])
            raise RenderingError("Framebuffer is not complete for offscreen rendering.")
        # Set viewport
        glViewport(0, 0, width, height)
        glDisable(GL_DEPTH_TEST)
        glClear(int(GL_COLOR_BUFFER_BIT) | int(GL_DEPTH_BUFFER_BIT))
        # Use shader program
        self.shader_manager.use()
        # Set uniforms
        self._set_standard_uniforms(width, height, time_offset)
        self._set_input_uniforms(validated_inputs)
        # Draw the quad
        glBindVertexArray(self.quad_vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        glBindVertexArray(0)
        glFlush()
        glFinish()
        # Read pixels from FBO
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
        if isinstance(data, bytes):
            image_array = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 4)
            image_array = np.flipud(image_array)
            # Cleanup FBO/texture
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glDeleteFramebuffers(1, [fbo])
            glDeleteTextures(1, [tex])
            return RenderResult(image_array)
        else:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glDeleteFramebuffers(1, [fbo])
            glDeleteTextures(1, [tex])
            logger.error(f"glReadPixels failed or returned unexpected type: {type(data)} value: {data}")
            raise RenderingError("glReadPixels failed to return pixel data.")
    
    def render_to_window(self, width: int = 800, height: int = 600, inputs: Optional[Dict[str, Any]] = None, metadata: Optional[ISFMetadata] = None, time_offset: float = 0.0, title: str = "ISF Shader Preview"):
        """
        Render the shader in a persistent window, updating in real time until the window is closed or ESC is pressed.

        Args:
            width (int): Window width.
            height (int): Window height.
            inputs (dict, optional): Input values for the shader.
            metadata (ISFMetadata, optional): Shader metadata.
            time_offset (float, optional): Initial time offset.
            title (str): Window title.
        """
        import time as _time
        if not self.context.initialized:
            self.context.initialize(width, height)
        else:
            # Resize window if needed
            if self.context.window:
                glfw.set_window_size(self.context.window, width, height)
        glfw.set_window_title(self.context.window, title)
        if not self.shader_manager:
            raise RenderingError("No shader loaded. Call load_shader() first.")
        if inputs is None:
            inputs = self._input_values
        if metadata is None:
            metadata = self.metadata
        # Merge user inputs with defaults from metadata.inputs (like render())
        merged_inputs = dict(inputs) if inputs else {}
        if metadata and metadata.inputs:
            for input_def in metadata.inputs:
                if input_def.name not in merged_inputs and input_def.default is not None:
                    merged_inputs[input_def.name] = input_def.default
        validated_inputs = self.parser.validate_inputs(metadata, merged_inputs) if metadata and merged_inputs else {}
        start_time = _time.time() - time_offset
        frame_index = 0
        while not glfw.window_should_close(self.context.window):
            glfw.poll_events()
            # Handle ESC key to close
            if glfw.get_key(self.context.window, glfw.KEY_ESCAPE) == glfw.PRESS:
                glfw.set_window_should_close(self.context.window, True)
                break
            # Set viewport and clear
            fb_width, fb_height = glfw.get_framebuffer_size(self.context.window)
            glViewport(0, 0, fb_width, fb_height)
            glDisable(GL_DEPTH_TEST)
            glClear(int(GL_COLOR_BUFFER_BIT) | int(GL_DEPTH_BUFFER_BIT))
            # Use shader program
            self.shader_manager.use()
            # Set uniforms (including time, frame index, etc.)
            now = _time.time()
            elapsed = now - start_time
            self._set_standard_uniforms(width, height, elapsed)
            self.shader_manager.set_uniform("FRAMEINDEX", frame_index)
            self._set_input_uniforms(validated_inputs)
            # Draw quad
            glBindVertexArray(self.quad_vao)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
            glBindVertexArray(0)
            glfw.swap_buffers(self.context.window)
            frame_index += 1
        self.cleanup()
    
    def _setup_quad(self):
        """Setup full-screen quad for rendering."""
        # Quad vertices (position, texcoord)
        # 4 vertices, each with (x, y, u, v)
        vertices = np.array([
            # position    # texcoord
            -1.0, -1.0,   0.0, 0.0,  # bottom-left
             1.0, -1.0,   1.0, 0.0,  # bottom-right
            -1.0,  1.0,   0.0, 1.0,  # top-left
             1.0,  1.0,   1.0, 1.0,  # top-right
        ], dtype=np.float32)
        # Create VAO
        self.quad_vao = glGenVertexArrays(1)
        glBindVertexArray(self.quad_vao)
        # Create VBO
        self.quad_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.quad_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        stride = 4 * vertices.itemsize  # 4 floats per vertex
        # Position attribute (location = 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        # TexCoord attribute (location = 1)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(2 * vertices.itemsize))
        glBindVertexArray(0)
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status is not None and status != GL_FRAMEBUFFER_COMPLETE:
            logger.error("Framebuffer is not complete after VAO/VBO setup!")

    def _set_input_uniforms(self, inputs: Dict[str, ISFValue]):
        """Set input uniform values."""
        if self.shader_manager is not None:
            for name, value in inputs.items():
                self.shader_manager.set_uniform(name, value)
    
    def save_render(self, output_path: str, width: int = 1920, height: int = 1080, inputs: Optional[Dict[str, Any]] = None, metadata: Optional[ISFMetadata] = None):
        """
        Render the shader and save the result to a file.

        Args:
            output_path (str): Path to save the output image.
            width (int): Output image width.
            height (int): Output image height.
            inputs (dict, optional): Input values for the shader.
            metadata (ISFMetadata, optional): Shader metadata.
        """
        from PIL import Image
        
        render_result = self.render(width, height, inputs, metadata)
        image = render_result.to_pil_image()
        image.save(output_path)
    
    def cleanup(self):
        """
        Clean up all OpenGL and rendering resources.
        """
        if self.shader_manager:
            self.shader_manager.cleanup()
            self.shader_manager = None
        
        if self.quad_vao:
            glDeleteVertexArrays(1, [self.quad_vao])
            self.quad_vao = None
        
        if self.quad_vbo:
            glDeleteBuffers(1, [self.quad_vbo])
            self.quad_vbo = None
        
        self.context.cleanup()
    
    def __enter__(self):
        """
        Enter the context manager, returning self.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager, cleaning up resources.
        """
        self.cleanup() 