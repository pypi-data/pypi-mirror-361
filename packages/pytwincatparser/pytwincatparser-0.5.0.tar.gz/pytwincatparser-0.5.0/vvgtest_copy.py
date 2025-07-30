text =  r"""
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

import re

def get_var_blocks(decl):
    """
    Extract variable blocks from a declaration string.
    
    Args:
        decl: The declaration string
        
    Returns:
        A dictionary with name, keyword, and content for a single block,
        or a list of such dictionaries for multiple blocks
    """
    # Define the pattern to match variable blocks
    # This pattern captures the variable block type (VAR, VAR_INPUT, etc.),
    # any keyword (PERSISTENT, CONSTANT), and the content between the block start and end
    # The pattern now handles indentation and whitespace in the test strings
    pattern = r'\s*(VAR(?:_[A-Z_]+)?)\s*(\w+)?\s*\n(.*?)\s*END_VAR'
    
    # Find all matches in the declaration string
    matches = re.finditer(pattern, decl, re.DOTALL | re.IGNORECASE)
    
    # Convert matches to a list of dictionaries
    blocks = []
    for match in matches:
        var_type = match.group(1)  # VAR, VAR_INPUT, etc.
        keyword = match.group(2) if match.group(2) else ""  # PERSISTENT, CONSTANT, etc.
        content = match.group(3).rstrip()  # Content between VAR and END_VAR
        
        blocks.append({
            "name": var_type,
            "keyword": keyword,
            "content": content
        })
    
    # Return a single dictionary if there's only one block, or a list of dictionaries otherwise
    if len(blocks) == 1:
        return blocks[0]
    elif len(blocks) > 1:
        return blocks
    else:
        return {}


def test_get_var_blocks():
    # Test case 1
    test_str1 = r"""
    VAR_STAT
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected1 = {"name":"VAR_STAT", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}
    result1 = get_var_blocks(test_str1)
    assert result1 == expected1, f"Test case 1 failed. Expected: {expected1}, Got: {result1}"

    # Test case 2
    test_str2 = r"""
    VAR
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected2 = {"name":"VAR", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}
    result2 = get_var_blocks(test_str2)
    assert result2 == expected2, f"Test case 2 failed. Expected: {expected2}, Got: {result2}"

    # Test case 3
    test_str3 = r"""
    VAR_INPUT
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected3 = {"name":"VAR_INPUT", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}
    result3 = get_var_blocks(test_str3)
    assert result3 == expected3, f"Test case 3 failed. Expected: {expected3}, Got: {result3}"

    # Test case 4
    test_str4 = r"""
    VAR_IN_OUT
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected4 = {"name":"VAR_IN_OUT", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}
    result4 = get_var_blocks(test_str4)
    assert result4 == expected4, f"Test case 4 failed. Expected: {expected4}, Got: {result4}"

    # Test case 5
    test_str5 = r"""
    VAR_OUTPUT
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected5 = {"name":"VAR_OUTPUT", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}
    result5 = get_var_blocks(test_str5)
    assert result5 == expected5, f"Test case 5 failed. Expected: {expected5}, Got: {result5}"

    # Test case 6
    test_str6 = r"""
    VAR_TEMP
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected6 = {"name":"VAR_TEMP", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}
    result6 = get_var_blocks(test_str6)
    assert result6 == expected6, f"Test case 6 failed. Expected: {expected6}, Got: {result6}"

    # Test case 7
    test_str7 = r"""
    VAR_INST
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected7 = {"name":"VAR_INST", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}
    result7 = get_var_blocks(test_str7)
    assert result7 == expected7, f"Test case 7 failed. Expected: {expected7}, Got: {result7}"

    # Test case 8
    test_str8 = r"""
    VAR_OUtput
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected8 = {"name":"VAR_OUtput", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}
    result8 = get_var_blocks(test_str8)
    assert result8 == expected8, f"Test case 8 failed. Expected: {expected8}, Got: {result8}"

    # Test case 9
    test_str9 = r"""
    VAR PERSISTENT
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected9 = {"name":"VAR", "keyword":"PERSISTENT", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}
    result9 = get_var_blocks(test_str9)
    assert result9 == expected9, f"Test case 9 failed. Expected: {expected9}, Got: {result9}"

    # Test case 10
    test_str10 = r"""
    VAR CONSTANT
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected10 = {"name":"VAR", "keyword":"CONSTANT", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}
    result10 = get_var_blocks(test_str10)
    assert result10 == expected10, f"Test case 10 failed. Expected: {expected10}, Got: {result10}"

    # Test case 11
    test_str11 = r"""
    VAR CONSTANT
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR
    VAR
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected11 = [{"name":"VAR", "keyword":"CONSTANT", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""},
        {"name":"VAR", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}]
    result11 = get_var_blocks(test_str11)
    assert result11 == expected11, f"Test case 11 failed. Expected: {expected11}, Got: {result11}"

    # Test case 12
    test_str12 = r"""
    VAR_INPUT
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR
    VAR
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected12 = [{"name":"VAR_INPUT", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""},
        {"name":"VAR", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}]
    result12 = get_var_blocks(test_str12)
    assert result12 == expected12, f"Test case 12 failed. Expected: {expected12}, Got: {result12}"

    # Test case 13
    test_str13 = r"""
    VAR
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR
    VAR
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected13 = [{"name":"VAR", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""},
        {"name":"VAR", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}]
    result13 = get_var_blocks(test_str13)
    assert result13 == expected13, f"Test case 13 failed. Expected: {expected13}, Got: {result13}"

    # Test case 14
    test_str14 = r"""
    VAR       persistent
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR
    VAR (* constant *)
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected14 = [{"name":"VAR", "keyword":"persistent", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""},
        {"name":"VAR", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}]
    result14 = get_var_blocks(test_str14)
    assert result14 == expected14, f"Test case 14 failed. Expected: {expected14}, Got: {result14}"

    # Test case 15
    test_str15 = r"""
    (* VAR 
    bTest : BOOL;
    END_VAR*)
    VAR       
        // persistent
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR
    VAR (* constant *)
	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb
    END_VAR"""
    expected15 = [{"name":"VAR", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""},
        {"name":"VAR", "keyword":"", "content":r"""	    {attribute 'hide'}
	    _bLicenseOk 							: BOOL := TRUE; // static class variable, access to all fb"""}]
    result15 = get_var_blocks(test_str15)
    assert result15 == expected15, f"Test case 15 failed. Expected: {expected15}, Got: {result15}"

def get_extend(decl):
    """
    Extract the class names that a function block extends from a declaration string.
    
    Args:
        decl: The declaration string
        
    Returns:
        A list of class names that the function block extends
    """
    # First, remove comments to avoid false matches
    # Remove block comments (* ... *)
    decl_no_comments = re.sub(r'\(\*.*?\*\)', '', decl, flags=re.DOTALL)
    
    # Remove line comments // ...
    decl_no_comments = re.sub(r'//.*?$', '', decl_no_comments, flags=re.MULTILINE)
    
    # Define the pattern to match "Extends" followed by class names
    # This pattern looks for "Extends" followed by one or more class names separated by commas
    # It stops at "IMPLEMENTS" keyword or end of string
    pattern = r'EXTENDS\s+([\w,\s]+?)(?:\s+IMPLEMENTS\s+|$)'
    
    # Search for the pattern in the declaration string (case-insensitive)
    match = re.search(pattern, decl_no_comments, re.IGNORECASE)
    
    if match:
        # Extract the matched group (the class names)
        extends_str = match.group(1)
        
        # Split by comma and strip whitespace to get individual class names
        extends_list = [name.strip() for name in extends_str.split(',') if name.strip()]
        
        return extends_list
    
    # Return empty list if no "Extends" found
    return []


def test_get_extend():

    assert get_extend("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED Extends FB_SubBase, FB_SubSubBase IMPLEMENTS I_Elementinformation, I_TestInterface, I_AnotherTestInterface""") == ["FB_SubBase", "FB_SubSubBase"]
    assert get_extend("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED Extends FB_SubBase, FB_SubSubBase""") == ["FB_SubBase", "FB_SubSubBase"]
    assert get_extend("""extends FB_SubBase, FB_SubSubBase""") == ["FB_SubBase", "FB_SubSubBase"]
    assert get_extend("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED""") == []
    assert get_extend("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED (* extends this and that *)""") == []
    assert get_extend("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED (* extends this and that *) EXTENDS FB_SubBase""") == ["FB_SubBase"]
    assert get_extend("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED // extends this and that """) == []
    assert get_extend("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED // extends this and that EXTENDS """) == []
    assert get_extend("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED EXTENDS FB_SubBase""") == ["FB_SubBase"]
    assert get_extend("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED IMPLEMENTS I_Elementinformation, I_TestInterface EXTENDS FB_SubBase""") == ["FB_SubBase"]
    assert get_extend("""FUNCTION_BLOCK FB_Base PROTECTED EXTENDS FB_SubBase implements I_AnotherTestInterface""") == ["FB_SubBase"]

def get_implements(decl):
    """
    Extract the interface names that a function block implements from a declaration string.
    
    Args:
        decl: The declaration string
        
    Returns:
        A list of interface names that the function block implements
    """
    # First, remove comments to avoid false matches
    # Remove block comments (* ... *)
    decl_no_comments = re.sub(r'\(\*.*?\*\)', '', decl, flags=re.DOTALL)
    
    # Remove line comments // ...
    decl_no_comments = re.sub(r'//.*?$', '', decl_no_comments, flags=re.MULTILINE)
    
    # Define the pattern to match "Implements" followed by interface names
    # This pattern looks for "Implements" followed by one or more interface names separated by commas
    # It stops at "EXTENDS" keyword or end of string
    pattern = r'IMPLEMENTS\s+([\w,\s]+?)(?:\s+EXTENDS\s+|$)'
    
    # Search for the pattern in the declaration string (case-insensitive)
    match = re.search(pattern, decl_no_comments, re.IGNORECASE)
    
    if match:
        # Extract the matched group (the interface names)
        implements_str = match.group(1)
        
        # Split by comma and strip whitespace to get individual interface names
        implements_list = [name.strip() for name in implements_str.split(',') if name.strip()]
        
        return implements_list
    
    # Return empty list if no "Implements" found
    return []


def test_get_implements():

    assert get_implements("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED Extends FB_SubBase, FB_SubSubBase IMPLEMENTS I_Elementinformation, I_TestInterface, I_AnotherTestInterface""") == ["I_Elementinformation", "I_TestInterface", "I_AnotherTestInterface"]
    assert get_implements("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED Extends FB_SubBase, FB_SubSubBase""") == []
    assert get_implements("""extends FB_SubBase, FB_SubSubBase""") == []
    assert get_implements("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED""") == []
    assert get_implements("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED IMPLEMENTS FB_SubBase""") == ["FB_SubBase"]
    assert get_implements("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED IMPLEMENTS I_Elementinformation, I_TestInterface EXTENDS FB_SubBase""") == ["I_Elementinformation", "I_TestInterface"]
    assert get_implements("""FUNCTION_BLOCK FB_Base PROTECTED EXTENDS FB_SubBase implements I_AnotherTestInterface""") == ["I_AnotherTestInterface"]




def get_access_modifier(decl):
    """
    Extract the access modifier from a function block declaration string.
    
    Args:
        decl: The declaration string
        
    Returns:
        The access modifier as a string, or an empty string if no access modifier is found
    """
    # First, remove comments to avoid false matches
    # Remove block comments (* ... *)
    decl_no_comments = re.sub(r'\(\*.*?\*\)', '', decl, flags=re.DOTALL)
    
    # Remove line comments // ...
    decl_no_comments = re.sub(r'//.*?$', '', decl_no_comments, flags=re.MULTILINE)
    
    # Define the pattern to match access modifiers
    # This pattern looks for PRIVATE, PROTECTED, PUBLIC, or INTERNAL keywords
    # It ensures these are standalone words by checking for word boundaries
    pattern = r'\b(PRIVATE|PROTECTED|PUBLIC|INTERNAL)\b'
    
    # Search for the pattern in the declaration string (case-insensitive)
    match = re.search(pattern, decl_no_comments, re.IGNORECASE)
    
    if match:
        # Return the matched access modifier with its original case
        return match.group(1)
    
    # Return empty string if no access modifier is found
    return ""


def test_get_access_modifier():

    assert get_access_modifier("""FUNCTION_BLOCK FB_Base ABSTRACT Private Extends FB_SubBase, FB_SubSubBase IMPLEMENTS I_Elementinformation, I_TestInterface, I_AnotherTestInterface""") == "Private"
    assert get_access_modifier("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED Extends FB_SubBase, FB_SubSubBase""") == "PROTECTED"
    assert get_access_modifier("""extends FB_SubBase, FB_SubSubBase""") == ""
    assert get_access_modifier("""FUNCTION_BLOCK FB_Base ABSTRACT INTERNAL""") == "INTERNAL"
    assert get_access_modifier("""FUNCTION_BLOCK FB_Base PROTECTED ABSTRACT EXTENDS FB_SubBase""") == "PROTECTED"
    assert get_access_modifier("""METHOD FB_Base ABSTRACT PUBLIC IMPLEMENTS I_Elementinformation, I_TestInterface EXTENDS FB_SubBase""") == "PUBLIC"
    assert get_access_modifier("""FUNCTION_BLOCK FB_Base ABSTRACT EXTENDS FB_SubBase implements I_AnotherTestInterface""") == ""


def get_abstract_keyword(decl):
    """
    Extract the ABSTRACT keyword from a function block declaration string.
    
    Args:
        decl: The declaration string
        
    Returns:
        The string "ABSTRACT" if the keyword is present, or an empty string if it's not found
    """
    # First, remove comments to avoid false matches
    # Remove block comments (* ... *)
    decl_no_comments = re.sub(r'\(\*.*?\*\)', '', decl, flags=re.DOTALL)
    
    # Remove line comments // ...
    decl_no_comments = re.sub(r'//.*?$', '', decl_no_comments, flags=re.MULTILINE)
    
    # Define the pattern to match the ABSTRACT keyword
    # This pattern looks for the ABSTRACT keyword as a standalone word
    pattern = r'\b(ABSTRACT)\b'
    
    # Search for the pattern in the declaration string (case-insensitive)
    match = re.search(pattern, decl_no_comments, re.IGNORECASE)
    
    if match:
        # Return the matched keyword with its original case
        return match.group(1)
    
    # Return empty string if ABSTRACT keyword is not found
    return ""


def test_get_abstract_keyword():

    assert get_abstract_keyword("""FUNCTION_BLOCK FB_Base ABSTRACT Private Extends FB_SubBase, FB_SubSubBase IMPLEMENTS I_Elementinformation, I_TestInterface, I_AnotherTestInterface""") == "ABSTRACT"
    assert get_abstract_keyword("""FUNCTION_BLOCK FB_Base ABSTRACT PROTECTED Extends FB_SubBase, FB_SubSubBase""") == "ABSTRACT"
    assert get_abstract_keyword("""extends FB_SubBase, FB_SubSubBase""") == ""
    assert get_abstract_keyword("""FUNCTION_BLOCK FB_Base ABSTRACT INTERNAL""") == "ABSTRACT"
    assert get_abstract_keyword("""FUNCTION_BLOCK FB_Base PROTECTED  EXTENDS FB_SubBase""") == ""
    assert get_abstract_keyword("""METHOD FB_Base ABSTRACT PUBLIC IMPLEMENTS I_Elementinformation, I_TestInterface EXTENDS FB_SubBase""") == "ABSTRACT"
    assert get_abstract_keyword("""FUNCTION_BLOCK FB_Base  EXTENDS FB_SubBase implements I_AnotherTestInterface""") == ""
