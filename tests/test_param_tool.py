import muuusiiik.util as msk

#===============
# VALIDATE LIST
#===============
def test_param_tool_validate_list_normal_string():
    content  = 'hello'
    result   = msk.param_tool.validate_list(content)
    assert result == 'hello'

def test_param_tool_validate_list_spacing_string():
    content  = ' hello '
    result   = msk.param_tool.validate_list(content)
    assert result == 'hello'

def test_param_tool_validate_list_string_in_list():
    content  = 'hello, world '
    result   = msk.param_tool.validate_list(content)
    assert result == ['hello', 'world']

def test_param_tool_validate_list_number_in_list():
    content  = ' 1.0, 2, 3.4'
    result   = msk.param_tool.validate_list(content)
    assert result == [1.0, 2, 3.4]

def test_param_tool_validate_list_mixed_number_in_list():
    """ number will be converted as number
    """
    content  = ' 1.0, two, 3.4'
    result   = msk.param_tool.validate_list(content)
    assert result == [1.0, 'two', 3.4]

def test_param_tool_validate_list_mixed_number_in_list_without_check_type():
    """ number will be converted as string
    """
    content  = ' 1.0, two, 3.4'
    result   = msk.param_tool.validate_list(content, check_type=False)
    assert result == ['1.0', 'two', '3.4']

#=================
# CONVERT CONTENT
#=================
def test_param_tool_convert_dict_to_text():
    content  = {'ch': 1, 'sch': 1, 'done': [1,2,3,4], 'session':'init'}
    result   = msk.param_tool.to_text(content, delimeter='|')
    expected = 'ch=1|sch=1|done=1,2,3,4|session=init'
    assert result == expected


def test_param_tool_convert_text_to_dict():
    content  = 'ch=1|sch=1|session=init'
    result   = msk.param_tool.to_dict(content, delimeter='|')
    expected = {'ch': 1, 'sch': 1, 'session':'init'}
    assert result == expected


def _test_param_tool_repack_param_to_content():
    ...



