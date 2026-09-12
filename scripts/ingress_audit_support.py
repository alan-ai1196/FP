"""External exact-data producer used by Runtime integration audits.

This helper owns the source values and serialization outside Runtime. Only
offered bounded byte chunks cross the public interface; it has no state,
resource, prediction or certificate authority.
"""
from fp_reference.ingress import encode_context
from fp_reference.runtime import PredictionResult


def deliver_context(runtime, observation_id, values):
    frame = encode_context(values)
    offer = runtime.begin_context(observation_id)
    if offer.status == 'UNRESOLVED':
        return PredictionResult('UNRESOLVED', observation_id, offer.cursor, (), offer.reason)
    while offer.next_offset < len(frame) and offer.max_bytes:
        offset = offer.next_offset
        offer = runtime.receive_context(offer.ingress_id, offset, frame[offset:offset+offer.max_bytes])
    # Capacity can end before the producer's frame. The suffix never enters
    # Runtime; finishing its actual incomplete prefix yields UNRESOLVED.
    return runtime.finish_context(offer.ingress_id)
