import re
from typing import Dict, List, Optional, Tuple, Any


class DeclarationParser:
    """
    A parser for PLC declaration files.
    
    This class provides methods to parse declaration files and extract
    information about variables, pragmas, comments, and other elements.
    """
    
    # Regular expression patterns for comments
    DETAILS_PATTERN = r'\(\*details\s+(.*?)\*\)'
    USAGE_PATTERN = r'\(\*usage\s+(.*?)\*\)'
    CUSTOM_COMMENT_PATTERN = r'\(\*(\w+)\s+(.*?)\*\)'
    
    # Function block declaration patterns
    FB_DECLARATION_PATTERN = r'(?:FUNCTION_BLOCK|METHOD|INTERFACE)\s+(\w+)'
    FB_MODIFIERS_PATTERN = r'(?:FUNCTION_BLOCK|METHOD|INTERFACE)\s+\w+\s+((?:ABSTRACT|PRIVATE|INTERNAL|PUBLIC|PROTECTED)(?:\s+(?:ABSTRACT|PRIVATE|INTERNAL|PUBLIC|PROTECTED))*)'
    EXTENDS_PATTERN = r'EXTENDS\s+([\w,\s]+?)(?:\s+IMPLEMENTS\s+|$)'
    IMPLEMENTS_PATTERN = r'IMPLEMENTS\s+([\w,\s]+)'
    
    # VAR block patterns
    VAR_TYPE = r'VAR(?:_INPUT|_OUTPUT|_IN_OUT|_STAT|_INST|_TEMP)?'
    VAR_MODIFIER = r'(?:\s+(?:CONSTANT|PERSISTENT))?'
    VAR_BLOCK_PATTERN = rf'({VAR_TYPE}{VAR_MODIFIER})\s+(.*?)END_VAR'
    
    # Pragma pattern
    PRAGMA_PATTERN = r'\{([^{}]*)\}'
    
    # Type patterns
    ARRAY_TYPE_PATTERN = r'array\s*\[.*?\]\s+of\s+\w+'
    POINTER_TYPE_PATTERN = r'pointer\s+to\s+\w+'
    REFERENCE_TYPE_PATTERN = r'reference\s+to\s+\w+'
    SIMPLE_TYPE_PATTERN = r'\w+(?:\(.*?\))?'
    
    # Combined type pattern
    TYPE_PATTERN = f'(?:{ARRAY_TYPE_PATTERN})|(?:{POINTER_TYPE_PATTERN})|(?:{REFERENCE_TYPE_PATTERN})|(?:{SIMPLE_TYPE_PATTERN})'
    
    # Variable declaration pattern
    VAR_DECL_PATTERN = rf'([\w,\s]+)\s*:\s*({TYPE_PATTERN})\s*(?::=\s*((?:\([^)]*\)|[^;]*)))?;(.*)'
    
    def __init__(self, declaration_text: str):
        """
        Initialize the parser with a declaration text.
        
        Args:
            declaration_text: The Twincat declaration text to parse
        """
        self.declaration_text = declaration_text
        self.fb_declaration = self._parse_fb_declaration()
        self.fb_comments = self._parse_fb_comments()
        self.var_blocks = self._extract_var_blocks()
    
    def _parse_fb_declaration(self) -> Dict[str, Any]:
        """
        Parse the function block declaration to extract name, extends, implements, and modifiers information.
        
        Returns:
            A dictionary containing the function block name, extends, implements, and modifiers information
        """
        result = {
            'name': None,
            'extends': [],
            'implements': [],
            'modifiers': []
        }
        
        # Extract function block name
        fb_match = re.search(self.FB_DECLARATION_PATTERN, self.declaration_text, re.IGNORECASE)
        if fb_match:
            result['name'] = fb_match.group(1)
        
        # Extract modifiers
        modifiers_match = re.search(self.FB_MODIFIERS_PATTERN, self.declaration_text, re.IGNORECASE)
        if modifiers_match:
            modifiers_str = modifiers_match.group(1)
            result['modifiers'] = [modifier.strip() for modifier in modifiers_str.split() if modifier.strip()]
        
        # Extract extends information
        extends_match = re.search(self.EXTENDS_PATTERN, self.declaration_text, re.IGNORECASE)
        if extends_match:
            extends_str = extends_match.group(1)
            result['extends'] = [name.strip() for name in extends_str.split(',') if name.strip()]
        
        # Extract implements information
        implements_match = re.search(self.IMPLEMENTS_PATTERN, self.declaration_text, re.IGNORECASE)
        if implements_match:
            implements_str = implements_match.group(1)
            result['implements'] = [name.strip() for name in implements_str.split(',') if name.strip()]
        
        return result
    
    def _parse_fb_comments(self) -> Dict[str, Optional[str]]:
        """
        Parse function block comments from the declaration text.
        
        Returns:
            A dictionary containing the extracted comment values with their names as keys
        """
        result = {
            'usage': None,
            'details': None
        }
        
        # Extract details
        details_match = re.search(self.DETAILS_PATTERN, self.declaration_text, re.DOTALL)
        if details_match:
            result['details'] = details_match.group(1).strip()
        
        # Extract usage
        usage_match = re.search(self.USAGE_PATTERN, self.declaration_text, re.DOTALL)
        if usage_match:
            result['usage'] = usage_match.group(1).strip()
        
        # Extract custom comments
        for match in re.finditer(self.CUSTOM_COMMENT_PATTERN, self.declaration_text, re.DOTALL):
            comment_name = match.group(1).strip()
            comment_content = match.group(2).strip()
            
            # Skip 'usage' and 'details' as they're already handled
            if comment_name not in ['usage', 'details']:
                result[comment_name] = comment_content
        
        return result
    
    def _extract_var_blocks(self) -> List[Dict[str, str]]:
        """
        Extract all VAR...END_VAR blocks from the declaration text.
        
        Returns:
            A list of dictionaries, each containing 'type' (the VAR type) and 'content' (the content between VAR and END_VAR)
        """
        var_blocks = []
        
        # Find all matches
        for match in re.finditer(self.VAR_BLOCK_PATTERN, self.declaration_text, re.DOTALL):
            var_type = match.group(1)  # The VAR type (VAR, VAR_INPUT, etc.)
            var_content = match.group(2).strip()  # The content between VAR and END_VAR
            
            var_blocks.append({
                'type': var_type,
                'content': var_content
            })
        
        return var_blocks
    
    @staticmethod
    def _extract_pragmas(lines_before_var: List[str]) -> List[str]:
        """
        Extract pragmas from lines before a variable declaration.
        
        Args:
            lines_before_var: Lines before the variable declaration
            
        Returns:
            A list of pragma strings
        """
        pragmas = []
        
        for line in lines_before_var:
            line = line.strip()
            if line.startswith('{'):
                pragma_match = re.search(DeclarationParser.PRAGMA_PATTERN, line)
                if pragma_match:
                    pragmas.append(pragma_match.group(1))
        
        return pragmas
    
    @staticmethod
    def _filter_comment_lines(comment: Optional[str]) -> Optional[str]:
        """
        Filter out pragma lines and empty lines from a comment.
        
        Args:
            comment: The comment to filter
            
        Returns:
            The filtered comment, or None if the comment is empty after filtering
        """
        if not comment:
            return None
            
        # Split the comment into lines and filter out pragma lines and empty lines
        comment_lines = comment.split('\n')
        filtered_lines = []
        
        for line in comment_lines:
            line = line.strip()
            if not line.startswith('{') and line:
                filtered_lines.append(line)
        
        # Return the filtered comment, or None if it's empty
        return '\n'.join(filtered_lines) if filtered_lines else None
    
    @staticmethod
    def _parse_variable_names(var_names_str: str) -> List[str]:
        """
        Parse a string of comma-separated variable names.
        
        Args:
            var_names_str: The string of comma-separated variable names
            
        Returns:
            A list of variable names
        """
        # Split by comma and strip whitespace
        return [name.strip() for name in var_names_str.split(',') if name.strip()]
    
    @staticmethod
    def _extract_multiline_comment(lines: List[str], start_idx: int, initial_comment: str) -> Tuple[str, int]:
        """
        Extract a multi-line comment starting from a specific line.
        
        Args:
            lines: List of lines from the VAR block
            start_idx: Index of the line where the comment starts
            initial_comment: The initial comment text from the first line
            
        Returns:
            A tuple of (comment_text, end_idx) where comment_text is the extracted comment
            and end_idx is the index of the last line of the comment
        """
        comment_text = initial_comment
        end_idx = start_idx
        
        # If the comment starts with (* and doesn't end with *), it's a multi-line comment
        if '(*' in comment_text and not '*)' in comment_text:
            # Find the end of the multi-line comment
            for j in range(start_idx + 1, len(lines)):
                comment_text += '\n' + lines[j].strip()
                end_idx = j
                if '*)' in lines[j]:  # Check for the end of a comment
                    break
        
        return comment_text, end_idx
    
    def parse_var_content(self, var_content: str) -> List[Dict[str, Any]]:
        """
        Parse the content of a VAR block and extract variable information.
        
        Args:
            var_content: The content between VAR and END_VAR tags
            
        Returns:
            A list of dictionaries, each containing information about a variable
        """
        variables = []
        lines = var_content.split('\n')
        
        # Process lines to find variable declarations and their attributes
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Check if this line contains a variable declaration
            var_decl_match = re.search(self.VAR_DECL_PATTERN, line, re.IGNORECASE)
            
            if var_decl_match:
                var_names_str = var_decl_match.group(1).strip()
                var_type = var_decl_match.group(2).strip()
                var_init_value = var_decl_match.group(3).strip() if var_decl_match.group(3) else None
                var_comment_start = var_decl_match.group(4).strip() if var_decl_match.group(4) else None
                
                # Extract multi-line comment if present
                var_comment = None
                if var_comment_start:
                    var_comment, comment_end_idx = self._extract_multiline_comment(lines, i, var_comment_start)
                    i = comment_end_idx  # Update the line index to skip the comment lines
                
                # Look back to find pragmas for this variable
                pragmas = []
                j = i - 1
                while j >= 0 and (lines[j].strip().startswith('{') or not lines[j].strip()):
                    pragma_line = lines[j].strip()
                    if pragma_line.startswith('{'):
                        pragma_match = re.search(self.PRAGMA_PATTERN, pragma_line)
                        if pragma_match:
                            pragmas.append(pragma_match.group(1))
                    j -= 1
                
                # Reverse pragmas to maintain original order
                pragmas.reverse()
                
                # Filter and parse the comment
                filtered_comment = self._filter_comment_lines(var_comment)
                
                # Parse any special comments in the variable comment
                comment_parser = DeclarationParser(var_comment if var_comment else "")
                usage_details = comment_parser._parse_fb_comments()
                
                # Process each variable name
                for var_name in self._parse_variable_names(var_names_str):
                    # Create variable dictionary with standard fields
                    var_dict = {
                        'name': var_name,
                        'type': var_type,
                        'init_value': var_init_value,
                        'pragmas': pragmas,
                        'comment': filtered_comment,
                        'usage': usage_details.get('usage'),
                        'details': usage_details.get('details')
                    }
                    
                    # Add any custom comments
                    for key, value in usage_details.items():
                        if key not in ['usage', 'details']:
                            var_dict[key] = value
                    
                    variables.append(var_dict)
            
            i += 1
        
        return variables
    
    def get_all_variables(self) -> List[Dict[str, Any]]:
        """
        Get all variables from all VAR blocks.
        
        Returns:
            A list of dictionaries, each containing information about a variable
        """
        all_variables = []
        
        for block in self.var_blocks:
            variables = self.parse_var_content(block['content'])
            for var in variables:
                var['block_type'] = block['type']
                all_variables.append(var)
        
        return all_variables
    
    @staticmethod
    def print_variable_info(var: Dict[str, Any]) -> None:
        """
        Print information about a variable in a formatted way.
        
        Args:
            var: The variable dictionary
        """
        print(f"  Name: {var['name']}")
        print(f"  Type: {var['type']}")
        
        if var.get('block_type'):
            print(f"  Block Type: {var['block_type']}")
        
        if var.get('init_value'):
            print(f"  Init Value: {var['init_value']}")
        
        if var.get('pragmas'):
            print(f"  Pragmas: {', '.join(var['pragmas'])}")
        
        if var.get('comment'):
            print(f"  Comment: {var['comment']}")
        
        # Print standard comment types
        if var.get('details'):
            print(f"  Details: {var['details']}")
            
        if var.get('usage'):
            print(f"  Usage: {var['usage']}")
        
        # Print any custom comment types
        for key, value in var.items():
            if key not in ['name', 'type', 'block_type', 'pragmas', 'comment', 'usage', 'details', 'init_value'] and value is not None:
                print(f"  {key.capitalize()}: {value}")
            
        print()  # Empty line for better readability


# Example usage
if __name__ == "__main__":
    declaration1 = """
FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED Extends FB_SubBase, FB_SubSubBase IMPLEMENTS I_Elementinformation, I_TestInterface, I_AnotherTestInterface
(*details This is a detail*)
(*usage 
this describes how to use this
# It can have markdown

```
someCode.someMethod();
```
*)



VAR
    _bCodeActive 						: BOOL; // this does that
	
    _bEnableCode, _bTest              			: BOOL; (*details this does something different*)  					
	{attribute 'hide'}                							
	_bUseParentEnableCode				: Array[1..10] OF BOOL; (*usage jkhsfkjhdkjhs
    skdfjlsdf
    sdfjklsjdkfljslfd
    sdfsjflsldkfjlsf
    sdfsjfslkjflskjdfs
    sdfsj*) (*details hskjhfksjfkjskdjfhskdhfiuhjwhefoiiweoifwjopeifjop*) (*example This is a custom comment type*) (* this should not be parsed *)
	
    _bEnableAlarm         				: Pointer To BOOL := TRUE;
    {attribute 'hide'}
	_bUseParentEnableAlarm				: Reference to BOOL := True;   
		
    _eSimulation      					: E_SimulationMode := E_SimulationMode.simOff;
    {attribute 'hide'}
	_bUseParentSimulation				: BOOL;
	
	_bReset								: BOOL;
    {attribute 'test'}
    {attribute 'hide'}
	_bUseParentReset					: ARRAY [1..C_nNumOfBool] OF BOOL;
	
	_nParentNumber						: INT;
    {attribute 'hide'}
	_bUseParentNumber					: BOOL;
	
	_sParentName						: STRING(Par_Core.C_nLengthOfParentName);
    {attribute 'hide'}
	_bUseParentName						: BOOL;	
	
    _sDesignationName     				: STRING(Par_Core.C_nLengthOfDesignationName);      
	
	_bError								: BOOL;
	
    {owntype '124'}
    {compile 'true'}
    _iParentInformation 				: I_ElementInformation;												
    {attribute 'hide'}
    _eCodeExecution 					: E_CodeExecutionMode; 										
	
	// Logging
	{attribute 'hide'}
	_LogCollector						: FB_LogCollector;
    {attribute 'hide'}	        		
	_BaseLogger							: FB_Log := (logCollector := _LogCollector);
END_VAR

VAR
    bTets                           : BOOL                           ;
    bFghgd                  : INT        ;
END_VAR



VAR_STAT
	{attribute 'hide'}
	_bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
END_VAR

"""

    # Create a parser instance
    parser = DeclarationParser(declaration1)
    
    # Print function block declaration information
    print("Function Block Name:", parser.fb_declaration.get('name'))
    
    if parser.fb_declaration.get('modifiers'):
        print("Modifiers:", ", ".join(parser.fb_declaration.get('modifiers')))
    
    if parser.fb_declaration.get('extends'):
        print("Extends:", ", ".join(parser.fb_declaration.get('extends')))
    
    if parser.fb_declaration.get('implements'):
        print("Implements:", ", ".join(parser.fb_declaration.get('implements')))
    
    # Print function block comments
    print("\nFunction Block Details:", parser.fb_comments.get('details'))
    print("Function Block Usage:", parser.fb_comments.get('usage'))
    
    # Print VAR blocks
    print("\nVAR Blocks:")
    for i, block in enumerate(parser.var_blocks):
        print(f"\nBlock {i+1} - Type: {block['type']}")
        
        # Parse variables in this block
        variables = parser.parse_var_content(block['content'])
        print(f"\nVariables in Block {i+1}:")
        
        for var in variables:
            parser.print_variable_info(var)
