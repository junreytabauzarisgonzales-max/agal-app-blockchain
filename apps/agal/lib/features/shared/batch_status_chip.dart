import 'package:flutter/material.dart';

import '../../core/models/enums.dart';

const _labels = {
  BatchStatus.harvested: 'Harvested',
  BatchStatus.drying: 'Drying',
  BatchStatus.dried: 'Dried',
  BatchStatus.withSupplier: 'With supplier',
  BatchStatus.withBuyer: 'With buyer',
  BatchStatus.exported: 'Exported',
  BatchStatus.rejected: 'Rejected',
};

class BatchStatusChip extends StatelessWidget {
  const BatchStatusChip({super.key, required this.status});
  final BatchStatus status;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final isRejected = status == BatchStatus.rejected;
    final bg = isRejected ? colors.errorContainer : colors.secondaryContainer;
    final fg = isRejected
        ? colors.onErrorContainer
        : colors.onSecondaryContainer;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        _labels[status] ?? status.value,
        style: TextStyle(color: fg, fontSize: 12, fontWeight: FontWeight.w600),
      ),
    );
  }

  static BatchStatus fromWire(String value) => BatchStatus.fromValue(value);
}
