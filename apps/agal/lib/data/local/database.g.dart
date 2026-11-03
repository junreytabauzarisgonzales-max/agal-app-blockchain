// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'database.dart';

// ignore_for_file: type=lint
class $LocalBatchesTable extends LocalBatches
    with TableInfo<$LocalBatchesTable, LocalBatch> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LocalBatchesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
    'id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _farmerIdMeta = const VerificationMeta(
    'farmerId',
  );
  @override
  late final GeneratedColumn<String> farmerId = GeneratedColumn<String>(
    'farmer_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _speciesMeta = const VerificationMeta(
    'species',
  );
  @override
  late final GeneratedColumn<String> species = GeneratedColumn<String>(
    'species',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _estimatedWeightKgMeta = const VerificationMeta(
    'estimatedWeightKg',
  );
  @override
  late final GeneratedColumn<double> estimatedWeightKg =
      GeneratedColumn<double>(
        'estimated_weight_kg',
        aliasedName,
        false,
        type: DriftSqlType.double,
        requiredDuringInsert: true,
      );
  static const VerificationMeta _unitMeta = const VerificationMeta('unit');
  @override
  late final GeneratedColumn<String> unit = GeneratedColumn<String>(
    'unit',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('kg'),
  );
  static const VerificationMeta _harvestLatitudeMeta = const VerificationMeta(
    'harvestLatitude',
  );
  @override
  late final GeneratedColumn<double> harvestLatitude = GeneratedColumn<double>(
    'harvest_latitude',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _harvestLongitudeMeta = const VerificationMeta(
    'harvestLongitude',
  );
  @override
  late final GeneratedColumn<double> harvestLongitude = GeneratedColumn<double>(
    'harvest_longitude',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _harvestedAtMeta = const VerificationMeta(
    'harvestedAt',
  );
  @override
  late final GeneratedColumn<DateTime> harvestedAt = GeneratedColumn<DateTime>(
    'harvested_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
    'status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('harvested'),
  );
  static const VerificationMeta _currentHolderIdMeta = const VerificationMeta(
    'currentHolderId',
  );
  @override
  late final GeneratedColumn<String> currentHolderId = GeneratedColumn<String>(
    'current_holder_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _versionMeta = const VerificationMeta(
    'version',
  );
  @override
  late final GeneratedColumn<int> version = GeneratedColumn<int>(
    'version',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(1),
  );
  static const VerificationMeta _createdAtMeta = const VerificationMeta(
    'createdAt',
  );
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
    'created_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
    defaultValue: currentDateAndTime,
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
    defaultValue: currentDateAndTime,
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    farmerId,
    species,
    estimatedWeightKg,
    unit,
    harvestLatitude,
    harvestLongitude,
    harvestedAt,
    status,
    currentHolderId,
    version,
    createdAt,
    updatedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'local_batches';
  @override
  VerificationContext validateIntegrity(
    Insertable<LocalBatch> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('farmer_id')) {
      context.handle(
        _farmerIdMeta,
        farmerId.isAcceptableOrUnknown(data['farmer_id']!, _farmerIdMeta),
      );
    } else if (isInserting) {
      context.missing(_farmerIdMeta);
    }
    if (data.containsKey('species')) {
      context.handle(
        _speciesMeta,
        species.isAcceptableOrUnknown(data['species']!, _speciesMeta),
      );
    } else if (isInserting) {
      context.missing(_speciesMeta);
    }
    if (data.containsKey('estimated_weight_kg')) {
      context.handle(
        _estimatedWeightKgMeta,
        estimatedWeightKg.isAcceptableOrUnknown(
          data['estimated_weight_kg']!,
          _estimatedWeightKgMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_estimatedWeightKgMeta);
    }
    if (data.containsKey('unit')) {
      context.handle(
        _unitMeta,
        unit.isAcceptableOrUnknown(data['unit']!, _unitMeta),
      );
    }
    if (data.containsKey('harvest_latitude')) {
      context.handle(
        _harvestLatitudeMeta,
        harvestLatitude.isAcceptableOrUnknown(
          data['harvest_latitude']!,
          _harvestLatitudeMeta,
        ),
      );
    }
    if (data.containsKey('harvest_longitude')) {
      context.handle(
        _harvestLongitudeMeta,
        harvestLongitude.isAcceptableOrUnknown(
          data['harvest_longitude']!,
          _harvestLongitudeMeta,
        ),
      );
    }
    if (data.containsKey('harvested_at')) {
      context.handle(
        _harvestedAtMeta,
        harvestedAt.isAcceptableOrUnknown(
          data['harvested_at']!,
          _harvestedAtMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_harvestedAtMeta);
    }
    if (data.containsKey('status')) {
      context.handle(
        _statusMeta,
        status.isAcceptableOrUnknown(data['status']!, _statusMeta),
      );
    }
    if (data.containsKey('current_holder_id')) {
      context.handle(
        _currentHolderIdMeta,
        currentHolderId.isAcceptableOrUnknown(
          data['current_holder_id']!,
          _currentHolderIdMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_currentHolderIdMeta);
    }
    if (data.containsKey('version')) {
      context.handle(
        _versionMeta,
        version.isAcceptableOrUnknown(data['version']!, _versionMeta),
      );
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  LocalBatch map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LocalBatch(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id'],
      )!,
      farmerId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}farmer_id'],
      )!,
      species: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}species'],
      )!,
      estimatedWeightKg: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}estimated_weight_kg'],
      )!,
      unit: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}unit'],
      )!,
      harvestLatitude: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}harvest_latitude'],
      ),
      harvestLongitude: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}harvest_longitude'],
      ),
      harvestedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}harvested_at'],
      )!,
      status: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}status'],
      )!,
      currentHolderId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}current_holder_id'],
      )!,
      version: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}version'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      )!,
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      )!,
    );
  }

  @override
  $LocalBatchesTable createAlias(String alias) {
    return $LocalBatchesTable(attachedDatabase, alias);
  }
}

class LocalBatch extends DataClass implements Insertable<LocalBatch> {
  final String id;
  final String farmerId;
  final String species;
  final double estimatedWeightKg;
  final String unit;
  final double? harvestLatitude;
  final double? harvestLongitude;
  final DateTime harvestedAt;
  final String status;
  final String currentHolderId;
  final int version;
  final DateTime createdAt;
  final DateTime updatedAt;
  const LocalBatch({
    required this.id,
    required this.farmerId,
    required this.species,
    required this.estimatedWeightKg,
    required this.unit,
    this.harvestLatitude,
    this.harvestLongitude,
    required this.harvestedAt,
    required this.status,
    required this.currentHolderId,
    required this.version,
    required this.createdAt,
    required this.updatedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['farmer_id'] = Variable<String>(farmerId);
    map['species'] = Variable<String>(species);
    map['estimated_weight_kg'] = Variable<double>(estimatedWeightKg);
    map['unit'] = Variable<String>(unit);
    if (!nullToAbsent || harvestLatitude != null) {
      map['harvest_latitude'] = Variable<double>(harvestLatitude);
    }
    if (!nullToAbsent || harvestLongitude != null) {
      map['harvest_longitude'] = Variable<double>(harvestLongitude);
    }
    map['harvested_at'] = Variable<DateTime>(harvestedAt);
    map['status'] = Variable<String>(status);
    map['current_holder_id'] = Variable<String>(currentHolderId);
    map['version'] = Variable<int>(version);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  LocalBatchesCompanion toCompanion(bool nullToAbsent) {
    return LocalBatchesCompanion(
      id: Value(id),
      farmerId: Value(farmerId),
      species: Value(species),
      estimatedWeightKg: Value(estimatedWeightKg),
      unit: Value(unit),
      harvestLatitude: harvestLatitude == null && nullToAbsent
          ? const Value.absent()
          : Value(harvestLatitude),
      harvestLongitude: harvestLongitude == null && nullToAbsent
          ? const Value.absent()
          : Value(harvestLongitude),
      harvestedAt: Value(harvestedAt),
      status: Value(status),
      currentHolderId: Value(currentHolderId),
      version: Value(version),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
    );
  }

  factory LocalBatch.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LocalBatch(
      id: serializer.fromJson<String>(json['id']),
      farmerId: serializer.fromJson<String>(json['farmerId']),
      species: serializer.fromJson<String>(json['species']),
      estimatedWeightKg: serializer.fromJson<double>(json['estimatedWeightKg']),
      unit: serializer.fromJson<String>(json['unit']),
      harvestLatitude: serializer.fromJson<double?>(json['harvestLatitude']),
      harvestLongitude: serializer.fromJson<double?>(json['harvestLongitude']),
      harvestedAt: serializer.fromJson<DateTime>(json['harvestedAt']),
      status: serializer.fromJson<String>(json['status']),
      currentHolderId: serializer.fromJson<String>(json['currentHolderId']),
      version: serializer.fromJson<int>(json['version']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'farmerId': serializer.toJson<String>(farmerId),
      'species': serializer.toJson<String>(species),
      'estimatedWeightKg': serializer.toJson<double>(estimatedWeightKg),
      'unit': serializer.toJson<String>(unit),
      'harvestLatitude': serializer.toJson<double?>(harvestLatitude),
      'harvestLongitude': serializer.toJson<double?>(harvestLongitude),
      'harvestedAt': serializer.toJson<DateTime>(harvestedAt),
      'status': serializer.toJson<String>(status),
      'currentHolderId': serializer.toJson<String>(currentHolderId),
      'version': serializer.toJson<int>(version),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  LocalBatch copyWith({
    String? id,
    String? farmerId,
    String? species,
    double? estimatedWeightKg,
    String? unit,
    Value<double?> harvestLatitude = const Value.absent(),
    Value<double?> harvestLongitude = const Value.absent(),
    DateTime? harvestedAt,
    String? status,
    String? currentHolderId,
    int? version,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) => LocalBatch(
    id: id ?? this.id,
    farmerId: farmerId ?? this.farmerId,
    species: species ?? this.species,
    estimatedWeightKg: estimatedWeightKg ?? this.estimatedWeightKg,
    unit: unit ?? this.unit,
    harvestLatitude: harvestLatitude.present
        ? harvestLatitude.value
        : this.harvestLatitude,
    harvestLongitude: harvestLongitude.present
        ? harvestLongitude.value
        : this.harvestLongitude,
    harvestedAt: harvestedAt ?? this.harvestedAt,
    status: status ?? this.status,
    currentHolderId: currentHolderId ?? this.currentHolderId,
    version: version ?? this.version,
    createdAt: createdAt ?? this.createdAt,
    updatedAt: updatedAt ?? this.updatedAt,
  );
  LocalBatch copyWithCompanion(LocalBatchesCompanion data) {
    return LocalBatch(
      id: data.id.present ? data.id.value : this.id,
      farmerId: data.farmerId.present ? data.farmerId.value : this.farmerId,
      species: data.species.present ? data.species.value : this.species,
      estimatedWeightKg: data.estimatedWeightKg.present
          ? data.estimatedWeightKg.value
          : this.estimatedWeightKg,
      unit: data.unit.present ? data.unit.value : this.unit,
      harvestLatitude: data.harvestLatitude.present
          ? data.harvestLatitude.value
          : this.harvestLatitude,
      harvestLongitude: data.harvestLongitude.present
          ? data.harvestLongitude.value
          : this.harvestLongitude,
      harvestedAt: data.harvestedAt.present
          ? data.harvestedAt.value
          : this.harvestedAt,
      status: data.status.present ? data.status.value : this.status,
      currentHolderId: data.currentHolderId.present
          ? data.currentHolderId.value
          : this.currentHolderId,
      version: data.version.present ? data.version.value : this.version,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LocalBatch(')
          ..write('id: $id, ')
          ..write('farmerId: $farmerId, ')
          ..write('species: $species, ')
          ..write('estimatedWeightKg: $estimatedWeightKg, ')
          ..write('unit: $unit, ')
          ..write('harvestLatitude: $harvestLatitude, ')
          ..write('harvestLongitude: $harvestLongitude, ')
          ..write('harvestedAt: $harvestedAt, ')
          ..write('status: $status, ')
          ..write('currentHolderId: $currentHolderId, ')
          ..write('version: $version, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    farmerId,
    species,
    estimatedWeightKg,
    unit,
    harvestLatitude,
    harvestLongitude,
    harvestedAt,
    status,
    currentHolderId,
    version,
    createdAt,
    updatedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LocalBatch &&
          other.id == this.id &&
          other.farmerId == this.farmerId &&
          other.species == this.species &&
          other.estimatedWeightKg == this.estimatedWeightKg &&
          other.unit == this.unit &&
          other.harvestLatitude == this.harvestLatitude &&
          other.harvestLongitude == this.harvestLongitude &&
          other.harvestedAt == this.harvestedAt &&
          other.status == this.status &&
          other.currentHolderId == this.currentHolderId &&
          other.version == this.version &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt);
}

class LocalBatchesCompanion extends UpdateCompanion<LocalBatch> {
  final Value<String> id;
  final Value<String> farmerId;
  final Value<String> species;
  final Value<double> estimatedWeightKg;
  final Value<String> unit;
  final Value<double?> harvestLatitude;
  final Value<double?> harvestLongitude;
  final Value<DateTime> harvestedAt;
  final Value<String> status;
  final Value<String> currentHolderId;
  final Value<int> version;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const LocalBatchesCompanion({
    this.id = const Value.absent(),
    this.farmerId = const Value.absent(),
    this.species = const Value.absent(),
    this.estimatedWeightKg = const Value.absent(),
    this.unit = const Value.absent(),
    this.harvestLatitude = const Value.absent(),
    this.harvestLongitude = const Value.absent(),
    this.harvestedAt = const Value.absent(),
    this.status = const Value.absent(),
    this.currentHolderId = const Value.absent(),
    this.version = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LocalBatchesCompanion.insert({
    required String id,
    required String farmerId,
    required String species,
    required double estimatedWeightKg,
    this.unit = const Value.absent(),
    this.harvestLatitude = const Value.absent(),
    this.harvestLongitude = const Value.absent(),
    required DateTime harvestedAt,
    this.status = const Value.absent(),
    required String currentHolderId,
    this.version = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : id = Value(id),
       farmerId = Value(farmerId),
       species = Value(species),
       estimatedWeightKg = Value(estimatedWeightKg),
       harvestedAt = Value(harvestedAt),
       currentHolderId = Value(currentHolderId);
  static Insertable<LocalBatch> custom({
    Expression<String>? id,
    Expression<String>? farmerId,
    Expression<String>? species,
    Expression<double>? estimatedWeightKg,
    Expression<String>? unit,
    Expression<double>? harvestLatitude,
    Expression<double>? harvestLongitude,
    Expression<DateTime>? harvestedAt,
    Expression<String>? status,
    Expression<String>? currentHolderId,
    Expression<int>? version,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (farmerId != null) 'farmer_id': farmerId,
      if (species != null) 'species': species,
      if (estimatedWeightKg != null) 'estimated_weight_kg': estimatedWeightKg,
      if (unit != null) 'unit': unit,
      if (harvestLatitude != null) 'harvest_latitude': harvestLatitude,
      if (harvestLongitude != null) 'harvest_longitude': harvestLongitude,
      if (harvestedAt != null) 'harvested_at': harvestedAt,
      if (status != null) 'status': status,
      if (currentHolderId != null) 'current_holder_id': currentHolderId,
      if (version != null) 'version': version,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LocalBatchesCompanion copyWith({
    Value<String>? id,
    Value<String>? farmerId,
    Value<String>? species,
    Value<double>? estimatedWeightKg,
    Value<String>? unit,
    Value<double?>? harvestLatitude,
    Value<double?>? harvestLongitude,
    Value<DateTime>? harvestedAt,
    Value<String>? status,
    Value<String>? currentHolderId,
    Value<int>? version,
    Value<DateTime>? createdAt,
    Value<DateTime>? updatedAt,
    Value<int>? rowid,
  }) {
    return LocalBatchesCompanion(
      id: id ?? this.id,
      farmerId: farmerId ?? this.farmerId,
      species: species ?? this.species,
      estimatedWeightKg: estimatedWeightKg ?? this.estimatedWeightKg,
      unit: unit ?? this.unit,
      harvestLatitude: harvestLatitude ?? this.harvestLatitude,
      harvestLongitude: harvestLongitude ?? this.harvestLongitude,
      harvestedAt: harvestedAt ?? this.harvestedAt,
      status: status ?? this.status,
      currentHolderId: currentHolderId ?? this.currentHolderId,
      version: version ?? this.version,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (farmerId.present) {
      map['farmer_id'] = Variable<String>(farmerId.value);
    }
    if (species.present) {
      map['species'] = Variable<String>(species.value);
    }
    if (estimatedWeightKg.present) {
      map['estimated_weight_kg'] = Variable<double>(estimatedWeightKg.value);
    }
    if (unit.present) {
      map['unit'] = Variable<String>(unit.value);
    }
    if (harvestLatitude.present) {
      map['harvest_latitude'] = Variable<double>(harvestLatitude.value);
    }
    if (harvestLongitude.present) {
      map['harvest_longitude'] = Variable<double>(harvestLongitude.value);
    }
    if (harvestedAt.present) {
      map['harvested_at'] = Variable<DateTime>(harvestedAt.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    if (currentHolderId.present) {
      map['current_holder_id'] = Variable<String>(currentHolderId.value);
    }
    if (version.present) {
      map['version'] = Variable<int>(version.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LocalBatchesCompanion(')
          ..write('id: $id, ')
          ..write('farmerId: $farmerId, ')
          ..write('species: $species, ')
          ..write('estimatedWeightKg: $estimatedWeightKg, ')
          ..write('unit: $unit, ')
          ..write('harvestLatitude: $harvestLatitude, ')
          ..write('harvestLongitude: $harvestLongitude, ')
          ..write('harvestedAt: $harvestedAt, ')
          ..write('status: $status, ')
          ..write('currentHolderId: $currentHolderId, ')
          ..write('version: $version, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $LocalCustodyEventsTable extends LocalCustodyEvents
    with TableInfo<$LocalCustodyEventsTable, LocalCustodyEvent> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LocalCustodyEventsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
    'id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _batchIdMeta = const VerificationMeta(
    'batchId',
  );
  @override
  late final GeneratedColumn<String> batchId = GeneratedColumn<String>(
    'batch_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _eventTypeMeta = const VerificationMeta(
    'eventType',
  );
  @override
  late final GeneratedColumn<String> eventType = GeneratedColumn<String>(
    'event_type',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _actorIdMeta = const VerificationMeta(
    'actorId',
  );
  @override
  late final GeneratedColumn<String> actorId = GeneratedColumn<String>(
    'actor_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _actorRoleMeta = const VerificationMeta(
    'actorRole',
  );
  @override
  late final GeneratedColumn<String> actorRole = GeneratedColumn<String>(
    'actor_role',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _occurredAtMeta = const VerificationMeta(
    'occurredAt',
  );
  @override
  late final GeneratedColumn<DateTime> occurredAt = GeneratedColumn<DateTime>(
    'occurred_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _payloadMeta = const VerificationMeta(
    'payload',
  );
  @override
  late final GeneratedColumn<String> payload = GeneratedColumn<String>(
    'payload',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('{}'),
  );
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
    'synced',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("synced" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _createdAtMeta = const VerificationMeta(
    'createdAt',
  );
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
    'created_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
    defaultValue: currentDateAndTime,
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    batchId,
    eventType,
    actorId,
    actorRole,
    occurredAt,
    payload,
    synced,
    createdAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'local_custody_events';
  @override
  VerificationContext validateIntegrity(
    Insertable<LocalCustodyEvent> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('batch_id')) {
      context.handle(
        _batchIdMeta,
        batchId.isAcceptableOrUnknown(data['batch_id']!, _batchIdMeta),
      );
    } else if (isInserting) {
      context.missing(_batchIdMeta);
    }
    if (data.containsKey('event_type')) {
      context.handle(
        _eventTypeMeta,
        eventType.isAcceptableOrUnknown(data['event_type']!, _eventTypeMeta),
      );
    } else if (isInserting) {
      context.missing(_eventTypeMeta);
    }
    if (data.containsKey('actor_id')) {
      context.handle(
        _actorIdMeta,
        actorId.isAcceptableOrUnknown(data['actor_id']!, _actorIdMeta),
      );
    } else if (isInserting) {
      context.missing(_actorIdMeta);
    }
    if (data.containsKey('actor_role')) {
      context.handle(
        _actorRoleMeta,
        actorRole.isAcceptableOrUnknown(data['actor_role']!, _actorRoleMeta),
      );
    } else if (isInserting) {
      context.missing(_actorRoleMeta);
    }
    if (data.containsKey('occurred_at')) {
      context.handle(
        _occurredAtMeta,
        occurredAt.isAcceptableOrUnknown(data['occurred_at']!, _occurredAtMeta),
      );
    } else if (isInserting) {
      context.missing(_occurredAtMeta);
    }
    if (data.containsKey('payload')) {
      context.handle(
        _payloadMeta,
        payload.isAcceptableOrUnknown(data['payload']!, _payloadMeta),
      );
    }
    if (data.containsKey('synced')) {
      context.handle(
        _syncedMeta,
        synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta),
      );
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  LocalCustodyEvent map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LocalCustodyEvent(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id'],
      )!,
      batchId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}batch_id'],
      )!,
      eventType: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}event_type'],
      )!,
      actorId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}actor_id'],
      )!,
      actorRole: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}actor_role'],
      )!,
      occurredAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}occurred_at'],
      )!,
      payload: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}payload'],
      )!,
      synced: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}synced'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      )!,
    );
  }

  @override
  $LocalCustodyEventsTable createAlias(String alias) {
    return $LocalCustodyEventsTable(attachedDatabase, alias);
  }
}

class LocalCustodyEvent extends DataClass
    implements Insertable<LocalCustodyEvent> {
  final String id;
  final String batchId;
  final String eventType;
  final String actorId;
  final String actorRole;
  final DateTime occurredAt;
  final String payload;
  final bool synced;
  final DateTime createdAt;
  const LocalCustodyEvent({
    required this.id,
    required this.batchId,
    required this.eventType,
    required this.actorId,
    required this.actorRole,
    required this.occurredAt,
    required this.payload,
    required this.synced,
    required this.createdAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['batch_id'] = Variable<String>(batchId);
    map['event_type'] = Variable<String>(eventType);
    map['actor_id'] = Variable<String>(actorId);
    map['actor_role'] = Variable<String>(actorRole);
    map['occurred_at'] = Variable<DateTime>(occurredAt);
    map['payload'] = Variable<String>(payload);
    map['synced'] = Variable<bool>(synced);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  LocalCustodyEventsCompanion toCompanion(bool nullToAbsent) {
    return LocalCustodyEventsCompanion(
      id: Value(id),
      batchId: Value(batchId),
      eventType: Value(eventType),
      actorId: Value(actorId),
      actorRole: Value(actorRole),
      occurredAt: Value(occurredAt),
      payload: Value(payload),
      synced: Value(synced),
      createdAt: Value(createdAt),
    );
  }

  factory LocalCustodyEvent.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LocalCustodyEvent(
      id: serializer.fromJson<String>(json['id']),
      batchId: serializer.fromJson<String>(json['batchId']),
      eventType: serializer.fromJson<String>(json['eventType']),
      actorId: serializer.fromJson<String>(json['actorId']),
      actorRole: serializer.fromJson<String>(json['actorRole']),
      occurredAt: serializer.fromJson<DateTime>(json['occurredAt']),
      payload: serializer.fromJson<String>(json['payload']),
      synced: serializer.fromJson<bool>(json['synced']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'batchId': serializer.toJson<String>(batchId),
      'eventType': serializer.toJson<String>(eventType),
      'actorId': serializer.toJson<String>(actorId),
      'actorRole': serializer.toJson<String>(actorRole),
      'occurredAt': serializer.toJson<DateTime>(occurredAt),
      'payload': serializer.toJson<String>(payload),
      'synced': serializer.toJson<bool>(synced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  LocalCustodyEvent copyWith({
    String? id,
    String? batchId,
    String? eventType,
    String? actorId,
    String? actorRole,
    DateTime? occurredAt,
    String? payload,
    bool? synced,
    DateTime? createdAt,
  }) => LocalCustodyEvent(
    id: id ?? this.id,
    batchId: batchId ?? this.batchId,
    eventType: eventType ?? this.eventType,
    actorId: actorId ?? this.actorId,
    actorRole: actorRole ?? this.actorRole,
    occurredAt: occurredAt ?? this.occurredAt,
    payload: payload ?? this.payload,
    synced: synced ?? this.synced,
    createdAt: createdAt ?? this.createdAt,
  );
  LocalCustodyEvent copyWithCompanion(LocalCustodyEventsCompanion data) {
    return LocalCustodyEvent(
      id: data.id.present ? data.id.value : this.id,
      batchId: data.batchId.present ? data.batchId.value : this.batchId,
      eventType: data.eventType.present ? data.eventType.value : this.eventType,
      actorId: data.actorId.present ? data.actorId.value : this.actorId,
      actorRole: data.actorRole.present ? data.actorRole.value : this.actorRole,
      occurredAt: data.occurredAt.present
          ? data.occurredAt.value
          : this.occurredAt,
      payload: data.payload.present ? data.payload.value : this.payload,
      synced: data.synced.present ? data.synced.value : this.synced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LocalCustodyEvent(')
          ..write('id: $id, ')
          ..write('batchId: $batchId, ')
          ..write('eventType: $eventType, ')
          ..write('actorId: $actorId, ')
          ..write('actorRole: $actorRole, ')
          ..write('occurredAt: $occurredAt, ')
          ..write('payload: $payload, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    batchId,
    eventType,
    actorId,
    actorRole,
    occurredAt,
    payload,
    synced,
    createdAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LocalCustodyEvent &&
          other.id == this.id &&
          other.batchId == this.batchId &&
          other.eventType == this.eventType &&
          other.actorId == this.actorId &&
          other.actorRole == this.actorRole &&
          other.occurredAt == this.occurredAt &&
          other.payload == this.payload &&
          other.synced == this.synced &&
          other.createdAt == this.createdAt);
}

class LocalCustodyEventsCompanion extends UpdateCompanion<LocalCustodyEvent> {
  final Value<String> id;
  final Value<String> batchId;
  final Value<String> eventType;
  final Value<String> actorId;
  final Value<String> actorRole;
  final Value<DateTime> occurredAt;
  final Value<String> payload;
  final Value<bool> synced;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const LocalCustodyEventsCompanion({
    this.id = const Value.absent(),
    this.batchId = const Value.absent(),
    this.eventType = const Value.absent(),
    this.actorId = const Value.absent(),
    this.actorRole = const Value.absent(),
    this.occurredAt = const Value.absent(),
    this.payload = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LocalCustodyEventsCompanion.insert({
    required String id,
    required String batchId,
    required String eventType,
    required String actorId,
    required String actorRole,
    required DateTime occurredAt,
    this.payload = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : id = Value(id),
       batchId = Value(batchId),
       eventType = Value(eventType),
       actorId = Value(actorId),
       actorRole = Value(actorRole),
       occurredAt = Value(occurredAt);
  static Insertable<LocalCustodyEvent> custom({
    Expression<String>? id,
    Expression<String>? batchId,
    Expression<String>? eventType,
    Expression<String>? actorId,
    Expression<String>? actorRole,
    Expression<DateTime>? occurredAt,
    Expression<String>? payload,
    Expression<bool>? synced,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (batchId != null) 'batch_id': batchId,
      if (eventType != null) 'event_type': eventType,
      if (actorId != null) 'actor_id': actorId,
      if (actorRole != null) 'actor_role': actorRole,
      if (occurredAt != null) 'occurred_at': occurredAt,
      if (payload != null) 'payload': payload,
      if (synced != null) 'synced': synced,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LocalCustodyEventsCompanion copyWith({
    Value<String>? id,
    Value<String>? batchId,
    Value<String>? eventType,
    Value<String>? actorId,
    Value<String>? actorRole,
    Value<DateTime>? occurredAt,
    Value<String>? payload,
    Value<bool>? synced,
    Value<DateTime>? createdAt,
    Value<int>? rowid,
  }) {
    return LocalCustodyEventsCompanion(
      id: id ?? this.id,
      batchId: batchId ?? this.batchId,
      eventType: eventType ?? this.eventType,
      actorId: actorId ?? this.actorId,
      actorRole: actorRole ?? this.actorRole,
      occurredAt: occurredAt ?? this.occurredAt,
      payload: payload ?? this.payload,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (batchId.present) {
      map['batch_id'] = Variable<String>(batchId.value);
    }
    if (eventType.present) {
      map['event_type'] = Variable<String>(eventType.value);
    }
    if (actorId.present) {
      map['actor_id'] = Variable<String>(actorId.value);
    }
    if (actorRole.present) {
      map['actor_role'] = Variable<String>(actorRole.value);
    }
    if (occurredAt.present) {
      map['occurred_at'] = Variable<DateTime>(occurredAt.value);
    }
    if (payload.present) {
      map['payload'] = Variable<String>(payload.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LocalCustodyEventsCompanion(')
          ..write('id: $id, ')
          ..write('batchId: $batchId, ')
          ..write('eventType: $eventType, ')
          ..write('actorId: $actorId, ')
          ..write('actorRole: $actorRole, ')
          ..write('occurredAt: $occurredAt, ')
          ..write('payload: $payload, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $LocalMessagesTable extends LocalMessages
    with TableInfo<$LocalMessagesTable, LocalMessage> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LocalMessagesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
    'id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _senderIdMeta = const VerificationMeta(
    'senderId',
  );
  @override
  late final GeneratedColumn<String> senderId = GeneratedColumn<String>(
    'sender_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _recipientIdMeta = const VerificationMeta(
    'recipientId',
  );
  @override
  late final GeneratedColumn<String> recipientId = GeneratedColumn<String>(
    'recipient_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _bodyMeta = const VerificationMeta('body');
  @override
  late final GeneratedColumn<String> body = GeneratedColumn<String>(
    'body',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _occurredAtMeta = const VerificationMeta(
    'occurredAt',
  );
  @override
  late final GeneratedColumn<DateTime> occurredAt = GeneratedColumn<DateTime>(
    'occurred_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
    'synced',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("synced" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _createdAtMeta = const VerificationMeta(
    'createdAt',
  );
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
    'created_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
    defaultValue: currentDateAndTime,
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    senderId,
    recipientId,
    body,
    occurredAt,
    synced,
    createdAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'local_messages';
  @override
  VerificationContext validateIntegrity(
    Insertable<LocalMessage> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('sender_id')) {
      context.handle(
        _senderIdMeta,
        senderId.isAcceptableOrUnknown(data['sender_id']!, _senderIdMeta),
      );
    }
    if (data.containsKey('recipient_id')) {
      context.handle(
        _recipientIdMeta,
        recipientId.isAcceptableOrUnknown(
          data['recipient_id']!,
          _recipientIdMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_recipientIdMeta);
    }
    if (data.containsKey('body')) {
      context.handle(
        _bodyMeta,
        body.isAcceptableOrUnknown(data['body']!, _bodyMeta),
      );
    } else if (isInserting) {
      context.missing(_bodyMeta);
    }
    if (data.containsKey('occurred_at')) {
      context.handle(
        _occurredAtMeta,
        occurredAt.isAcceptableOrUnknown(data['occurred_at']!, _occurredAtMeta),
      );
    } else if (isInserting) {
      context.missing(_occurredAtMeta);
    }
    if (data.containsKey('synced')) {
      context.handle(
        _syncedMeta,
        synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta),
      );
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  LocalMessage map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LocalMessage(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id'],
      )!,
      senderId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sender_id'],
      )!,
      recipientId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}recipient_id'],
      )!,
      body: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}body'],
      )!,
      occurredAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}occurred_at'],
      )!,
      synced: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}synced'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      )!,
    );
  }

  @override
  $LocalMessagesTable createAlias(String alias) {
    return $LocalMessagesTable(attachedDatabase, alias);
  }
}

class LocalMessage extends DataClass implements Insertable<LocalMessage> {
  final String id;
  final String senderId;
  final String recipientId;
  final String body;
  final DateTime occurredAt;
  final bool synced;
  final DateTime createdAt;
  const LocalMessage({
    required this.id,
    required this.senderId,
    required this.recipientId,
    required this.body,
    required this.occurredAt,
    required this.synced,
    required this.createdAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['sender_id'] = Variable<String>(senderId);
    map['recipient_id'] = Variable<String>(recipientId);
    map['body'] = Variable<String>(body);
    map['occurred_at'] = Variable<DateTime>(occurredAt);
    map['synced'] = Variable<bool>(synced);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  LocalMessagesCompanion toCompanion(bool nullToAbsent) {
    return LocalMessagesCompanion(
      id: Value(id),
      senderId: Value(senderId),
      recipientId: Value(recipientId),
      body: Value(body),
      occurredAt: Value(occurredAt),
      synced: Value(synced),
      createdAt: Value(createdAt),
    );
  }

  factory LocalMessage.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LocalMessage(
      id: serializer.fromJson<String>(json['id']),
      senderId: serializer.fromJson<String>(json['senderId']),
      recipientId: serializer.fromJson<String>(json['recipientId']),
      body: serializer.fromJson<String>(json['body']),
      occurredAt: serializer.fromJson<DateTime>(json['occurredAt']),
      synced: serializer.fromJson<bool>(json['synced']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'senderId': serializer.toJson<String>(senderId),
      'recipientId': serializer.toJson<String>(recipientId),
      'body': serializer.toJson<String>(body),
      'occurredAt': serializer.toJson<DateTime>(occurredAt),
      'synced': serializer.toJson<bool>(synced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  LocalMessage copyWith({
    String? id,
    String? senderId,
    String? recipientId,
    String? body,
    DateTime? occurredAt,
    bool? synced,
    DateTime? createdAt,
  }) => LocalMessage(
    id: id ?? this.id,
    senderId: senderId ?? this.senderId,
    recipientId: recipientId ?? this.recipientId,
    body: body ?? this.body,
    occurredAt: occurredAt ?? this.occurredAt,
    synced: synced ?? this.synced,
    createdAt: createdAt ?? this.createdAt,
  );
  LocalMessage copyWithCompanion(LocalMessagesCompanion data) {
    return LocalMessage(
      id: data.id.present ? data.id.value : this.id,
      senderId: data.senderId.present ? data.senderId.value : this.senderId,
      recipientId: data.recipientId.present
          ? data.recipientId.value
          : this.recipientId,
      body: data.body.present ? data.body.value : this.body,
      occurredAt: data.occurredAt.present
          ? data.occurredAt.value
          : this.occurredAt,
      synced: data.synced.present ? data.synced.value : this.synced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LocalMessage(')
          ..write('id: $id, ')
          ..write('senderId: $senderId, ')
          ..write('recipientId: $recipientId, ')
          ..write('body: $body, ')
          ..write('occurredAt: $occurredAt, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    senderId,
    recipientId,
    body,
    occurredAt,
    synced,
    createdAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LocalMessage &&
          other.id == this.id &&
          other.senderId == this.senderId &&
          other.recipientId == this.recipientId &&
          other.body == this.body &&
          other.occurredAt == this.occurredAt &&
          other.synced == this.synced &&
          other.createdAt == this.createdAt);
}

class LocalMessagesCompanion extends UpdateCompanion<LocalMessage> {
  final Value<String> id;
  final Value<String> senderId;
  final Value<String> recipientId;
  final Value<String> body;
  final Value<DateTime> occurredAt;
  final Value<bool> synced;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const LocalMessagesCompanion({
    this.id = const Value.absent(),
    this.senderId = const Value.absent(),
    this.recipientId = const Value.absent(),
    this.body = const Value.absent(),
    this.occurredAt = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LocalMessagesCompanion.insert({
    required String id,
    this.senderId = const Value.absent(),
    required String recipientId,
    required String body,
    required DateTime occurredAt,
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : id = Value(id),
       recipientId = Value(recipientId),
       body = Value(body),
       occurredAt = Value(occurredAt);
  static Insertable<LocalMessage> custom({
    Expression<String>? id,
    Expression<String>? senderId,
    Expression<String>? recipientId,
    Expression<String>? body,
    Expression<DateTime>? occurredAt,
    Expression<bool>? synced,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (senderId != null) 'sender_id': senderId,
      if (recipientId != null) 'recipient_id': recipientId,
      if (body != null) 'body': body,
      if (occurredAt != null) 'occurred_at': occurredAt,
      if (synced != null) 'synced': synced,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LocalMessagesCompanion copyWith({
    Value<String>? id,
    Value<String>? senderId,
    Value<String>? recipientId,
    Value<String>? body,
    Value<DateTime>? occurredAt,
    Value<bool>? synced,
    Value<DateTime>? createdAt,
    Value<int>? rowid,
  }) {
    return LocalMessagesCompanion(
      id: id ?? this.id,
      senderId: senderId ?? this.senderId,
      recipientId: recipientId ?? this.recipientId,
      body: body ?? this.body,
      occurredAt: occurredAt ?? this.occurredAt,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (senderId.present) {
      map['sender_id'] = Variable<String>(senderId.value);
    }
    if (recipientId.present) {
      map['recipient_id'] = Variable<String>(recipientId.value);
    }
    if (body.present) {
      map['body'] = Variable<String>(body.value);
    }
    if (occurredAt.present) {
      map['occurred_at'] = Variable<DateTime>(occurredAt.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LocalMessagesCompanion(')
          ..write('id: $id, ')
          ..write('senderId: $senderId, ')
          ..write('recipientId: $recipientId, ')
          ..write('body: $body, ')
          ..write('occurredAt: $occurredAt, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $LocalBatchesTable localBatches = $LocalBatchesTable(this);
  late final $LocalCustodyEventsTable localCustodyEvents =
      $LocalCustodyEventsTable(this);
  late final $LocalMessagesTable localMessages = $LocalMessagesTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    localBatches,
    localCustodyEvents,
    localMessages,
  ];
}

typedef $$LocalBatchesTableCreateCompanionBuilder =
    LocalBatchesCompanion Function({
      required String id,
      required String farmerId,
      required String species,
      required double estimatedWeightKg,
      Value<String> unit,
      Value<double?> harvestLatitude,
      Value<double?> harvestLongitude,
      required DateTime harvestedAt,
      Value<String> status,
      required String currentHolderId,
      Value<int> version,
      Value<DateTime> createdAt,
      Value<DateTime> updatedAt,
      Value<int> rowid,
    });
typedef $$LocalBatchesTableUpdateCompanionBuilder =
    LocalBatchesCompanion Function({
      Value<String> id,
      Value<String> farmerId,
      Value<String> species,
      Value<double> estimatedWeightKg,
      Value<String> unit,
      Value<double?> harvestLatitude,
      Value<double?> harvestLongitude,
      Value<DateTime> harvestedAt,
      Value<String> status,
      Value<String> currentHolderId,
      Value<int> version,
      Value<DateTime> createdAt,
      Value<DateTime> updatedAt,
      Value<int> rowid,
    });

class $$LocalBatchesTableFilterComposer
    extends Composer<_$AppDatabase, $LocalBatchesTable> {
  $$LocalBatchesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get farmerId => $composableBuilder(
    column: $table.farmerId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get species => $composableBuilder(
    column: $table.species,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get estimatedWeightKg => $composableBuilder(
    column: $table.estimatedWeightKg,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get unit => $composableBuilder(
    column: $table.unit,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get harvestLatitude => $composableBuilder(
    column: $table.harvestLatitude,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get harvestLongitude => $composableBuilder(
    column: $table.harvestLongitude,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get harvestedAt => $composableBuilder(
    column: $table.harvestedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get currentHolderId => $composableBuilder(
    column: $table.currentHolderId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get version => $composableBuilder(
    column: $table.version,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LocalBatchesTableOrderingComposer
    extends Composer<_$AppDatabase, $LocalBatchesTable> {
  $$LocalBatchesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get farmerId => $composableBuilder(
    column: $table.farmerId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get species => $composableBuilder(
    column: $table.species,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get estimatedWeightKg => $composableBuilder(
    column: $table.estimatedWeightKg,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get unit => $composableBuilder(
    column: $table.unit,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get harvestLatitude => $composableBuilder(
    column: $table.harvestLatitude,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get harvestLongitude => $composableBuilder(
    column: $table.harvestLongitude,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get harvestedAt => $composableBuilder(
    column: $table.harvestedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get currentHolderId => $composableBuilder(
    column: $table.currentHolderId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get version => $composableBuilder(
    column: $table.version,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LocalBatchesTableAnnotationComposer
    extends Composer<_$AppDatabase, $LocalBatchesTable> {
  $$LocalBatchesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get farmerId =>
      $composableBuilder(column: $table.farmerId, builder: (column) => column);

  GeneratedColumn<String> get species =>
      $composableBuilder(column: $table.species, builder: (column) => column);

  GeneratedColumn<double> get estimatedWeightKg => $composableBuilder(
    column: $table.estimatedWeightKg,
    builder: (column) => column,
  );

  GeneratedColumn<String> get unit =>
      $composableBuilder(column: $table.unit, builder: (column) => column);

  GeneratedColumn<double> get harvestLatitude => $composableBuilder(
    column: $table.harvestLatitude,
    builder: (column) => column,
  );

  GeneratedColumn<double> get harvestLongitude => $composableBuilder(
    column: $table.harvestLongitude,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get harvestedAt => $composableBuilder(
    column: $table.harvestedAt,
    builder: (column) => column,
  );

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<String> get currentHolderId => $composableBuilder(
    column: $table.currentHolderId,
    builder: (column) => column,
  );

  GeneratedColumn<int> get version =>
      $composableBuilder(column: $table.version, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);
}

class $$LocalBatchesTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $LocalBatchesTable,
          LocalBatch,
          $$LocalBatchesTableFilterComposer,
          $$LocalBatchesTableOrderingComposer,
          $$LocalBatchesTableAnnotationComposer,
          $$LocalBatchesTableCreateCompanionBuilder,
          $$LocalBatchesTableUpdateCompanionBuilder,
          (
            LocalBatch,
            BaseReferences<_$AppDatabase, $LocalBatchesTable, LocalBatch>,
          ),
          LocalBatch,
          PrefetchHooks Function()
        > {
  $$LocalBatchesTableTableManager(_$AppDatabase db, $LocalBatchesTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LocalBatchesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$LocalBatchesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$LocalBatchesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> id = const Value.absent(),
                Value<String> farmerId = const Value.absent(),
                Value<String> species = const Value.absent(),
                Value<double> estimatedWeightKg = const Value.absent(),
                Value<String> unit = const Value.absent(),
                Value<double?> harvestLatitude = const Value.absent(),
                Value<double?> harvestLongitude = const Value.absent(),
                Value<DateTime> harvestedAt = const Value.absent(),
                Value<String> status = const Value.absent(),
                Value<String> currentHolderId = const Value.absent(),
                Value<int> version = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<DateTime> updatedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalBatchesCompanion(
                id: id,
                farmerId: farmerId,
                species: species,
                estimatedWeightKg: estimatedWeightKg,
                unit: unit,
                harvestLatitude: harvestLatitude,
                harvestLongitude: harvestLongitude,
                harvestedAt: harvestedAt,
                status: status,
                currentHolderId: currentHolderId,
                version: version,
                createdAt: createdAt,
                updatedAt: updatedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String id,
                required String farmerId,
                required String species,
                required double estimatedWeightKg,
                Value<String> unit = const Value.absent(),
                Value<double?> harvestLatitude = const Value.absent(),
                Value<double?> harvestLongitude = const Value.absent(),
                required DateTime harvestedAt,
                Value<String> status = const Value.absent(),
                required String currentHolderId,
                Value<int> version = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<DateTime> updatedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalBatchesCompanion.insert(
                id: id,
                farmerId: farmerId,
                species: species,
                estimatedWeightKg: estimatedWeightKg,
                unit: unit,
                harvestLatitude: harvestLatitude,
                harvestLongitude: harvestLongitude,
                harvestedAt: harvestedAt,
                status: status,
                currentHolderId: currentHolderId,
                version: version,
                createdAt: createdAt,
                updatedAt: updatedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$LocalBatchesTable, LocalBatch>(table),
                  BaseReferences<_$AppDatabase, $LocalBatchesTable, LocalBatch>(
                    db,
                    table,
                    e,
                  ),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LocalBatchesTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $LocalBatchesTable,
      LocalBatch,
      $$LocalBatchesTableFilterComposer,
      $$LocalBatchesTableOrderingComposer,
      $$LocalBatchesTableAnnotationComposer,
      $$LocalBatchesTableCreateCompanionBuilder,
      $$LocalBatchesTableUpdateCompanionBuilder,
      (
        LocalBatch,
        BaseReferences<_$AppDatabase, $LocalBatchesTable, LocalBatch>,
      ),
      LocalBatch,
      PrefetchHooks Function()
    >;
typedef $$LocalCustodyEventsTableCreateCompanionBuilder =
    LocalCustodyEventsCompanion Function({
      required String id,
      required String batchId,
      required String eventType,
      required String actorId,
      required String actorRole,
      required DateTime occurredAt,
      Value<String> payload,
      Value<bool> synced,
      Value<DateTime> createdAt,
      Value<int> rowid,
    });
typedef $$LocalCustodyEventsTableUpdateCompanionBuilder =
    LocalCustodyEventsCompanion Function({
      Value<String> id,
      Value<String> batchId,
      Value<String> eventType,
      Value<String> actorId,
      Value<String> actorRole,
      Value<DateTime> occurredAt,
      Value<String> payload,
      Value<bool> synced,
      Value<DateTime> createdAt,
      Value<int> rowid,
    });

class $$LocalCustodyEventsTableFilterComposer
    extends Composer<_$AppDatabase, $LocalCustodyEventsTable> {
  $$LocalCustodyEventsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get batchId => $composableBuilder(
    column: $table.batchId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get eventType => $composableBuilder(
    column: $table.eventType,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get actorId => $composableBuilder(
    column: $table.actorId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get actorRole => $composableBuilder(
    column: $table.actorRole,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get occurredAt => $composableBuilder(
    column: $table.occurredAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get payload => $composableBuilder(
    column: $table.payload,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get synced => $composableBuilder(
    column: $table.synced,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LocalCustodyEventsTableOrderingComposer
    extends Composer<_$AppDatabase, $LocalCustodyEventsTable> {
  $$LocalCustodyEventsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get batchId => $composableBuilder(
    column: $table.batchId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get eventType => $composableBuilder(
    column: $table.eventType,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get actorId => $composableBuilder(
    column: $table.actorId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get actorRole => $composableBuilder(
    column: $table.actorRole,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get occurredAt => $composableBuilder(
    column: $table.occurredAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get payload => $composableBuilder(
    column: $table.payload,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get synced => $composableBuilder(
    column: $table.synced,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LocalCustodyEventsTableAnnotationComposer
    extends Composer<_$AppDatabase, $LocalCustodyEventsTable> {
  $$LocalCustodyEventsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get batchId =>
      $composableBuilder(column: $table.batchId, builder: (column) => column);

  GeneratedColumn<String> get eventType =>
      $composableBuilder(column: $table.eventType, builder: (column) => column);

  GeneratedColumn<String> get actorId =>
      $composableBuilder(column: $table.actorId, builder: (column) => column);

  GeneratedColumn<String> get actorRole =>
      $composableBuilder(column: $table.actorRole, builder: (column) => column);

  GeneratedColumn<DateTime> get occurredAt => $composableBuilder(
    column: $table.occurredAt,
    builder: (column) => column,
  );

  GeneratedColumn<String> get payload =>
      $composableBuilder(column: $table.payload, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$LocalCustodyEventsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $LocalCustodyEventsTable,
          LocalCustodyEvent,
          $$LocalCustodyEventsTableFilterComposer,
          $$LocalCustodyEventsTableOrderingComposer,
          $$LocalCustodyEventsTableAnnotationComposer,
          $$LocalCustodyEventsTableCreateCompanionBuilder,
          $$LocalCustodyEventsTableUpdateCompanionBuilder,
          (
            LocalCustodyEvent,
            BaseReferences<
              _$AppDatabase,
              $LocalCustodyEventsTable,
              LocalCustodyEvent
            >,
          ),
          LocalCustodyEvent,
          PrefetchHooks Function()
        > {
  $$LocalCustodyEventsTableTableManager(
    _$AppDatabase db,
    $LocalCustodyEventsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LocalCustodyEventsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$LocalCustodyEventsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$LocalCustodyEventsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> id = const Value.absent(),
                Value<String> batchId = const Value.absent(),
                Value<String> eventType = const Value.absent(),
                Value<String> actorId = const Value.absent(),
                Value<String> actorRole = const Value.absent(),
                Value<DateTime> occurredAt = const Value.absent(),
                Value<String> payload = const Value.absent(),
                Value<bool> synced = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalCustodyEventsCompanion(
                id: id,
                batchId: batchId,
                eventType: eventType,
                actorId: actorId,
                actorRole: actorRole,
                occurredAt: occurredAt,
                payload: payload,
                synced: synced,
                createdAt: createdAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String id,
                required String batchId,
                required String eventType,
                required String actorId,
                required String actorRole,
                required DateTime occurredAt,
                Value<String> payload = const Value.absent(),
                Value<bool> synced = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalCustodyEventsCompanion.insert(
                id: id,
                batchId: batchId,
                eventType: eventType,
                actorId: actorId,
                actorRole: actorRole,
                occurredAt: occurredAt,
                payload: payload,
                synced: synced,
                createdAt: createdAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$LocalCustodyEventsTable, LocalCustodyEvent>(
                    table,
                  ),
                  BaseReferences<
                    _$AppDatabase,
                    $LocalCustodyEventsTable,
                    LocalCustodyEvent
                  >(db, table, e),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LocalCustodyEventsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $LocalCustodyEventsTable,
      LocalCustodyEvent,
      $$LocalCustodyEventsTableFilterComposer,
      $$LocalCustodyEventsTableOrderingComposer,
      $$LocalCustodyEventsTableAnnotationComposer,
      $$LocalCustodyEventsTableCreateCompanionBuilder,
      $$LocalCustodyEventsTableUpdateCompanionBuilder,
      (
        LocalCustodyEvent,
        BaseReferences<
          _$AppDatabase,
          $LocalCustodyEventsTable,
          LocalCustodyEvent
        >,
      ),
      LocalCustodyEvent,
      PrefetchHooks Function()
    >;
typedef $$LocalMessagesTableCreateCompanionBuilder =
    LocalMessagesCompanion Function({
      required String id,
      Value<String> senderId,
      required String recipientId,
      required String body,
      required DateTime occurredAt,
      Value<bool> synced,
      Value<DateTime> createdAt,
      Value<int> rowid,
    });
typedef $$LocalMessagesTableUpdateCompanionBuilder =
    LocalMessagesCompanion Function({
      Value<String> id,
      Value<String> senderId,
      Value<String> recipientId,
      Value<String> body,
      Value<DateTime> occurredAt,
      Value<bool> synced,
      Value<DateTime> createdAt,
      Value<int> rowid,
    });

class $$LocalMessagesTableFilterComposer
    extends Composer<_$AppDatabase, $LocalMessagesTable> {
  $$LocalMessagesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get senderId => $composableBuilder(
    column: $table.senderId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get recipientId => $composableBuilder(
    column: $table.recipientId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get body => $composableBuilder(
    column: $table.body,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get occurredAt => $composableBuilder(
    column: $table.occurredAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get synced => $composableBuilder(
    column: $table.synced,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LocalMessagesTableOrderingComposer
    extends Composer<_$AppDatabase, $LocalMessagesTable> {
  $$LocalMessagesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get senderId => $composableBuilder(
    column: $table.senderId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get recipientId => $composableBuilder(
    column: $table.recipientId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get body => $composableBuilder(
    column: $table.body,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get occurredAt => $composableBuilder(
    column: $table.occurredAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get synced => $composableBuilder(
    column: $table.synced,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LocalMessagesTableAnnotationComposer
    extends Composer<_$AppDatabase, $LocalMessagesTable> {
  $$LocalMessagesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get senderId =>
      $composableBuilder(column: $table.senderId, builder: (column) => column);

  GeneratedColumn<String> get recipientId => $composableBuilder(
    column: $table.recipientId,
    builder: (column) => column,
  );

  GeneratedColumn<String> get body =>
      $composableBuilder(column: $table.body, builder: (column) => column);

  GeneratedColumn<DateTime> get occurredAt => $composableBuilder(
    column: $table.occurredAt,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$LocalMessagesTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $LocalMessagesTable,
          LocalMessage,
          $$LocalMessagesTableFilterComposer,
          $$LocalMessagesTableOrderingComposer,
          $$LocalMessagesTableAnnotationComposer,
          $$LocalMessagesTableCreateCompanionBuilder,
          $$LocalMessagesTableUpdateCompanionBuilder,
          (
            LocalMessage,
            BaseReferences<_$AppDatabase, $LocalMessagesTable, LocalMessage>,
          ),
          LocalMessage,
          PrefetchHooks Function()
        > {
  $$LocalMessagesTableTableManager(_$AppDatabase db, $LocalMessagesTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LocalMessagesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$LocalMessagesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$LocalMessagesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> id = const Value.absent(),
                Value<String> senderId = const Value.absent(),
                Value<String> recipientId = const Value.absent(),
                Value<String> body = const Value.absent(),
                Value<DateTime> occurredAt = const Value.absent(),
                Value<bool> synced = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalMessagesCompanion(
                id: id,
                senderId: senderId,
                recipientId: recipientId,
                body: body,
                occurredAt: occurredAt,
                synced: synced,
                createdAt: createdAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String id,
                Value<String> senderId = const Value.absent(),
                required String recipientId,
                required String body,
                required DateTime occurredAt,
                Value<bool> synced = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalMessagesCompanion.insert(
                id: id,
                senderId: senderId,
                recipientId: recipientId,
                body: body,
                occurredAt: occurredAt,
                synced: synced,
                createdAt: createdAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$LocalMessagesTable, LocalMessage>(table),
                  BaseReferences<
                    _$AppDatabase,
                    $LocalMessagesTable,
                    LocalMessage
                  >(db, table, e),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LocalMessagesTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $LocalMessagesTable,
      LocalMessage,
      $$LocalMessagesTableFilterComposer,
      $$LocalMessagesTableOrderingComposer,
      $$LocalMessagesTableAnnotationComposer,
      $$LocalMessagesTableCreateCompanionBuilder,
      $$LocalMessagesTableUpdateCompanionBuilder,
      (
        LocalMessage,
        BaseReferences<_$AppDatabase, $LocalMessagesTable, LocalMessage>,
      ),
      LocalMessage,
      PrefetchHooks Function()
    >;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$LocalBatchesTableTableManager get localBatches =>
      $$LocalBatchesTableTableManager(_db, _db.localBatches);
  $$LocalCustodyEventsTableTableManager get localCustodyEvents =>
      $$LocalCustodyEventsTableTableManager(_db, _db.localCustodyEvents);
  $$LocalMessagesTableTableManager get localMessages =>
      $$LocalMessagesTableTableManager(_db, _db.localMessages);
}
