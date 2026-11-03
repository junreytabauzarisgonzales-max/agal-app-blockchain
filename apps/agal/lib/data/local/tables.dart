import 'package:drift/drift.dart';

/// Local read-model projection of a batch's current state -- the Farmer
/// app's on-device mirror of the backend's `harvest_batches` table. `id` is
/// the client-generated UUID minted when the batch is created, so it's
/// stable across the eventual sync to the server.
@DataClassName('LocalBatch')
class LocalBatches extends Table {
  TextColumn get id => text()();
  TextColumn get farmerId => text()();
  TextColumn get species => text()();
  RealColumn get estimatedWeightKg => real()();
  TextColumn get unit => text().withDefault(const Constant('kg'))();
  // Captured automatically from the device's GPS at harvest time, not typed
  // in by the farmer -- see FarmerCreateBatchScreen.
  RealColumn get harvestLatitude => real().nullable()();
  RealColumn get harvestLongitude => real().nullable()();
  DateTimeColumn get harvestedAt => dateTime()();
  TextColumn get status => text().withDefault(const Constant('harvested'))();
  TextColumn get currentHolderId => text()();
  IntColumn get version => integer().withDefault(const Constant(1))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

/// Immutable, append-only local mirror of `custody_events`. This table
/// doubles as the offline sync queue: any row with `synced = false` is
/// something the background sync service still needs to push to
/// POST /sync. Rows are never updated except to flip `synced` once the
/// server has confirmed it (as "created" or "duplicate" -- both mean the
/// server now has it).
class LocalCustodyEvents extends Table {
  TextColumn get id => text()();
  TextColumn get batchId => text()();
  TextColumn get eventType => text()();
  TextColumn get actorId => text()();
  TextColumn get actorRole => text()();
  DateTimeColumn get occurredAt => dateTime()();
  TextColumn get payload => text().withDefault(const Constant('{}'))();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

/// Outgoing chat messages composed while offline -- mirrors the same
/// append-only, client-generated-id pattern as LocalCustodyEvents, and is
/// pushed to the server the same way (via /sync). Only the Farmer role
/// needs this: Supplier/Buyer send messages directly online, with no local
/// queue. Incoming messages aren't cached here -- the chat thread screen
/// fetches those from the server, merging in any of these not-yet-synced
/// outgoing rows so a farmer sees their own pending sends immediately.
@DataClassName('LocalMessage')
class LocalMessages extends Table {
  TextColumn get id => text()();
  TextColumn get senderId => text().withDefault(const Constant(''))();
  TextColumn get recipientId => text()();
  TextColumn get body => text()();
  DateTimeColumn get occurredAt => dateTime()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}
