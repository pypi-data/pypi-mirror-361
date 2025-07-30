"""Tests for error handling and user experience in failure scenarios."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from doteval.core import ForEach
from doteval.evaluators import exact_match
from doteval.metrics import accuracy
from doteval.models import EvaluationStatus, Result, Score
from doteval.sessions import SessionManager
from doteval.storage.json import JSONStorage


@pytest.fixture
def temp_storage():
    """Provide temporary storage for error handling tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_evaluation_function_raises_value_error(temp_storage):
    """Test evaluation function raising ValueError provides helpful error message."""
    test_data = [("Q1", "A1"), ("Q2", "A2"), ("Q3", "A3")]

    def eval_with_value_error(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            raise ValueError("Invalid input format")
        return Result(prompt=prompt, scores=[exact_match(answer, "A1")])

    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="error_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", test_data)
    def eval_with_value_error_wrapped(question, answer):
        return eval_with_value_error(question, answer)

    # Should not crash - should continue processing other items
    result = eval_with_value_error_wrapped(
        evaluation_name="eval_with_value_error",
        experiment_name="error_test",
        samples=None,
    )

    # Should have processed all 3 items (including the error)
    assert len(result.results) == 3

    # First and third items should succeed, second should have error
    assert result.results[0].error is None
    assert result.results[1].error is not None
    assert "Invalid input format" in result.results[1].error
    assert result.results[2].error is None

    # Results should be stored
    results = session_manager.storage.get_results("error_test", "eval_with_value_error")
    assert len(results) == 3

    # Only successful items should be in completed_ids
    completed_ids = session_manager.storage.completed_items(
        "error_test", "eval_with_value_error"
    )
    assert set(completed_ids) == {0, 2}  # Only successful items, not errors


def test_evaluation_function_raises_key_error(temp_storage):
    """Test evaluation function raising KeyError provides helpful context."""
    test_data = [("Q1", "A1"), ("Q2", "A2")]

    def eval_with_key_error(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            # Simulates accessing missing dictionary key
            raise KeyError("missing_field")
        return Result(prompt=prompt, scores=[exact_match(answer, "A1")])

    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="key_error_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", test_data)
    def eval_with_key_error_wrapped(question, answer):
        return eval_with_key_error(question, answer)

    result = eval_with_key_error_wrapped(
        evaluation_name="eval_with_key_error",
        experiment_name="key_error_test",
        samples=None,
    )

    # Should continue processing despite KeyError
    assert len(result.results) == 2
    assert result.results[0].error is None
    assert result.results[1].error is not None
    assert "missing_field" in result.results[1].error


def test_evaluation_function_raises_type_error(temp_storage):
    """Test evaluation function raising TypeError provides clear error context."""
    test_data = [("Q1", "A1"), ("Q2", "A2")]

    def eval_with_type_error(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            # Simulates type mismatch
            return question + 123  # String + int TypeError
        return Result(prompt=prompt, scores=[exact_match(answer, "A1")])

    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="type_error_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", test_data)
    def eval_with_type_error_wrapped(question, answer):
        return eval_with_type_error(question, answer)

    result = eval_with_type_error_wrapped(
        evaluation_name="eval_with_type_error",
        experiment_name="type_error_test",
        samples=None,
    )

    assert len(result.results) == 2
    assert result.results[0].error is None
    assert result.results[1].error is not None
    # Should capture the actual TypeError message
    assert (
        "concatenate" in result.results[1].error
        or "TypeError" in result.results[1].error
    )


@pytest.mark.xfail(
    reason="Framework doesn't yet validate return types - progress tracker crashes on invalid types"
)
def test_evaluation_function_returns_invalid_type(temp_storage):
    """Test evaluation function returning non-Result objects raises clear error."""
    test_data = [("Q1", "A1"), ("Q2", "A2")]

    def eval_with_invalid_return(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            return "invalid_return_value"  # Should return Result objects
        return Result(prompt=prompt, scores=[exact_match(answer, "A1")])

    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="invalid_return_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", test_data)
    def eval_with_invalid_return_wrapped(question, answer):
        return eval_with_invalid_return(question, answer)

    result = eval_with_invalid_return_wrapped(
        evaluation_name="eval_with_invalid_return",
        experiment_name="invalid_return_test",
        samples=None,
    )

    assert len(result.results) == 2
    assert result.results[0].error is None
    assert result.results[1].error is not None
    # Should have helpful error message about Result objects
    assert "Result" in result.results[1].error


def test_multiple_errors_in_single_evaluation(temp_storage):
    """Test handling multiple errors in the same evaluation batch."""
    test_data = [(f"Q{i}", f"A{i}") for i in range(1, 6)]  # 5 items

    def eval_with_multiple_errors(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            raise ValueError("Error in item 2")
        elif question == "Q4":
            raise KeyError("Error in item 4")
        return Result(prompt=prompt, scores=[exact_match(answer, "A1")])

    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="multiple_errors_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", test_data)
    def eval_with_multiple_errors_wrapped(question, answer):
        return eval_with_multiple_errors(question, answer)

    result = eval_with_multiple_errors_wrapped(
        evaluation_name="eval_with_multiple_errors",
        experiment_name="multiple_errors_test",
        samples=None,
    )

    # All items should be processed
    assert len(result.results) == 5

    # Check specific error patterns
    assert result.results[0].error is None  # Q1 succeeds
    assert "Error in item 2" in result.results[1].error  # Q2 fails
    assert result.results[2].error is None  # Q3 succeeds
    assert "Error in item 4" in result.results[3].error  # Q4 fails
    assert result.results[4].error is None  # Q5 succeeds

    # Only successful items should be in completed_ids
    completed_ids = session_manager.storage.completed_items(
        "multiple_errors_test", "eval_with_multiple_errors"
    )
    assert set(completed_ids) == {0, 2, 4}  # Only successful items


def test_storage_directory_permission_denied():
    """Test handling when storage directory has no write permissions."""
    # Create a directory with no write permissions
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "no_write_perms"
        storage_path.mkdir()
        os.chmod(storage_path, 0o444)  # Read-only

        try:
            # Should provide clear error message about permissions
            with pytest.raises(Exception) as exc_info:
                session_manager = SessionManager(
                    storage=f"json://{storage_path}", experiment_name="permission_test"
                )
                session_manager.storage.create_experiment("permission_test")

            # Error should be informative for users
            error_msg = str(exc_info.value).lower()
            assert any(word in error_msg for word in ["permission", "access", "write"])

        finally:
            # Restore permissions for cleanup
            os.chmod(storage_path, 0o755)


def test_storage_file_corruption_recovery(temp_storage):
    """Test handling when evaluation files are corrupted."""
    # Create an evaluation first
    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="corruption_test"
    )

    test_data = [("Q1", "A1")]

    def simple_eval(question, answer):
        return Result(prompt=f"Q: {question}", scores=[exact_match(answer, "A1")])

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", test_data)
    def simple_eval_wrapped(question, answer):
        return simple_eval(question, answer)

    simple_eval_wrapped(
        evaluation_name="simple_eval", experiment_name="corruption_test", samples=None
    )
    session_manager.finish_evaluation("simple_eval", success=True)

    # Corrupt the evaluation file
    eval_file = temp_storage / "corruption_test" / "simple_eval.jsonl"
    with open(eval_file, "w") as f:
        f.write("{ invalid json content }")

    # Should handle corruption gracefully
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="corruption_test"
    )

    # Should either return None for corrupted evaluation or raise clear error
    try:
        corrupted_eval = session_manager2.storage.load_evaluation(
            "corruption_test", "simple_eval"
        )
        # If it doesn't raise, it should return None or valid evaluation
        assert corrupted_eval is None or hasattr(corrupted_eval, "evaluation_name")
    except Exception as e:
        # If it raises, error should be informative
        error_msg = str(e).lower()
        # Check for JSON decoding error messages
        assert any(
            word in error_msg
            for word in ["expecting", "property", "json", "decode", "error"]
        )


def test_disk_space_exhaustion_simulation(temp_storage):
    """Test behavior when disk space is exhausted during save operations."""
    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="disk_space_test"
    )

    # Mock the storage add_results to simulate disk full error
    with patch.object(session_manager.storage, "add_results") as mock_add:
        mock_add.side_effect = OSError(28, "No space left on device")  # ENOSPC

        test_data = [("Q1", "A1")]

        def disk_test_eval(question, answer):
            return Result(prompt=f"Q: {question}", scores=[exact_match(answer, "A1")])

        # Create ForEach instance with custom storage
        custom_foreach = ForEach(storage=session_manager.storage)

        @custom_foreach("question,answer", test_data)
        def disk_test_eval_wrapped(question, answer):
            return disk_test_eval(question, answer)

        # Should handle disk space error gracefully
        with pytest.raises(OSError) as exc_info:
            disk_test_eval_wrapped(
                evaluation_name="disk_test_eval",
                experiment_name="disk_space_test",
                samples=None,
            )

        # Error should be informative
        assert "space" in str(exc_info.value).lower()


def test_storage_backend_unavailable():
    """Test handling when storage backend is unavailable."""
    # Test with invalid storage backend
    with pytest.raises(ValueError) as exc_info:
        SessionManager(storage="invalid://nonexistent/path")

    # Should provide clear, helpful error message
    error_msg = str(exc_info.value).lower()
    assert "unknown storage backend" in error_msg
    assert "invalid" in error_msg  # Should mention the invalid backend name

    # Test with no backend specified should default to json (backward compatibility)
    # This should not raise an error
    manager = SessionManager(storage="just_a_path")
    assert manager.storage.__class__.__name__ == "JSONStorage"


def test_empty_dataset_handling(temp_storage):
    """Test handling of empty datasets."""
    empty_data = []

    def eval_empty_dataset(question, answer):
        return Result(prompt=f"Q: {question}", scores=[exact_match(answer, "A1")])

    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="empty_dataset_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", empty_data)
    def eval_empty_dataset_wrapped(question, answer):
        return eval_empty_dataset(question, answer)

    # Should handle empty dataset gracefully
    result = eval_empty_dataset_wrapped(
        evaluation_name="eval_empty_dataset",
        experiment_name="empty_dataset_test",
        samples=None,
    )

    assert len(result.results) == 0
    assert result.summary == {}  # Empty summary for empty results


def test_malformed_dataset_entries(temp_storage):
    """Test handling of malformed dataset entries."""
    # Dataset with inconsistent structure
    malformed_data = [
        ("Q1", "A1"),  # Good entry
        ("Q2",),  # Missing answer
        ("Q3", "A3", "extra"),  # Extra field
        ("Q4", "A4"),  # Good entry
    ]

    def eval_malformed_dataset(question, answer):
        prompt = f"Q: {question}"
        return Result(prompt=prompt, scores=[exact_match(answer, "A1")])

    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="malformed_dataset_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", malformed_data)
    def eval_malformed_dataset_wrapped(question, answer):
        return eval_malformed_dataset(question, answer)

    # Check what actually happens with malformed entries
    result = eval_malformed_dataset_wrapped(
        evaluation_name="eval_malformed_dataset",
        experiment_name="malformed_dataset_test",
        samples=None,
    )

    # Should have attempted to process all entries
    assert len(result.results) == 4

    # Check what actually happens - the system is surprisingly robust
    # ("Q2",) - missing answer - should cause unpacking error
    assert result.results[1].error is not None
    # ("Q3", "A3", "extra") - extra field - actually handled gracefully! Extra field ignored
    # This shows the system is more robust than expected
    assert result.results[2].error is None  # System ignores extra fields


def test_dataset_iterator_exhaustion(temp_storage):
    """Test handling when dataset iterator is exhausted unexpectedly."""

    def problematic_iterator():
        yield ("Q1", "A1")
        yield ("Q2", "A2")
        # Iterator ends unexpectedly
        return

    def eval_exhausted_iterator(question, answer):
        return Result(prompt=f"Q: {question}", scores=[exact_match(answer, "A1")])

    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="exhausted_iterator_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", problematic_iterator())
    def eval_exhausted_iterator_wrapped(question, answer):
        return eval_exhausted_iterator(question, answer)

    # Should handle iterator exhaustion gracefully
    result = eval_exhausted_iterator_wrapped(
        evaluation_name="eval_exhausted_iterator",
        experiment_name="exhausted_iterator_test",
        samples=None,
    )

    # Should process available items
    assert len(result.results) == 2


def test_evaluation_already_running_handling(temp_storage):
    """Test handling when trying to start an evaluation that's already running."""
    # First session manager starts evaluation
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="concurrent_test"
    )
    session_manager1.start_evaluation("test_eval")

    # Second session manager should handle the running evaluation appropriately
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="concurrent_test"
    )

    # Should either resume the existing evaluation or handle conflict gracefully
    session_manager2.start_evaluation("test_eval")

    # Should be able to load the evaluation
    eval1 = session_manager1.storage.load_evaluation("concurrent_test", "test_eval")
    eval2 = session_manager2.storage.load_evaluation("concurrent_test", "test_eval")

    assert eval1 is not None
    assert eval2 is not None
    assert eval1.evaluation_name == eval2.evaluation_name


def test_evaluation_status_after_completion(temp_storage):
    """Test that evaluations have correct status after completion."""
    storage = JSONStorage(temp_storage)

    # Test completed evaluation (success=True)
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="status_test"
    )
    session_manager1.start_evaluation("completed_eval")
    session_manager1.finish_evaluation("completed_eval", success=True)

    evaluation = storage.load_evaluation("status_test", "completed_eval")
    assert evaluation.status == EvaluationStatus.COMPLETED

    # Test failed evaluation (success=False)
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="status_test"
    )
    session_manager2.start_evaluation("failed_eval")
    session_manager2.finish_evaluation("failed_eval", success=False)

    evaluation = storage.load_evaluation("status_test", "failed_eval")
    assert evaluation.status == EvaluationStatus.FAILED

    # Test running evaluation (never finished)
    session_manager3 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="status_test"
    )
    session_manager3.start_evaluation("running_eval")
    # Don't call finish_evaluation() - simulates process crash

    evaluation = storage.load_evaluation("status_test", "running_eval")
    assert evaluation.status == EvaluationStatus.RUNNING


def test_memory_pressure_large_results(temp_storage):
    """Test handling when evaluation results consume excessive memory."""
    # Create large dataset
    large_data = [(f"Q{i}", f"A{i}") for i in range(1000)]

    def eval_memory_intensive(question, answer):
        # Create a large score object (simulating memory pressure)
        large_metrics = [accuracy() for _ in range(100)]
        score = Score("memory_test", True, large_metrics)
        return Result(prompt=f"Q: {question}", scores=[score])

    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="memory_pressure_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", large_data)
    def eval_memory_intensive_wrapped(question, answer):
        return eval_memory_intensive(question, answer)

    # Should handle large results gracefully
    result = eval_memory_intensive_wrapped(
        evaluation_name="eval_memory_intensive",
        experiment_name="memory_pressure_test",
        samples=10,
    )

    assert len(result.results) == 10
    # Each result should have the large score
    assert all(
        len(r.result.scores) == 1 for r in result.results if r.result and not r.error
    )


def test_many_evaluations_file_descriptor_management(temp_storage):
    """Test handling when system creates many evaluations."""
    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="file_test"
    )

    # Create and finish many evaluations to test file descriptor cleanup
    for i in range(100):
        session_manager.start_evaluation(f"eval_{i}")
        session_manager.finish_evaluation(f"eval_{i}", success=True)

    # Should not accumulate file descriptors
    # All evaluations should be properly saved and closed
    evaluations = session_manager.storage.list_evaluations("file_test")
    assert len(evaluations) == 100


def test_helpful_error_context_in_results(temp_storage):
    """Test that error results include helpful context for debugging."""
    test_data = [("Q1", "A1"), ("Q2", "A2")]

    def eval_with_context_error(question, answer):
        if question == "Q2":
            # Error that should include context
            raise ValueError(f"Failed to process question: {question}")
        return Result(prompt=f"Q: {question}", scores=[exact_match(answer, "A1")])

    session_manager = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="context_error_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager.storage)

    @custom_foreach("question,answer", test_data)
    def eval_with_context_error_wrapped(question, answer):
        return eval_with_context_error(question, answer)

    result = eval_with_context_error_wrapped(
        evaluation_name="eval_with_context_error",
        experiment_name="context_error_test",
        samples=None,
    )

    # Error should include the original error message
    error_result = result.results[1]
    assert error_result.error is not None
    assert "Failed to process question: Q2" in error_result.error

    # Error result should still include item data for debugging
    assert error_result.dataset_row == {"question": "Q2", "answer": "A2"}
    assert error_result.item_id == 1


def test_evaluation_resumption_after_errors(temp_storage):
    """Test that evaluations can be resumed properly after errors occur."""
    test_data = [("Q1", "A1"), ("Q2", "A2"), ("Q3", "A3")]

    def eval_resumption_after_error(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            raise ValueError("Temporary error")
        return Result(prompt=prompt, scores=[exact_match(answer, "A1")])

    # First run with errors
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="resumption_error_test"
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach(storage=session_manager1.storage)

    @custom_foreach("question,answer", test_data)
    def eval_resumption_after_error_wrapped(question, answer):
        return eval_resumption_after_error(question, answer)

    result1 = eval_resumption_after_error_wrapped(
        evaluation_name="eval_resumption_after_error",
        experiment_name="resumption_error_test",
        samples=None,
    )
    session_manager1.finish_evaluation("eval_resumption_after_error", success=False)

    # Verify error was recorded
    assert len(result1.results) == 3
    assert result1.results[1].error is not None

    # Resume evaluation
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="resumption_error_test"
    )
    session_manager2.start_evaluation("eval_resumption_after_error")

    # Evaluation should be loaded and should have previous results
    results = session_manager2.storage.get_results(
        "resumption_error_test", "eval_resumption_after_error"
    )
    assert len(results) == 3

    # Only successful items should be in completed_ids
    completed_ids = session_manager2.storage.completed_items(
        "resumption_error_test", "eval_resumption_after_error"
    )
    assert set(completed_ids) == {0, 2}  # Only successful items


def test_evaluation_status_display_for_cli(temp_storage):
    """Test that evaluations show correct status for CLI display."""
    # Test completed evaluation (success=True)
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="cli_status_test"
    )
    session_manager1.start_evaluation("completed_evaluation")
    session_manager1.finish_evaluation("completed_evaluation", success=True)

    evaluation = session_manager1.storage.load_evaluation(
        "cli_status_test", "completed_evaluation"
    )
    assert evaluation.status == EvaluationStatus.COMPLETED

    # Test error evaluation (success=False)
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="cli_status_test"
    )
    session_manager2.start_evaluation("error_evaluation")
    session_manager2.finish_evaluation("error_evaluation", success=False)

    evaluation = session_manager2.storage.load_evaluation(
        "cli_status_test", "error_evaluation"
    )
    assert evaluation.status == EvaluationStatus.FAILED

    # Test interrupted evaluation (never finished)
    session_manager3 = SessionManager(
        storage=f"json://{temp_storage}", experiment_name="cli_status_test"
    )
    session_manager3.start_evaluation("interrupted_evaluation")
    # Don't call finish() - simulates process crash

    evaluation = session_manager3.storage.load_evaluation(
        "cli_status_test", "interrupted_evaluation"
    )
    assert evaluation.status == EvaluationStatus.RUNNING
