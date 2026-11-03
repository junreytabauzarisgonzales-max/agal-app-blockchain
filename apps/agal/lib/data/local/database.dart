import 'package:drift/drift.dart';
import 'package:drift_flutter/drift_flutter.dart';

import '../../core/models/enums.dart';
import 'tables.dart';

part 'database.g.dart';

@DriftDatabase(tables: [LocalBatches, LocalCustodyEvents, LocalMessages])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(driftDatabase(name: 'agal'));
  AppDatabase.forTesting(QueryExecutor executor) : super(executor);

  @override
  int get schemaVersion => 2;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onUpgrade: (m, from, to) async {
      if (from < 2) await m.addColumn(localMessages, localMessages.senderId);
    },
  );

  /// Creates the batch's projection row and its BATCH_CREATED event in one
  /// transaction. The event shares `id` with the batch it creates, exactly
  /// like the backend's apply_batch_created -- one client-minted UUID
  /// identifies both.
  Future<void> insertBatchCreated({
    required String id,
    required String farmerId,
    required String species,
    required double estimatedWeightKg,
    required String unit,
    double? harvestLatitude,
    double? harvestLongitude,
    required DateTime harvestedAt,
    required String payloadJson,
  }) async {
    await transaction(() async {
      await into(localBatches).insert(
        LocalBatchesCompanion.insert(
          id: id,
          farmerId: farmerId,
          species: species,
          estimatedWeightKg: estimatedWeightKg,
          unit: Value(unit),
          harvestLatitude: Value(harvestLatitude),
          harvestLongitude: Value(harvestLongitude),
          harvestedAt: harvestedAt,
          status: Value(BatchStatus.harvested.value),
          currentHolderId: farmerId,
        ),
      );
      await into(localCustodyEvents).insert(
        LocalCustodyEventsCompanion.insert(
          id: id,
          batchId: id,
          eventType: CustodyEventType.batchCreated.value,
          actorId: farmerId,
          actorRole: UserRole.farmer.value,
          occurredAt: harvestedAt,
          payload: Value(payloadJson),
        ),
      );
    });
  }

  /// Appends a custody event and folds it into the batch's local
  /// projection (status + current_holder_id), mirroring
  /// app/services/projection.py's apply_custody_event.
  Future<void> insertCustodyEvent({
    required String id,
    required String batchId,
    required CustodyEventType eventType,
    required String actorId,
    required UserRole actorRole,
    required DateTime occurredAt,
    required String payloadJson,
  }) async {
    await transaction(() async {
      await into(localCustodyEvents).insert(
        LocalCustodyEventsCompanion.insert(
          id: id,
          batchId: batchId,
          eventType: eventType.value,
          actorId: actorId,
          actorRole: actorRole.value,
          occurredAt: occurredAt,
          payload: Value(payloadJson),
        ),
      );

      final newStatus = statusTransitions[eventType];
      final isTransfer =
          eventType == CustodyEventType.transferredToSupplier ||
          eventType == CustodyEventType.transferredToBuyer;

      if (newStatus != null || isTransfer) {
        final batch = await (select(
          localBatches,
        )..where((b) => b.id.equals(batchId))).getSingle();
        await (update(localBatches)..where((b) => b.id.equals(batchId))).write(
          LocalBatchesCompanion(
            status: newStatus != null
                ? Value(newStatus.value)
                : Value(batch.status),
            currentHolderId: isTransfer
                ? Value(actorId)
                : Value(batch.currentHolderId),
            version: Value(batch.version + 1),
            updatedAt: Value(DateTime.now()),
          ),
        );
      } else {
        await (update(localBatches)..where((b) => b.id.equals(batchId))).write(
          LocalBatchesCompanion(
            version: Value(
              (await (select(
                    localBatches,
                  )..where((b) => b.id.equals(batchId))).getSingle()).version +
                  1,
            ),
            updatedAt: Value(DateTime.now()),
          ),
        );
      }
    });
  }

  Stream<List<LocalBatch>> watchBatchesForFarmer(String farmerId) {
    return (select(localBatches)
          ..where((b) => b.farmerId.equals(farmerId))
          ..orderBy([(b) => OrderingTerm.desc(b.createdAt)]))
        .watch();
  }

  Stream<LocalBatch?> watchBatch(String batchId) {
    return (select(
      localBatches,
    )..where((b) => b.id.equals(batchId))).watchSingleOrNull();
  }

  Stream<List<LocalCustodyEvent>> watchEventsForBatch(String batchId) {
    return (select(localCustodyEvents)
          ..where((e) => e.batchId.equals(batchId))
          ..orderBy([(e) => OrderingTerm.asc(e.occurredAt)]))
        .watch();
  }

  /// Everything the background sync service still needs to push, oldest first.
  Future<List<LocalCustodyEvent>> unsyncedEvents(String farmerId) {
    return (select(localCustodyEvents)
          ..where((e) => e.synced.equals(false) & e.actorId.equals(farmerId))
          ..orderBy([(e) => OrderingTerm.asc(e.createdAt)]))
        .get();
  }

  /// Live count of events not yet pushed to the server, for a "N pending
  /// sync" badge in the UI.
  Stream<int> watchUnsyncedCount([String? farmerId]) {
    final countExp = localCustodyEvents.id.count();
    final query = selectOnly(localCustodyEvents)
      ..addColumns([countExp])
      ..where(localCustodyEvents.synced.equals(false));
    if (farmerId != null)
      query.where(localCustodyEvents.actorId.equals(farmerId));
    return query.map((row) => row.read(countExp) ?? 0).watchSingle();
  }

  Future<void> markSynced(Iterable<String> ids) async {
    if (ids.isEmpty) return;
    await (update(localCustodyEvents)..where((e) => e.id.isIn(ids))).write(
      const LocalCustodyEventsCompanion(synced: Value(true)),
    );
  }

  /// Queues a chat message composed while offline. `senderId` isn't stored
  /// -- it's always the logged-in farmer, attributed server-side from the
  /// auth token when this row is eventually pushed via /sync.
  Future<void> insertOutgoingMessage({
    required String id,
    required String senderId,
    required String recipientId,
    required String body,
    required DateTime occurredAt,
  }) {
    return into(localMessages).insert(
      LocalMessagesCompanion.insert(
        id: id,
        senderId: Value(senderId),
        recipientId: recipientId,
        body: body,
        occurredAt: occurredAt,
      ),
    );
  }

  Stream<List<LocalMessage>> watchOutgoingMessagesTo(
    String recipientId,
    String senderId,
  ) {
    return (select(localMessages)
          ..where(
            (m) =>
                m.recipientId.equals(recipientId) & m.senderId.equals(senderId),
          )
          ..orderBy([(m) => OrderingTerm.asc(m.occurredAt)]))
        .watch();
  }

  Future<List<LocalMessage>> unsyncedMessages(String senderId) {
    return (select(localMessages)
          ..where((m) => m.synced.equals(false) & m.senderId.equals(senderId))
          ..orderBy([(m) => OrderingTerm.asc(m.createdAt)]))
        .get();
  }

  Future<void> markMessagesSynced(Iterable<String> ids) async {
    if (ids.isEmpty) return;
    await (update(localMessages)..where((m) => m.id.isIn(ids))).write(
      const LocalMessagesCompanion(synced: Value(true)),
    );
  }
}
