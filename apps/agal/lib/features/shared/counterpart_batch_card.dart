import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

/// A batch row for the Supplier/Buyer worklists -- unlike the Farmer's own
/// log, these roles are always looking at *someone else's* batch, so who
/// it's from/with is the first thing that matters, not just what it is.
class CounterpartBatchCard extends StatelessWidget {
  const CounterpartBatchCard({
    super.key,
    required this.batch,
    required this.counterpartLabel,
    required this.counterpartName,
    this.actionLabel,
    this.onAction,
    this.statusNote,
    required this.onTap,
  });

  final Map<String, dynamic> batch;
  final String counterpartLabel;
  final String? counterpartName;

  /// Both null means there's nothing actionable for this row right now
  /// (e.g. a supplier just waiting on a buyer) -- shown as a plain note
  /// instead of a button that looks clickable but does nothing.
  final String? actionLabel;
  final VoidCallback? onAction;
  final String? statusNote;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final harvestedAt = DateTime.tryParse(
      batch['harvested_at'] as String? ?? '',
    );

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      batch['species'] as String,
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                  ),
                  Text(
                    '${batch['estimated_weight_kg']} ${batch['unit']}',
                    style: TextStyle(color: colors.onSurfaceVariant),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Row(
                children: [
                  Icon(
                    Icons.person_outline,
                    size: 15,
                    color: colors.onSurfaceVariant,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '$counterpartLabel: ${counterpartName ?? 'Unknown'}',
                    style: TextStyle(
                      fontSize: 13,
                      color: colors.onSurfaceVariant,
                    ),
                  ),
                  if (harvestedAt != null) ...[
                    const SizedBox(width: 12),
                    Icon(
                      Icons.event_outlined,
                      size: 15,
                      color: colors.onSurfaceVariant,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      DateFormat.yMMMd().format(harvestedAt),
                      style: TextStyle(
                        fontSize: 13,
                        color: colors.onSurfaceVariant,
                      ),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  if (statusNote != null)
                    Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: Text(
                        statusNote!,
                        style: TextStyle(
                          fontSize: 12,
                          color: colors.onSurfaceVariant,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                  TextButton.icon(
                    onPressed: onTap,
                    icon: const Icon(Icons.history, size: 16),
                    label: const Text('History'),
                  ),
                  if (actionLabel != null && onAction != null) ...[
                    const SizedBox(width: 8),
                    FilledButton(
                      onPressed: onAction,
                      child: Text(actionLabel!),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
