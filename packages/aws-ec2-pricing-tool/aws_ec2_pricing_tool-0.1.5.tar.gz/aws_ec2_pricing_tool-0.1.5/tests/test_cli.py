import subprocess

def test_ec2pricing_help():
    # Run 'ec2pricing -h' and capture the output
    result = subprocess.run(
        ["ec2pricing", "-h"],
        capture_output=True,
        text=True,
    )
    
    # The command should exit with code 0 (success)
    assert result.returncode == 0
    
    # The output should contain some expected help text (adjust as needed)
    assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()
