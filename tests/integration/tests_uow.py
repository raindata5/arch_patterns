from adapters import (
    repository,
    uow
)
from domain import model

def tests_uow_does_not_serialize_uncommitted_edits(get_uow_context, return_unserialized_sample_data):
    uow_ins, repo = get_uow_context
    batch_nat, order_nat, list_ol = return_unserialized_sample_data
    with uow_ins as repo:
        repo.add(batch_nat)

    queried_batch = repo.get(model.Batch, model.Batch.reference, batch_nat.reference)
    assert not queried_batch

def tests_uow_serializes_committed_edits(get_uow_context, return_unserialized_sample_data):
    uow_ins, repo = get_uow_context
    batch_nat, order_nat, list_ol = return_unserialized_sample_data
    with uow_ins as repo:
        repo.add(batch_nat)
        repo.commit()

    queried_batch = repo.get(model.Batch, model.Batch.reference, batch_nat.reference)
    assert queried_batch == batch_nat