"""
Tests for meta commands (self-configuration).

These tests verify that wtf can modify its own configuration
via natural language commands.

NOTE: These tests run against real AI to verify end-to-end behavior.
Set ANTHROPIC_API_KEY or similar environment variable to run.
"""

import os
import json
import pytest
from pathlib import Path
from wtf.core.config import get_config_dir, load_config, save_config
from wtf.conversation.memory import load_memories, save_memory, delete_memory
from wtf.core.permissions import load_allowlist, add_to_allowlist


class TestMemoryCommands:
    """Test memory management via natural language."""
    
    @pytest.fixture
    def clean_config(self):
        """Ensure clean config for tests."""
        config_dir = get_config_dir()
        memories_file = config_dir / "memories.json"
        
        # Backup existing memories
        backup = None
        if memories_file.exists():
            backup = memories_file.read_text()
            memories_file.unlink()
        
        yield
        
        # Restore
        if backup:
            memories_file.write_text(backup)
    
    def test_remember_command(self, clean_config):
        """Test: wtf remember my name is dave and my favorite editor is emacs"""
        from wtf.cli import main
        
        # Run the command
        result = main(["remember", "my", "name", "is", "dave", "and", "my", "favorite", "editor", "is", "emacs"])
        
        # Verify memories were saved
        memories = load_memories()
        assert "name" in memories or "user_name" in memories
        assert "editor" in memories or "favorite_editor" in memories
        
        # Check that dave and emacs are in the values
        memory_str = json.dumps(memories).lower()
        assert "dave" in memory_str
        assert "emacs" in memory_str
    
    def test_show_memories_command(self):
        """Test: wtf show me what you remember about me"""
        from wtf.cli import main
        
        # Set up some memories
        save_memory("name", "dave", confidence=1.0)
        save_memory("editor", "emacs", confidence=1.0)
        
        # Run the command
        result = main(["show", "me", "what", "you", "remember", "about", "me"])
        
        # Result should contain the memories
        # (This would check console output in real implementation)
        assert result is not None
    
    def test_forget_specific_command(self):
        """Test: wtf forget about my editor preference"""
        from wtf.cli import main
        
        # Set up a memory
        save_memory("editor", "emacs", confidence=1.0)
        
        # Verify it exists
        memories = load_memories()
        assert "editor" in memories
        
        # Run forget command
        result = main(["forget", "about", "my", "editor", "preference"])
        
        # Verify it's gone
        memories = load_memories()
        assert "editor" not in memories
    
    def test_forget_everything_command(self):
        """Test: wtf forget everything we just did"""
        from wtf.cli import main
        from wtf.conversation.history import append_to_history, get_recent_conversations
        
        # Add some history entries
        append_to_history({
            "query": "test query 1",
            "response": "test response 1"
        })
        append_to_history({
            "query": "test query 2",
            "response": "test response 2"
        })
        
        # Verify history exists
        history = get_recent_conversations(count=5)
        initial_count = len(history)
        assert initial_count >= 2
        
        # Run forget command
        result = main(["forget", "everything", "we", "just", "did"])
        
        # Verify recent entries are cleared
        history = get_recent_conversations(count=5)
        # Should have fewer entries or they should be the forget command itself
        assert len(history) <= initial_count


class TestPersonalityCommands:
    """Test personality modification via natural language."""
    
    @pytest.fixture
    def clean_personality(self):
        """Ensure clean personality config."""
        config_dir = get_config_dir()
        personality_file = config_dir / "personality.txt"
        
        # Backup existing personality
        backup = None
        if personality_file.exists():
            backup = personality_file.read_text()
            personality_file.unlink()
        
        yield
        
        # Restore
        if backup:
            personality_file.write_text(backup)
        elif personality_file.exists():
            personality_file.unlink()
    
    def test_change_personality_sycophant(self, clean_personality):
        """Test: wtf change your personality to be more of a super sycophant"""
        from wtf.cli import main
        from wtf.ai.prompts import load_personality
        
        # Run the command
        result = main(["change", "your", "personality", "to", "be", "more", "of", "a", "super", "sycophant"])
        
        # Verify personality.txt was created
        config_dir = get_config_dir()
        personality_file = config_dir / "personality.txt"
        assert personality_file.exists()
        
        # Verify content
        personality = load_personality()
        assert personality is not None
        personality_lower = personality.lower()
        assert "sycophant" in personality_lower or "enthusiastic" in personality_lower or "compliment" in personality_lower
    
    def test_change_personality_encouraging(self, clean_personality):
        """Test: wtf be more encouraging and positive"""
        from wtf.cli import main
        from wtf.ai.prompts import load_personality
        
        # Run the command  
        result = main(["be", "more", "encouraging", "and", "positive"])
        
        # Verify personality was saved
        personality = load_personality()
        assert personality is not None
        personality_lower = personality.lower()
        assert "encouraging" in personality_lower or "positive" in personality_lower or "supportive" in personality_lower
    
    def test_reset_personality(self, clean_personality):
        """Test: wtf reset your personality"""
        from wtf.cli import main
        from wtf.ai.prompts import load_personality
        
        # First set a custom personality
        config_dir = get_config_dir()
        personality_file = config_dir / "personality.txt"
        personality_file.write_text("You are super happy!")
        
        # Verify it exists
        assert personality_file.exists()
        
        # Run reset command
        result = main(["reset", "your", "personality"])
        
        # Verify personality.txt was deleted
        assert not personality_file.exists()
        
        # Verify load_personality returns None (uses default)
        personality = load_personality()
        assert personality is None


class TestPermissionCommands:
    """Test permission modification via natural language."""
    
    @pytest.fixture
    def clean_allowlist(self):
        """Ensure clean allowlist."""
        config_dir = get_config_dir()
        allowlist_file = config_dir / "allowlist.json"
        
        # Backup existing allowlist
        backup = None
        if allowlist_file.exists():
            backup = allowlist_file.read_text()
        
        # Reset to empty
        allowlist_file.write_text(json.dumps({"patterns": [], "denylist": []}))
        
        yield
        
        # Restore
        if backup:
            allowlist_file.write_text(backup)
    
    def test_give_permission_all_commands(self, clean_allowlist):
        """Test: wtf give yourself permission to run all commands"""
        from wtf.cli import main
        
        # Run the command (should ask for confirmation in real usage)
        # For testing, we'd mock the confirmation
        result = main(["give", "yourself", "permission", "to", "run", "all", "commands"])
        
        # This should show a warning about dangerous permissions
        # In real usage, user would need to confirm
        # For now, just verify the agent understands the request
        assert result is not None
    
    def test_allow_git_commands(self, clean_allowlist):
        """Test: wtf allow git commands without asking"""
        from wtf.cli import main
        
        # Run the command
        result = main(["allow", "git", "commands", "without", "asking"])
        
        # Verify allowlist was updated
        allowlist = load_allowlist()
        
        # Should have git-related patterns
        patterns_str = " ".join(allowlist.get("patterns", []))
        assert "git" in patterns_str.lower()
    
    def test_stop_auto_running_npm(self, clean_allowlist):
        """Test: wtf stop auto-running npm commands"""
        from wtf.cli import main
        
        # First add npm to allowlist
        add_to_allowlist("npm")
        
        # Verify it's there
        allowlist = load_allowlist()
        assert "npm" in allowlist.get("patterns", [])
        
        # Run stop command
        result = main(["stop", "auto-running", "npm", "commands"])
        
        # Verify npm was removed
        allowlist = load_allowlist()
        assert "npm" not in allowlist.get("patterns", [])


class TestIntegrationMetaCommands:
    """Integration tests that verify end-to-end meta command behavior."""
    
    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="Requires API key")
    def test_full_memory_workflow(self):
        """Test complete memory workflow: remember, show, forget."""
        from wtf.cli import main
        
        # Remember something
        main(["remember", "I", "prefer", "pytest", "over", "unittest"])
        
        # Show memories
        result = main(["show", "what", "you", "remember"])
        # Should mention pytest
        
        # Forget it
        main(["forget", "about", "my", "testing", "preference"])
        
        # Verify it's gone
        memories = load_memories()
        memory_str = json.dumps(memories).lower()
        assert "pytest" not in memory_str
    
    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="Requires API key")
    def test_full_personality_workflow(self):
        """Test complete personality workflow: change, use, reset."""
        from wtf.cli import main
        from wtf.ai.prompts import load_personality
        
        # Change personality
        main(["be", "super", "enthusiastic", "and", "use", "lots", "of", "exclamation", "marks"])
        
        # Verify it was saved
        personality = load_personality()
        assert personality is not None
        assert "enthusiastic" in personality.lower() or "exclamation" in personality.lower()
        
        # Use it (make a query with new personality)
        result = main(["echo", "hello"])
        # The response should reflect the new personality (more enthusiastic)
        
        # Reset
        main(["reset", "your", "personality"])
        
        # Verify it's back to default
        personality = load_personality()
        assert personality is None


# Test data for parameterized tests
META_COMMAND_EXAMPLES = [
    ("remember my name is dave", "memory", "dave"),
    ("remember I use emacs", "memory", "emacs"),
    ("forget about my editor", "memory", None),
    ("change personality to pirate", "personality", "pirate"),
    ("be more encouraging", "personality", "encouraging"),
    ("reset personality", "personality", None),
    ("allow git commands", "permissions", "git"),
    ("show what you remember", "query", "memories"),
]

@pytest.mark.parametrize("command,category,expected", META_COMMAND_EXAMPLES)
def test_meta_command_detection(command, category, expected):
    """Test that meta commands are correctly detected and categorized."""
    from wtf.ai.response_parser import detect_meta_command
    
    result = detect_meta_command(command)
    assert result["category"] == category
    
    if expected:
        assert expected.lower() in str(result).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

