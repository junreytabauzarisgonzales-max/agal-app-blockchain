/// Mirrors app.models.enums on the backend -- the wire values (`.value`)
/// must match exactly, since they're sent/received as plain JSON strings.
enum UserRole {
  farmer('farmer'),
  supplier('supplier'),
  buyer('buyer');

  const UserRole(this.value);
  final String value;

  static UserRole fromValue(String value) =>
      UserRole.values.firstWhere((r) => r.value == value);
}

enum BatchStatus {
  harvested('harvested'),
  drying('drying'),
  dried('dried'),
  withSupplier('with_supplier'),
  withBuyer('with_buyer'),
  exported('exported'),
  rejected('rejected');

  const BatchStatus(this.value);
  final String value;

  static BatchStatus fromValue(String value) =>
      BatchStatus.values.firstWhere((s) => s.value == value);
}

enum CustodyEventType {
  batchCreated('batch_created'),
  dryingStarted('drying_started'),
  dryingCompleted('drying_completed'),
  qualityGraded('quality_graded'),
  transferredToSupplier('transferred_to_supplier'),
  transferredToBuyer('transferred_to_buyer'),
  priceAgreed('price_agreed'),
  paymentRecorded('payment_recorded'),
  exported('exported'),
  rejected('rejected'),
  noteAdded('note_added');

  const CustodyEventType(this.value);
  final String value;

  static CustodyEventType fromValue(String value) =>
      CustodyEventType.values.firstWhere((e) => e.value == value);
}

/// Status transition implied by each event type -- kept in sync with
/// app/services/projection.py's _STATUS_TRANSITIONS on the backend, so the
/// Farmer app's local read-model reflects the same derived state offline
/// that the server will derive once the event syncs.
const Map<CustodyEventType, BatchStatus> statusTransitions = {
  CustodyEventType.dryingStarted: BatchStatus.drying,
  CustodyEventType.dryingCompleted: BatchStatus.dried,
  CustodyEventType.transferredToSupplier: BatchStatus.withSupplier,
  CustodyEventType.transferredToBuyer: BatchStatus.withBuyer,
  CustodyEventType.exported: BatchStatus.exported,
  CustodyEventType.rejected: BatchStatus.rejected,
};
