from headroom import system_tools

def test_check_command_exists_true():
    assert system_tools.check_command_exists("python") or system_tools.check_command_exists("python3")

def test_check_command_exists_false():
    result = system_tools.check_command_exists("definitelynotarealcommand")
    assert not result["exists"]

def test_web_search_placeholder():
    result = system_tools.web_search("test")
    assert not result["success"]
    assert "not implemented" in result["output"].lower()